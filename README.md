# ShopAssist — support copilot cost lab

**ShopAssist** is a Tier-1 support agent for an e-commerce company. For each ticket it:

1. Reads the customer thread (`data/tickets/`)
2. Loads order facts (`data/orders/` via `shared/tools.py`)
3. Picks an action (`REFUND`, `REPLACE`, `SEND_ARTICLE`, `ESCALATE_TIER2`)
4. Cites the help-center article that backs the decision (`data/kb/`)

| Track | Code | Spec |
|-------|------|------|
| Q1 — single call | [question1/agent.py](question1/agent.py) | [questions/question-1.md](questions/question-1.md) |
| Q2 — pipeline | [question2/agent.py](question2/agent.py) | [questions/question-2.md](questions/question-2.md) |

## Run

```bash
pip install -r requirements.txt
pytest -q
python question1/run.py
python question2/run.py
```

`shared/llm.py` provides a local `LlmClient` with the same billing accounting you would use against a hosted chat API. Do not import `eval/reference.py` from your agent.

## Billing

| Input | Cached input | Output |
|------:|-------------:|-------:|
| 3 | 0.3 | 15 |

Cached input = identical prefix ≥ 1024 tokens across calls.

```
points = uncached_input × 3 + cached_input × 0.3 + output × 15
```

Per-call details are in `shared/billing.py` (`CostSession` on your agent).

## Optimized submission

| Public ticket | Q1 points (budget 3,000) | Q2 points (budget 2,500) |
|---|---:|---:|
| T-1001 | 1,464 | 1,311 |
| T-1002 | 1,341 | 1,275 |
| T-1003 | 1,302 | 1,236 |
| T-1004 | 1,263 | 1,197 |
| Mean | 1,342.50 | 1,254.75 |

All counts use real `tiktoken` with `cl100k_base`. Cached input is zero.
These are billing points from the supplied local simulator, not currency or
hosted-model performance measurements.
The full suite passes: **22 tests**, including the oversized knowledge-base fixture.
The checked-in cold-session benchmark measures **83.54–85.84%** lower Q1 points
and **98.22–98.37%** lower Q2 points on public tickets versus the original scaffold.
For T-1001, Q1 falls from 8,892 to 1,464 points and Q2 from 73,449 to 1,311.

### Reproduce from a fresh clone

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python question1/run.py
python question2/run.py
python benchmark.py --output results/benchmark.json
```

The first tokenizer use can download its encoding. The oversized help-center
fixture is constructed by repeated tokenization and may take several minutes.
The optimized agents never build that expanded blob. The benchmark compares
each ticket in a fresh session against original scaffold commit `d9989e2`.
Baseline UUIDs can change baseline costs slightly between runs.

Q1 retains exactly one LLM call, using a compact policy capsule and structured
output. Q2 retains all four nodes and uses deterministic triage, file retrieval,
and audit around one compose call. This is an explicit interpretation of the
four-node requirement: the specification does not require four model calls.

The audit checks schema, allowed actions, retrieved citations, and policy
eligibility. Contradictions raise `ValueError` for the caller to handle; a human
review queue is not integrated. Boundary tests cover 7/8-day replacement,
30/31-day returns and subscriptions, synthetic ticket IDs, malformed responses,
and incorrect drafts. Existing correctness checks remain; the two scaffold tests
that demanded high cost were changed to enforce the requested per-ticket budgets.

### Scope and tradeoffs

The supplied `LlmClient` derives answers from the evaluation reference internally.
The agents do not import that reference, and the simulator, billing logic, source
policies, and evaluator are unchanged. Passing these tests proves simulator
compatibility, retrieval coverage on tested cases, guardrail behavior, and cost
accounting; it does not establish real-model accuracy or injection resistance.

The compact Q1 capsule and Q2 routing/eligibility rules suit this small, fixed
policy domain. They require maintenance when policies change. For a larger live
KB, use versioned policy metadata, evaluate retrieval recall on held-out tickets,
and test a hosted model with structured outputs and adversarial customer text.
The independent audit duplicates policy checks deliberately, so policy-version
synchronization is a maintenance consideration.

### Submission and demo

- [Q1 approach and call breakdown](question1/README.md)
- [Q2 approach and call breakdown](question2/README.md)
- [Detailed ChatGPT PowerPoint prompt](PRESENTATION_PROMPT.md)
- [Demo narration and recording guide](DEMO_SCRIPT.md)
- [Reproducible baseline/optimized report](results/benchmark.json)

Use slides to support the explanation, then show the actual terminal and code.
The application asks for a repository link and a demo video.
