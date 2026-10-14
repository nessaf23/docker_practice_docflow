## Отчёт о самостоятельной работе по главе "контейнеризация" студента `Фарафонтовой Анастасии` группы `когорта 33`.

### Итоговый файл Dockerfile приложения `image-compress`

FROM python:3.11.9-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    COMPRESS_RATIO=10 \
    IMAGE_PATH=/data/images

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser && \
    mkdir -p /data/images && chown 10001:10001 /data/images
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

USER 10001:10001
EXPOSE 18080

CMD ["python", "/app/server.py"]

### Итоговый файл Dockerfile приложения `image-serve`

FROM golang:1.22.3-alpine3.19 AS builder

WORKDIR /build

RUN echo 'appuser:x:10001:10001:appuser:/:' > /passwd && \
    echo 'appuser:x:10001:' > /group && \
    mkdir -p /data/images

COPY go.mod go.sum* ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o server .

FROM scratch

COPY --from=builder /passwd /etc/passwd
COPY --from=builder /group /etc/group
COPY --from=builder --chown=10001:10001 /data /data

WORKDIR /app
COPY --from=builder /build/server .

USER 10001:10001
EXPOSE 18080
CMD ["./server", "-image_path=/data/images"]

### Команды для предварительной настройки и запуска приложений совместно

docker compose up --build -d
docker compose ps

### Демонстрация работы системы
bash testdata/test_image_upload.sh
bash testdata/test.sh

Результат: 

test image uploaded OK
compressed image downloaded OK
compressed image size verified
test OK!



### Демонстрация работы встроенного DNS
$docker compose exec proxy getent hosts image-serve image-compress

172.18.0.2        image-serve  image-serve
172.18.0.3        image-compress  image-compress

$docker compose exec proxy wget -S -O- http://image-serve:18080/ 2>&1 | head

Connecting to image-serve:18080 (172.18.0.2:18080)
  HTTP/1.1 400 Bad Request
wget: server returned error: HTTP/1.1 400 Bad Request

$docker compose exec proxy wget -S -O- http://image-compress:18080/ 2>&1 | head

Connecting to image-compress:18080 (172.18.0.3:18080)
  HTTP/1.1 404 NOT FOUND
wget: server returned error: HTTP/1.1 404 NOT FOUND

### Статистика работы контейнеров
Проверка стабильности

fail=0; for i in $(seq 500); do bash test.sh >/dev/null 2>&1 || fail=$((fail+1)); done; echo "ошибок: $fail"
ошибок: 0

(for i in $(seq 500); do bash test.sh >/dev/null 2>&1; done) &
JOB=$!
while kill -0 $JOB 2>/dev/null; do
  docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
done | tee during.txt
wait $JOB
echo "=== после завершения ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | tee after.txt

Во время работы тестового скрипта 

NAME                                            CPU %     MEM USAGE / LIMIT     NET I/O           BLOCK I/O

docker_practice_docflow-main-proxy-1            1.74%     8.938MiB / 31.21GiB   7.41MB / 7.36MB   0B / 4.1kB

docker_practice_docflow-main-image-compress-1   10.99%    30.84MiB / 31.21GiB   5.75MB / 318kB    0B / 2.15MB

docker_practice_docflow-main-image-serve-1      1.14%     5.129MiB / 31.21GiB   303kB / 1.09MB    0B / 0B


NAME                                            CPU %     MEM USAGE / LIMIT     NET I/O           BLOCK I/O
docker_practice_docflow-main-proxy-1            1.77%     8.242MiB / 31.21GiB   8.12MB / 8.06MB   0B / 4.1kB
docker_practice_docflow-main-image-compress-1   11.38%    30.16MiB / 31.21GiB   6.3MB / 349kB     0B / 2.35MB
docker_practice_docflow-main-image-serve-1      1.08%     5.215MiB / 31.21GiB   336kB / 1.23MB    0B / 0B


NAME                                            CPU %     MEM USAGE / LIMIT     NET I/O           BLOCK I/O
docker_practice_docflow-main-proxy-1            1.73%     8.832MiB / 31.21GiB   8.92MB / 8.86MB   0B / 4.1kB
docker_practice_docflow-main-image-compress-1   11.33%    30.79MiB / 31.21GiB   6.92MB / 383kB    0B / 2.58MB
docker_practice_docflow-main-image-serve-1      1.03%     5.387MiB / 31.21GiB   366kB / 1.35MB    0B / 0B

=== после завершения ===
NAME                                            CPU %     MEM USAGE / LIMIT     NET I/O          BLOCK I/O
docker_practice_docflow-main-proxy-1            0.00%     7.805MiB / 31.21GiB   14.1MB / 14MB    0B / 4.1kB
docker_practice_docflow-main-image-compress-1   0.02%     30.26MiB / 31.21GiB   11MB / 607kB     0B / 4.1MB
docker_practice_docflow-main-image-serve-1      0.00%     5.953MiB / 31.21GiB   564kB / 2.14MB   0B / 0B


image-compress нагружен сильнее всех,proxy пропускает весь трафик, image-serve потребляет около 1,1% CPU и около 5 Мб памяти. Дисковых чтений нет (BLOCK I/O 0B / 0B), файлы отдаются из кэша страниц ОС.
После завершения нагрузки CPU падает до ~0%, память возвращается к прежним значениям. 

### Пространства имён
$ PID=$(docker inspect -f '{{.State.Pid}}' $(docker compose ps -q image-serve))

Интерфейсы, настроенные в сетевом пространстве имён image-serve:

sudo nsenter -t $PID -n ip addr

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000

    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    
    inet 127.0.0.1/8 scope host lo
    
       valid_lft forever preferred_lft forever
       
    inet6 ::1/128 scope host proto kernel_lo 
    
       valid_lft forever preferred_lft forever
       
2: eth0@if37: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 

    link/ether d6:e6:32:c4:1c:92 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    
    inet 172.18.0.2/16 brd 172.18.255.255 scope global eth0
    
       valid_lft forever preferred_lft forever

Таблица маршрутизации:

$sudo nsenter -t $PID -n ip route

default via 172.18.0.1 dev eth0 

172.18.0.0/16 dev eth0 proto kernel scope link src 172.18.0.2

Открытые порты TCP:


$sudo nsenter -t $PID -n ss -tlnp

State    Recv-Q   Send-Q     Local Address:Port        Peer Address:Port   Process                                                                    
LISTEN   0        4096          127.0.0.11:38567            0.0.0.0:*       users:(("dockerd",pid=1333,fd=35))                                        
LISTEN   0        4096                   *:18080                  *:*       users:(("server",pid=14696,fd=3))


### iptables
правило DNAT пробрасывает порт 18080 хоста в контейнер proxy (172.18.0.4:18080) 

sudo iptables -t nat -L DOCKER -n -v

Chain DOCKER (2 references)

 pkts bytes target     prot opt in     out     source               destination     
 
    0     0 DNAT       tcp  --  !br-a24fbb09ec36 *       0.0.0.0/0            0.0.0.0/0            tcp dpt:18080 to:172.18.0.4:18080

