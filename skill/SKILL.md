---
name: igcse-a-level-revision-guide
description: Generate image-rich IGCSE and A-Level revision handbooks for OxfordAQA International GCSE and International AS-A-level subjects, with syllabus-based explanations, worked examples, visual learning units, review questions, HTML output, and optional PDF export.
---

# IGCSE & A-Level AI Revision Guide Skill

Use this skill when the user asks for an International GCSE or International
AS-A-level subject study/revision guide, especially for OxfordAQA. Treat IGCSE
as a user-facing alias for International GCSE, but use the full qualification
names in generated documentation.

Before generating a guide, read `references/revision_guide_spec.md`. That file
defines the handbook contract inherited from the original IGCSE revision-guide
Skill: the output must be a student study/revision handbook with HTML, PDF,
modular sections, visual assets, worked examples, and validation. Do not turn
the output into project documentation.

Current provider support is OxfordAQA only. Pearson Edexcel and Cambridge
International / CAIE are roadmap providers for the China-market version, but
they need their own provider references and parser checks before generation.
Do not run the OxfordAQA provider against Edexcel, Cambridge, or generic AQA UK
pages.

## User-Facing Use

The end user should not need to run Python commands. They can install the skill
by giving an agent this link:

```text
https://github.com/ethanzhangliang-creator/igcse-a-level-revision-guide/tree/main/skill
```

After installation, plain-language requests are enough, for example:

```text
帮我生成 OxfordAQA Chemistry International GCSE 复习手册，并导出 PDF。
帮我生成 Chemistry 9202 学习手册。
帮我生成 OxfordAQA Business International AS-A-level revision guide。
```

Do not start generation immediately after a broad request. Run the preflight
choice step first.

## Required Preflight Choices

Before downloading a specification, generating content, or creating images, ask
for and confirm these four choices if the user did not already provide them:

1. **Subject choice**: exam board, qualification level, subject, and code if
   known. Current supported board is OxfordAQA only.
2. **Output language**: ask whether the handbook should be `en` or `zh-CN`.
   This is a required language lock, not a bilingual mode. Do not offer a
   combined bilingual output. Do not render handbook labels
   as bilingual `Chinese / English`, `English / Chinese`, `中文 / English`, or
   similar mixed pairs. Template labels, explanations, topic framing, worked
   examples, image prompts, and visible infographic text must follow the
   selected language. If `zh-CN` is selected, keep official English snippets in
   structured source files or a clearly separated source appendix for review;
   do not mix English source paragraphs, raw English topic headings, or raw
   English syllabus bullet points into the student-facing topic map/body. If the
   user changes language, regenerate the guide in the new language instead of
   merging old sections.
3. **Infographic/image route**: ask which image model or provider the user wants
   to use for complex visuals. Accepted built-in labels for this repository are
   `gpt-image-2`, `qwen-image-pro`, `sensenova-u1-fast`, `custom`,
   `deterministic-svg`, and `prompt-queue`.
4. **Explanation style**: ask how the knowledge points and examples should read:
   `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`.

For `custom`, ask for the model name, endpoint URL, and the environment variable
name that stores the API key. Never ask the user to paste a raw API key into the
chat or commit one to the repository.

`prompt-queue` is only a deliberate dry-run choice: it creates source-bound
image prompts and SVG-safe drafts but does not produce final complex
infographics. Do not use it silently.

Handle repository setup, CLI execution, validation checks, and PDF export as the
agent. Do not ask the user to install dependencies unless the local environment
is genuinely missing the required runtime and cannot proceed.

## Core Contract

This skill is a cross-subject framework, not a Mathematics, Chemistry, or
Economics template. Do not hard-code one subject's examples, diagrams, topic
counts, tone, or revision structure into another subject.
Within OxfordAQA, do not maintain a per-subject allowlist. If the official
qualification page and specification PDF can be discovered, run the same
source-bound generation pipeline. Specialist subject profiles may improve
examples and visual decisions; subjects without a specialist profile must fall
back to generic source-bound examples instead of borrowing another subject's
template.

The end product is a study/revision handbook package. A valid run writes:

- `guide.html`;
- `guide.pdf` when PDF export is available;
- `sections/` with modular handbook source fragments;
- `images/` with deterministic SVG drafts or reviewed infographic assets;
- `guide-plan.json`;
- `qualification.json`;
- `validation.json`;
- `handbook-package.json`.

The required generation logic is:

