---
name: harden-agent-instructions
description: Audits and iteratively improves agent instruction files (AGENTS.md open standard, plus tool-specific variants like CLAUDE.md, .cursorrules, copilot-instructions.md, codex instructions) for any repository. Use when asked to audit, analyze, assess, evaluate, harden, improve, create, or align agent instructions.
---

# Harden Instructions

## Hard Rules

- Verify repo facts before judging instructions. Do not assume paths, commands, CI jobs, hooks, or contributors.
- Treat the build system, CI config, and enforcement hooks as the source of truth. Instructions must match them.
- When discovery requires enumerating files, matching patterns, or listing targets, execute the search literally and report all matches. Do not sample, estimate, or substitute judgment for mechanical inspection. Creative discretion applies to what you do with the results, not to whether you collect them.
- Do not create files, directories, command patterns, or verification workflows that do not already exist in the repo unless the user explicitly approves. Extend and adapt what the repo already has. "Split references" means split into a file you create for instruction content, not invent new repo conventions.
- Fix cold-start blockers first: missing runnable commands, stale paths, missing key entry points, or nonexistent verification steps.
- Default to single-agent execution.
- Fewer high-impact instructions outperform comprehensive coverage. Prefer focused over complete. Split reference-heavy material into secondary files when the repo tier needs it.
- Prefer concrete terms: exact verbs, real file paths, command names, explicit conditions, and concrete change triggers. Replace vague qualifiers like "risky", "important", or "non-trivial" with repo-grounded boundaries. Cut synonyms, hedges, and filler.
- Use the same shared terms across the primary file and references. Prefer `activation gate`, `tier-required behavior`, `done-when checklist`, and `discoverable`; do not rename the same concept across files.
- When two fixes cost about the same, choose the repo-grounded change that removes the most active failure modes.
- Treat root `AGENTS.md` as a minimal control surface: constraints, exact commands, approval boundaries, non-obvious behavior corrections, and done criteria only.
- Make approval boundaries explicit for destructive, privileged, networked, or externally visible actions. Good instructions say when the agent must stop, escalate, or ask for approval before running them.
- Root `AGENTS.md` is for operational instructions only. Do not add explanatory rationale unless the rationale itself changes agent behavior.
- Write tool-agnostic rules in `AGENTS.md`. No model-specific UX assumptions or tool-only gestures; avoid tool-specific wording when a portable alternative exists. Add tool-specific sections only when behavior genuinely differs across platforms.
- Limit each edit pass to 5-7 fixes, then re-check. If P1-P4 issues remain (cold-start failures, budget violations, stale paths, or missing tier-required sections) and you have done fewer than 3 passes, continue. If only P5-P6 issues remain, present them and ask the user whether to continue.
- When you discover a recurring convention, failure mode, or missing rule that would help future sessions, persist it into the repo's instruction files.
- Every audit response MUST include the `## Audit Summary` block and the `### Rubric Scores (final)` section. The response is incomplete without them.

## When To Use
Use this skill when the task is to audit, create, or improve AI agent instruction files. `AGENTS.md` is the open standard; tool-specific variants include `CLAUDE.md` (Anthropic), `.cursorrules` (Cursor), `copilot-instructions.md` (GitHub Copilot), and codex instructions (OpenAI).
Activate it when the user asks to audit, analyze, assess, evaluate, harden, improve, create, or align agent instructions, or asks whether those files match repo reality, this skill, or the rubric.

Do NOT activate for general documentation (READMEs, API docs, changelogs), non-agent-facing files, or code review tasks that don't involve instruction files.

If the request sounds diagnostic ("analyze", "audit", "review", "assess"), treat it as permission to fix high-priority instruction defects during the same turn unless the user explicitly asks for a report-only pass.

## Operating Mode
**Default:** single agent with parallel read-only discovery tracks when useful.
**Opt-in multi-agent:** only use when the user asks for it or the tool supports explicit delegation and handoff. If multiple agents are used, assign one owner per file set and require a written checkpoint before handoff.

## Quick Workflow
Copy this checklist and track progress:

```
- [ ] Phase 1: Discovery — repo facts collected (build, CI, hooks, paths)
- [ ] Phase 2: Assess — cold-start checks scored, rubric rated
- [ ] Phase 3: Fix — top 5-7 issues edited (pass N of 3)
- [ ] Phase 4: Verify — re-check passed or remaining gaps reported
```

## Phase 1: Discovery
Start with instruction files and the primary build manifest. Then inspect CI configs, local enforcement hooks, and contributor history when VCS metadata exists.

