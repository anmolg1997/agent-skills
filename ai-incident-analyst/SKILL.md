---
name: ai-incident-analyst
description: Use when analyzing failures of AI/LLM/agentic systems, an agent took a destructive or unintended action, a chatbot hallucinated with real-world consequences, prompt injection or jailbreak, model-quality or behavior regression after an update, reviewing an agent system design for failure modes before launch, writing a postmortem for an AI incident, or when the user mentions AI incidents, agent safety review, guardrails, prompt injection precedent, or "has an AI system done this before".
---

# AI Incident Analyst

## Overview

An agentic harness over a curated corpus of **canonical AI/LLM/agent failure incidents** (Replit's production-DB deletion, Anthropic's three-bug quality postmortem, GPT-4o sycophancy rollback, EchoLeak zero-click injection, Gemini CLI file destruction, Grok behavior-config incidents, Air Canada chatbot liability, …), each tagged with a **12-class failure vocabulary** that mirrors SRE root-cause taxonomies. Workflows run nested: index search first, reader agents for depth, synthesis last. For classic infrastructure mechanics (capacity, DNS, deploys), delegate to the sibling **postmortem-analyst** skill, AI services inherit all of those failure modes plus the twelve here.

## Quick reference

All commands run from this skill's directory.

| Task | Command |
|---|---|
| Find incidents by keyword | `python3 scripts/ai.py search injection exfiltration` (multiple terms are AND-matched against id/title/mechanism/lesson/class, if a query returns few hits, drop a term and retry; prefer `--class` filters over guessing synonyms) |
| Filter by failure class | `python3 scripts/ai.py search --class runaway-autonomy` |
| Full record for one incident | `python3 scripts/ai.py show replit-saastr-db-deletion` |
| Fetch source text | `python3 scripts/ai.py fetch <id> --out /tmp/inc.txt` (tries each URL, then Wayback) |
| Class distribution | `python3 scripts/ai.py classes` |

References (read on demand):
- `references/failure-classes.md`: the 12-class vocabulary: definitions, SRE analogs, exemplar incidents, design controls per class.
- `references/mast-taxonomy.md`: Berkeley MAST's 14 multi-agent design-time failure modes + review checklist.
- `references/databases.md`: live databases (AIID, AVID, MIT tracker, OECD AIM, Charlotin) and security vocabularies (OWASP LLM Top-10, MITRE ATLAS) for breadth beyond the curated corpus.

The corpus is small and curated (~20 incidents chosen for lesson density): reading `data/ai_incidents.json` whole is acceptable when synthesizing across it; prefer `ai.py search` for lookups.

## Workflows

### Precedent lookup (L0/L1)

"Has an AI system failed this way before?", search by class + keywords; answer from the index's mechanisms and lessons. For depth, use the nested reader pattern: dispatch one agent per relevant incident with the prompt template below, then synthesize with citations (id + URL).

> Fetch this incident's sources: run `python3 <skill-dir>/scripts/ai.py fetch <id> --out <absolute-scratchpad-path>/<id>.txt` then read the file. Extract, ≤300 words: (1) the failure mechanism chain, (2) which safety controls were missing or bypassed, (3) remediations adopted (or absent, note that too), (4) how this maps onto: <one-paragraph description of the user's situation>. If the file is dominated by nav/page-chrome and thin on article text (common for JS-heavy sites), the substance is usually still there, grep for it, or re-run `fetch` on the entry's other URLs before giving up. Only say FETCH-FAILED if no candidate URL yields usable content.

For incidents beyond the curated corpus, query AIID (see `references/databases.md`) via WebFetch.

### Agentic pre-mortem / design review

Use when reviewing a planned or existing agent system (a design doc, a repo, a tool manifest). This is the skill's highest-value workflow.

1. Inventory the system: model(s), tools and their permission scopes, credential reach, retrieval sources, output channels (links/images/commits/API calls), autonomy level (human gates? irreversible ops?), update/config paths for prompts and personas, eval coverage.
2. Walk **all 12 failure classes** from `references/failure-classes.md` against the inventory. For each class: applicable? what's the concrete scenario here? which design control is present/absent? Cite corpus precedent for every risk you flag (this is what separates the review from generic advice). If a real risk has no close corpus precedent (e.g. a domain-specific hazard), say so explicitly and query AIID (`references/databases.md`) for one rather than dropping the risk or forcing a weak analogy.
3. For multi-agent designs, additionally run the MAST review checklist (`references/mast-taxonomy.md`).
4. For security-audience deliverables, map findings to OWASP LLM Top-10 codes.
5. Output: a risk table, failure class | concrete scenario | precedent (id) | severity (Critical/High/Med/Low) | existing control | recommended guardrail, ranked by severity and **capped at the top 8–10 rows** (you assessed all 12 classes; surface the ones that matter). Follow with the top-5 guardrails ranked by blast-radius reduction. The recurring big five: environment separation, human gates on irreversible operations, tool-result read-back verification, prompt-injection trust boundaries on retrieval and output channels, behavior-config change control (prompts in git + review).

### AI-incident postmortem writing

Use when the user's own AI system had an incident.

1. **Preserve artifacts first** (agent evidence is uniquely volatile): full traces, tool-call logs, exact prompts/system prompts, model + config versions, retrieval corpus state, seeds/temperatures where relevant. Say explicitly what was not captured.
2. **Never trust agent narration as evidence**: ground every timeline claim in environment state (logs, DB counts, file listings). If the agent's self-reports diverge from reality, that is itself a finding (`deceptive-self-report`).
3. Classify: primary + contributing classes from the vocabulary; find the 2-3 closest corpus precedents and compare remediations.
4. Draft using the classic structure (summary, impact, timeline, mechanism chain, not "root cause" singular, detection gap, response analysis, action items with owner/date/verifiable criterion), plus an AI-specific section: which safety controls existed, which were bypassed and how.
5. For the writing/review rubric itself, use the sibling postmortem-analyst skill's `references/review-rubric.md` and `references/methodology.md`.

### Cross-domain delegation

If the incident's mechanism is classic infrastructure (capacity, DNS, config rollout, database): even at an AI company, run the postmortem-analyst workflows over its 260+-incident corpus instead; use this skill only for the AI-behavior layers. `openai-dec-2024-outage` and `cloudflare-nov-2025-ai-dependency` are the bridge examples.

## Common mistakes

- **Treating prompt instructions as safety controls**: every corpus incident where the only guardrail was prose (Replit's code freeze, Chevrolet's persona) ended with the guardrail bypassed. Recommend structural controls.
- **Flagging risks without precedent**: a review that cites `gemini-cli-file-destruction` for missing read-back verification lands; an unsourced "agents can be dangerous" doesn't. Always attach entry ids.
- **Using agent self-reports as incident evidence**: see `deceptive-self-report`; verify against environment state.
- **Claiming autonomous RCA**: frontier agents solve ~11% of OpenRCA cases; frame outputs as analysis assistance with cited reasoning, not verdicts.
- **Forgetting the classic layer**: an AI service outage usually has an ordinary SRE mechanism underneath; check whether postmortem-analyst's corpus is the better lens before deep-diving here.
