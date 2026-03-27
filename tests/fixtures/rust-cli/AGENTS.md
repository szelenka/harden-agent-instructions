# rust-cli

Small Rust CLI tool for processing input with configurable output formats.

## Hard Rules

- Run `make lint` before committing — clippy must pass with `-D warnings`
- Run `make test` before submitting changes — all tests must pass
- Never disable clippy warnings in code — fix the underlying issue
- Use existing dependencies only — do not add new crates without confirming compatibility with edition 2021
- Extend existing modules rather than creating new files

## Quick Start

```bash
make build              # Build release binary
make test               # Run test suite
make lint               # Run clippy with warnings as errors
make fmt                # Format code with rustfmt
```

## Key Entry Points

- `src/main.rs` — CLI argument parsing and entry point (binary: rust-cli)
- `src/config.rs` — Application configuration loading
- `tests/cli_test.rs` — Integration tests using assert_cmd

## Done Checklist

A task is complete when:

- [ ] `make lint` passes (clippy with no warnings)
- [ ] `make test` passes (all tests green)
- [ ] `make fmt` applied (code formatted)
- [ ] Changes use existing clap/serde patterns from `src/main.rs` and `src/config.rs`

## Codebase Conventions

- CLI parsing: Use `clap::Parser` derive macro — see `src/main.rs` for existing pattern
- Configuration: Serde `Deserialize` structs — extend `AppConfig` in `src/config.rs` rather than creating new config types
- Testing: Use `assert_cmd` for CLI integration tests — see `tests/cli_test.rs` for the pattern

## Enforcement

This repo has no CI or pre-commit hooks. Verify changes manually using the done checklist commands before sharing your work. Maintainers: consider adding a pre-commit hook that runs `make lint && make test` to catch issues early.

## Self-Improvement

When you discover a Rust idiom, CLI pattern, or error recovery approach that should guide future work on this repo, add it to this file under the most specific section. Session-specific debugging notes belong in your agent memory, not here.
