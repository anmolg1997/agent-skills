# Agent Skills

A growing collection of [Agent Skills](https://agentskills.io) for Claude Code and compatible agents. Each skill is a self-contained folder with a `SKILL.md` entry point, its own curated data, references, and scripts — no dependencies beyond Python 3 stdlib and standard CLI tools.

## Skills

| Skill | What it's for |
|---|---|
| [postmortem-analyst](postmortem-analyst/) | Incident precedent & failure-pattern analysis over **261 tagged real-world postmortems** (danluu/post-mortems + AWS Post-Event Summaries), plus the analysis workflows incident tooling doesn't serve: pre-mortems/FMEA grounded in precedent, rubric-based postmortem review, methodology-driven postmortem writing, and cross-incident pattern mining over your own org's postmortems. |
| [ai-incident-analyst](ai-incident-analyst/) | Failure analysis for **AI/LLM/agentic systems** over a curated corpus of canonical incidents (Replit's DB-deleting agent, Anthropic's silent-quality-degradation postmortem, EchoLeak zero-click injection, GPT-4o sycophancy rollback, …) with a 12-class failure vocabulary mirroring SRE taxonomies, agentic pre-mortem/design review (MAST + OWASP LLM Top-10), and AI-incident postmortem discipline. |

The two skills cross-delegate: AI services inherit every classic infrastructure failure mode (postmortem-analyst's domain) plus the twelve AI-specific classes (ai-incident-analyst's domain).

## Install

**As Claude Code plugins** (recommended):

```
/plugin marketplace add anmolg1997/agent-skills
/plugin install postmortem-analyst@agent-skills
/plugin install ai-incident-analyst@agent-skills
```

**Or clone + symlink** into your agent's skills directory:

```bash
git clone https://github.com/anmolg1997/agent-skills ~/agent-skills
ln -s ~/agent-skills/postmortem-analyst ~/.claude/skills/postmortem-analyst
ln -s ~/agent-skills/ai-incident-analyst ~/.claude/skills/ai-incident-analyst
```

Claude Code discovers each skill automatically. To update: `git -C ~/agent-skills pull`.

## Layout convention

```
<skill-name>/
  SKILL.md              # entry point: frontmatter (name, description) + workflows
  README.md             # human-facing docs for the skill
  .claude-plugin/       # plugin manifest (marketplace install)
  data/                 # machine-readable corpora / indexes
  references/           # heavy reference material loaded on demand
  scripts/              # executable tooling the skill drives
```

Design docs for the collection live in [docs/specs/](docs/specs/). Skills that outgrow the collection (dedicated contributors, releases, issue tracker) can be spun out into their own repo and linked from here.