1. Find the public qualification page and course specification PDF.
2. Use the web page only as discovery metadata; use the downloaded PDF as the
   source of truth for detailed syllabus content.
3. Parse the detailed subject content into teachable knowledge units. If the PDF
   has specification references such as `N1`, `A13`, `G20`, `S18`, or equivalent
   subject codes, use those references as the unit level. If a subject has no
   codes, use the lowest reliable section/subsection level available in the PDF.
4. Generate source-bound study notes and original worked examples for each unit.
   Each worked example must include a real question prompt, a solve-it-first
   frame, public solution steps, final answer/checkpoints, and source anchors.
5. Run a second visual-needs pass over each knowledge unit and worked example.
   Decide whether text is enough, a deterministic SVG is enough, or a richer
   infographic/image model is needed.
6. Render the guide to HTML/PDF only after the content, examples, visual briefs,
   and source checks are present.

For student-facing guides, do not produce a text-only template. During preflight,
ask the user which infographic/image route to use:

- `prompt-queue` for a dry run that writes prompts but no complex images;
- `deterministic-svg` for offline concept maps and simple diagrams only;
- `gpt-image-2` for high-quality polished educational visuals;
- `qwen-image-pro` for text-heavy Chinese or English infographics;
- `sensenova-u1-fast` for fast infographic drafts or local experiments;
- `custom` if the user has another provider, URL, model name, and key env var.

If the user has not chosen an output language, image route, and explanation
style, stop and ask. The generation process starts only after the subject,
output language, image route, and writing style are confirmed. Do not claim that
complex infographics have been generated until the selected model has actually
produced reviewed image assets.

When the full repository is available and the user has confirmed GPT Image 2
Codex-only Router parameters, use
`scripts/generate_pending_infographics_router.py` to generate pending complex
visuals and update each `images/visual_manifest.json`. If images are generated
outside the guide package with another provider, use
`scripts/import_infographic_assets.py` to import them before finalizing HTML/PDF.

## Repository Access

This skill may be installed from the repository's `skill/` directory, which
contains the agent instructions but not the Python engine. Before running the
generator, check whether the current workspace has `pyproject.toml` and
`src/intl_exam_guide`.

If the full repository is not available, clone or otherwise fetch this public
repository into a workspace directory, then run commands from that checkout:

```text
https://github.com/ethanzhangliang-creator/igcse-a-level-revision-guide.git
```

## Workflow

1. Confirm the required preflight choices: subject, output language, image
   route, and explanation style.
2. Read `references/revision_guide_spec.md`.
3. For OxfordAQA, read `references/oxfordaqa.md`.
4. If the requested provider is Pearson Edexcel or Cambridge International /
   CAIE, explain that it is planned but not implemented in the current release.
5. Run the generator CLI from the repository root with the confirmed
   `--language`, `--image-provider`, and `--explanation-style`. Confirm that detailed PDF
   syllabus units were extracted; do not accept broad web summary topics as the
   final guide structure when the PDF contains finer subject content.
6. Check `validation.json` before presenting the guide. A usable student guide
   needs detailed units, worked examples, source snippets, visual briefs,
   `sections/`, and `images/`; a guide with only broad topic headings is a
   failed draft.
7. If the guide will be used with children, require subject-specialist review for
   worked examples before treating it as final exam preparation material.
8. Preserve the visual and narrative learning layer: after the base topic guide
   and practice items are generated, analyze which knowledge points or examples
   need visual explanation. Use deterministic SVG for simple diagrams. For
   complex infographic needs, ask the user to choose an image model and keep
   source-bound prompts without copying protected IP.

## Commands

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level igcse --language en --image-provider qwen-image-pro --explanation-style friendly --out ./outputs/chemistry-9202
```

Use `--skip-pdf` only when no local browser or Playwright runtime is available.

## Safety Rules

- Do not copy OxfordAQA past paper questions, mark schemes, or large passages of
  specification text into generated public examples.
- Keep the official page URL, specification URL, and PDF hash in every output.
- Treat the generated guide as incomplete if topic extraction, assessment
  extraction, source download, or HTML validation fails.
- Do not invent exam claims. If a topic needs deeper explanation, keep it inside
  the extracted syllabus text and mark it for review.
- Use AI image generation only as an optional illustration layer. Prefer
  deterministic SVG concept maps for simple structures. If an AI image model is
  used, record the model, prompt, source topic, caption, and review status; never
  let an illustration introduce unsupported exam claims.
