# Demo video script (about 4 minutes)

## 0:00–0:20 — Intro

"Hi, I'm Aryan. This is my solution to the ShopAssist LLM cost-optimization
assignment. I completed both tracks while preserving the required action and
knowledge-base citation for every public ticket and the subscription holdout."

Show the repository root and briefly open `questions/question-1.md` and
`questions/question-2.md`.

## 0:20–1:20 — Question 1

Open `question1/agent.py` with the baseline diff visible.

"The baseline sent a random UUID, four examples, the full help center, and asked
for long reasoning. That made both input and output expensive and also prevented
prefix caching. I replaced it with a stable policy decision table, compact JSON,
and a JSON-only response with a one-sentence customer reply. It still makes
exactly one LLM call per ticket. I also made parsing safer by locating the first
JSON object that actually contains the two required fields."

Run:

```bash
python question1/run.py
```

Point to T-1001: 258 input tokens, 46 output tokens, 1,464 points versus the
3,000-point target. Mention that all four public outputs match the expected
action and article.

## 1:20–2:40 — Question 2

Open `question2/agent.py` and follow `handle_ticket` through its four calls.

"The production pipeline still has four explicit stages, but I use the LLM only
where generation adds value. Triage extracts intent and candidate article IDs
from trusted order facts. Retrieve loads only those articles from disk, instead
of passing a 200,000-token help center. Compose makes one focused model call.
Audit is deterministic: it validates schema, the allowed action, the retrieved
citation, and order eligibility. If a draft conflicts with policy, it raises for
the caller to route to manual review. None of these checks requires another
model call."

Run:

```bash
python question2/run.py
```

Highlight T-1001 at 1,311 points and T-1002 at 1,275 points, both below the
2,500-point target. These are simulator billing points, not currency amounts.

## 2:40–3:20 — Tests and edge case

Run:

```bash
pytest -q
```

"The suite checks all public decisions, the 200,000-token knowledge-base setup,
both cost targets, boundary ages, malformed responses, incorrect drafts, and the
T-1091 subscription holdout. I retained the holdout
behavior: a day-38 subscription cancellation sends the cooling-off article
instead of issuing an automatic refund. The provided LLM is a local simulator,
so these tests don't measure a hosted model's semantic accuracy. Before a real
deployment I would evaluate retrieval recall, structured output reliability, and
adversarial customer text on unseen tickets."

## 3:20–3:40 — Close

"The main design principle was to spend tokens only on information and tasks
that need probabilistic reasoning. Stable rules, retrieval, and validation stay
in deterministic code; the LLM receives a small evidence-backed prompt. Thanks
for reviewing my solution."

Before recording, maximize the terminal font, hide notifications and secrets,
and record at 1080p. Keep the GitHub repository URL visible in the final frame.
