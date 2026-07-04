# Live AI-Incident Databases & Security Vocabularies

The bundled corpus (`data/ai_incidents.json`) is curated for lesson density, not completeness. For breadth or fresh incidents, query these (all verified live 2026-07-04):

## Incident databases

- **AI Incident Database (AIID)** — https://incidentdatabase.ai — ~1,200+ curated incidents, each a stable ID aggregating press reports (our corpus cross-references these as `aiid_id`; cite as `https://incidentdatabase.ai/cite/<id>/`). Taxonomies overlaid: CSET AI Harm (harm type, sector, harmed party) and GMF (Goals/Methods/Failures). **Machine-readable: full JSON/MongoDB snapshots downloadable from the site.** Best first stop for "has an AI system done X before?"
- **AVID (AI Vulnerability Database)** — https://avidml.org — CVE-style reports for AI, rebuilt 2025-26 for agents. 3-axis taxonomy: SEP domains (Security/Ethics/Performance) × sub-category × lifecycle stage. **Machine-readable: MISP-format JSON taxonomy + JSON report schema** — the most schema-rigorous; borrow its shape for new incident records.
- **MIT AI Incident Tracker** — https://airisk.mit.edu/ai-incident-tracker — AIID incidents re-classified against the MIT AI Risk Repository (7 domains), with severity scores; monthly updates; downloadable spreadsheet.
- **OECD AI Incidents & Hazards Monitor (AIM)** — https://oecd.ai/en/incidents — automated global news ingestion; distinguishes incidents (harm occurred) from hazards (plausible harm); underpins EU AI Act reporting definitions. Browsable/filterable; weaker as a citation system.
- **AIAAIC Repository** — https://www.aiaaic.org/aiaaic-repository — editor-curated incidents *and controversies* (broader than harm); CSV export; best for reputational/ethics cases.
- **AI Hallucination Cases (Charlotin)** — https://www.damiencharlotin.com/hallucinations/ — ~1,700 court decisions involving AI-fabricated citations (mid-2026); jurisdiction, party type, AI tool, sanction. The best longitudinal dataset of a single failure class. (403s to bots — browse manually.)
- **vectara/awesome-agent-failures** — https://github.com/vectara/awesome-agent-failures — community case studies of agent failures.

## Security vocabularies (for design review)

- **OWASP Top 10 for LLM Applications** — https://owasp.org/www-project-top-10-for-large-language-model-applications/ — LLM01 Prompt Injection … LLM06 Excessive Agency etc.; the de-facto security vocabulary. Map findings to it for audiences that speak OWASP.
- **MITRE ATLAS** — https://atlas.mitre.org — adversarial-ML tactics/techniques matrix (ATT&CK for AI).
- **MAST** — see `mast-taxonomy.md` (design-time multi-agent failure modes).

## Research anchors

- "Incident Analysis for AI Agents" (arXiv:2508.14231) — adapts safety-engineering incident analysis to agents; defines which artifacts (traces, tool logs, prompts, model/config versions) must be preserved for agent postmortems. Basis of this skill's artifact-preservation checklist.
- OpenRCA benchmark — https://github.com/microsoft/OpenRCA — frontier agents solve ~11% of RCA cases; grounds this skill's stance: assist analysis, don't claim autonomous diagnosis.
- "Why Do AI Agents Systematically Fail at Cloud RCA?" (arXiv:2602.09937) — 12 systematic pitfalls of RCA agents.
