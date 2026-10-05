
FROM golang:1.22-alpine3.19 AS builder

WORKDIR /build


RUN mkdir /user && \
    echo 'nobody:x:65534:65534:nobody:/:' > /user/passwd && \
    echo 'nobody:x:65534:' > /user/group


COPY go.mod ./

RUN go mod download


COPY . .


RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server .


FROM scratch


COPY --from=builder /user/passwd /etc/passwd
COPY --from=builder /user/group /etc/group

WORKDIR /app


COPY --from=builder /build/server .


USER nobody:nobody


CMD ["./server"]
