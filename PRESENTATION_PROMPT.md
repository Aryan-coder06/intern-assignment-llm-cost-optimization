# Copy this prompt into ChatGPT to create the PowerPoint

Attach this repository's README.md, question1/README.md, question2/README.md,
results/benchmark.json, and DEMO_SCRIPT.md along with the prompt below.
Review and rehearse the technical explanation before recording.

---

Create an editable 16:9 PowerPoint (.pptx) for my remote LLM Agent Engineering
internship application. My name is Aryan. The project is ShopAssist: LLM Cost
Optimization. Repository:
https://github.com/Aryan-coder06/intern-assignment-llm-cost-optimization

Audience: engineers evaluating my implementation, judgment, correctness, and
ability to explain tradeoffs. The deck supports a 5–6 minute narrated video with
a live terminal/code demonstration. Make it concrete and technically accurate.
Deliver the actual PPTX if file generation is available, plus speaker notes and
a slide thumbnail overview. If file generation is unavailable, provide complete
slide-by-slide content and notes without pretending to have generated a file.

DESIGN
- Eight slides, 16:9, light background, dark navy text, teal for optimized values,
  muted orange for baseline or risks. Use one consistent visual system.
- Titles 30–36 pt; body at least 22 pt; chart labels at least 18 pt. Large whitespace.
- Use native editable shapes, tables, charts, and arrows. No generic robot art.
- At most three concise points on a slide. Put explanation in speaker notes.
- Use a small footer with the project name and slide number.
- Include a clickable repository link on the closing slide.
- Use captions on charts that say “local simulator; billing points”.

FACTS YOU MUST PRESERVE
- Assignment: Q1 requires one LLM call/ticket and <=3,000 points/ticket.
- Q2 requires triage -> retrieve -> compose -> audit, <=2,500 points/ticket.
  All four stages execute; triage, retrieval, and audit are deterministic Python;
  compose is the only paid LLM call.
- Billing: uncached input * 3 + cached input * 0.3 + output * 15.
- Q1 public ticket points, in T-1001..T-1004 order: 1464, 1341, 1302, 1263.
- Q2 public ticket points, same order: 1311, 1275, 1236, 1197.
- Q1 public mean 1342.5; Q2 public mean 1254.75.
- Measured T-1001 baseline comparison: Q1 8892 -> 1464 points (83.54% lower);
  Q2 73449 -> 1311 points (98.22% lower). These match benchmark.json.
- Q1 T-1001: 258 input, 0 cached input, 46 output = 1464 points.
- Q2 T-1001: 207 input, 0 cached input, 46 output = 1311 points.
- Q2 T-1002: 230 input, 0 cached input, 39 output = 1275 points.
- Correct outputs:
  T-1001 REFUND / returns-within-30-days
  T-1002 SEND_ARTICLE / digital-license-no-refund
  T-1003 ESCALATE_TIER2 / custom-items-no-replace
  T-1004 REPLACE / damage-replacement-7-days
  T-1091 SEND_ARTICLE / subscription-cooling-off (day 38).
- The baseline Q2 carries help-center slices and repeated intermediate text.
  The expanded fixture exceeds 200,000 tokens. Optimized retrieval reads only
  relevant policy files and a fallback article.
- Q1 removes random run IDs, examples, full policy dump, verbose output requests,
  and JSON indentation. It uses a stable compact policy capsule.
- Audit rejects malformed schema, invalid actions, unretrieved citations, and
  action/article pairs inconsistent with the order's policy eligibility.
- Agents do not import the grading reference. The supplied LLM simulator itself
  uses the reference internally. Neither agents nor billing/simulator/reference
  code were modified to fake a result.
- Existing baseline-high-cost assertions were explicitly replaced with cold
  per-ticket upper limits. Existing correctness assertions were retained.
- This is a local simulator experiment. DO NOT claim a hosted model was tested,
  actual rupee/dollar savings, latency benchmarks, production deployment,
  prompt-injection resistance, semantic accuracy on real models, or guarantees
  about internship selection.
- No prefix-cache savings are claimed: prompts are below the 1024-token cache
  threshold and every reported cached-input count is zero. Stable prefixes are
  good hygiene, but adding padding merely to qualify would increase this cost.
- Take before/after percentages and baseline figures ONLY from the attached
  benchmark JSON. Baseline UUIDs can cause small run-to-run count differences.
