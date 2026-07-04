# Postmortem Quality Review Rubric

Score a draft postmortem against each dimension: **pass / weak / fail**, with the specific passage quoted for anything below pass. Recommendations must cite corpus precedent where one exists (`pm.py search`).

## 1. Blameless language
Fail markers: named-individual blame; "X failed to", "should have", "carelessly", "if only". These are counterfactual/normative judgments, not analysis.
Fix: rewrite as the local rationality question — what information did the actor have, and why did the action make sense at the time? "Human error" is a starting point for analysis, never a conclusion (see Cook, `methodology.md`).

## 2. Mechanism chain vs. single root cause
Fail markers: one "Root Cause:" sentence; no contributing factors; no enabling conditions.
Pass looks like: trigger (what set it off) distinguished from contributing factors (what let it propagate) and enabling conditions (what made it possible at all) — complex-systems failures require multiple factors, and the writeup should name each.

## 3. Hindsight-bias markers
Fail markers: "it was obvious that", "clearly the team missed", timeline narration that assumes responders knew the ending.
Fix: describe what responders actually saw at each timestamp (their dashboards, their hypotheses — including the wrong ones; wrong hypotheses are data about system observability).

## 4. Detection analysis
Questions the draft must answer: How was it detected (alert, customer, luck)? What was the detection gap — why didn't earlier defenses/alerts fire? Would we detect a recurrence faster?
A postmortem without a detection section documents the failure but not the monitoring debt.

## 5. Response analysis
Did the writeup examine the response itself — time lost to wrong hypotheses, tooling that failed during the incident (recovery depending on the broken system is a corpus-wide recurring pattern), escalation friction, communication load? What went *well* is required content, not decoration — adaptive responses are where resilience lives.

## 6. Action-item quality
Each item needs: **owner, date, verifiable completion criterion**. Fail markers: "improve monitoring", "be more careful", "add more tests" (unfalsifiable); all items being local patches with no systemic item (if the class of failure isn't addressed, it recurs — check the corpus for the same mechanism recurring at other orgs).
Balance check: at least one item should remove the failure class, not just this instance.

## 7. Luck accounting
Where did the outcome depend on chance (time of day, who was on-call, a coincidental deploy freeze)? Unexamined luck is unpriced risk — the next occurrence gets the unlucky draw.

## 8. Impact honesty
Quantified user-facing impact (duration, requests failed, data lost, customers affected), not "some users may have experienced". Internal impact (responder hours, opportunity cost) counts too.

## Output format for a review

1. Scorecard table (dimension | verdict | worst passage).
2. Top 3 rewrites, shown as before → after.
3. Missing-content list, each item with why it matters and — where available — a corpus incident id demonstrating the cost of the omission.
