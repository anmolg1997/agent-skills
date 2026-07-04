# ai-incident-analyst

An [Agent Skill](https://agentskills.io) for Claude Code that analyzes failures of **AI, LLM, and agentic systems**: grounded in a curated corpus of canonical real-world incidents rather than generic "AI safety" advice.

## What it does

- **~20 canonical AI incidents, tagged and searchable** (`data/ai_incidents.json`): Replit's agent deleting a production database mid-code-freeze, Anthropic's three-bug silent-quality-degradation postmortem, OpenAI's GPT-4o sycophancy rollback, EchoLeak (first zero-click exploit of a production agent), Gemini CLI destroying files off a hallucinated `mkdir`, Grok's system-prompt incidents, Air Canada's legally binding chatbot hallucination, and more, each with mechanism, canonical sources, AIID cross-references, and a transferable lesson.
- **A 12-class failure vocabulary** (`references/failure-classes.md`) that mirrors SRE root-cause taxonomies: prompt-injection, hallucination-with-authority, runaway-autonomy, hallucinated-state, excessive-agency, guardrail-bypass, behavior-config-change, model-quality-regression, reward-misspecification, eval-gap, deceptive-self-report, infra-outage-of-ai-service, each with its SRE analog and design controls.
- **Agentic pre-mortem / design review workflow**: walks all 12 classes plus Berkeley's MAST multi-agent taxonomy and OWASP LLM Top-10 against your agent system's actual tool scopes, credentials, retrieval sources, and autonomy level, every flagged risk cited to precedent.
- **AI-incident postmortem workflow**: artifact preservation (traces, prompts, tool logs, uniquely volatile), never-trust-agent-narration evidence discipline, classification, and drafting.
- **Pointers to the live databases** (`references/databases.md`): AI Incident Database, AVID, MIT AI Incident Tracker, OECD AIM, the ~1,700-case hallucinated-citations tracker.

Sibling skill: [postmortem-analyst](../postmortem-analyst/) covers classic infrastructure/SRE incidents; this skill delegates to it when an AI incident's mechanism is ordinary infrastructure.

## Install

Via the [prepostmortem-skills](https://github.com/anmolg1997/prepostmortem-skills) collection:

```bash
git clone https://github.com/anmolg1997/prepostmortem-skills ~/prepostmortem-skills
ln -s ~/prepostmortem-skills/ai-incident-analyst ~/.claude/skills/ai-incident-analyst
```

Or as a plugin: `/plugin marketplace add anmolg1997/prepostmortem-skills` then `/plugin install ai-incident-analyst@prepostmortem-skills`.

## Direct CLI usage

```bash
cd ~/.claude/skills/ai-incident-analyst
python3 scripts/ai.py search --class prompt-injection
python3 scripts/ai.py show replit-saastr-db-deletion
python3 scripts/ai.py fetch anthropic-three-bug-postmortem --out /tmp/inc.txt
python3 scripts/ai.py classes
```

## Example prompts once installed

- *"We're giving our coding agent access to the production database, review the design for failure modes."*
- *"Our support chatbot told a customer something false and they're citing it as policy. What's the precedent?"*
- *"Users say the model got dumber after our last deploy but availability metrics are green, where do we start?"*
- *"Write the postmortem for yesterday's incident where the agent overwrote the config directory."*

## References

Public work that helped bring this to life. Thanks to the people behind:

1. First-party postmortems, court records, and security disclosures, for the incidents themselves.
2. The [AI Incident Database](https://incidentdatabase.ai) and AVID, for cross-referencing and taxonomy ideas.
3. Berkeley's MAST taxonomy and the OWASP LLM Top-10, for the agentic failure model.

Each entry links its canonical sources, whose content belongs to their publishers. The failure vocabulary, tagging, and workflows here are our own.
