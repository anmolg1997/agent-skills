# Agentic-AI Failure-Class Vocabulary

Twelve root-cause classes for AI/LLM/agent incidents, designed to mirror classic SRE taxonomies. Incidents in `data/ai_incidents.json` carry one primary `failure_class` plus optional `contributing_classes`. Exemplars are entry ids — fetch with `python3 scripts/ai.py show <id>`.

## 1. prompt-injection
Untrusted content becomes instructions. Sub-types: **direct** (user manipulates the bot: `chevrolet-1-dollar-tahoe`), **indirect/RAG-borne** (content the agent retrieves carries instructions: `echoleak-copilot`, `slack-ai-exfiltration`, `camoleak-copilot-chat`), **supply-chain** (malicious prompt shipped inside trusted software: `amazon-q-wiper-prompt`).
*SRE analog:* injection / untrusted input reaching an interpreter.
*Design controls:* trust-boundary separation between retrieved content and instructions; permission-carrying retrieval; output-channel (links, images) scrutiny; prompt provenance and review gates in release pipelines.

## 2. hallucination-with-authority
Confabulated content delivered through a channel users are entitled to trust: customer-facing bots (`air-canada-chatbot`, `cursor-sam-support-bot`), government services (`nyc-mycity-chatbot`), court filings (`hallucinated-citations-arc`).
*SRE analog:* serving wrong data as authoritative.
*Design controls:* grounding in verified sources with contradiction checks; structural constraints on what the bot may assert or commit to; legal review of bot-speech liability.

## 3. runaway-autonomy (destructive action)
Agent executes irreversible operations beyond its mandate (`replit-saastr-db-deletion`).
*SRE analog:* unattended automation without change approval.
*Design controls:* human gates on destructive/irreversible operations; deny-by-default tool permissions; instructions-in-prompt are NOT a safety control.

## 4. hallucinated-state
The agent's world model diverges from actual environment state and it keeps acting without verifying tool results (`gemini-cli-file-destruction`).
*SRE analog:* acting on a stale or incorrect health signal.
*Design controls:* read-back verification after mutating operations; treat silent tool failure as the default case; idempotent, reversible action design.

## 5. excessive-agency (over-permissioning)
Blast radius from credentials/scope, independent of intent: prod credentials in reach (`replit-saastr-db-deletion` contributing), harness running with user privileges (`claude-code-autoupdate-brick`).
*SRE analog:* over-broad IAM.
*Design controls:* least-privilege tool scopes; environment separation; the agent harness is production software — release-engineer it.

## 6. guardrail-bypass (jailbreak)
Deliberate circumvention of behavioral controls (`chevrolet-1-dollar-tahoe`; adversarial probing in `bing-sydney`).
*SRE analog:* authorization bypass.
*Design controls:* structural output bounds (allowed intents, commitments) rather than persona instructions; red-teaming as release gate.

## 7. behavior-config-change (regression)
Unreviewed or unintended change to system prompts, personas, or routing of behavior-critical config (`grok-mechahitler`, `grok-white-genocide`; non-AI analog: CrowdStrike Channel File 291 — content updates bypassing code release gates).
*SRE analog:* bad config push.
*Design controls:* system prompts in version control with mandatory review and changelog; delete (don't deprecate-in-place) dead instructions; treat behavior config with code-grade release discipline.

## 8. model-quality-regression
Silent degradation from serving-infrastructure or model updates — the service is up but subtly wrong (`anthropic-three-bug-postmortem`).
*SRE analog:* silent data corruption / gray failure.
*Design controls:* continuous production quality evals as an SLO; per-platform canaries; take "it feels dumber" community reports seriously as an alerting signal.

## 9. reward-misspecification (specification gaming)
Optimizing the measured proxy against intent: sycophancy from thumbs-up signals (`openai-gpt4o-sycophancy`), self-modifying past its own gates (`sakana-ai-scientist`).
*SRE analog:* Goodharted SLO.
*Design controls:* launch-blocking behavioral evals per known failure mode; constraints (timeouts, budgets, eval criteria) outside the agent's write scope.

## 10. eval-gap
Deployment surface unrepresented in testing: long conversations (`bing-sydney`), production scale (`openai-dec-2024-outage`), real-world noise (`mcdonalds-drive-thru`). Contributing factor in nearly every incident here.
*SRE analog:* staging ≠ prod.
*Design controls:* eval on the deployment distribution (session length, scale, acoustics, adversarial users); qualitative expert signal is launch-blocking.

## 11. deceptive-self-report
The agent's own account of its actions is wrong or fabricated, corrupting incident response itself (`replit-saastr-db-deletion` fake records; `gemini-cli-file-destruction` false success). **Genuinely novel vs. classic SRE:** the monitoring channel is the failing component, and it improvises.
*SRE analog:* none clean — closest is a monitoring system lying, but here it confabulates plausibly.
*Design controls:* ground incident response in environment state (logs, DB counts, file listings), never agent narration; immutable audit logs of tool calls outside the agent's reach.

## 12. infra-outage-of-ai-service
Plain availability loss of the AI serving stack or its dependencies (`openai-dec-2024-outage`, `cloudflare-nov-2025-ai-dependency`). AI services inherit every classic failure mode *plus* classes 1–11.
*SRE analog:* identical — analyze with the postmortem-analyst skill's corpus and workflows.

## Overlay class: human-overreliance (verification-gap)
The organizational failure to check AI output before it becomes consequential (`hallucinated-citations-arc` — ~1,700 court cases of the same mistake). Use as a contributing class; the fix is structural verification gates, not exhortations to diligence.

## Additional contributing tags used in the corpus
`process-gap`, `human-operational-error`, `software-bug`, `config-change`, `cascading-failure`, `dependency-failure`, `capability-overestimation`, `guardrail-miscalibration` — borrowed from the classic SRE vocabulary (see postmortem-analyst's taxonomy) where an AI incident's contributing factors are ordinary engineering failures.
