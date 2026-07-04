# Contributing

Thanks for helping make `(pre·post)mortem` better. The most valuable contributions are usually small and concrete.

## Good first contributions

- **Add an incident.** Found a well-documented postmortem the corpus is missing? Add it with tags and a one-line lesson (see the schema below). AI/LLM/agent failures go in `ai-incident-analyst/data/ai_incidents.json`; infrastructure/SRE incidents go in `postmortem-analyst/data/extra_incidents.json`.
- **Fix a dead link.** `python3 postmortem-analyst/scripts/pm.py fetch <id>` falls back to archive.org; if an entry has a better live URL, update it.
- **Sharpen a lesson or tag.** Lessons should be one transferable sentence, not a summary. Tags must come from the controlled vocabularies.
- **Improve a workflow** in a `SKILL.md`, or add a new skill (see below).

## Incident schema

Every incident carries: a stable `id` (kebab-case), `org`, `date`, source `url`(s), a mechanism-focused `summary`, one or more tags from the controlled vocabulary, and a single-sentence `lesson`.

- Infrastructure tags and patterns: `postmortem-analyst/references/taxonomy.md`.
- AI failure classes: `ai-incident-analyst/references/failure-classes.md`.

Use existing entries as templates. One primary cause plus optional contributing causes. Prefer a first-party postmortem as the source; note when only press coverage exists.

## Adding a skill

Each skill is a self-contained folder: `SKILL.md` (frontmatter with `name` and a "Use when" `description`, then nested workflows), plus optional `data/`, `references/`, `scripts/`, and a `.claude-plugin/plugin.json`. Register it in `.claude-plugin/marketplace.json`. Keep scripts to Python 3 standard library plus `curl` so the zero-dependency promise holds.

## Style

- **No em dashes.** Use commas, colons, or parentheses. CI enforces this.
- Plain, direct prose. Complete sentences, spelled-out terms, no marketing filler.
- Every incident claim links to its source. Every recommendation cites precedent by incident id.

## Before you open a PR

Run the same checks CI runs:

```bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null   # all JSON parses
python3 postmortem-analyst/scripts/pm.py stats                     # index loads
python3 ai-incident-analyst/scripts/ai.py classes                  # corpus loads
grep -rlP "\x{2014}" --include='*.md' --include='*.json' --include='*.py' .  # GNU grep; should print nothing
```

Then open a pull request using the template. By contributing you agree your work is licensed under the project's Apache-2.0 license.
