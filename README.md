# Agent Skills

A growing collection of [Agent Skills](https://agentskills.io) for Claude Code and compatible agents. Each skill is a self-contained folder with a `SKILL.md` entry point, its own data, references, and scripts — no dependencies beyond Python 3 stdlib and standard CLI tools unless noted.

## Skills

| Skill | What it's for |
|---|---|
| [postmortem-analyst](postmortem-analyst/) | Incident precedent & failure-pattern analysis over 243 real-world postmortems (danluu/post-mortems), tagged and searchable, with nested agent fan-out workflows for deep dives, surveys, and postmortem review. |

## Install

Clone once, then symlink the skills you want into your agent's skills directory:

```bash
git clone https://github.com/anmolg1997/agent-skills ~/agent-skills
ln -s ~/agent-skills/postmortem-analyst ~/.claude/skills/postmortem-analyst
```

Claude Code discovers each linked skill automatically. To update everything: `git -C ~/agent-skills pull`.

## Layout convention

```
<skill-name>/
  SKILL.md        # entry point: frontmatter (name, description) + workflows
  README.md       # human-facing docs for the skill
  data/           # machine-readable corpora / indexes (optional)
  references/     # heavy reference material loaded on demand (optional)
  scripts/        # executable tooling the skill drives (optional)
```
