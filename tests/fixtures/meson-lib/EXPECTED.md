# Expected Audit Results: meson-lib

A C library using the Meson build system with `meson.build`, no instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** Meson (`meson.build`)
- **Verification commands:** `meson setup builddir`, `meson compile -C builddir`, `meson test -C builddir`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`meson setup builddir`, `meson compile -C builddir`, `meson test -C builddir`)
- Key paths with roles (`src/mathutil.c` — library implementation, `include/mathutil.h` — public API header, `tests/test_mathutil.c` — unit tests, `meson.build` — build definition)
- Architecture description noting a C17 shared library with pkg-config support

## Key Signals

- The skill must use `meson` commands, NOT `cmake`, `make`, or `gcc` directly — the `meson.build` file is definitive
- The audit should note the Meson build system with Ninja backend (implicit)
- The done checklist should use `meson test` as canonical verification
- The skill must NOT invent `cmake`, `make`, `npm`, or `python` commands
- The skill should note the `test()` declaration in `meson.build` as the test surface
