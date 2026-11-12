# Karpathy Council — Skill Pack

**Category:** Decision Intelligence  
**Complexity:** Advanced  
**Best for:** High-stakes decisions, irreversible actions, strategic choices

---

## What This Does

Transforms any high-stakes question into a structured multi-perspective deliberation. Five AI advisors analyse your question independently, peer-review each other anonymously, then a chairman synthesises a final verdict — telling you where they agree, where they clash, what they all missed, and what you should actually do.

Built on Andrej Karpathy's LLM Council methodology.

---

## Why This Is Valuable

A single AI gives you a single answer. That answer might be brilliant or it might be subtly wrong in a way that only becomes obvious from a different angle. The council solves this by forcing systematic disagreement before synthesis.

**The results are different from what you'd get asking once:**
- The Contrarian finds the fatal flaw you're avoiding
- The First Principles thinker asks if you're solving the right problem
- The Outsider sees what you're too close to notice
- The Expansionist finds the upside everyone else missed
- The Executor cuts through theory to what you actually do

**Real example:** Used to pressure-test a termination decision. The council was unanimous on outcome — but the Contrarian caught a legal exposure (verbal-only performance standard) that would have been missed. The gap was closed before action was taken. Clean exit.

---

## Trigger Phrases

- "Council this"
- "War room this"  
- "Pressure-test this"
- "Stress-test this"
- "Run the council"
- Any decision where being wrong is expensive

---

## What's Included

```
karpathy-council/
├── SKILL.md       - Full methodology, advisor prompts, chairman synthesis template
└── README.md      - This file
```

---

## Setup

Install via OpenClaw skill installer. No credentials required. No external dependencies. Works out of the box.

---

## Example Output Structure

```
## Where the Council Agrees
...high-confidence convergence points...

## Where the Council Clashes  
...genuine disagreements, both sides presented...

## Blind Spots the Council Caught
...things that only emerged through peer review...

## The Recommendation
...direct recommendation, not "it depends"...

## The One Thing to Do First
...single concrete next step...
```

---

*Built and battle-tested by the NGU Group AI fleet. Used on real business decisions.*
