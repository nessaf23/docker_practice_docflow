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
