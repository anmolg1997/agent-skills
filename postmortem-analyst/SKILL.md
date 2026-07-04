---
name: postmortem-analyst
description: Use when analyzing an incident or outage and wanting precedent, researching how real companies failed (config errors, cascading failures, DNS/BGP, data loss, cloud outages), writing or reviewing a postmortem/incident report, running a pre-mortem or FMEA on a risky change or migration plan, mining a directory of past postmortems for recurring patterns, or when the user mentions danluu/post-mortems, incident retrospectives, RCA, blameless postmortems, or "has anyone else hit this".
---

# Postmortem Analyst

## Overview

An agentic harness over **261 real-world incident postmortems** (Google, Cloudflare, AWS, GitHub, GitLab, Facebook, NASA, and more), parsed into tagged, link-health-checked indexes (`data/postmortems.json` + `data/extra_incidents.json`) with per-category references and a failure-mode taxonomy. Analysis runs **nested**: cheap index search first, then fan-out subagents that deep-read only the relevant postmortems, then synthesis. Never bulk-read the corpus into the main context. For AI/LLM/agent behavior failures, use the sibling **ai-incident-analyst** skill.

## Quick reference

All commands run from this skill's directory (`cd ~/.claude/skills/postmortem-analyst`).

| Task | Command |
|---|---|
| Find incidents by keyword | `python3 scripts/pm.py search dns cascading --limit 10` (multiple terms are AND-matched, if a query returns few hits, drop a term and retry before concluding "no precedent") |
| Filter by tag | `python3 scripts/pm.py search --cause config-change --blast global-outage` |
| Filter by org/category | `python3 scripts/pm.py search --org cloudflare` / `--category database` |
| Full record for one entry | `python3 scripts/pm.py show gitlab` |
| Fetch full postmortem text | `python3 scripts/pm.py fetch <id> --out /tmp/pm.txt` (tries live original, archived snapshot, then Wayback API; on FAILED, fall back to WebFetch with the URL it prints) |
| Corpus stats | `python3 scripts/pm.py stats` |
| Sync with upstream repo | `python3 scripts/pm.py refresh` (preserves tags; new entries need tagging) |

Tag vocabularies and recurring mechanisms: `references/taxonomy.md`.
Per-category curated lists: `references/<category-slug>.md` (config-errors, hardware-power-failures, conflicts, time, database, uncategorized, other-lists-of-postmortems, analysis).
Methodology canon (SRE template, Howie, Etsy facilitation, Cook, Klein pre-mortem): `references/methodology.md`.
Postmortem quality rubric: `references/review-rubric.md`. Further public corpora and feeds: `references/sources.md`.

## Choosing the nesting level

| Question shape | Level | Cost |
|---|---|---|
| "Which incidents involved X?" / "show me the Y outage" | L0: index only | seconds |
| "We just had incident X, what precedent exists, what should we check?" | L1: search + 3–8 reader agents | minutes |
| "What do all the <category> failures teach?" | L2: one agent per slice, each reads several postmortems | tens of minutes |
| "Analyze the whole corpus for Z" | L3: L2 + Workflow tool | needs user opt-in for orchestration |

## L0, Direct lookup

`pm.py search` / `show` / `fetch`. Answer from the index's summaries and lessons; fetch at most 1–2 full texts into main context. Reading one per-category reference file is fine when the target category is small (≤ ~15 entries: time, conflicts, database, hardware): that's where the canonical patterns live; for config-errors and uncategorized, use `pm.py search` instead.

## L1, Incident-similarity deep dive

Use when the user describes *their* incident and wants precedent and guidance.

1. Extract the failure signature: root-cause class(es), trigger, blast radius (use `references/taxonomy.md` vocabulary).
2. Run 2–4 `pm.py search` queries (tag filters + keyword variants). Pick the 3–8 strongest matches, rank by overlap with the failure signature: a match on ≥2 dimensions (cause + trigger mechanism, or cause + blast radius) beats any single-dimension match; same-layer incidents (DNS vs DNS) beat same-cause-different-layer.
3. Dispatch **one reader agent per match, in parallel**. Prompt template (you, the dispatcher, must replace `<id>`, `<scratchpad>` with an absolute path, and the incident description before sending):

   > Fetch this postmortem: run `python3 ~/.claude/skills/postmortem-analyst/scripts/pm.py fetch <id> --out <scratchpad>/<id>.txt` then read the file. Extract as your final message, ≤300 words: (1) failure mechanism chain, (2) detection gap, why it wasn't caught earlier, (3) remediations they adopted, (4) which parts map onto this incident: <one-paragraph incident description>. If the file is dominated by nav/page-chrome and thin on article text (common for JS-heavy sites), the substance is usually still there, grep for it before giving up. Only say FETCH-FAILED if the fetch produced no usable content at all.

4. Synthesize across agent reports: shared mechanism, remediations that repeat across ≥2 incidents (those generalize), and a checklist for the user's incident. Cite each claim with entry id + URL.

## L2, Category / theme survey

Use for "what are the lessons of <category or theme>".

