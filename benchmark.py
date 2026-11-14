"""Reproduce cold-ticket baseline/optimized billing without changing grading code.

Run: python benchmark.py --output results/benchmark.json
The baseline source is read from the original scaffold commit, never imported
by either production agent. UUIDs make baseline counts vary slightly per run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import types

from question1.agent import SupportCopilot
from question2.agent import SupportPipeline

BASELINE = "d9989e2"
TICKETS = ["T-1001", "T-1002", "T-1003", "T-1004", "T-1091"]


def baseline_class(track, name):
    source = subprocess.check_output(
        ["git", "show", f"{BASELINE}:{track}/agent.py"], text=True)
    module = types.ModuleType(f"_baseline_{track}")
    sys.modules[module.__name__] = module
    exec(compile(source, f"{BASELINE}/{track}/agent.py", "exec"), module.__dict__)
    return getattr(module, name)


def measure(cls, ticket):
    agent = cls()
    result = agent.handle_ticket(ticket)
    return {
        "action": result.action, "kb_article": result.kb_article,
        "points": agent.session.total_points(),
        "calls": [
            dict(label=c.label, input_tokens=c.input_tokens,
                 cached_input_tokens=c.cached_prefix_tokens,
                 output_tokens=c.output_tokens, points=c.points())
            for c in agent.session.calls
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for track, optimized, name, limit in (
        ("question1", SupportCopilot, "SupportCopilot", 3000),
        ("question2", SupportPipeline, "SupportPipeline", 2500),
    ):
        original = baseline_class(track, name)
        for ticket in TICKETS:
            before, after = measure(original, ticket), measure(optimized, ticket)
            assert (before["action"], before["kb_article"]) == (after["action"], after["kb_article"])
            assert after["points"] <= limit
            rows.append(dict(track=track, ticket=ticket, baseline=before,
                             optimized=after,
                             reduction_percent=round(100 * (1 - after["points"] / before["points"]), 2)))
    report = dict(baseline_commit=BASELINE, tokenizer="cl100k_base",
                  mode="fresh session per ticket; local simulator", results=rows)
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload)


if __name__ == "__main__":
    main()
