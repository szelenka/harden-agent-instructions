# Expected Audit Results: rust-service-with-policy

A small Rust service repo with no instruction files, a `Cargo.toml`, and explicit fmt/lint/test policy surfaces.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `Cargo.toml` plus `rustfmt.toml`
- **Verification commands:** `cargo test`, `cargo fmt --check`, `cargo clippy -- -D warnings`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks centered on the repo-defined Rust verification surface
- A note that formatting and lint expectations come from `rustfmt.toml` and `Cargo.toml`
- Key paths with roles (`src/main.rs` — CLI entry point, `src/policy.rs` — policy logic, `tests/cli_test.rs` — deterministic verification)

## Key Signals

- The skill should not treat this like the sparse git fixture or the shallow Rust command-family fixture
- The audit should preserve the multi-surface verification contract: test, format-check, and clippy
- The done checklist should distinguish deterministic execution from policy expectations grounded in repo config
