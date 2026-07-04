# postmortem-analyst

An [Agent Skill](https://agentskills.io) for Claude Code: an incident-analysis engine that turns a body of real-world postmortems into a searchable, tagged corpus and drives it with nested agentic workflows for precedent lookup, pre-mortems, and postmortem review.

## What it does

- **261 incidents indexed and tagged** (Google, AWS, Cloudflare, GitHub, GitLab, Facebook, NASA, and more), each carrying our own root-cause class (16-term controlled vocabulary), trigger, blast radius, and a one-sentence transferable lesson.
- **Link-health checked**: 233/243 sources reachable; entries whose pages died carry archive.org fallbacks, and the fetcher resolves live original → archived snapshot → Wayback API automatically.
- **32 canonical failure patterns** distilled per category in `references/taxonomy.md` (e.g. *"the HA machinery causes the outage"*, *"backup power fails at the moment of truth"*, *"leap second violates monotonic-time assumptions"*).
- **Nested agentic workflows** (defined in `SKILL.md`): from instant index lookups (L0), to incident-similarity deep dives that fan out one reader agent per matched postmortem (L1), to category surveys where each survey agent internally runs its own reader loop (L2), to corpus-wide studies (L3).
- **Methodology-driven analysis workflows** no incident tool serves: **pre-mortem/FMEA** for a risky change (Klein prospective hindsight + failure-mode table, every mode grounded in corpus precedent), **rubric-based postmortem review** (8 dimensions: blameless language, mechanism chain vs single root cause, hindsight bias, detection/response analysis, action-item quality, luck accounting, impact honesty), **postmortem writing** per the Google SRE / Howie / Etsy / Cook canon (`references/methodology.md`), and **cross-incident pattern analysis** over your own org's postmortem directory.
- **Vetted source catalog** (`references/sources.md`): where more postmortems live (the VOID, Azure PIRs, Cloudflare/GitHub feeds, Wikimedia) with freshness and machine-readability notes.

## Install

This skill lives in the [agent-skills](https://github.com/anmolg1997/agent-skills) collection:

```bash
git clone https://github.com/anmolg1997/agent-skills ~/agent-skills
ln -s ~/agent-skills/postmortem-analyst ~/.claude/skills/postmortem-analyst
```

Claude Code picks it up automatically as skill `postmortem-analyst`. No dependencies beyond Python 3 stdlib and `curl`.

## Direct CLI usage

```bash
cd ~/.claude/skills/postmortem-analyst
python3 scripts/pm.py search --cause config-change --blast global-outage
python3 scripts/pm.py search leap second
python3 scripts/pm.py show cloudflare-10
python3 scripts/pm.py fetch gitlab-2 --out /tmp/pm.txt   # full postmortem text, Wayback fallback
python3 scripts/pm.py stats
python3 scripts/pm.py refresh   # re-sync the seed incident list, preserving our tags
```

## Example prompts once installed

- *"We just had an outage where a config rollout removed a safety limit, what precedent exists and what should our remediation checklist contain?"*
- *"What do all the database postmortems teach about failover?"*
- *"Review this draft postmortem against how the best incident reports are written."*
- *"We're planning this database migration next week, run a pre-mortem on the plan."*
- *"Here's a folder of our last 15 postmortems, what keeps biting us?"*

## Layout

```
SKILL.md                 # entry point: workflows + nested agent dispatch patterns
data/postmortems.json    # enriched index (the machine-readable corpus)
references/<category>.md # curated per-category lists + canonical patterns
references/taxonomy.md   # controlled vocabularies + cross-category pattern catalog
scripts/pm.py            # search / show / fetch / stats / refresh
```

## References

Public work that helped bring this to life. Thanks to the people behind:

1. [danluu/post-mortems](https://github.com/danluu/post-mortems) and the AWS Post-Event Summaries, for the incident record.
2. The Google SRE Book, the Howie guide, Etsy's debriefing guide, Richard Cook, and Gary Klein, for postmortem and pre-mortem methodology.

Each entry links to its original postmortem, whose content belongs to its publisher. The tags, lessons, taxonomy, canonical patterns, and tooling here are our own.
