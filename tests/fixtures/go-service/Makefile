.PHONY: format lint build test

format:
	gofmt -w ./cmd ./internal

lint:
	golangci-lint run ./...

build:
	go build ./cmd/...

test: build
	go test ./...
