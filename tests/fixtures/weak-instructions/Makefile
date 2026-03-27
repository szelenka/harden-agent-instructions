.PHONY: fmt lint build test run migrate

fmt:
	gofmt -w ./cmd ./internal

lint:
	golangci-lint run ./...

build:
	go build -o bin/server ./cmd/server

test:
	go test ./...

run:
	go run ./cmd/server

migrate:
	go run ./cmd/migrate
