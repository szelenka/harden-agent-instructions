# Expected Audit Results: rust-cli

A small Rust CLI repo with no instruction files, a `Cargo.toml`, and a root `Makefile`.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `Cargo.toml` plus root `Makefile`
- **Verification commands:** `make lint`, `make build`, `make test` (backed by `cargo clippy`, `cargo build`, `cargo test`)

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Build/test/lint commands in fenced code blocks (`make lint`, `make build`, `make test` or the underlying `cargo` equivalents)
- Key entry points with roles (`src/main.rs` — CLI entry point with clap argument parsing, `src/config.rs` — configuration loading, `tests/cli_test.rs` — integration test)
- Architecture description limited to a small Rust CLI with a `src/` layout

## Key Signals

- The skill must prefer `cargo` and `make` over invented npm, Python, or Go commands
- The audit should note both the Makefile targets and the underlying cargo commands
- The done checklist should use `cargo clippy`, `cargo test`, or the Makefile targets as canonical verification
- The skill should note `cargo fmt` as the formatting check, not invent a different formatter