Collect these facts:

- Which instruction files exist, what each one covers, and whether they contain managed-content markers (e.g., `<!-- BEGIN project-specific -->`, `<!-- repo-standards:doc-managed:<scope>:start -->`) from an external distribution tool. When repo-standards markers are present, note which sections are machine-maintained — edits outside those markers persist, edits inside may be overwritten by the automated updater
- Build manifests, task runners, package configs, and every named verification target
- CI/CD jobs and the exact verification commands they run
- Pre-commit hooks or VCS hooks and which checks they enforce locally
- Contributor count from version control history, or mark it unavailable when the repo is not a checkout
- Repo languages, estimated LOC tier, and whether tests exist

Discovery rules:

- Read each instruction file you find. Do not stop at existence checks.
- Prefer manifests and configs over source-tree exploration when identifying commands.
- Record which commands, binaries, and task runners the repo uses, and note dependency versions from lock files and manifests.
- Note the project's runtime and framework version constraints (e.g., `engines` in package.json, `python_requires` in pyproject.toml).
- If tests exist, record at least one concrete test file path and its role. If a workflow or hook config exists, record that file as a verification source, not just the commands it runs.
- If a workflow file is the strongest verification source, carry that path into the final instruction file and label it as the verification contract or canonical source of truth instead of flattening it into plain commands.
- If CI, hooks, lock files, or task runners are absent, say so explicitly and downgrade confidence instead of inventing policy.
- If the repo has multiple manifests or task runners, list each candidate workflow and mark which one appears primary from the evidence.
- For large repos, estimate LOC from tracked file sizes instead of reading the full tree.
- Distinguish enforced policy from aspirational guidance.
- If VCS metadata is unavailable, mark contributor count and source-control workflow as unverified instead of guessing.

Discovery is complete when all six fact categories above are populated or confirmed absent. Do not proceed to Phase 2 until you can state the repo tier, list every verification command, and name the instruction files (or confirm none exist).

### LOC Estimation

Estimate LOC as total bytes of tracked source files divided by 40. Cap at 5,000 files. Filter extensions based on the repo languages you detected.

| Tier | LOC Range |
|------|-----------|
| Small | <= 10,000 |
| Medium | 10,001 - 50,000 |
| Large | 50,001 - 200,000 |
| Very Large | > 200,000 |

### Zone Detection

Check root AGENTS.md for `<!-- zones: none -->`. If present, skip zone detection.

Identify operational zones: subtrees with independent build/test/verify commands.

Strong signals (CI jobs per subtree with `working-directory` or path filters are sufficient alone; others need one confirming signal): distinct build manifests with different runtimes at different paths, separate lock files per subtree.

Medium signals (need 2+ to trigger): same language but separate test suites and build targets per subtree, separate deploy configs per subtree.

Not a signal: just having subdirectories, multi-module builds with a shared root manifest (Gradle/Maven), same runtime everywhere with shared manifests.

Nesting check: if zone A's path is a prefix of zone B's path, discard zone B.

Maximum zones: 5. If more detected, warn and process only the top 5 by signal strength.

Record each zone with: path, runtime/language, build command, test command, primary manifest.

If 0-1 zones found, proceed with single root file. If 2+ zones, carry the zone list into Phase 2.

## Phase 2: Assess
Evaluate the instruction files against repo reality.

Cold-start checks must all pass:

- Build, test, and lint commands appear in fenced code blocks
- Key entry points are named with their roles, grounded by concrete file paths that exist in the repo — include verification sources (CI workflows, pre-commit configs, task runners) alongside runtime entry points
- Every referenced verification command exists and its binary is available on `$PATH` (e.g., `command -v pio`, `which pytest`) or via a declared task runner (e.g., `npm run`)
- Instructions define approval boundaries for destructive, privileged, networked, or externally visible actions instead of only listing the commands
- Do not treat passing unit tests alone as sufficient when a change touches business rules, schemas, validators, data transformations, deploy or infra logic, or other behavior with repo-defined semantic checks; strong instructions point agents to fixtures, golden outputs, invariants, smoke tests, or required human review when those exist
- When a command wraps other tools (e.g., a Makefile target calling `poetry run pytest`), dry-run the wrapper to discover the underlying commands and verify those binaries too

### Dry-Run Verification

When instructions reference a wrapper command (Makefile target, tox environment, npm script, etc.), probe it in dry-run mode to discover the underlying binaries it invokes. See [`references/GOLDEN_TASKS.md`](references/GOLDEN_TASKS.md) § Dry-Run Verification Reference for the per-wrapper table and procedure.

