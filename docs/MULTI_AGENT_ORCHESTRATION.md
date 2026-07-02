# Multi-Agent Orchestration Contract

The project records every handbook run as a three-role workflow:

1. `syllabus_outline_analyst` parses official provider evidence into
   `CourseSpec` and `LearningUnit` records.
2. `handbook_writer` creates source-bound `PedagogicalUnit` content, practice,
   visuals, HTML, and PDF.
3. `final_reviewer` inspects rendered output and review evidence independently
   before handoff.

`final_reviewer` must list both earlier roles in `independent_from`. A completed
review is not the same as a final-ready verdict: the reviewer can still mark the
output draft or blocked.

Artifacts:

- `agent-orchestration.json`: role status and evidence.
- `delivery-contract.json`: public delivery contract, including role evidence.
- `final-review-packet.json`: final reviewer evidence and verdict.

The current open-source implementation records and enforces the contract without
requiring a private model API. A future runner can replace each role with a real
agent process as long as it writes the same artifacts and preserves reviewer
independence.
