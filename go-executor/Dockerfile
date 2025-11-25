# go-executor/Dockerfile

# 1. Builder Stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod .
COPY go.sum .
RUN go mod download

COPY . .
RUN go build -o /go-executor main.go

# 2. Final Stage
FROM alpine:latest

RUN apk add --no-cache ca-certificates docker-cli

WORKDIR /usr/bin

COPY --from=builder /go-executor /go-executor

ENTRYPOINT ["/go-executor"]