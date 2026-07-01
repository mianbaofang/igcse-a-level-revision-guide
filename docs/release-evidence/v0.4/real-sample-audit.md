# v0.4 Real Sample Audit

Date: 2026-07-01

This audit records fresh generated samples across three exam boards and
non-mathematics subjects. It is evidence for pipeline behavior, not a certified
student handoff. Every sample below remains `draft` because reviewed concept
explanations have not been imported; accounting samples with complex visuals
also have pending infographic assets.

## Matrix

| Sample | Board | Subject | Topics | Practice | Visuals | SVG max repeat | Pending images | Pending concepts | Validation | Final review |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `_audit10-oxfordaqa-business` | OxfordAQA | Business | 29 | 29 | 10 | 2 | 0 | 29 | 0 errors, 1 warning | `must_not_present_as_final: true` |
| `_audit10-oxfordaqa-accounting` | OxfordAQA | Accounting | 68 | 68 | 33 | 3 | 21 | 68 | 0 errors, 2 warnings | `must_not_present_as_final: true` |
| `_audit11-pearson-accounting` | Pearson Edexcel | Accounting | 22 | 22 | 8 | 1 | 3 | 22 | 0 errors, 2 warnings | `must_not_present_as_final: true` |
| `_audit11-pearson-history` | Pearson Edexcel | History | 13 | 13 | 2 | 2 | 0 | 13 | 0 errors, 1 warning | `must_not_present_as_final: true` |
| `_audit10-cambridge-history` | Cambridge | History | 30 | 30 | 3 | 2 | 0 | 30 | 0 errors, 1 warning | `must_not_present_as_final: true` |
| `_audit10-cambridge-accounting` | Cambridge | Accounting | 28 | 28 | 14 | 1 | 9 | 28 | 0 errors, 2 warnings | `must_not_present_as_final: true` |

## Manual Checks

- Syllabus shell phrases no longer appear in student-facing guide, practice, or
  visual fields for the six fresh samples:
  `Candidates should have an understanding of`, `Students will:`,
  `Students must study one breadth study`, generic
  `definition, one application, and one check`, and common cross-subject maths
  templates all scanned at 0 occurrences in visible outputs.
- Business now uses business-context practice rather than generic
  definition/application prompts.
- History option codes such as `A1` no longer route into mathematics algebra
  examples.
- Cambridge Accounting no longer exposes `Candidates should have an
  understanding of:` in the roadmap or practice focus; the first sample topics
  now use concrete points such as `the difference between book-keeping and
  accounting` and `assets, liabilities and owner's equity`.
- SVG repetition is no longer a blocking issue in the sampled routes. Complex
  accounting visuals remain queued as infographics instead of being forced into
  repeated SVG fallback diagrams.

## Remaining Blocks

- None of these samples is certified or final-ready.
- All six samples need reviewed concept explanations imported before final
  delivery.
- OxfordAQA Accounting, Pearson Accounting, and Cambridge Accounting still need
  reviewed infographic assets for queued complex visuals.
- PDF export was intentionally skipped in these samples, so PDF page/blank-page
  quality is not part of this audit.
