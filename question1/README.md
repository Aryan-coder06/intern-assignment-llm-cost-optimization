# Question 1 — SupportCopilot

Entry point: `SupportCopilot.handle_ticket(ticket_id)`.

```bash
python run.py
pytest -q ../tests/test_question1.py
```

Use `get_ticket` / `get_order` for ticket data. Spec: [questions/question-1.md](../questions/question-1.md).

## Approach

The optimized copilot keeps the required one-call design, but removes the UUID
cache buster, four redundant examples, full article dump, and request for hidden
chain-of-thought. The system prompt is now a compact policy decision table, the
order is serialized without indentation, and the model is asked for JSON plus a
one-sentence reply. `parse_resolution` also scans for the first valid resolution
object instead of greedily matching from the first `{` to the last `}`.

## Cost breakdown

Measured with the repository's `cl100k_base` counter for T-1001:

| Call | Input | Cached input | Output | Points |
|---|---:|---:|---:|---:|
| `handle_ticket` | 258 | 0 | 46 | 1,464 |

Calculation: `258 * 3 + 0 * 0.3 + 46 * 15 = 1,464` points. This is
below the 3,000-point target. `python question1/run.py` prints the same breakdown
for every public ticket.
