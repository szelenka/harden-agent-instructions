# Installation

Works best with high-capability models like Claude Opus or GPT-5.4.

## Table of Contents

- [Claude Code](#claude-code)
- [Codex](#codex)
- [Cursor](#cursor)
- [Gemini](#gemini)
- [GitHub Copilot](#github-copilot)
- [Other Agents](#other-agents)
- [Windsurf](#windsurf)

## Claude Code

Official skills docs: <https://code.claude.com/docs/en/skills>
Official marketplace docs: <https://code.claude.com/docs/en/discover-plugins>

Native GitHub marketplace install:

```bash
/plugin marketplace add szelenka/harden-agent-instructions
/plugin install harden-agent-instructions@harden-agent-instructions
```

Native skills-directory install:

Claude Code also discovers skills from `.claude/skills/` and `~/.claude/skills/`. This repo ships a Claude workspace shim in `.claude/skills/harden-agent-instructions/SKILL.md`.

```bash
git clone https://github.com/szelenka/harden-agent-instructions.git ~/harden-agent-instructions
mkdir -p ~/.claude/skills
ln -s ~/harden-agent-instructions/.claude/skills/harden-agent-instructions ~/.claude/skills/harden-agent-instructions
```

Verify: `/harden-agent-instructions` should be available, or Claude should load it automatically for instruction-audit tasks.

## Codex

Official docs: <https://developers.openai.com/codex/skills>

Native GitHub install:

```bash
$skill-installer https://github.com/szelenka/harden-agent-instructions/tree/main/skills/harden-agent-instructions
```

Verify: `$harden-agent-instructions` should be available, or Codex should load it automatically for instruction-audit tasks.

## Cursor

Official skills docs: <https://cursor.com/docs/skills>
Official plugins docs: <https://cursor.com/docs/plugins>

Native GitHub install for a project:

1. Open `Cursor Settings -> Rules`
2. In `Project Rules`, click `Add Rule`
3. Select `Remote Rule (Github)`
4. Enter `https://github.com/szelenka/harden-agent-instructions`

Cursor should discover the skill from the repo's checked-in plugin metadata in `.cursor-plugin/plugin.json`, which points at the canonical files under `skills/harden-agent-instructions/`.

Verify in `Cursor Settings -> Rules`: the skill should appear under `Agent Decides`.

Native team marketplace flow from GitHub:
Admins can import this GitHub repo under `Dashboard -> Settings -> Plugins -> Team Marketplaces -> Import`. The checked-in `.cursor-plugin/plugin.json` is the plugin manifest for that flow.

## Gemini

Official skills docs: <https://geminicli.com/docs/cli/skills/>

Native GitHub install:

Gemini CLI discovers skills from `.gemini/skills/` or the `.agents/skills/` alias in either the workspace or the user home directory. Install this repo's skill with Gemini's documented skill manager:

```bash
# install for your user account
gemini skills install https://github.com/szelenka/harden-agent-instructions.git --path skills/harden-agent-instructions

# or install only for this workspace
gemini skills install https://github.com/szelenka/harden-agent-instructions.git --path skills/harden-agent-instructions --scope workspace
```

If you already have a local checkout, install or link from disk instead:

```bash
gemini skills install /path/to/harden-agent-instructions/skills/harden-agent-instructions
gemini skills link /path/to/harden-agent-instructions --scope workspace
```

Verify with:

```bash
gemini skills list
```

The current Gemini CLI skills docs describe `gemini skills install` / `gemini skills link` plus `.gemini/skills` or `.agents/skills` as the install path; this repo does not require extra Gemini-specific packaging files for that flow.

## GitHub Copilot

Official skills docs: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>

No native GitHub-repo installer or marketplace import for skills is documented in the current GitHub Copilot skills docs. GitHub documents directory-based skill discovery instead.

GitHub Copilot discovers project skills from `.github/skills/` or `.claude/skills/`, and personal skills from `~/.copilot/skills/` or `~/.claude/skills/`. This repo already ships a Claude-compatible shim in `.claude/skills/harden-agent-instructions/SKILL.md`, so the simplest install is to clone the repo and link that checked-in skill directory into your personal Copilot skills directory.

```bash
git clone https://github.com/szelenka/harden-agent-instructions.git ~/harden-agent-instructions
mkdir -p ~/.copilot/skills
ln -s ~/harden-agent-instructions/skills/harden-agent-instructions/ ~/.copilot/skills/harden-agent-instructions
```

If you want to try it only in one repository, link or copy the same checked-in directory into that repo's `.github/skills/` or `.claude/skills/` directory instead:

```bash
mkdir -p .github/skills
ln -s /path/to/harden-agent-instructions/.claude/skills/harden-agent-instructions .github/skills/harden-agent-instructions
```

Verify by opening Copilot coding agent in a repo and asking it to audit or improve an instruction file such as `AGENTS.md` or `copilot-instructions.md`. The GitHub docs require `SKILL.md` to live inside the skill directory; this repo's checked-in shim already satisfies that requirement.

## Other Agents

Copy `skills/harden-agent-instructions/SKILL.md` and `skills/harden-agent-instructions/references/` into your agent's skill directory.

## Windsurf

Official docs: <https://docs.windsurf.com/windsurf/cascade/skills>

No native marketplace or GitHub importer for skills is documented in the current Windsurf skills docs. Install from GitHub by cloning this repo and linking the canonical skill directory.

Windsurf discovers skills from workspace `.windsurf/skills/`, user `~/.codeium/windsurf/skills/`, and compatible `.agents/skills/` locations.

```bash
git clone https://github.com/szelenka/harden-agent-instructions.git ~/harden-agent-instructions
mkdir -p ~/.codeium/windsurf/skills
ln -s ~/harden-agent-instructions/skills/harden-agent-instructions/ ~/.codeium/windsurf/skills/harden-agent-instructions
```

Verify in Windsurf's Rules or Skills UI that `@harden-agent-instructions` is discovered.