- Take the final test count ONLY from actual pytest output I supply. If absent,
  describe the categories of tests without inventing a pass count.
- Verified local pytest output for this revision: 22 passed in 170.04 seconds.
  Most time comes from the oversized fixture construction; do not present this
  as per-ticket agent latency.

SLIDE PLAN AND SPEAKER NOTES

1. “ShopAssist: Smaller Context, Preserved Decisions” (20 seconds)
   Subtitle: “LLM optimization assignment | Aryan”.
   Three chips: “Q1: one call”, “Q2: four stages”, “Reproducible billing”.
   Notes: Introduce the support decision task: choose an action and cite policy.
   Say that the objective is lowering points while preserving required outputs.

2. “Where the baseline spends tokens” (35 seconds)
   Draw a prompt stack: random run ID -> examples -> full KB/slices -> repeated
   context -> verbose answer. Mark input and output costs.
   Include the three-part billing equation, not a made-up currency figure.
   Notes: Explain why output costs 5x uncached input per token, why repeated
   histories matter, and why cache padding is inappropriate for this workload.

3. “Q1: One compact decision call” (40 seconds)
   Diagram: thread + compact order + policy capsule -> one LLM -> parsed JSON.
   One large cost card: “1,464 / 3,000 points” and small calculation
   “258 × 3 + 46 × 15”.
   Notes: Describe removal of redundant prompt material, one-sentence replies,
   stable prefixes, and robust schema parsing. Mention policies must be kept
   synchronized if the source help center changes.

4. “Q2: Four stages, one generative step” (50 seconds)
   Four editable boxes left to right: TRIAGE, RETRIEVE, COMPOSE, AUDIT.
   Under each: candidate IDs; selected policy files; one LLM call; schema +
   citation + eligibility checks. Color COMPOSE teal; mark others “Python”.
   Notes: Clarify that “four-node pipeline” is an architectural requirement.
   Describe deterministic node substitution as an explicit design choice.
   Show why retrieval should fetch evidence directly rather than ask a model to
   reproduce full articles. A conflicting draft raises for caller/manual review.

5. “Every public ticket is below its budget” (40 seconds)
   Use two grouped charts or a clean table with four tickets and both tracks.
   Show budget reference lines at 3000 and 2500, clearly associated with track.
   Include representative physical and denial path call breakdowns in notes.
   If benchmark.json is attached, optionally add a small baseline-vs-optimized
   inset for T-1001 with exact measured percent reduction. Otherwise omit it.
   Notes: Decisions/citations match all supplied fixtures including T-1091.
   Do not turn simulator agreement into a real-model accuracy claim.

6. “Live proof: implementation and tests” (90 seconds, pause slides)
   Three large commands:
     python -m pytest -q
     python question1/run.py
     python question2/run.py
   Small fourth command in notes:
     python benchmark.py --output results/benchmark.json
   Notes: Switch to the real terminal. Show actual test output, then T-1001 and
   T-1002 token accounting. Open question2/agent.py and show handle_ticket,
   targeted retrieval, and the eligibility audit. Show T-1091 or boundary tests.
   Return to slides. Use a reserved “live terminal” frame, not a fabricated
   screenshot with imaginary test results.

7. “Tradeoffs I would validate next” (35 seconds)
   Three columns: Current evidence / Limit / Next validation.
   Simulator correctness + token billing / not real-model accuracy / held-out
   hosted-model evaluation with schema enforcement and injection tests.
   Static policy routing / maintenance when KB grows / versioned policy metadata
   and retrieval-recall evaluation.
   Audit rejection / no human queue integrated / connect caller review workflow.
   Notes: Explain that the deterministic audit repeats eligibility logic and
   therefore must stay synchronized with policy versions. Describe it as a
   small-domain guardrail, not a general semantic auditor.

8. “Ready to reproduce” (15 seconds)
   Repository link, two mean point figures (1342.5 and 1254.75), and the line:
   “Compact context. Grounded retrieval. Explicit validation.”
   Notes: Thank the reviewer and invite discussion of the implementation.

FINAL QUALITY CHECK
Ensure numbers agree with the attached artifacts; no text overflows; no tiny
footnotes; diagrams and charts remain editable; all notes use natural spoken
English. Avoid invented testimonials, logos, certifications, metrics, or features.
Include a separate slide-by-slide narration transcript and recording checklist.
Do not suggest submitting the slide deck alone: the application requires a demo
video explaining the implementation and approach.
