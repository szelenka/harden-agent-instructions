# Project Instructions

## Hard Rules

- Do not commit secrets or credentials
- All changes require tests
- Do not modify CI workflows without approval

## Build & Test

### Billing (Python)
```bash
cd services/billing && pip install -e ".[dev]" && python -m pytest tests/
```

### Gateway (Go)
```bash
cd services/gateway && go test ./...
```

### Infrastructure (Terraform)
```bash
cd infra && terraform fmt -check && terraform init -backend=false && terraform validate
```

## Lint

### Billing
```bash
cd services/billing && ruff check app/
```

### Gateway
```bash
cd services/gateway && go vet ./...
```

## Done Checklist

- [ ] Billing tests pass
- [ ] Gateway tests pass
- [ ] Terraform validates
- [ ] Linters pass for affected zone
