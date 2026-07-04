# postmortem-analyst

An [Agent Skill](https://agentskills.io) for Claude Code that turns [danluu/post-mortems](https://github.com/danluu/post-mortems) — the community-curated list of real-world incident postmortems — into a searchable, tagged, agentically-analyzable corpus.

## What it does

- **243 incidents indexed** (Google, AWS, Cloudflare, GitHub, GitLab, Facebook, NASA, …) in `data/postmortems.json`, each tagged with root-cause class (16-term controlled vocabulary), trigger, blast radius, and a one-sentence transferable lesson.
- **Link-health checked**: 233/243 sources reachable; entries whose pages died carry archive.org fallbacks, and the fetcher resolves live original → archived snapshot → Wayback API automatically.
- **32 canonical failure patterns** distilled per category in `references/taxonomy.md` (e.g. *"the HA machinery causes the outage"*, *"backup power fails at the moment of truth"*, *"leap second violates monotonic-time assumptions"*).
- **Nested agentic workflows** (defined in `SKILL.md`): from instant index lookups (L0), to incident-similarity deep dives that fan out one reader agent per matched postmortem (L1), to category surveys where each survey agent internally runs its own reader loop (L2), to corpus-wide studies (L3). Plus a postmortem review/writing workflow that uses the corpus as an evidence-backed rubric.

## Install

```bash
git clone https://github.com/<you>/postmortem-analyst ~/.claude/skills/postmortem-analyst
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
python3 scripts/pm.py refresh   # re-sync with upstream danluu/post-mortems, preserving tags
```

## Example prompts once installed

- *"We just had an outage where a config rollout removed a safety limit — what precedent exists and what should our remediation checklist contain?"*
- *"What do all the database postmortems teach about failover?"*
- *"Review this draft postmortem against how the best incident reports are written."*

## Layout

```
SKILL.md                 # entry point: workflows + nested agent dispatch patterns
data/postmortems.json    # enriched index (the machine-readable corpus)
references/<category>.md # curated per-category lists + canonical patterns
references/taxonomy.md   # controlled vocabularies + cross-category pattern catalog
scripts/pm.py            # search / show / fetch / stats / refresh
```

## Attribution

Incident list and summaries derive from [danluu/post-mortems](https://github.com/danluu/post-mortems) (thank you to Dan Luu and its many contributors). Tags, lessons, canonical patterns, link-health data, and tooling are original to this repo. Each entry links to the original postmortem, whose content belongs to its publisher.
