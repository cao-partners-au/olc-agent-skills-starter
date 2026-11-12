---
name: karpathy-council
description: Run any high-stakes decision through a structured 5-advisor deliberation. Five independent advisors analyse the question simultaneously from different thinking styles, peer-review each other anonymously, then a chairman synthesises a final verdict. Based on Andrej Karpathy's LLM Council methodology. Trigger on phrases like "council this", "war room this", "pressure-test this", "stress-test this", "run the council", or whenever a decision has real consequences and multiple valid perspectives.
---

# Karpathy Council

You ask one AI a question, you get one answer. That answer might be great. It might be wrong. You have no way to tell — because you only saw one perspective.

The council fixes this. Five independent advisors analyse your question simultaneously from fundamentally different angles. They peer-review each other anonymously. A chairman synthesises everything into a final recommendation that tells you where the advisors agree, where they clash, and what you should actually do.

Adapted from Andrej Karpathy's LLM Council methodology.

---

## When to Run the Council

**Run it when being wrong is expensive.**

Good council questions:
- High-stakes people decisions (hiring, termination, performance management)
- Strategic pivots or major resource commitments
- Irreversible actions with legal, financial, or reputational consequences
- When you've already made up your mind and want it challenged

**Don't run it for:**
- Factual lookups (one right answer)
- Simple creation tasks (write a tweet)
- Decisions where you just want validation — the council will tell you things you don't want to hear

---

## The Five Advisors

Each advisor thinks from a different angle, creating natural tension:

| Advisor | Thinking Style |
|---|---|
| **The Contrarian** | Finds the fatal flaw. Assumes the idea is wrong and tries to prove it. |
| **The First Principles Thinker** | Strips assumptions. Asks "what are we actually solving?" |
| **The Expansionist** | Looks for upside everyone else misses. What could be bigger? |
| **The Outsider** | Zero context bias. Sees what insiders are too close to notice. |
| **The Executor** | Only cares about what you do Monday morning. |

---

## How to Run the Council

### Step 1: Frame the Question

When triggered, enrich the question with workspace context before framing:
- Read MEMORY.md, daily notes, any directly relevant files
- Frame a neutral, specific question that all five advisors will receive
- Include: the core decision, key context, what's at stake, any constraints

### Step 2: Spawn All 5 Advisors in Parallel

Spawn all five as sub-agents simultaneously. Each gets:
- Their advisor identity and thinking style
- The framed question
- Instruction to lean fully into their assigned perspective — not to hedge

Each advisor responds in 150-300 words.

**Advisor prompt template:**
```
You are [Advisor Name] on an LLM Council.

Your thinking style: [description]

Question brought to the council:
---
[framed question]
---

Respond from your perspective. Be direct. Don't hedge. Lean fully into your angle.
150-300 words. No preamble.
```

### Step 3: Anonymous Peer Review

Collect all 5 responses. Anonymise as Response A through E (randomise mapping to remove positional bias).

Spawn 5 reviewers simultaneously. Each sees all 5 anonymised responses and answers:
1. Which response is strongest and why? (pick one)
2. Which response has the biggest blind spot?
3. What did ALL five responses miss?

**Reviewer prompt template:**
```
You are reviewing outputs of an LLM Council. Five advisors answered:
---
[framed question]
---
Response A: [response]
Response B: [response]
...

Answer:
1. Strongest response and why? (pick one)
2. Biggest blind spot — which response, what's missing?
3. What did ALL five miss?

Under 200 words. Be specific.
```

### Step 4: Chairman Synthesis

One final agent receives everything — all advisor responses (de-anonymised), all peer reviews — and produces the verdict.

**Chairman output structure:**
```
## Where the Council Agrees
[Points multiple advisors converged on independently. High-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Don't smooth them over.]

## Blind Spots the Council Caught
[Things that only emerged through peer review.]

## The Recommendation
[A direct recommendation. Not "it depends." A real answer.]

## The One Thing to Do First
[Single concrete next step. Not a list. One thing.]
```

The chairman can disagree with the majority if the reasoning supports it.

### Step 5: Present the Verdict

Present the full verdict directly in chat using markdown. No HTML reports, no files — readable in the conversation.

---

## Real-World Example

**Decision:** Should we terminate an underperforming employee during probation?

**What the council caught that a single advisor would have missed:**
- The Contrarian flagged the legal gap: performance standard only communicated verbally, creating a general protections exposure
- The Outsider noted that terminating right before a holiday looks retaliatory regardless of merit
- The Executor provided the exact 5-step action sequence including timing, script, and access revocation

**Outcome:** Council unanimous on termination. Key action item (written performance notice) completed before the call was made. Clean exit, documented properly.

---

## Important Notes

- Always spawn all 5 advisors in parallel — never sequentially
- Always anonymise for peer review — positional bias is real
- The chairman can and should disagree with the majority if reasoning supports it
- Don't run the council on trivial questions — it's for decisions where being wrong matters
