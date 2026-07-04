# Postmortem Methodology (distilled canon)

The analysis frameworks this skill's workflows encode. Read the section you need; canonical sources linked (all verified 2026-07-04).

## Google SRE postmortem template

Canonical section order (from the SRE Book's example postmortem):
**Summary → Impact (user-visible, duration, magnitude) → Root Causes → Trigger → Resolution → Detection → Action Items (owner, priority, tracking id) → Lessons Learned (what went well / what went wrong / where we got lucky) → Timeline (timestamped, with detection and mitigation moments marked).**

Culture rules: blameless (assume everyone acted reasonably on the information they had), postmortems for every user-visible incident above threshold, reviewed like code, shared widely.
Sources: https://sre.google/sre-book/postmortem-culture/ · https://sre.google/sre-book/example-postmortem/ · https://sre.google/workbook/postmortem-culture/ (good vs bad postmortem comparison).

## Howie: the post-incident process (Jeli/PagerDuty)

Eight stages: **Assign → Identify (data sources) → Analyze → Interview → Calibrate → Meet → Report → Distribute.** The differentiator vs template-filling: interviews and multiple-perspective analysis — the incident looks different from each responder's seat, and the writeup should preserve that rather than flatten it into one narrative.
Source: https://howie-guide.pagerduty.com/

## Etsy Debriefing Facilitation Guide (CC-BY-SA-4.0)

The debrief is for **learning, not documentation** — the facilitator's job is drawing out what people actually saw and did. Signature question shapes:
- "When you saw X, what did you think was happening?" (recovers real-time mental models)
- "What did you do next, and what were you expecting to happen?" (actions + expectations)
- "Was there anything about this incident that surprised you?" (locates the model-reality gap)
- "How did you know to look there?" (surfaces unwritten expertise worth spreading)
Avoid "why" questions (invite justification, not recall) and any question containing "should."
Source: https://github.com/etsy/DebriefingFacilitationGuide (archived but stable; PDF at extfiles.etsy.com/DebriefingFacilitationGuide.pdf).

## Cook: How Complex Systems Fail (analysis stance)

The points that most change how you analyze (of 18): complex systems run in degraded mode all the time; catastrophe requires **multiple** contributing failures — single-point explanations are wrong; **"post-accident attribution to a 'root cause' is fundamentally wrong"** (point 7) — hindsight bias makes the path look obvious only afterwards; the people blamed for the failure are usually also the ones who normally create safety.
Practical consequence for this skill: prefer "mechanism chain + contributing factors + enabling conditions" over any singular root cause; treat "human error" in a draft as the *start* of analysis (why did that action make sense at the time?), never the conclusion.
Source: https://how.complexsystems.fail/ · companion critique: https://github.com/readme/guides/root-cause (Allspaw).

## Klein: the pre-mortem

Prospective hindsight: assume the plan **has already failed spectacularly** — "it's six months later; this was a disaster" — then have everyone write down why. The framing legitimizes dissent and surfaces risks planning optimism suppresses. Beats critique-the-plan reviews because participants generate failure narratives instead of defending positions.
Source: Klein, "Performing a Project Premortem," HBR 2007 — https://hbr.org/2007/09/performing-a-project-premortem
This skill's pre-mortem workflow adds two things to Klein: an FMEA-style table (mode / effect / detection / severity) and corpus precedent for each imagined failure.

## Theory shelf (when you need more)

lorin/resilience-engineering — https://github.com/lorin/resilience-engineering — 200+ curated papers (Allspaw, Cook, Dekker, Woods); the field's reading list, maintained.
