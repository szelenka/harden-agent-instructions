# Project Instructions

## Build & Test

```bash
./gradlew build
./gradlew test
```

## Modules

- `app` — main application, depends on core and api
- `core` — shared business logic
- `api` — API layer, depends on core
