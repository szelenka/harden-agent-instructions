# Expected Audit Results: polyglot-monorepo-zones

A polyglot monorepo with 3 operationally distinct zones: a Python billing service, a Go API gateway, and Terraform infrastructure. Each zone has its own manifest, lock file, and CI job.

## Zone Detection (Phase 1)

- **Zones detected:** 3
  - `services/billing/` — Python (pyproject.toml, poetry.lock)
  - `services/gateway/` — Go (go.mod, go.sum)
  - `infra/` — Terraform (main.tf, terraform.lock.hcl)
- **Strongest signal:** separate CI jobs with `working-directory` per zone (sufficient alone)
- **Confirming signals:** distinct runtimes, separate lock files per subtree
- **Nesting check:** no nested zones detected

## Split Decision (Phase 2)

- **Zone suppression marker:** not present
- **Command ambiguity:** yes — `cd` prefix commands share similar patterns but require different runtimes and arguments; 6 zone-scoped headings needed (Build x3, Lint x2, plus per-zone done items)
- **Budget pressure:** combined single-file content approaches tier budget with all zones inlined
- **Decision:** split is recommended (mandatory if budget exceeded by >20%)

## Expected Phase 3 Actions

The skill should:
1. Rewrite root `AGENTS.md` to contain only shared constraints:
   - Hard rules (no secrets, tests required, CI approval)
   - Zone pointer table (Zone | Path | Runtime | Purpose)
   - Cross-zone done checklist ("all zone verification passes")
   - Feedback loop rule
2. Create `services/billing/AGENTS.md` with:
   - Drift marker: `<!-- Zone: billing | Root: /AGENTS.md -->`
   - Python build/test commands in fenced code blocks
   - Ruff lint command
   - Billing-specific verification checklist
3. Create `services/gateway/AGENTS.md` with:
   - Drift marker: `<!-- Zone: gateway | Root: /AGENTS.md -->`
   - Go build/test commands in fenced code blocks
   - Go vet lint command
   - Gateway-specific verification checklist
4. Create `infra/AGENTS.md` with:
   - Drift marker: `<!-- Zone: infra | Root: /AGENTS.md -->`
   - Terraform fmt/init/validate commands in fenced code blocks
   - Infra-specific verification checklist

## Evaluation

- **Rubric passes:** 4 (1 root + 3 zones, each scored as merged root + zone)
- **Per-zone budget check:** each merged root + zone document fits within tier budget independently
- **Shared-content issues:** attributed to root only, not duplicated across zone reports

## Negative Assertions

- Zone files do NOT restate root hard rules or constraints
- Zone files do NOT contain cross-zone conventions
- Concatenation of root + any single zone file contains zero duplicated instruction lines
- Root AGENTS.md does NOT contain zone-specific build/test/lint commands

## Key Signals

- The skill must detect 3 distinct operational zones, not treat this as a single-file repo
- The existing single-file AGENTS.md should be identified as creating command ambiguity
- The skill must correctly attribute shared constraints to root and zone-specific commands to zone files
