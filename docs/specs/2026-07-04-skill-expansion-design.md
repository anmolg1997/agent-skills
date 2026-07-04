# Agent-Skills Expansion: postmortem-analyst v2 + ai-incident-analyst

Date: 2026-07-04. Status: approved (audience: public/community artifact; approach A of three presented).

## Goal

Make the collection a reference-grade public artifact by (1) upgrading `postmortem-analyst` with the analysis workflows commercial incident tooling doesn't serve, (2) adding a second flagship skill, `ai-incident-analyst`, covering agentic-AI failures, a green-field niche, and (3) making the collection installable both by clone+symlink and via the Claude Code plugin marketplace.

Grounded in three web-research reports (2026-07-04): incident-tooling capability map, public postmortem-source survey, and agentic-AI incident catalog. Key findings driving the design:

- Commercial AI-SRE (incident.io, Rootly, Datadog Bits, PagerDuty…) owns live triage and first-draft postmortems. Unserved: methodology-driven analysis, rubric-based postmortem review, cross-incident pattern mining, facilitation prep, pre-mortems/FMEA.
- Best integrable corpus add: AWS Post-Event Summaries (20 canonical RCAs, stable, tiny). VOID (~10k reports) deferred: ToS-gated scraping. Feeds (Cloudflare/GitHub/Azure) deferred to a possible later automation phase.
- Agentic-AI failures have no curated skill/corpus anywhere: ~20 canonical incidents identified, a 12-class failure vocabulary mirroring SRE taxonomies, MAST (Berkeley) for design-time multi-agent modes, AIID/AVID as machine-readable databases.

## Scoping decision: two skills, not three

The candidate third skill ("postmortem-writer/methodology") was rejected: every methodology workflow (review rubric, pre-mortem, pattern analysis) is differentiated precisely by being grounded in corpus precedent, splitting methodology from corpus would create a hard cross-skill dependency and weaken both. Boundary between the two shipped skills is by failure domain, which keeps trigger descriptions non-overlapping:

- `postmortem-analyst`: infrastructure/SRE incidents (danluu corpus + AWS PES).
- `ai-incident-analyst`: AI/LLM/agent behavior, security, and autonomy failures.

Infra outages *of* AI services (e.g. OpenAI Dec 2024) live in ai-incident-analyst's corpus but its SKILL.md delegates classic-SRE analysis to postmortem-analyst.

## Part 1, postmortem-analyst v2

New/changed files:

- `SKILL.md`: three workflow additions/upgrades:
  - **Pre-mortem / FMEA**: input: design doc/PR/plan. Klein prospective hindsight → FMEA table (mode, effect, detection, severity) → ground each mode in corpus precedent via `pm.py search` → guardrails. Output: pre-mortem report.
  - **Postmortem quality review** (upgrades existing section): rubric-driven via `references/review-rubric.md`.
  - **Cross-incident pattern analysis**: input: directory of user's own postmortems. Reader agents extract structured fields per doc (corpus taxonomy) → cluster contributing factors → systemic-risk report. Nested, same dispatch pattern as L1/L2.
- `references/methodology.md`: distilled: Google SRE postmortem template + culture, Howie 8 stages, Etsy debriefing facilitation questions (CC-BY-SA, attributed), Cook's How Complex Systems Fail principles, Klein pre-mortem method. Links to canonical sources.
- `references/review-rubric.md`: scored rubric: blame/counterfactual language, hindsight-bias markers, single-root-cause seduction, missing detection/response analysis, action-item specificity (owner/date/verifiable), what-went-well, near-miss luck.
- `references/sources.md`: vetted catalog of further corpora (VOID, AWS PES, Cloudflare/GitHub/Azure feeds, Wikimedia, k8s.af, SRE Weekly) with freshness/machine-readability/integration notes; marks dead sources (learningfromincidents.io).
- `data/extra_incidents.json`: AWS PES entries (~20), same tag schema as the danluu index.
- `scripts/pm.py`: `load()` merges `extra_incidents.json` (as additional categories) when present; `refresh` continues to touch only `postmortems.json`, so upstream sync never clobbers additions.

## Part 2, ai-incident-analyst (new skill)

Layout mirrors the sibling: `SKILL.md`, `README.md`, `data/ai_incidents.json`, `references/{failure-classes,mast-taxonomy,databases}.md`, `scripts/ai.py`.

- `data/ai_incidents.json`: ~20 canonical incidents (Replit/SaaStr, Anthropic three-bug, GPT-4o sycophancy, EchoLeak, CamoLeak, Slack AI exfil, Amazon Q wiper, Gemini CLI destruction, Grok ×2, Air Canada, Mata/Wadsworth, Cursor Sam, NYC MyCity, Bing Sydney, Gemini image-gen, McDonald's drive-thru, Sakana, Claude Code brick, OpenAI Dec-2024, Cloudflare Nov-2025 as dependency example). Fields: id, org, date, title, urls[], aiid_id, failure_class (primary), contributing_classes[], mechanism, lesson, postmortem_quality note (first-party postmortem vs press-only, itself a lesson).
- `references/failure-classes.md`: 12-class vocabulary, each with definition, SRE analog, exemplar incidents: prompt-injection (direct/indirect/supply-chain), hallucination-with-authority, runaway-autonomy, hallucinated-state, excessive-agency, guardrail-bypass, behavior-config-change, model-quality-regression, reward-misspecification, eval-gap, deceptive-self-report, infra-outage-of-ai-service.
- `references/mast-taxonomy.md`: Berkeley MAST 14 failure modes / 3 categories for design-time multi-agent review; link to dataset.
- `references/databases.md`: AIID, AVID, MIT AI Incident Tracker, OECD AIM, Charlotin hallucination-cases tracker, OWASP LLM Top-10, MITRE ATLAS: coverage, machine-readability, how to query live.
- `scripts/ai.py`: search/show/fetch over the flat incident list (adapted from pm.py; no refresh, corpus is hand-curated).
- `SKILL.md` workflows: L0 lookup; L1 precedent deep-dive (nested reader agents, same pattern); **agentic pre-mortem / design review** (walk 12 classes + OWASP LLM10 + MAST against a proposed agent system → risk table + guardrail checklist: env separation, human gates on destructive ops, tool-result verification, injection surface inventory, long-horizon eval coverage, behavior-config change control); **AI-incident postmortem writing** (artifact preservation: traces, prompts, tool logs, model/config versions; classic template adapted). Cross-delegation note to postmortem-analyst for classic-SRE mechanics.

## Part 3, Collection packaging

- Catalog `README.md`: two-skill table, both install paths.
- Plugin marketplace: `.claude-plugin/marketplace.json` (+ per-plugin manifests as the schema requires) so `/plugin marketplace add anmolg1997/agent-skills` works. Exact schema per official docs (verified by a docs agent during implementation). Clone+symlink path must keep working unchanged.
- `~/.claude/skills/ai-incident-analyst` symlinked into the local checkout, like its sibling.

## Testing

- Blind subagent tests (agent gets only the skill path): (a) ai-incident-analyst retrieval ("what precedent exists for an AI agent deleting production data?"), (b) agentic pre-mortem applied to a sample agent design, (c) postmortem-analyst pre-mortem workflow on a sample migration plan, (d) re-run a v1 regression test (search/fetch still work with merged indexes).
- Fix gaps found, re-verify (same loop as v1).

## Out of scope (deferred)

VOID snapshot integration (needs ToS blessing), live feed scrapers + GitHub Action refresh automation, facilitation-prep workflow (W4, candidate for v3), embedding-based similarity search.
