# Agent Instructions

## Hard Rules

- Run `make verify` from the root to execute all verification steps across services
- Run focused checks per service: `make -C services/ml-proxy lint` and `make -C services/ml-proxy render` for ml proxy, `make -C services/wordcloud diff` for wordcloud
- Do not modify `clusters/dev/values.yaml` without testing the render output
- Changes to Helm charts require running `helm lint` before commit

## Verification Commands

Root verification:
```bash
make verify
```

Per-service checks:
```bash
# ml proxy
make -C services/ml-proxy lint
make -C services/ml-proxy render

# Wordcloud
make -C services/wordcloud diff
```

## Key Paths

- `Makefile` — root orchestration that calls nested service verification
- `services/ml-proxy/Makefile` — ml proxy deploy checks (helm lint, helm template)
- `services/wordcloud/Makefile` — wordcloud diff workflow (helmfile diff)
- `charts/ml-proxy/Chart.yaml` — Helm chart definition
- `clusters/dev/values.yaml` — shared environment values for dev cluster

## Done Checklist

- [ ] Ran `make verify` from root (required when changes span multiple services or touch shared config)
- [ ] Ran focused service checks when changes are isolated to one service directory
- [ ] Verified helm chart lints cleanly if chart or values changed
- [ ] Tested helm template render output if chart or values changed
