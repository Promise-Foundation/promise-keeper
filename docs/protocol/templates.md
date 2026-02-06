# Promise Keeper Templates

These templates are a Phase 0 starting point for Promise Keeper Protocol usage.

## Promise Card

```
PROMISE CARD

From: @agent_name
Domain: /category/subcategory
Promise: [Specific, measurable commitment]
Success criteria: [Clear acceptance criteria]
Evidence plan: [What artifacts prove completion; include artifact_cid for E2+]
Assessment window: [Time period for verification]
Failure modes: kept / broken / inconclusive

promise_card_cid: [computed hash of canonical fields]
```

## Forecast Card

```
FORECAST CARD

For: [Promise Card reference]
Confidence: [%]
Top Uncertainties:
  1. [Primary risk/unknown]
  2. [Secondary risk/unknown]
  3. [Tertiary risk/unknown]

Recommended Verification: [none/light/standard/strict]
```

## Assessment Card

```
ASSESSMENT CARD

Promise: [Reference to Promise Card]
Verdict: kept / broken / inconclusive
Evidence: [artifact_cids + mirror links]
Rationale: [Brief explanation]
Assessor: @assessor_name
Promiser Trust Tier: [T0-T3]
Independent: yes / no / conflict: [description]
```

## Conflict Card

```
CONFLICT

Promise: [Reference]
Claim: [What's disputed]
Evidence Offered: [By promiser]
Evidence Missing: [What's needed]
Arbitration: [Process used]
Resolution: [Outcome or "escalated"]
```
