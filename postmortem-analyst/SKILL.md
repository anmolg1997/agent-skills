---
name: postmortem-analyst
description: Use when analyzing an incident or outage and wanting precedent, researching how real companies failed (config errors, cascading failures, DNS/BGP, data loss, cloud outages), writing or reviewing a postmortem/incident report, surveying failure patterns across the industry, or when the user mentions danluu/post-mortems, incident retrospectives, RCA, or "has anyone else hit this".
---

# Postmortem Analyst

## Overview

An agentic harness over the danluu/post-mortems corpus: **243 real-world incident postmortems** (Google, Cloudflare, AWS, GitHub, GitLab, Facebook, NASA, …) parsed into a tagged, link-health-checked index at `data/postmortems.json`, with per-category references and a failure-mode taxonomy. Analysis runs **nested**: cheap index search first, then fan-out subagents that deep-read only the relevant postmortems, then synthesis. Never bulk-read the corpus into the main context.

## Quick reference

All commands run from this skill's directory (`cd ~/.claude/skills/postmortem-analyst`).

| Task | Command |
|---|---|
| Find incidents by keyword | `python3 scripts/pm.py search dns cascading --limit 10` |
| Filter by tag | `python3 scripts/pm.py search --cause config-change --blast global-outage` |
| Filter by org/category | `python3 scripts/pm.py search --org cloudflare` / `--category database` |
| Full record for one entry | `python3 scripts/pm.py show gitlab` |
| Fetch full postmortem text | `python3 scripts/pm.py fetch <id> --out /tmp/pm.txt` (tries live original, archived snapshot, then Wayback API; on FAILED, fall back to WebFetch with the URL it prints) |
| Corpus stats | `python3 scripts/pm.py stats` |
| Sync with upstream repo | `python3 scripts/pm.py refresh` (preserves tags; new entries need tagging) |

Tag vocabularies and recurring mechanisms: `references/taxonomy.md`.
Per-category curated lists: `references/<category-slug>.md` (config-errors, hardware-power-failures, conflicts, time, database, uncategorized, other-lists-of-postmortems, analysis).

## Choosing the nesting level

| Question shape | Level | Cost |
|---|---|---|
| "Which incidents involved X?" / "show me the Y outage" | L0: index only | seconds |
| "We just had incident X — what precedent exists, what should we check?" | L1: search + 3–8 reader agents | minutes |
| "What do all the <category> failures teach?" | L2: one agent per slice, each reads several postmortems | tens of minutes |
| "Analyze the whole corpus for Z" | L3: L2 + Workflow tool | needs user opt-in for orchestration |

## L0 — Direct lookup

`pm.py search` / `show` / `fetch`. Answer from the index's summaries and lessons; fetch at most 1–2 full texts into main context. Reading one per-category reference file is fine when the target category is small (≤ ~15 entries: time, conflicts, database, hardware) — that's where the canonical patterns live; for config-errors and uncategorized, use `pm.py search` instead.

## L1 — Incident-similarity deep dive

Use when the user describes *their* incident and wants precedent and guidance.

1. Extract the failure signature: root-cause class(es), trigger, blast radius (use `references/taxonomy.md` vocabulary).
2. Run 2–4 `pm.py search` queries (tag filters + keyword variants). Pick the 3–8 strongest matches — rank by overlap with the failure signature: a match on ≥2 dimensions (cause + trigger mechanism, or cause + blast radius) beats any single-dimension match; same-layer incidents (DNS vs DNS) beat same-cause-different-layer.
3. Dispatch **one reader agent per match, in parallel**. Prompt template (you, the dispatcher, must replace `<id>`, `<scratchpad>` with an absolute path, and the incident description before sending):

   > Fetch this postmortem: run `python3 ~/.claude/skills/postmortem-analyst/scripts/pm.py fetch <id> --out <scratchpad>/<id>.txt` then read the file. Extract as your final message, ≤300 words: (1) failure mechanism chain, (2) detection gap — why it wasn't caught earlier, (3) remediations they adopted, (4) which parts map onto this incident: <one-paragraph incident description>. If the fetch fails, say FETCH-FAILED and stop.

4. Synthesize across agent reports: shared mechanism, remediations that repeat across ≥2 incidents (those generalize), and a checklist for the user's incident. Cite each claim with entry id + URL.

## L2 — Category / theme survey

Use for "what are the lessons of <category or theme>".

1. Slice the target set with `pm.py search --json` (a category, a `--cause` tag, or an org). For >10 entries, split into slices of 5–8.
2. Dispatch one agent per slice in parallel; each agent runs the L1 reader loop internally over its slice (this is the nesting: survey agent → per-incident fetches) and returns a slice synthesis: mechanisms, repeated remediations, standout incidents.
3. Merge slice syntheses; reconcile against `canonical_patterns` in `data/postmortems.json` — flag patterns the agents found that the catalog lacks.

## L3 — Corpus-wide study

Same shape as L2 across all categories, orchestrated with the Workflow tool (pipeline: slice → read → verify → synthesize). Multi-agent orchestration at this scale needs explicit user opt-in — confirm before launching unless they already asked for it.

## Reviewing or writing a postmortem

Use the corpus as the rubric, not a template:

1. Identify the draft's root-cause classes; pull the matching taxonomy section and 3–5 tagged precedents (L1 if depth needed).
2. Check the draft against what good corpus postmortems contain: mechanism chain (not just "root cause"), timeline with detection/mitigation timestamps, why defenses missed it, contributing factors beyond the trigger, remediations that remove the failure class (compare with precedent remediations), and blameless framing (see `human-operational-error` incidents — the fix is never "be more careful").
3. Cite precedent incidents in the review so recommendations carry evidence.

## Data contract (`data/postmortems.json`)

`categories[].entries[]`: `id` (stable slug, e.g. `cloudflare-3`), `org`, `url`, `summary`, `alive` + `http_status` (link health), `archived`/`wayback_url` (archive fallbacks), `root_cause_class[]`, `trigger`, `blast_radius[]`, `lesson`, `suggested_category` (proposed sub-bucket for uncategorized). Top-level `canonical_patterns` maps category → recurring mechanisms with entry ids.

## Common mistakes

- **Reading `data/postmortems.json` or whole reference files into main context** — that's ~250 summaries; use `pm.py search` and read only hits.
- **Curl/WebFetch on a raw URL that's dead** — `pm.py fetch <id>` already resolves Wayback fallbacks; use it.
- **Reader agents returning full page text** — the prompt template caps them at a ≤300-word structured extract; keep that cap.
- **Trusting summaries for deep claims** — index summaries are one-paragraph; any specific technical claim in a deliverable must come from a fetched full text.
- **Skipping the tag filters** — keyword-only search misses synonyms ("BGP" vs "routing"); combine `--cause`/`--blast` with keywords.
- **After `pm.py refresh`** — new upstream entries have no tags; tag them (taxonomy vocabulary) before relying on tag search.
