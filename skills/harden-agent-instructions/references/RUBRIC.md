# Rubric Reference

Load this file at the start of Phase 2. Criteria are listed in impact-when-applicable order: a gated criterion ranked higher than an always-on criterion means it has greater severity when its gate is active, not that it applies more often. Earlier items should drive scoring severity and fix order. Let document order follow the concrete behaviors those criteria require; do not force a section just because a higher-ranked criterion exists. When evidence overlaps, score the narrowest active criterion first, collapse broader duplicates by default, and treat later overlap as supporting evidence unless it survives the narrower fix. The tier table in `SKILL.md` is placement guidance, not an activation signal.
Use the same shared terms as `SKILL.md`: `activation gate`, `tier-required behavior`, `done-when checklist`, and `discoverable`. If you need a shorter label inside a criterion, keep the canonical term visible in the same section.

## Rating Scale

- **Missing**: the concept is absent, or present only as vague aspiration ("follow best practices"). An agent receiving this instruction would have to guess or fall back on generic behavior.
- **Weak**: the concept is present and directionally correct, but lacks enough specificity to prevent drift or error. An agent could start but would likely deviate.
- **Pass**: an agent can act correctly on the first attempt without interpretation or guessing.
- **Not Applicable**: the criterion's activation signal is not present in this repo or instruction set.
- **Unverified**: the criterion may matter, but the needed evidence is unavailable in the workspace.

Key distinction: Missing means no actionable signal at all. Weak means the right concept is named but the command, path, or condition is omitted. A rule that could be copy-pasted into any repo unchanged is Missing, not Weak.

## Scoring Shortcuts

When a weakness could fit multiple criteria, use the first matching rule below and note the overlap in evidence:

- **Startup facts** (commands, entry points, binaries, dependency compatibility) → `Startup Reliability`
- **Architecture is vague** (file-role maps, component relationships) → `Structural Orientation`
- **Claim lacks evidence** (missing paths, examples, named artifacts) → `Grounding Density`
- **Rule lacks any deterministic check** → `Action-Outcome Coupling`
- **Checks exist but routing is weak** (ordering, scope, blast radius) → `Verification Routing`; **dangerous operations** → `Failure Blast Radius Awareness`
- **Done checklist exists but proof is weak** → `Deterministic Verification` (Done-When passes when the exit gate is present)
- **Code patterns diverge or duplicate** → `Codebase Drift Prevention`; **review partitioning or confidence signals** → `Review Burden Reduction`; **cross-document contradictions** → `Cross-Document Consistency`; **intra-file terminology drift** → `Linguistic Precision`
- **Primary-file bloat** → `Context Efficiency`; **missing tiered-loading architecture** → `Context Budget Design` (advanced)
- **Repo enforcement absent** → `Codified Policy Enforcement`; **eval harness or fixture-validation surface exists but instructions ignore it** → `Golden Tasks` or `Deterministic Verification`, whichever is narrower

Apply these thresholds consistently:

- Score `Missing` when the agent would have to invent the command, path, condition, or exit gate.
- Score `Weak` when the instruction names the right idea but leaves a real execution choice open.
- Score `Pass` only when a first-pass agent could act without guessing.

## Applicability Rules

- Core criteria without an activation line are always on.
- Core criteria with an activation line should be scored only when that activation signal is present; otherwise use `Not Applicable`.
- Use `Unverified` instead of `Missing` when the criterion depends on evidence you cannot inspect, such as contributor workflow without `.git` metadata.
- A tier-table row marked `conditional` does not activate the criterion on its own; first confirm the rubric's own activation gate.
- When a weakness seems to fit multiple criteria, use the narrowest bucket:
  - missing commands or entry points -> `Startup Reliability`
  - buried critical rules -> `Instruction Salience`
  - missing paths or examples -> `Grounding Density`
  - missing IF->THEN logic -> `Decision Boundary Precision`
  - missing per-rule check -> `Action-Outcome Coupling`
  - missing finish gate -> `Done-When Checklists`
  - missing ordering or scope guidance for checks -> `Verification Routing`
  - verification ends in prose or LLM judgment instead of deterministic proof -> `Deterministic Verification`

