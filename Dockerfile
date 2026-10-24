FROM golang:1.20-alpine AS build
RUN apk add --no-cache git
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/kcpraw_server ./server && \
    CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/kcpraw_client ./client

FROM alpine:3.19
COPY --from=build /out/kcpraw_server /out/kcpraw_client /usr/local/bin/
# 默认工作在伪造 TCP(raw socket)之上, 容器运行时需要 NET_RAW 能力:
#   docker run --cap-add=NET_RAW ...
# 使用 --udp 模式时则需要放行对应 UDP 端口, 例: -p 29900:29900/udp
EXPOSE 29900/udp 12948
CMD ["kcpraw_server", "-h"]