If dry-run is not available or safe, fall back to static analysis: read the wrapper config and extract command strings directly.

Fallback rules for sparse repos:

- If no instruction file exists, assess repo facts first and then create the minimal instruction file that the tier requires.
- If no CI or hooks exist, do not invent CI-backed policy; score `Codified Policy Enforcement` as `Weak` per the rubric and note the absence.
- If no CI or hooks exist, you may recommend lightweight enforcement, but do not name a specific new workflow, hook, or config path unless that path already exists in the repo.
- If no task runner exists, list the discovered direct commands and mark verification as partial rather than pretending there is a single canonical entry point.
- If no tests exist, say that coverage is absent and keep the done checklist focused on the deterministic checks that do exist.
- If the repo shape is ambiguous, say which interpretations are plausible and avoid fabricated architecture claims.

Load [`references/RUBRIC.md`](references/RUBRIC.md) at the start of Phase 2.

Scoring rules:

- Score repo facts first, then score the instruction file against those facts.
- Score every always-on Core Criterion as `Missing`, `Weak`, or `Pass`.
- If a criterion has an activation gate, check the gate first. If inactive, score `Not Applicable`.
- Activate a gated criterion only when the signal materially changes what good instructions must contain. Do not activate on a one-off mention that adds no real decision surface.
- Keep activation gates criterion-specific. Do not activate a broader neighboring criterion from a narrower signal alone, and do not use repo size by itself as a proxy for a missing decision surface; for example, approval boundaries by themselves do not activate `Scope Boundaries`, one generic verification command does not activate `Verification Routing`, and one obvious deterministic check does not activate `Deterministic Verification`.
- If the needed evidence is not inspectable from the workspace, score `Unverified`.
- Score only Advanced Criteria whose gates are active.
- If multiple guidance surfaces exist, score `Cross-Document Consistency` against overlapping facts, commands, constraints, and output rules.
- Use the rubric's Scoring Shortcuts and Applicability Rules to break ties. Do not restate that logic here.
- When the same evidence touches multiple criteria, score the narrowest active criterion first: startup -> structure -> grounding -> per-rule checks -> done-when -> decision boundary -> verification routing -> deterministic verification -> blast radius -> review shape -> cross-document drift. Collapse broader duplicates unless the weakness still survives after the narrower fix. Do not manufacture broader criteria just because a nearby gate is active.

Score both tracks: tier-required behaviors (table below) AND all rubric criteria whose activation gates are met.

### Budget Check

**Actionable instruction count**: count imperatives, commands, and conditional rules. Target <150 in the root file. Above 150, split into references.

| Repo Size | Primary File Lines | Token Warning | Token Danger |
|-----------|--------------------|---------------|--------------|
| small | 200 | 4,000 | 8,000 |
| medium | 300 | 6,000 | 12,000 |
| large | 400 | 8,000 | 15,000 |
| very large | 500 | 10,000 | 18,000 |

Line budgets are outer bounds, not targets. If actionable lines / total lines < 60%, cut prose and discoverable content.
Delete accurate-but-discoverable lines before adding new ones. Every line must prevent a likely failure; do not emit that rationale into the file unless it changes behavior.

### Zone Assessment (when 2+ zones detected)

- Can the root file cover all zones without command ambiguity? (Ambiguity: same verb/different args across zones, or >4 zone-scoped headings needed) → single root with headings
- Estimate combined content. Exceeds tier line budget by >20%? → split is mandatory
- Otherwise split is recommended but optional
- Split placement: shared constraints in root, zone-specific commands in zone files
- Zone files inherit root constraints — do not restate

### Tier-Required Behaviors

This table lists required **behaviors in the instruction surface**. Use a dedicated section only when the repo needs one. If the repo is conventional and the behavior is obvious from manifests or the tree, keep the root file minimal and score the behavior through rubric evidence instead of forcing a section. Parenthetical notes show the rubric criterion each behavior feeds into. `conditional` means the behavior becomes tier-required only after that rubric item's activation gate is active; the tier table never activates a gated criterion by itself.

