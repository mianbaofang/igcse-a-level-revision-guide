# Revision Guide Handbook Spec

This repository is an open-source version of the original IGCSE revision-guide
Skill. Its first job is to generate a student-facing study and revision
handbook, not a project report.

## Output Package

Each generated handbook must include:

- `guide.html`: one print-friendly UTF-8 HTML file.
- `guide.pdf`: A4 PDF export when a browser runtime is available.
- `sections/`: modular source fragments used to assemble the handbook.
- `images/`: deterministic SVG drafts and reviewed infographic assets.
- `guide-plan.json`: structured topic guides, worked examples, and visual briefs.
- `qualification.json`: source metadata extracted from the official provider.
- `validation.json`: machine-readable quality checks.
- `handbook-package.json`: manifest for sections and image assets.

Downloaded specification PDFs and extracted text belong under `source/` and must
not be committed to the repository.

## Required Preflight

Do not start the handbook pipeline until the user has confirmed:

1. subject selection: board, qualification level, subject, and code if known;
2. output language: `en` or `zh-CN`;
3. infographic/image route: a named provider or a custom API connection;
4. writing style: `formal`, `friendly`, `life`, `story`, `detective`, or
   `adventure`.

For custom image providers, record the model name, endpoint URL, and the API-key
environment variable name. Do not collect or store the raw API key. If the user
chooses `prompt-queue`, treat it as a dry run: create source-bound prompts and
SVG-safe drafts, but do not present the result as a final image-rich handbook.

## Handbook Structure

The final handbook should read like a revision book for a student. Use this
order unless the subject requires a reviewed alternative:

1. Cover.
2. How to use this handbook.
3. Study roadmap / topic map.
4. Topic guide blocks.
5. Worked examples and practice.
6. Visual explanations.
7. Exam structure and source appendix.

Each topic or knowledge unit should include:

- one-sentence essence;
- student-friendly analogy or life-scene explanation;
- key syllabus points;
- at least one worked example;
- public solution steps;
- answer checkpoints;
- exam pitfall;
- source anchor back to the specification PDF.

## Writing Style

Use one selected output language for handbook labels, explanations, image
prompts, topic framing, and worked-example framing. Do not render labels as
bilingual `Chinese / English` pairs. In `en` mode, student-facing text should be
English. In `zh-CN` mode, student-facing labels, explanations, examples, and
image prompts should be Simplified Chinese. Official English source snippets may
be retained in structured JSON or a clearly separated review appendix, but do
not mix raw English source paragraphs, topic headings, or syllabus bullet points
into the student-facing topic map/body.

The tone should help teenagers stay awake and oriented:

- use life-scene explanations for abstract ideas;
- use detective-style reasoning for solution steps;
- use original adventure/anime-like framing for motivation when useful;
- avoid copying protected characters, stories, or exam-paper artwork;
- avoid long academic paragraphs and unsupported syllabus claims.

## Visual Workflow

Do not make the handbook text-only by default.

After the source-bound topic guide and examples are drafted, run a second pass
to decide which items need visuals:

- `text-ok`: no image needed;
- `svg-basic`: deterministic SVG is enough;
- `infographic`: ask the user to choose an image model before generation.

Good SVG cases include number lines, simple graphs, pH scales, particle models,
energy profiles, and basic geometry. Good infographic cases include lab
apparatus, complex geometry, circuits, economics diagrams, business workflows,
and text-heavy single-language charts.

If a richer infographic is needed, keep a prompt queue with:

- topic title;
- focus point;
- source syllabus points;
- image provider;
- prompt;
- review status.

Do not claim that an infographic has been generated until the selected provider
has produced an image and the asset is saved under `images/`.

## Source And Accuracy Rules

- Use the public qualification page for discovery metadata.
- Use the downloaded course specification PDF as the source of truth for
  detailed syllabus content.
- Prefer detailed reference codes such as `N1`, `A13`, `G20`, or `S18` when the
  PDF exposes them.
- Do not copy past-paper questions, mark schemes, or large passages from the PDF.
- Generate original worked examples that stay inside the extracted syllabus
  points.
- Treat a guide as incomplete if the detailed topic extraction, source snippets,
  examples, visuals, HTML, or validation report are missing.

## Validation Checklist

Before presenting a handbook, confirm:

- topic count is detailed enough for the source PDF;
- every topic has a guide block and worked example;
- every topic has a source snippet or a manual-review warning;
- visual briefs exist for visual topics;
- `sections/` and `images/` are present;
- `validation.json` has no `error` issues;
- PDF export succeeded or the user is told why it was skipped.
