# Golden Tasks

Use this file when the user wants examples, when the audit output needs calibration, or when multi-agent coordination is in scope.

## Golden Task 1: Improve A Weak Instruction File

Goal: turn a vague instruction file into a cold-start-ready file.

Steps:

1. Discover the actual build system, CI checks, hooks, and test layout.
2. Identify missing runnable commands, stale paths, vague wording, and absent verification.
3. Fix only the top 5-7 issues in the first pass.
4. Re-run the audit checks and report what still fails.

Expected improvements:

- hard rules moved near the top
- commands placed in fenced code blocks
- key paths mapped to roles
- verification expressed as a done checklist

## Golden Task 2: Create Instructions From Scratch

Goal: create a primary instruction file that works on first invocation.

Section order:

1. Hard rules derived from CI or build constraints
2. Build, test, and lint commands
3. Architecture and key entry points
4. Verification checklist
5. Repo-specific testing or codebase conventions

Stop when the primary file reaches the tier budget. Move deeper taxonomy into references.

## Golden Task 3: Preserve A Good Instruction File

Goal: improve a strong file without collapsing repo-specific grounding.

Rules:

1. Keep concrete path-role mappings that already prevent mistakes.
2. Keep at least one verification-source path and one concrete test path when the repo exposes them.
3. Prune generic prose before removing repo-specific file references.
4. If you shorten a section, preserve the operational noun that makes routing obvious (`action.yml`, `CMakeLists.txt`, `src/routes/`, module names, service names).

Repo-shape reminders:

- GitHub Action repos: keep `action.yml`, source path, and test path visible.
- Workflow-first repos: keep the workflow file visible as the canonical verification source, not just the commands it runs.
- C++ repos: prefer `CMakeLists.txt`, `ctest`, and `clang-tidy` over flattening to generic `make`.
- Gradle repos: keep Gradle-native commands or wrapper usage.
- Maven multi-module repos: keep root manifest plus module names/paths.

## Golden Task 4: Audit a Monorepo With Distinct Operational Zones

Goal: detect operationally independent zones and create appropriate instruction file placement.

Detection:
1. Check for zone suppression marker (`<!-- zones: none -->`)
2. Identify distinct build manifests with different runtimes
3. Check for separate CI jobs per subtree (strongest signal)
4. Confirm with lock files or other signals
5. Run nesting check — discard inner zones
6. Count zones (cap at 5)

Decision:
- 1 zone or ambiguity resolves with headings → single root file
- 2+ zones with different runtimes and budget pressure → split

Output:
- Root AGENTS.md with shared constraints and zone pointer table
- Per-zone AGENTS.md with zone-specific commands and verification
- No restated root constraints in zone files
- Audit summary lists all created zone files

Evaluation:
- Rubric scores root standalone + each zone as merged (root + zone)
- Shared-content issues attributed to root only
- Zone-specific issues attributed to zone file
- Each merged document fits within tier budget independently

**Before** (wrong — everything in one bloated root):
```markdown
# AGENTS.md
## Hard Rules
- Do not commit secrets
- All changes require tests
## Build & Test
### Billing (Python)
cd services/billing && pip install -e ".[dev]" && python -m pytest tests/
### Gateway (Go)
cd services/gateway && go test ./...
### Infrastructure (Terraform)
cd infra && terraform fmt -check && terraform init -backend=false && terraform validate
## Lint
### Billing
cd services/billing && ruff check app/
### Gateway
cd services/gateway && go vet ./...
## Done Checklist
- Billing tests pass
- Gateway tests pass
- Terraform validates
- Linters pass for affected zone
```

**After** (right — split by zone with clean inheritance):

Root `AGENTS.md`:
```markdown
## Hard Rules
- Do not commit secrets or credentials
- All changes require tests
- Do not modify CI workflows without approval

## Operational Zones
| Zone | Path | Runtime | Purpose |
|------|------|---------|---------|
| billing | services/billing/ | Python | Billing API service |
| gateway | services/gateway/ | Go | API gateway |
| infra | infra/ | Terraform | Infrastructure definitions |

Each zone has its own AGENTS.md with zone-specific build, test, and verify commands.

## Done Checklist
- [ ] All zone verification passes
- [ ] No cross-zone regressions
```

Zone `services/billing/AGENTS.md`:
```markdown
<!-- Zone: billing | Root: /AGENTS.md -->
## Build & Test
\```bash
pip install -e ".[dev]" && python -m pytest tests/
\```
## Lint
\```bash
ruff check app/
\```
## Verification
- [ ] pytest passes
- [ ] ruff clean
```

## Negative Calibration: Delete These From Root AGENTS.md

Remove lines like these when they are discoverable and do not change behavior:

- "This project uses Python and pytest."
- "The `src/` directory contains the source code."
- "Please be careful and follow best practices."
- "Run the appropriate tests for your changes."
- "Read the codebase carefully before editing."

Rewrite broad advice into decision gates:

- Weak: "Ask before risky changes."
- Better: "If a command is destructive, networked, privileged, or externally visible, stop and ask for approval before running it."

Move explanatory rationale out of root `AGENTS.md`:

- Too much: "We prefer small diffs because review is easier and historical context matters."
- Better: "Keep changes atomic. Separate mechanical renames from behavioral edits."

## Parallel Discovery Pattern

Default mode is still single-agent ownership. If the environment supports safe delegation, parallelize only discovery tasks such as:

- one agent extracts build targets
- one agent extracts CI checks
- one agent reads existing instruction files

