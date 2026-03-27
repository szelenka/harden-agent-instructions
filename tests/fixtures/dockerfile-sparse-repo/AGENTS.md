# Agent Instructions

## Hard Rules

- Docker is the only available verification signal in this repo
- Do not invent application-level build commands (npm, Python, Go, Maven, etc.) — none exist here
- Do not assume test infrastructure exists — none is present
- Changes to `Dockerfile` or `entrypoint.sh` require rebuild verification

## Build and Verification

Build the container image:

```bash
docker build -t dockerfile-sparse-repo .
```

Verify the image was created:

```bash
docker images | grep dockerfile-sparse-repo
```

Run the container (optional verification):

```bash
docker run --rm dockerfile-sparse-repo
```

Expected output: `start`

## Key Paths

- `Dockerfile` — container build contract (Alpine 3.20 base)
- `scripts/entrypoint.sh` — runtime entry script
- `config/default.env` — runtime configuration (PORT=8080)

## Done-When Checklist

- [ ] `docker build -t dockerfile-sparse-repo .` exits 0
- [ ] `docker images | grep dockerfile-sparse-repo` shows the built image
- [ ] Verification is partial: no tests, no CI, no application-level checks

## Codebase Conventions

- This is a minimal container-only repo with no application code
- Search existing files before creating new ones — keep the repo minimal
- Preserve the Alpine base and shell script simplicity

## Self-Improvement

When you discover repo conventions or failure patterns not covered here, add them to this file in the relevant section. Remove rules that no longer prevent mistakes.
