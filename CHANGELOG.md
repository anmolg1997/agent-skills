# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-04

First public release: two Claude Code skills for pre-mortems and postmortems.

### Added

- **postmortem-analyst** skill: an incident-analysis engine over 261 tagged
  real-world postmortems (243 from the community postmortem index plus 18 AWS
  Post-Event Summaries), with root-cause / blast-radius / lesson tags, 32
  canonical failure patterns, and link-health data with archive.org fallbacks.
  Workflows: nested precedent lookup (L0 to L3), pre-mortem / FMEA, rubric-based
  postmortem review, methodology-driven postmortem writing, and cross-incident
  pattern analysis. CLI: `pm.py` (search / show / fetch / stats / refresh).
- **ai-incident-analyst** skill: a curated corpus of 22 canonical AI / LLM /
  agent failure incidents, a 12-class failure vocabulary that mirrors SRE
  taxonomies, plus the MAST multi-agent taxonomy and OWASP LLM Top-10 as
  references. Workflows: precedent lookup, agentic pre-mortem / design review,
  and AI-incident postmortem writing. CLI: `ai.py` (search / show / fetch /
  classes).
- Claude Code plugin marketplace (`.claude-plugin/marketplace.json` and
  per-skill manifests) so both skills install with `/plugin marketplace add`.
- Reference material: failure taxonomies, postmortem and pre-mortem methodology
  (Google SRE, Howie, Etsy, Cook, Klein), a review rubric, and a catalog of
  further public postmortem sources.