| Behavior / content | Rubric Criterion | Placement | Small | Medium | Large | Very Large |
|--------------------|-----------------|-----------|-------|--------|-------|------------|
| Hard rules / constraints | Instruction Salience, Codified Policy Enforcement | root only | yes | yes | yes | yes |
| Build, test, lint commands | Startup Reliability | root only | yes | yes | yes | yes |
| Non-obvious entry points with roles | Startup Reliability | root only | yes | yes | yes | yes |
| Done-when checklist | Done-When Checklists | root only | yes | yes | yes | yes |
| Codebase drift prevention | Codebase Drift Prevention | root only | yes | yes | yes | yes |
| Review burden reduction | Review Burden Reduction | root or reference | — | conditional | conditional | conditional |
| Structural orientation when layout is non-obvious or failure-prone | Structural Orientation | root or reference | — | conditional | conditional | conditional |
| Testing conventions | Testing Conventions | root or reference | — | conditional | conditional | conditional |
| Error recovery patterns | Failure Blast Radius Awareness | root if immediate side effects; else root or reference | — | conditional | conditional | conditional |
| Decision boundary precision | Decision Boundary Precision | root if high-frequency; else root or reference | — | conditional | conditional | conditional |
| Self-improving feedback loop | Self-Improving Feedback Loop | root only | yes | yes | yes | yes |
| Scope boundaries | Scope Boundaries | root only | — | — | conditional | conditional |
| Source control workflow (2+ contributors when VCS evidence exists) | Source Control Workflow | reference preferred unless prohibitive | — | conditional | conditional | conditional |
| Split references / on-demand loading | Context Budget Design (advanced) | reference only | — | — | conditional | conditional |
| Zone-specific instruction files | Context Budget Design | zone root | — | — | conditional | conditional |

## Phase 3: Fix
Every audit pass should remove at least as many lines as it adds, unless the file is newly created.

Edit instruction files directly. Fix in this order:

1. Cold-start failures
2. Budget violations in the primary file
3. Prune stale, discoverable, or behaviorally useless root-file content — actively delete known anti-patterns: "follow best practices", "be careful", "ensure quality", "make sure everything works", and any rule that could be pasted unchanged into any repo
4. Stale paths, nonexistent commands, or unverified dependency versions
5. Missing tier-required behaviors that the repo actually needs
6. Weak verification guidance, decision-gate precision, dependency guidance, or feedback-loop gaps
7. Lower-priority rubric weaknesses

For the full fix-priority-to-rubric-criterion mapping, see [`references/RUBRIC.md`](references/RUBRIC.md) § Fix Priority to Rubric Crosswalk.

When creating instructions from scratch, write sections in this order until you hit the tier budget:

1. Hard rules derived from CI, lint, hooks, or build constraints
2. Build, test, and lint commands in fenced code blocks
3. Non-obvious entry points, structural traps, and wrong-layer risks only when they change agent behavior
4. Dependency management: repo-grounded library preference, version verification, compatibility constraints
5. Done-when checklist with quality-oriented completion signals — when the repo involves parsing, transforms, or data conversion, include completion gates that catch single-case implementations (e.g., tests must cover 3+ input variations per transform, use format-complete libraries instead of sample-fitted logic)
6. Testing conventions, naming conventions, and codebase conventions as needed

Before adding content, apply the discoverability test:

