# Expected Audit Results: gradle-multimodule

A multi-module Gradle repo with 3 subprojects (app, core, api) sharing one build system, one runtime (Java 17), and one CI job.

## Zone Detection (Phase 1)

- **Zones detected:** 0
- **Why:** shared root build system (`build.gradle.kts` with `subprojects {}` block), same runtime everywhere (Java 17), single CI job (`./gradlew build`), no separate lock files per subtree
- **Not a signal:** per-module `build.gradle.kts` files are part of the shared Gradle build, not independent build surfaces

## Split Decision (Phase 2)

- **Decision:** single root file (0-1 zones, stop at step 2)
- **No zone files created**

## Expected Phase 3 Actions

The skill should create or improve a single root `AGENTS.md` containing:
- Hard rules section
- Build/test commands: `./gradlew build`, `./gradlew test`
- Module descriptions with roles (app, core, api)
- Key paths with roles
- Done checklist referencing the single build/test surface

## Negative Assertions

- No zone-specific `AGENTS.md` files created in app/, core/, or api/
- No zone pointer table in root (no zones to point to)
- The skill must NOT treat Gradle subprojects as operational zones

## Key Signals

- This fixture validates the "not a signal" rule: multi-module builds with a shared root manifest are one zone, not multiple zones
- The single CI job with `./gradlew build` confirms operational unity
- Per-module build files are configuration, not independence
