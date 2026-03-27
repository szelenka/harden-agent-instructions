# Installation

Works best with high-capability models like Claude Opus or GPT-5.4.

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

## Codex

Official docs: <https://developers.openai.com/codex/skills>

Native GitHub install:

```bash
$skill-installer https://github.com/szelenka/harden-agent-instructions
```

There is no separate marketplace flow documented in the current Codex skills docs. See [.codex/INSTALL.md](.codex/INSTALL.md) for the repo-specific install flow.

## Windsurf

Official docs: <https://docs.windsurf.com/windsurf/cascade/skills>

No native marketplace or GitHub importer for skills is documented in the current Windsurf skills docs. Install from GitHub by cloning this repo and linking the checked-in Windsurf shim.

Windsurf discovers skills from workspace `.windsurf/skills/`, user `~/.codeium/windsurf/skills/`, and compatible `.agents/skills/` locations. This repo ships a Windsurf workspace shim in `.windsurf/skills/harden-agent-instructions/SKILL.md`.

```bash
git clone https://github.com/szelenka/harden-agent-instructions.git ~/harden-agent-instructions
mkdir -p ~/.codeium/windsurf/skills
ln -s ~/harden-agent-instructions/.windsurf/skills/harden-agent-instructions ~/.codeium/windsurf/skills/harden-agent-instructions
```

Verify in Windsurf's Rules or Skills UI that `harden-agent-instructions` is discovered.

## OpenCode

Official docs: <https://opencode.ai/docs/skills/>

No native marketplace or GitHub installer for skills is documented in the current OpenCode skills docs. Install from GitHub by cloning this repo and linking the checked-in OpenCode shim.

OpenCode discovers skills from `.opencode/skills/`, `~/.config/opencode/skills/`, and compatible `.agents/skills/` paths. This repo ships an OpenCode workspace shim in `.opencode/skills/harden-agent-instructions/SKILL.md`.

```bash
git clone https://github.com/szelenka/harden-agent-instructions.git ~/harden-agent-instructions
mkdir -p ~/.config/opencode/skills
ln -s ~/harden-agent-instructions/.opencode/skills/harden-agent-instructions ~/.config/opencode/skills/harden-agent-instructions
```

Verify by asking OpenCode to audit this repo's agent instructions, or confirm the skill is available in the `skill` tool.

See [.opencode/INSTALL.md](.opencode/INSTALL.md) for details.

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

## Other Agents

Copy `skills/harden-agent-instructions/SKILL.md` and `skills/harden-agent-instructions/references/` into your agent's skill directory.