- Discoverable means recoverable from one direct inspection of repo artifacts such as manifests, task-runner configs, CI files, lock files, or the obvious tree. If you cannot name the artifact and the one tool call that surfaces the fact, do not classify it as discoverable.
- If discoverable: don't add it unless agents repeatedly get it wrong or a hidden caveat changes behavior.
- If partially discoverable: add only the non-obvious part (e.g., don't say "we use pytest" if pyproject.toml declares it; DO say "run pytest with `--tb=short -q` because the default output overflows context").
- If already present but discoverable, stale, or behaviorally inert: delete it or move it out of the root file before adding anything new.
- For every rule — new or existing — identify privately the failure it prevents. If you cannot name one, cut the rule.
- For already-strong files, preserve concrete path-role mappings and verification paths unless they are wrong. When verification is split across multiple concrete surfaces with different operational roles, keep those surfaces explicit instead of collapsing them into a generic summary. Prune generic prose before collapsing repo-specific grounding.

Keep the file action-oriented:

- Imperative rules over prose; operational instructions over rationale; file-role mappings over directory dumps
- Reuse the same term for the same concept; prefer repo-native nouns over abstract synonyms
- Commands that already exist over inventing new workflows; when a repo task runner or workflow defines the canonical verification surface, prefer it over language-native fallback commands; repo-adopted libraries over hand-rolled implementations (verify adoption from manifests, lock files, or existing modules)
- Prefer named repo scripts or existing repo task runners for repeated non-trivial commands that are long, option-heavy, approval-sensitive, or encode important defaults; do not wrap simple one-line commands just to avoid retyping them
- When the chosen verification surface defines multiple canonical commands that are meant to run together (for example build + test in one root workflow), preserve that full command set in the done-when checklist instead of collapsing it to one representative command
- Conditional rules over blanket rules — attach activation gates (`if X changed`), decision gates (`then run Y`), and escape hatches (`skip Z unless W`)
- When you add a decision gate, prefer this shape: trigger -> action -> escalation -> minimum deterministic verification
- Do not duplicate the same defect across adjacent criteria; if a weak score disappears once the earlier, narrower criterion is fixed, collapse the later score too
- Deterministic verification over LLM-based review; quality metrics (coverage delta, complexity) over volume metrics (LOC, PR count)
- Minimal root `AGENTS.md`: constraints, exact commands, approval boundaries, non-obvious conventions, done criteria. Split references rather than bloating the primary file
- If the instruction file has managed-content markers, write fixes into the project-specific section only; report conflicts with managed content as findings
- Match instruction structure to repo facts — do not force software-app sections onto docs, infra, data, or prompt repos
- Repo-shape reminders: GitHub Action repos should name `action.yml`, source, and test paths; C++ repos should preserve `CMakeLists.txt`/`ctest`/`clang-tidy` when present; Gradle repos should preserve Gradle-native commands; Maven multi-module repos should preserve root manifest plus module paths.
- Workflow-first repos should keep the workflow path visible in Key Paths and route the done-when checklist through that workflow-backed verification source.

When creating zone files:
- Root AGENTS.md: shared constraints, approval boundaries, cross-zone conventions, zone pointer table (Zone | Path | Runtime | Purpose)
- Zone AGENTS.md: build/test/lint commands, entry points, zone-specific traps, zone-specific verification
- Zone files do not restate root constraints
- If AGENTS.md already exists at zone path, merge: replace content between `<!-- BEGIN zone-specific -->` and `<!-- END zone-specific -->` markers (idempotent on re-runs); if markers absent, append them
- Zone drift marker at top of each zone file: `<!-- Zone: name | Root: /AGENTS.md -->`

For before/after calibration examples, see [`references/GOLDEN_TASKS.md`](references/GOLDEN_TASKS.md) § Before / After Calibration.

## Phase 4: Verify
Re-run the Phase 2 checks against the edited files. Apply the iteration logic from Hard Rules.

## Self-Improvement Rule

When you discover a convention or failure pattern that is both:

- non-obvious from the repo layout, and
- likely to help future agents avoid repeated mistakes,

persist it into the repo's instruction file you are editing. Repo-universal conventions go in instruction files. Session-specific or user-specific insights go in agent memory (e.g., `MEMORY.md`). The test: "would a different contributor's agent need this?" If yes, instruction file. If no, agent memory.
Prune too: remove rules that no longer prevent a real mistake, duplicate repo evidence, or belong in a secondary reference instead of the primary file.

## Output Format
Return an action-oriented summary in fix priority order. The response is incomplete if `### Rubric Scores (final)` is missing.
Allowed score values: `Missing`, `Weak`, `Pass`, `Not Applicable`, `Unverified`.

```
## Audit Summary
Cold-start ready: yes/no
Instruction files: [list with line counts]
Repo tier: small/medium/large/very large
Passes completed: N
Enforcement sustainability: enforced / partially enforced / unenforced
```

Use **enforced** when CI, hooks, or scheduled checks validate all key instruction claims (referenced commands run, referenced paths exist, verification passes). Use **partially enforced** when some claims are validated by automation but others rely on manual compliance — e.g., CI runs tests but no check verifies that referenced paths still exist. Use **unenforced** when no automated system validates instruction claims against repo reality. Flag partially enforced and unenforced as sustainability risks in Remaining Issues.

### Fixes Applied
- [change, grouped by priority]

### Remaining Issues
- [anything still below Pass that wasn't addressed]

### Rubric Scores (final)
Render scores as a compact table with columns: Criterion, Score, Evidence. Use any clear Markdown-friendly table format the environment supports. Show only criteria scored `Weak`, `Missing`, `Not Applicable`, or `Unverified`. Omit criteria that pass. If the table is empty, say "All scored criteria pass."
## Load On Demand

- [`references/GOLDEN_TASKS.md`](references/GOLDEN_TASKS.md) — load when creating instructions from scratch or when the user asks for worked examples
