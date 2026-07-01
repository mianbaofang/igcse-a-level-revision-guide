# AQA AS Sample Audit

Date: 2026-07-01

This audit records the four local AQA AS handbook samples used to find and fix
cross-subject delivery problems before handoff. These are sample evidence
outputs, not a claim that every board and subject route is certified.

## Sample Status

| Sample | Topics | PDF pages | Blank text pages | Visual summary | Final review |
| --- | ---: | ---: | ---: | --- | --- |
| AQA AS Mathematics | 99 | 115 | 0 | 23 SVG, 16 structures, 3 generated infographics | ready / final-ready |
| AQA AS Economics | 84 | 97 | 0 | 4 SVG, 1 structure, no pending images | ready / final-ready |
| AQA AS Accounting | 22 | 30 | 0 | 8 SVG, 6 structures, no pending images | ready / final-ready |
| AQA AS Business | 29 | 38 | 0 | 6 SVG, 6 structures, no pending images | ready / final-ready |

All four outputs had:

- `pending_concept_explanations: 0`;
- `pending_infographic_assets: 0`;
- no validation issues after the final rerun;
- `final-review-packet.json` present with `agent_self_review.status: ready`;
- a final review contract requiring Agent/LLM inspection before user handoff.

## Problems Found

1. Similar topics could receive duplicated mastery requirements.
   - Example: AQA AS Economics initially gave the same mastery text to
     `3.1.4.5 - The competitive market process` and
     `3.3.3.8 - The dynamics of competition and competitive market processes`.
   - Fix: competition-process explanations now split basic non-price
     competition from short-run/long-run competition dynamics.

2. Keyword practice routing could choose the wrong worked example.
   - Example: Economics competition topics were routed to a demand/supply
     oranges example because `market` appeared in the title.
   - Fix: economics practice generation now handles competitive process and
     competition dynamics before generic market-equilibrium routing.

3. Syllabus fragments could leak into student-facing prompts.
   - Example: practice questions were prefixed with incomplete source fragments
     such as `Firms do not just compete on price but`.
   - Fix: question contextualization now suppresses incomplete syllabus
     fragments and short/unsafe focus strings.

4. SVG visuals could be formally valid but pedagogically repetitive.
   - Example: Accounting statement variants used one generic table-like SVG
     structure for partnership, manufacturing, club, and limited-company topics.
   - Fix: accounting statement visuals now use distinct professional layouts
     for partnership appropriation/current accounts, manufacturing cost flow,
     club receipts/income-expenditure, and limited-company statements.

5. Validation-ready was too close to user-facing final-ready.
   - Risk: a clean machine validation result could be mistaken for a finished
     handoff without Agent/LLM inspection.
   - Fix: `ready` validation now maps to `review-ready` until a final review
     packet reports `agent_self_review.status: ready`; only then can the
     delivery contract show `final-ready`.

## Common Cause

The repeated failures shared one product-level cause: the pipeline relied too
much on flat keyword routing plus post-generation checks. This made the output
look complete while some topic units, examples, and visuals were still generic
or mismatched.

The v0.4 corrective pattern is:

1. classify the learning unit and subject context first;
2. generate concept explanations and practice from the current source-bound
   topic, not from broad keyword fallbacks;
3. use SVG only for visual types with reliable diagram grammar;
4. rerender and inspect actual outputs after fixes;
5. require Agent/LLM self-review evidence before final user handoff.
