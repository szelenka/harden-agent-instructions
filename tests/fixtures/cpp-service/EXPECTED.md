# Expected Audit Results: cpp-service

A small C++ service repo with no instruction files, a `CMakeLists.txt`, and a root `Makefile`.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `CMakeLists.txt` plus root `Makefile`
- **Verification commands:** `make lint`, `make build`, `make test` (backed by `clang-tidy`, `cmake --build`, `ctest`)

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Build/test/lint commands in fenced code blocks (`make build`, `make test`, `make lint` or the underlying cmake/ctest/clang-tidy equivalents)
- Key entry points with roles (`src/main.cpp` — server entry point, `src/handler.cpp` — request handling, `include/handler.h` — public API, `tests/handler_test.cpp` — unit tests)
- Architecture description limited to a small C++20 service with `src/`, `include/`, `tests/` layout

## Key Signals

- The skill must prefer `cmake`, `ctest`, and `make` over invented npm, Python, or Go commands
- The audit should note the CMake build system and the Makefile convenience targets
- The done checklist should use `make test` and `make lint` (or the underlying cmake/ctest/clang-tidy commands) as canonical verification
- The skill should recognize `clang-tidy` as the linting tool, not invent a different linter