## Contents

- [Rating Scale](#rating-scale): Missing, Weak, Pass definitions
- [Scoring Shortcuts](#scoring-shortcuts): tie-breakers for overlapping criteria
- [Applicability Rules](#applicability-rules): when to use Not Applicable or Unverified
- [Core Criteria](#core-criteria): Startup Reliability, Instruction Salience, Structural Orientation, Grounding Density, Action-Outcome Coupling, Done-When Checklists, Codebase Drift Prevention, Review Burden Reduction, Context Efficiency, Codified Policy Enforcement, Decision Boundary Precision, Verification Routing, Deterministic Verification, Failure Blast Radius Awareness, Linguistic Precision, Self-Improving Feedback Loop, Testing Conventions, Scope Boundaries, Source Control Workflow, Cross-Document Consistency
- [Advanced Criteria](#advanced-criteria): Context Budget Design, Persona Separation, Routing Architecture, Golden Tasks, Variance Control, Handoff Protocol

## Fix Priority to Rubric Crosswalk

| Fix Priority | Primary Rubric Criteria |
|---|---|
| 1. Cold-start failures | Startup Reliability, Structural Orientation, Grounding Density |
| 2. Budget violations | Context Efficiency |
| 3. Prune filler / stale-but-accurate content | Context Efficiency, Self-Improving Feedback Loop |
| 4. Stale paths / nonexistent commands / unverified deps | Grounding Density, Startup Reliability |
| 5. Missing tier behaviors | Criterion matching the behavior (see tier table) |
| 6. Weak verification / decision-gate / feedback gaps | Action-Outcome Coupling, Decision Boundary Precision, Verification Routing, Deterministic Verification, Self-Improving Feedback Loop |
| 7. Lower-priority rubric | Remaining criteria scored Weak or Missing |

## Core Criteria

**Startup Reliability**
- Can the agent bootstrap and start working without guessing?
- Look for: quick-start commands in code blocks, key entry points with roles, runnable build/test/lint commands whose binaries are verified available (via `command -v` or a declared task runner)
- Look for: wrapper commands (Makefile targets, tox envs, npm scripts) verified via dry-run to confirm underlying binaries are present — not just the wrapper itself
- Look for: dependency compatibility verified against the project's runtime and framework versions (`engines`, `python_requires`, peer dependency ranges) and against lock files — hallucinated or incompatible versions block bootstrapping
- Anti-pattern: commands extracted from manifests without verifying the binary exists — e.g., writing `pio run` when `pio` is not installed

**Instruction Salience**
- Look for: hard rules in the first 30 lines, strong emphasis, quick-start before reference material, descending impact order
- Anti-pattern: critical rules buried under overview text

**Structural Orientation**
- Activation: the repo layout is non-obvious, the file assigns architectural roles, or a wrong-layer edit would be plausible from the tree and manifests alone
- Does the agent understand how the codebase is organized? Use this for file-role mappings and component relationships, not for bare path-count failures.
- Discoverability filter: if the repo follows a standard framework layout (e.g., Rails, Next.js, Django, Spring Boot) and the structure is self-evident from the directory tree and manifests, score Pass with minimal content or Not Applicable. Only require structural documentation for non-obvious decisions (unconventional layouts, cross-cutting concerns, shared modules with non-obvious ownership, fragile entry points, or known wrong-layer risks).
- Look for: architecture overview, data flow description, design patterns with file locations, schema specifics, domain vocabulary, file-role mappings
- Look for: placement guidance when wrong-layer edits are a realistic failure mode — where new code belongs, which layer owns the behavior, and one wrong-vs-right placement example when the boundary is not obvious
- Anti-pattern: directory tree with no explanation of what things do; restating discoverable conventions ("src/ contains source code") that don't change the agent's next action

**Grounding Density**
- Are claims and rules backed by concrete evidence? Use this for missing proof attached to a claim, not for missing architecture explanation.
- Look for: concrete file paths, worked examples, right-vs-wrong examples, key paths section
- Anti-pattern: abstract pattern names with no examples or locations

**Action-Outcome Coupling**
- Is each rule tied to a deterministic verification command? Use this only when the check is absent, not when ordering or scope is weak.
- Look for: explicit commands tied to rules, commands that exist in the build system
- Anti-pattern: "ensure quality" without naming verification steps

**Done-When Checklists**
- Does the file define when a task is finished? (Distinct from Action-Outcome Coupling: Done-When is the exit gate for the whole task; A-O is inline verification for individual rules.)
- Equivalent labels: "Done-when checklist", "Definition of done", "Verification checklist", "Change checklist" — score identically regardless of heading name
- Look for: concrete completion criteria with commands and contextual requirements
- Look for: quality-oriented completion signals — test coverage unchanged or improved, no new linter warnings, cyclomatic complexity within repo norms — not just "tests pass"
- Anti-pattern: no definition of when a task is finished, agent decides on its own when to stop

**Codebase Drift Prevention**
- Look for: search-before-create discipline — search for existing methods before writing new; extend existing code over parallel implementations; flag conflicts rather than silently diverge; YAGNI as default
- Look for: proven-library preference grounded in repo evidence — prefer libraries already adopted in manifests, lock files, or existing modules; prohibit one-off abstractions that duplicate established patterns; prefer extending current modules over creating new files (see Linguistic Precision for naming conventions). Common violations: hand-rolling HTTP clients, retry logic, date parsing, or schema validation
- Look for: conciseness expectations — no verbose or over-abstracted code when shorter implementations exist
- Anti-pattern: "follow existing patterns" with no guidance on how to find or evaluate them — each agent session introduces its own conventions

**Review Burden Reduction**
- Activation: the instruction file defines change partitioning rules, review buckets, confidence markers, or explicit mechanical-vs-judgment separation. Repo size alone is not enough.
- Use this only for how reviewers consume or triage changes, not for source-control mechanics, verification scope, edit permissions, or risk-classification rules.
- Look for: small atomic changes with clear diffs; mechanical changes (renames, formatting) separated from judgment calls (new abstractions, API design); low-confidence decisions marked (e.g., `// AI-UNCERTAIN: [reason]`)
- Anti-pattern: all agent output treated as equally review-worthy — no distinction between mechanical and judgment changes

**Context Efficiency**
- Look for: line-budget discipline, split references, tables or bullets over repetitive prose; front-load highest-impact rules and defer the rest
- Look for: signal-to-noise discipline — every line should fail the discoverability test (auditor names the artifact and one inspection that yields the fact). Lines restating manifests, CI files, lock files, or standard framework layout cost tokens and add zero value
- Look for: concreteness — commands, paths, concrete nouns, and conditions beat abstract paraphrase
- Look for: primary-file minimalism — root `AGENTS.md` stays focused on constraints, exact commands, boundaries, non-obvious conventions, and done criteria; editorial reasoning stays out unless it changes agent behavior
- Look for: active pruning — stale-but-accurate lines, project-map filler, and rules with no remaining failure-prevention value are removed, not merely tolerated
- Anti-pattern: 50+ rules at the same priority level — models lose focus and start ignoring later rules
- Anti-pattern: accurate but behaviorally inert content retained because "it is still true" — this includes tech-stack facts, directory listings, and explanatory rationale. Worse: discoverable content that restates manifests can also become stale, causing active harm
- Anti-pattern: rules stated in both positive and negative form — "Do X" paired with "Don't skip X" doubles the content for zero additional signal; only keep anti-patterns that name a distinct failure mode

**Codified Policy Enforcement**
- Are rules backed by automated enforcement rather than behavioral guidance alone?
- Look for: pre-commit hooks, CI, linter configs, policy backed by automation; instruction-repo alignment enforcement (a CI step, hook, or job that validates instruction-file claims)
- For repos with enforcement infrastructure: verify the instruction file documents them and ties rules to enforcement
- For repos without enforcement infrastructure: score Weak (not Missing) — note the absence and recommend the lightest enforcement pattern that fits
- Look for: quality metrics backed by configured tooling — stated metrics (complexity, coverage, duplication) without corresponding tool config are aspirational, not enforced
- Anti-pattern: CI or hooks exist but are undocumented in instructions; quality metrics stated without corresponding tooling — agents cite unverifiable claims; instruction files that silently drift because no automated system validates their claims

**Decision Boundary Precision**
- Activation: the instruction file contains repeated conditional routing, approval, path-based, or mode-switching rules that materially change the agent's next step. Do not activate on a one-off caveat or a single ask-before-X rule. Repo size alone is not enough.
- Look for: explicit IF->THEN rules, task routing, path-based conditions, task-mode classification
- Look for: plan-before-edit or investigate-first rules only when they change the agent's next step for risky, ambiguous, or multi-stage work; fold planning into the relevant decision gate instead of creating a standalone planning section by default
- Look for: a failure-prevention link — persistent rules explain what mistake, ambiguity, or repeated wrong move they are there to prevent
- Look for: repeated decision surfaces, not one-off caveats better handled as a single concrete rule under a narrower criterion
- Overlap rule: if the condition is mainly about danger, reversibility, or escalation, score `Failure Blast Radius Awareness` instead; if it is mainly about which verification branch to run, score `Verification Routing` instead.
- Anti-pattern: blanket rules with no conditions
- Anti-pattern: rules with no identifiable decision effect — true statements that do not change the agent's next action

**Verification Routing**
- Activation: the repo or instruction surface offers more than one verification branch, scope rule, ordering choice, or blast-radius-dependent verification path. Do not activate when the file only lists one universal check and no scoping choice exists. Repo size alone is not enough.
- Does the verification workflow go beyond presence to provide execution guidance? Score this only after `Action-Outcome Coupling` passes at the basic command-present level.
- Overlap rule: score this after `Action-Outcome Coupling` and `Decision Boundary Precision`. If fixing one of those earlier criteria removes the weakness, do not score `Verification Routing` separately.
- Look for: verification ordering (fast checks before slow), selective verification by change type, exit-code expectations, severity-to-action mapping
- Look for: verification scope matched to blast radius; path-based or change-type-based rules that say when focused verification is sufficient and when full verification is mandatory
- Look for: lightweight checks for isolated, low-risk edits and full-suite verification for shared logic, instruction files, build config, CI, hooks, schemas, test harnesses, or fixtures
- Anti-pattern: no ordering guidance, agent cannot tell pass from fail without reading prose output
- Anti-pattern: always run the full suite for trivial low-risk edits, or always run focused checks even when changes can affect shared rules, enforcement logic, or multiple subsystems

**Deterministic Verification**
- Activation: the repo or instruction surface offers more than one plausible proof path, includes an eval harness, fixture runner, simulation path, artifact validator, or review-only language, or otherwise creates a real choice between deterministic verification and softer judgment. Do not activate when one obvious deterministic check is the only available proof path.
- Score this after `Action-Outcome Coupling` and `Done-When Checklists`. If the file already names the deterministic end gate clearly, do not score this just because a stronger proof surface also exists.
- Look for: verification that bottoms out in deterministic checks (tests, linters, type checkers, CI exit codes, fixture runners, artifact validators) — not in another LLM generation pass
- Look for: when the repo ships an eval harness, fixture runner, simulation path, or artifact-validation surface, instructions route agents to that deterministic check instead of stopping at prose review
- Look for: explicit pass/fail interpretation when the deterministic check is not self-evident from the command alone
- Anti-pattern: AI-verifying-AI loop — using LLM output as the sole verification of other LLM output with no deterministic check in the chain
- Anti-pattern: eval or fixture infrastructure exists, but instructions never mention when to run it
- Anti-pattern: "review manually" or "inspect output" used as the terminal gate when the repo exposes a stronger deterministic proof path

**Failure Blast Radius Awareness**
- Activation: the instruction file classifies operations by risk, defines ask-before-X rules, or provides rollback guidance. Repo size alone is not enough.
- Use this for risk classification, rollback, retry, and escalation boundaries, not for persistent edit-surface ownership rules.
- Use this instead of `Decision Boundary Precision` when the main question is danger or reversibility rather than routing between normal work modes.
- Look for: severity classification, ask-before-X rules, common mistakes, wrong-vs-right examples
- Look for: plan-before-edit, checkpoint, or pause-for-review rules when risky multi-step work can expand damage if executed in one pass
- Look for: iterative-loop guardrails — checkpoint or commit boundaries between tool-use iterations, caps on how many files or lines an agent may change before pausing for review, rollback guidance when an iteration produces unexpected state
- Sub-gate (score only when agents interact with external services, APIs, generated artifacts, or flaky infrastructure): error recovery boundaries — explicit retry limits, transient vs structural failure distinction, when to stop and escalate to the user
- Anti-pattern: no distinction between safe and dangerous operations
- Anti-pattern: agent may iterate through unbounded tool-use cycles with no checkpoint, commit, or review gate between iterations
- Anti-pattern: "retry" with no boundary or limit

**Linguistic Precision**
- Look for: imperative verbs, short declarative sentences, stable terminology, conditions before actions
- Look for: terminology discipline — reuse the same repo term for the same concept; avoid near-synonyms that blur routing or ownership
- Look for: naming conventions enforced in instructions — variable/function/file naming patterns the agent must follow, so generated code is indistinguishable from human-written code in style
- Look for: single source of truth within the file — no duplicate rules, consistent terminology throughout
- Look for: logical consistency — no contradictory rules without explicit boundary conditions distinguishing when each applies (e.g., "always use mocks" vs "never mock in integration tests" needs a clear scope delimiter)
- Anti-pattern: hedges, vague qualifiers, passive voice, meaningless numbered lists
- Anti-pattern: multiple labels for the same thing ("validation", "checks", "quality gate") when the repo already has one stable term
- Anti-pattern: instructions silent on naming style — agent invents its own conventions, producing inconsistent identifiers across sessions
- Anti-pattern: conflicting directives in the same file with no conditional scope — agent must guess which rule wins

**Self-Improving Feedback Loop**
- Look for: explicit write-back rules, where to persist discoveries, what qualifies as reusable knowledge
- Look for: clear boundary — repo-universal knowledge (conventions, build constraints, architecture) persisted to instruction files; session-specific insights (debugging history, personal preferences) to agent memory
- Look for: maintenance philosophy — reactive addition (add when agents make mistakes), periodic pruning (remove what agents now follow unprompted), update-in-same-PR discipline
- Look for: per-rule justification — persistent lines traceable to a real failure mode or non-obvious caveat; descriptively-true-only lines should be cut
- Anti-pattern: misplaced persistence — session-specific discoveries dumped into shared instruction files, or repo-universal conventions buried in personal agent memory where other contributors' agents never see them
- Anti-pattern: persisting conventions without verifying against build system, test suite, or existing code — write-back must be grounded in repo evidence
- Anti-pattern: instruction files that only grow — no pruning discipline accumulates stale rules that degrade agent performance

**Testing Conventions**
- Activation: the repo has tests or test harnesses the agent is expected to edit or extend, or the instruction file tells the agent to add or update tests, and repo-specific test-writing choices are not fully obvious from framework defaults alone. Repo size alone is not enough.
- Look for: how to write tests, where tests live, naming conventions, what not to test
- Look for: test-quality guardrails — tests must assert behavioral intent (what the code should do), not just structural agreement (that output matches what the implementation happens to produce). At least one acceptance criterion per feature should be traceable to a human-specified requirement, not solely to AI-generated logic
- Anti-pattern: agent generates both implementation and tests in the same pass with no independent check that the tests capture the actual requirement — co-generated tests can share the same reasoning blind spots as the code they verify, producing green suites that miss the real specification
- Anti-pattern: test coverage used as sole quality signal — high coverage of wrong behavior is worse than low coverage of correct behavior

**Scope Boundaries**
- Activation: the instruction file or repo surface has explicit read-only zones, generated files, ownership boundaries, or edit-surface restrictions beyond ordinary ask-before-X approval gates. Repo size alone is not enough.
- Use this for persistent edit-surface boundaries. Ordinary destructive, privileged, networked, or externally visible approval gates belong under `Failure Blast Radius Awareness` unless the repo also partitions where the agent may work.
- Look for: what can be modified, what is read-only, escalation triggers, exploration guardrails
- Look for: three-tier permission structure — actions the agent should always do without asking, actions requiring human approval before proceeding, and actions the agent must never take
- Anti-pattern: agent free-roams with no edit boundaries
- Anti-pattern: flat permission list with no distinction between safe, approval-required, and prohibited actions

**Source Control Workflow**
- Activation: 2+ contributors. If VCS metadata is unavailable in the workspace, mark this criterion Unverified rather than Missing
- Look for: branch strategy, commit expectations, PR protocol, prohibited actions
- Look for: attribution or review-label requirements only when the repo already uses them or exposes policy artifacts that require them
- Anti-pattern: inventing source-control policy that is not grounded in repo evidence, team workflow, or checked-in contributor guidance

**Cross-Document Consistency**
- Activation: more than one overlapping instruction or guidance surface exists, such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.cursorrules`, or agent-facing policy docs, and at least one shared operational fact, command, constraint, trigger, or output rule appears across them
- Look for: shared facts and rules staying aligned across overlapping documents, especially activation signals, hard constraints, score states, output format, escalation rules, commands, and file references
- Look for: intentional audience-specific differences made explicit rather than accidental drift
- Anti-pattern: one document says a rule, score model, or trigger exists while another overlapping document contradicts or omits it

## Advanced Criteria

Use criterion-level activation. Do not score the entire Advanced section just because one signal is present.

Low-yield advanced criteria should stay optional. Do not treat them as defects unless the activation signal is obvious and the missing guidance would change agent behavior in this repo.

**Context Budget Design**
- Activation: the instruction set is already split across a primary file plus on-demand references, or repo complexity and file-budget pressure make a split necessary, or Phase 1 detected 2+ operational zones with distinct build/test/verify surfaces. Repo size alone is not enough.
- Look for: tiered loading, on-demand references, resume support
- Look for: zone-specific instruction files when zone detection signals are strong (separate CI jobs per subtree, distinct runtimes, separate lock files)
- Look for: root file limited to shared constraints with a zone pointer table; zone files that specialize without restating root constraints
- Anti-pattern: all zones crammed into root file creating command ambiguity or budget overflow
- Anti-pattern: zone files that duplicate root constraints (creates drift surface)

**Persona Separation**
- Activation: multiple named agent roles, role-specific files, or explicit owner/worker splits
- Look for: role capsules, ownership boundaries, single-agent fallback

**Routing Architecture**
- Activation: multiple instruction files target different agents or roles, or instructions route tasks by file type, tool, or workflow mode
- Look for: routing table, decision tree, file-to-rule mapping

**Golden Tasks**
- Activation: the skill or instruction package includes worked examples, calibration fixtures, or exemplar audits
- Look for: worked examples showing a complete task, touch set, and verification path
- Look for: examples that demonstrate the highest-leverage deterministic checks the repo actually expects, such as eval harnesses, fixture runners, dry-run wrappers, or simulation paths when those exist

**Variance Control**
- Activation: agents contribute to high-stakes changes, stochastic generation is part of the workflow, or the repo exposes run-to-run instability risks that instructions can mitigate
- Look for: guidance to generate twice and diff before committing, require deterministic test ordering, pin model parameters in automated pipelines, or otherwise detect and reduce run-to-run variance
- Anti-pattern: assuming a single generation pass is reliable for high-stakes changes with no variance check or mitigation

**Handoff Protocol**
- Activation: multi-agent work, owner handoff, checkpointing, or resume support is explicitly supported
- Look for: checkpoint template, resume instructions, ownership transfer expectations
