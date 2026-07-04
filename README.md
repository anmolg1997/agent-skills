# Agent Skills

A growing collection of [Agent Skills](https://agentskills.io) for Claude Code and compatible agents. **Each skill lives in its own repository** (own issues, stars, releases) and is included here as a git submodule — this repo is the central catalog and one-command installer.

## Skills

| Skill | Repo | What it's for |
|---|---|---|
| [postmortem-analyst](postmortem-analyst/) | [anmolg1997/postmortem-analyst](https://github.com/anmolg1997/postmortem-analyst) | Incident precedent & failure-pattern analysis over 243 real-world postmortems (danluu/post-mortems), tagged and searchable, with nested agent fan-out workflows for deep dives, surveys, and postmortem review. |

## Install

Clone with submodules, then symlink the skills you want into your agent's skills directory:

```bash
git clone --recurse-submodules https://github.com/anmolg1997/agent-skills ~/agent-skills
ln -s ~/agent-skills/postmortem-analyst ~/.claude/skills/postmortem-analyst
```

Claude Code discovers each linked skill automatically.

Want just one skill? Clone its repo directly:

```bash
git clone https://github.com/anmolg1997/postmortem-analyst ~/.claude/skills/postmortem-analyst
```

## Managing the collection

```bash
# Pull latest of every skill and record the new pins
git -C ~/agent-skills submodule update --remote --merge
git -C ~/agent-skills commit -am "Bump skill pins"

# Add a new skill to the collection
gh repo create <skill-name> --public --source <skill-folder> --push
git submodule add https://github.com/anmolg1997/<skill-name>.git <skill-name>
git commit -m "Add <skill-name>"
```

Each submodule is pinned to a specific commit, so the collection is always a known-good set; bumping pins is an explicit, reviewable change.

## Layout convention (per skill repo)

```
<skill-name>/
  SKILL.md        # entry point: frontmatter (name, description) + workflows
  README.md       # human-facing docs for the skill
  data/           # machine-readable corpora / indexes (optional)
  references/     # heavy reference material loaded on demand (optional)
  scripts/        # executable tooling the skill drives (optional)
```