The owning agent merges the findings, decides priorities, and performs or coordinates the edits.

## Multi-Agent Handoff Checkpoint

Use this only when multi-agent work is explicitly enabled.

```markdown
## Checkpoint

Owner: [agent or role]
Files owned: [paths]
Repo facts established:
- [fact]
- [fact]

Open risks:
- [risk]

Verification state:
- [command]: pass/fail/not run

Next action:
- [specific next step]
```

Rules:

- assign one owner per file set
- do not edit another agent's owned files without a handoff
- hand off only after writing the checkpoint

## Dry-Run Verification Reference

When instructions reference a wrapper command, probe it in dry-run mode to discover underlying binaries:

| Wrapper | Dry-Run Command | What To Check |
|---------|----------------|---------------|
| `make <target>` | `make -n <target>` | Each shell command printed — extract binary names and `command -v` each |
| `tox -e <env>` | `tox -e <env> --list-dependencies` then read `commands` from `tox.ini` | Deps installable, command binaries present |
| `npm run <script>` | Read `scripts.<name>` from `package.json` | Resolve the actual binary (e.g., `eslint`, `jest`) |
| `poetry run <cmd>` | `poetry run which <cmd>` | Binary resolvable inside Poetry virtualenv |
| `uv run <cmd>` | `uv run which <cmd>` | Binary resolvable inside uv virtualenv |

Procedure:

1. Run the dry-run command for each wrapper-style verification command
2. Parse the output for binary names (first token of each shell command line)
3. Verify each discovered binary with `command -v <binary>` or the tool-specific equivalent
4. If a binary is missing, report it as a cold-start blocker — the instruction looks valid but will fail at runtime
5. If the dry-run itself errors (e.g., `make -n test` fails because the Makefile has a syntax issue), report the error as a cold-start blocker

## Before / After Calibration

Use these pairs to calibrate the difference between weak and actionable instruction content.

**Before** (weak — vague, no commands, no paths):

```markdown
## Testing
Run tests to make sure everything works. We use pytest for testing.
Make sure to add tests for new features.
```

**After** (actionable — concrete command, location, naming convention):

````markdown
## Testing

```bash
python -m pytest tests/          # unit + integration tests
```

- Test files mirror source: `tests/test_invoice_service.py` for `app/invoice_service.py`
- Name tests: `class TestCreateInvoice` -> `test_rejects_negative_amounts`
- Use `unittest.mock.patch` for DB calls — never hit a real DB in unit tests
````

**Before** (weak — blanket rule, no conditions):
```markdown
## Verification
Run all tests and the linter before committing.
```
**After** (actionable — verification scoped by change type):
````markdown
## Verification
- `src/schemas/` or `src/validators/` changed → full: `pytest tests/ && mypy src/`
- `docs/` only → lint: `ruff check docs/`
- Other changes → fast-fail: `pytest tests/ -x --ff`
````

## Conditional Rule Patterns

When writing rules in instruction files, prefer conditional rules over blanket rules. Three patterns:

**Activation gate** — when does the rule fire?

```markdown
If the change touches `src/schemas/` or `src/validators/`, run the full type-check suite.
If the PR adds a new dependency, verify it against the project's runtime version constraints.
```

**Decision gate** — what action for what context?

```markdown
## Verification by change type
- Schema or validator changes → full: `pytest tests/ && mypy src/`
- Documentation only → lint: `ruff check docs/`
- Other changes → fast-fail: `pytest tests/ -x --ff`
```

**Escape hatch** — when can you skip or override?

```markdown
Always run unit tests before committing.
Skip integration tests only for changes isolated to `docs/` or `README.md`.
Never skip pre-commit hooks unless the user explicitly passes `--no-verify`.
```

Rules:

- Blanket rules (no conditions) are appropriate for universal constraints: "never commit secrets," "always run the linter." Use them sparingly.
- Conditional rules reduce wasted verification on low-risk changes and ensure thorough verification on high-risk changes.
- Every escape hatch needs a boundary — "skip X" without "only when Y" is a loophole.
- The Decision Boundary Precision rubric criterion scores for these patterns at medium+ repos.

## Enforcement Recommendation Pattern

When the audit finds no automated enforcement of instruction-file claims (Enforcement sustainability: unenforced), recommend the lightest option that fits the repo's existing infrastructure. Do not generate CI or hook configs — recommend the pattern and let the team implement it.

Recommended patterns, from lightest to heaviest:

1. **Pre-commit hook**: validate that paths referenced in the instruction file still exist before each commit
2. **CI step**: run the verification commands from the done-when checklist as a CI job on PRs that touch instruction files or build config
3. **Scheduled cold-start re-check**: periodically re-run cold-start checks (binary availability, path existence, command execution) to catch drift from dependency upgrades or infrastructure changes

Include the recommendation in the `### Remaining Issues` section of the audit output, not as a fix — the skill audits instruction files, not CI pipelines.

## Rubric Migration Log

When rubric criteria are renamed, merged, split, or removed, record the change here so that agents and users referencing old names can resolve them.

| Date | Change | Old Name(s) | New Name(s) | Notes |
|------|--------|-------------|-------------|-------|
| — | (no changes yet) | — | — | — |

Rules:

- Add a row when any criterion in RUBRIC.md is renamed, merged, split, or removed
- Keep old names searchable — agents may encounter them in existing instruction files or cached audit results
- If a criterion is split, list both new names and note which aspects each covers
- If a criterion is merged, note which old criteria fed into the new one
