---
name: international-exam-guide
description: Generate source-traceable OxfordAQA International GCSE and International AS/A-level revision guides from public subject pages and course specification PDFs, including syllabus extraction, assessment summaries, student guide rendering, validation, and optional PDF export.
---

# International Exam Guide

Use this skill when the user asks for an International GCSE or International
AS/A-level subject revision guide, especially for OxfordAQA. Treat IGCSE as a
user-facing alias for International GCSE, but use the full qualification names
in generated documentation.

Current provider support is OxfordAQA only. Pearson Edexcel and Cambridge
International / CAIE are roadmap providers for the China-market version, but
they need their own provider references and parser checks before generation.
Do not run the OxfordAQA provider against Edexcel, Cambridge, or generic AQA UK
pages.

## User-Facing Use

The end user should not need to run Python commands. They can install the skill
by giving an agent this link:

```text
https://github.com/ethanzhangliang-creator/international-exam-guide/tree/main/skill
```

After installation, plain-language requests are enough, for example:

```text
帮我生成 OxfordAQA Chemistry International GCSE 复习手册，并导出 PDF。
帮我生成 Chemistry 9202 学习手册。
帮我生成 OxfordAQA Business International AS/A-level revision guide。
```

Handle repository setup, CLI execution, validation checks, and PDF export as the
agent. Do not ask the user to install dependencies unless the local environment
is genuinely missing the required runtime and cannot proceed.

For student-facing guides, do not produce a text-only template. Before
generating complex visuals, ask the user which infographic/image model to use:

- `deterministic-svg` for offline concept maps and simple diagrams;
- `gpt-image-2` for high-quality polished educational visuals;
- `qwen-image-pro` for Chinese/English text-heavy infographics;
- `sensenova-u1-fast` for fast infographic drafts or local experiments;
- `custom` if the user has another provider.

If the user has not chosen a model, run the guide with visual briefs and SVG
drafts only, then present the image prompt queue for confirmation. Do not claim
that complex infographics have been generated until the selected model has
actually produced reviewed image assets.

## Repository Access

This skill may be installed from the repository's `skill/` directory, which
contains the agent instructions but not the Python engine. Before running the
generator, check whether the current workspace has `pyproject.toml` and
`src/intl_exam_guide`.

If the full repository is not available, clone or otherwise fetch this public
repository into a workspace directory, then run commands from that checkout:

```text
https://github.com/ethanzhangliang-creator/international-exam-guide.git
```

## Workflow

1. Identify the qualification board, subject, level, and code if available.
2. For OxfordAQA, read `references/oxfordaqa.md`.
3. If the requested provider is Pearson Edexcel or Cambridge International /
   CAIE, explain that it is planned but not implemented in the current release.
4. Run the generator CLI from the repository root.
5. Check `validation.json` before presenting the guide.
6. If the guide will be used with children, require subject-specialist review for
   worked examples before treating it as final exam preparation material.
7. Preserve the visual and narrative learning layer: after the base topic guide
   and practice items are generated, analyze which knowledge points or examples
   need visual explanation. Use deterministic SVG for simple diagrams. For
   complex infographic needs, ask the user to choose an image model and keep
   source-bound prompts without copying protected IP.

## Commands

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level igcse --image-provider qwen-image-pro --out ./outputs/chemistry-9202
```

Use `--skip-pdf` only when no local browser or Playwright runtime is available.

## Safety Rules

- Do not copy OxfordAQA past paper questions, mark schemes, or large passages of
  specification text into generated public examples.
- Keep the official page URL, specification URL, and PDF hash in every output.
- Treat the generated guide as incomplete if topic extraction, assessment
  extraction, source download, or HTML validation fails.
- Do not invent syllabus facts. If a topic needs deeper explanation, generate it
  from the extracted specification text and mark it for review.
- Use AI image generation only as an optional illustration layer. Prefer
  deterministic SVG concept maps for source-traceable syllabus structure. If an
  AI image model is used, record the model, prompt, source topic, caption, and
  review status; never let an illustration introduce unsupported syllabus facts.
