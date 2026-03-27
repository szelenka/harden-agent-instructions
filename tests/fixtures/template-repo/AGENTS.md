# Agent Instructions

## Hard Rules

- This is a cookiecutter template repository. All paths containing `{{project_slug}}` or other `{{...}}` placeholders are template variables, not concrete runtime code.
- Do not treat template files as executable application code. The repo generates projects; it is not itself a runnable application.
- Changes to template structure must preserve cookiecutter variable syntax.
- Before modifying `cookiecutter.json`, verify that all template files referencing those variables remain valid.

## Commands

Render the template with default values:
```bash
make render
```

Or render directly:
```bash
cookiecutter template --no-input
```

## Key Paths

- `Makefile` — render orchestration, defines `make render` target
- `cookiecutter.json` — template variables (project_slug, etc.)
- `template/{{project_slug}}/` — template files with placeholders that will be rendered into generated projects
- `hooks/post_gen_project.py` — cookiecutter post-generation hook, runs after template rendering

## Done-When Checklist

Before completing template changes:
- [ ] Run `make render` successfully
- [ ] Verify generated output contains expected structure
- [ ] Confirm cookiecutter variables are valid and referenced correctly in template files
- [ ] Check that placeholder syntax (`{{...}}`) is preserved in template files

## Codebase Drift Prevention

When the template structure changes (new files added to `template/`, variables added to `cookiecutter.json`, hooks modified), update this file to reflect the new paths or generation behavior. If template validation steps change, update the Done-When Checklist.

## Self-Improvement

When you discover a template-specific convention or failure pattern not covered here, add it to this file. For example, if certain variable names cause rendering failures, or if hook ordering matters, document that constraint in Hard Rules.
