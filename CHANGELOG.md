# Changelog

## 0.1.1 - 2026-06-18

### Fixed

- Fixed OxfordAQA syllabus parsing so subjects such as Accounting no longer fall back to a few top-level table-of-contents headings.
- Expanded body-table syllabus sections into teachable knowledge units when the official PDF uses broad `3.x` sections instead of many leaf topic codes.
- Preserved PDF body source snippets from the parser and skipped contents/index pages during fallback source matching.
- Added Accounting/finance subject profiling so Accounting examples use source documents, books of prime entry, ledgers, reconciliation, statements, and ratios instead of borrowed Mathematics templates.
- Routed Accounting, Economics, Business, and other complex visual explanations to infographic prompts instead of unsafe or misleading SVG drafts.
- Strengthened validation to fail empty syllabus topics, contents-page-only source anchors, placeholder practice frames, and cross-subject borrowed practice questions.
- Added regression tests for Accounting-style body tables, source-snippet preservation, and non-math example generation.

### Added

- Added the first multi-provider foundation: a common `ExamBoardProvider` contract, provider registry, URL-based provider inference, and model fields for Cambridge syllabus year ranges and Edexcel modular/unit structures.
- Added explicit guardrails for Pearson Edexcel and Cambridge International / CAIE URLs. They are recognised as roadmap providers, but generation is still blocked with a clear "planned but not implemented" message in this release.

### Verified

- Accounting International GCSE: 68 topics, 136 practice cards, 68 infographic briefs.
- Mathematics International GCSE: 90 topics, 180 practice cards, 43 SVG-safe briefs, 39 infographic briefs.
- Chemistry International GCSE: 35 topics, 70 practice cards, 14 SVG-safe briefs, 18 infographic briefs.
- Economics International GCSE: 38 topics, 76 practice cards, 38 infographic briefs.
- Business International AS-A-level: 29 topics, 58 practice cards, 29 infographic briefs.

### Notes

- `prompt-queue` remains a dry-run image route. Complex infographic briefs still require a user-selected image model/API before final raster assets are generated.
- Official specification PDFs and extracted official text are generated at runtime and are not committed to the repository.

## 0.1.0 - Initial public architecture draft

- Initial OxfordAQA-focused Skill architecture for generating International GCSE and International AS-A-level revision handbooks.
- Added language selection, explanation style selection, visual routing, source appendix, HTML/PDF packaging, and release-sample documentation.