1. Slice the target set with `pm.py search --json` (a category, a `--cause` tag, or an org). For >10 entries, split into slices of 5–8.
2. Dispatch one agent per slice in parallel; each agent runs the L1 reader loop internally over its slice (this is the nesting: survey agent → per-incident fetches) and returns a slice synthesis: mechanisms, repeated remediations, standout incidents.
3. Merge slice syntheses; reconcile against `canonical_patterns` in `data/postmortems.json`: flag patterns the agents found that the catalog lacks.

## L3, Corpus-wide study

Same shape as L2 across all categories, orchestrated with the Workflow tool (pipeline: slice → read → verify → synthesize). Multi-agent orchestration at this scale needs explicit user opt-in, confirm before launching unless they already asked for it.

## Reviewing a postmortem draft

Rubric-driven, read `references/review-rubric.md` and score the draft against all 8 dimensions (blameless language, mechanism chain vs single root cause, hindsight bias, detection analysis, response analysis, action-item quality, luck accounting, impact honesty). Pull 3–5 tagged precedents for the draft's root-cause classes (L1 if depth needed) and cite them in every recommendation. Output the rubric's format: scorecard, top-3 before→after rewrites, missing-content list.

## Writing a postmortem

Follow `references/methodology.md`: Google SRE section structure, Howie's multiple-perspectives discipline (don't flatten responders' differing views into one narrative), Cook's stance (mechanism chain + contributing factors + enabling conditions, never a singular root cause; "human error" starts analysis, never concludes it). Ground remediation proposals in corpus precedent. Self-check the result against `references/review-rubric.md` before delivering.

## Pre-mortem / FMEA for a planned change

Use when the user has a design doc, migration plan, or risky PR and wants failure analysis *before* shipping.

1. Read the plan; inventory what it touches (systems, data, traffic, config surfaces, rollback paths).
2. Klein framing (see `references/methodology.md`): "It is six months later and this change caused a serious incident, write the postmortem headline." Generate 5–10 concrete failure narratives, not abstract risks.
3. For each narrative, ground it in precedent: `pm.py search` for the same mechanism (config rollout, migration, failover, capacity). A pre-mortem entry with a real incident id ("this is exactly `circleci`: type change made rollback unsafe") carries weight an invented scenario doesn't. Drop narratives with neither precedent nor a concrete mechanism. For this workflow, citing the corpus at the index/summary level is sufficient, you don't need to fetch full texts (that "Common mistakes" rule applies to deep technical claims in a finished postmortem, not to precedent-grounding a pre-mortem).
4. Output an FMEA-style table, failure mode | mechanism | precedent (id) | how we'd detect it | severity (Critical/High/Med/Low) | likelihood (High/Med/Low) | mitigation, followed by: the 3 modes with the highest severity×likelihood, recommended guardrails (staged rollout, semantic config validation, tested rollback, detection additions), and what to verify in a drill before the change ships. Use the two ordinal scales exactly as given so rows are comparable.

## Cross-incident pattern analysis (your own corpus)

Use when the user points at a directory of *their org's* postmortems ("what keeps biting us?").

1. Inventory the directory; dispatch one reader agent per document (batch into slices of 5–8 if many) extracting structured fields per the corpus schema: trigger, root_cause_class[], contributing factors, detection source, time-to-mitigate, action items (+ whether verifiable), what-went-well.
2. Cluster in the main context: recurring root-cause classes, repeat contributing factors, action items that recur across incidents (= previous items didn't remove the class), detection sources (how often did customers detect before monitoring?).
3. Compare the org's distribution against the public corpus (`pm.py stats`): over-represented classes are the systemic signal.
4. Output: systemic-risk report, top recurring patterns with per-incident citations, orphaned/recurring action items, detection-gap summary, and the 3 highest-leverage structural fixes.

## Data contract (`data/postmortems.json` + `data/extra_incidents.json`)

`categories[].entries[]`: `id` (stable slug, e.g. `cloudflare-3`), `org`, `url`, `summary`, `alive` + `http_status` (link health), `archived`/`wayback_url` (archive fallbacks), `root_cause_class[]`, `trigger`, `blast_radius[]`, `lesson`, `suggested_category` (proposed sub-bucket for uncategorized). Top-level `canonical_patterns` maps category → recurring mechanisms with entry ids. `extra_incidents.json` holds additional corpora (currently AWS Post-Event Summaries) in the same shape; `pm.py` merges it into every search and `refresh` never touches it.

## Common mistakes

- **Reading `data/postmortems.json` or whole reference files into main context**: that's ~250 summaries; use `pm.py search` and read only hits.
- **Curl/WebFetch on a raw URL that's dead**: `pm.py fetch <id>` already resolves Wayback fallbacks; use it.
- **Reader agents returning full page text**: the prompt template caps them at a ≤300-word structured extract; keep that cap.
- **Trusting summaries for deep claims**: index summaries are one-paragraph; any specific technical claim in a deliverable must come from a fetched full text.
- **Skipping the tag filters**: keyword-only search misses synonyms ("BGP" vs "routing"); combine `--cause`/`--blast` with keywords.
- **After `pm.py refresh`**: new upstream entries have no tags; tag them (taxonomy vocabulary) before relying on tag search.
