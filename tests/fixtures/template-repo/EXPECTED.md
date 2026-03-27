# Expected Audit Results: template-repo

A small template repo with placeholder paths and no instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** template-oriented workflow via root `Makefile`
- **Verification reality:** render-oriented
  - `make render`
  - placeholder paths must not be described as concrete generated output

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`make render`)
- Key paths with roles (`template/{{project_slug}}/README.md` — generated-project template, `cookiecutter.json` — template inputs, `hooks/post_gen_project.py` — post-render hook)
- A note that placeholder paths are templates, not concrete runtime modules

## Key Signals

- The skill must not treat `{{project_slug}}` paths as already materialized repo code
- The audit should explain the repo as a scaffold/template
- The done checklist should stay focused on rendering or template validation, not app execution
