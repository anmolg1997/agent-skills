# MAST: Multi-Agent System Failure Taxonomy (design-time review lens)

From "Why Do Multi-Agent LLM Systems Fail?" (Cemri et al., UC Berkeley, arXiv:2503.13657, 2025): the first empirically grounded taxonomy of multi-agent failures: 200+ traces across 7 frameworks, 6 annotators, Cohen's κ 0.88. **Key finding: most failures stem from system design, not model capability.** Annotated dataset + LLM-as-judge annotator are open-sourced (linked from the paper).

Use this taxonomy when reviewing a multi-agent design or debugging a misbehaving agent pipeline, it covers design-time failure modes, complementing `failure-classes.md` (production incident root causes).

## Category 1, Specification issues
1. **Disobey task specification**: agent ignores task constraints or requirements.
2. **Disobey role specification**: agent acts outside its assigned role.
3. **Step repetition**: redundant re-execution of completed steps.
4. **Loss of conversation history**: context truncation/reset drops earlier decisions.
5. **Unaware of termination conditions**: agent doesn't know when it's done, loops or stops arbitrarily.

## Category 2, Inter-agent misalignment
6. **Conversation reset**: dialogue restarts, losing agreed state.
7. **Failure to ask for clarification**: proceeds on ambiguity instead of resolving it.
8. **Task derailment**: drifts to a different task than assigned.
9. **Information withholding**: one agent holds data another needs and never shares it.
10. **Ignored other agent's input**: contributions dropped without consideration.
11. **Reasoning-action mismatch**: stated reasoning and executed action diverge.

## Category 3, Task verification
12. **Premature termination**: ends before the task is actually complete.
13. **No or incomplete verification**: results never checked, or checked superficially.
14. **Incorrect verification**: the check itself is wrong, blessing bad output.

## Review checklist derived from MAST

For each agent in a proposed design, ask:
- Is its role/task spec enforceable (schema, validation) or only prose? (modes 1-2)
- What bounds loops and declares termination? Who owns that state? (modes 3, 5, 12)
- What survives context compaction/handoffs? Is shared state externalized? (modes 4, 6)
- What forces clarification on ambiguous input rather than best-effort guessing? (mode 7)
- How does information provably flow between agents, is there a contract? (modes 9, 10)
- Is verification a distinct step with its own agent/criteria, and is the verifier itself testable? (modes 13, 14)

Cross-reference: production incidents from these design gaps typically land in `hallucinated-state`, `runaway-autonomy`, or `deceptive-self-report` in the incident vocabulary.
