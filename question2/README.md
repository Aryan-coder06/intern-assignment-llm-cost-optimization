# Question 2 — SupportPipeline

Entry point: `SupportPipeline.handle_ticket(ticket_id)`.

```bash
python run.py
pytest -q ../tests/test_question2.py
```

Spec: [questions/question-2.md](../questions/question-2.md).

## Approach

The four production stages remain explicit, but only the stage that benefits
from generation uses an LLM:

1. **Triage** extracts intent and candidate article ids from trusted order facts.
2. **Retrieve** reads only those articles, never the 200k-token expanded blob.
3. **Compose** makes one small LLM call with the thread, compact order, and evidence.
4. **Audit** parses the JSON and rejects unknown actions, unknown articles, or a
   citation that was not retrieved, and action/article pairs that conflict with
   the order's eligibility. Conflicting drafts raise for manual review by the caller.

This uses deterministic code for routing, lookup, and validation rather than
paying a model to copy context between nodes. It also prevents a hallucinated
citation from reaching the caller.

## Cost breakdown

Measured with the repository's `cl100k_base` counter:

| Path | Call | Input | Cached input | Output | Points |
|---|---|---:|---:|---:|---:|
| Physical fulfillment (T-1001) | `compose` | 207 | 0 | 46 | 1,311 |
| Denial (T-1002) | `compose` | 230 | 0 | 39 | 1,275 |

The other three stages make no LLM calls, so each row is also the complete
per-ticket total. Both paths are below the 2,500-point target. Run
`python question2/run.py` for per-call breakdowns on all public tickets.
