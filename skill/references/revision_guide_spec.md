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
- `concepts/`: source-bound concept-writing jobs and reviewed concept
  explanations imported before final delivery.
- `guide-plan.json`: structured topic guides, worked examples, and visual briefs.
- `qualification.json`: source metadata extracted from the official provider.
- `validation.json`: machine-readable quality checks.
- `final-review-packet.json`: Agent/LLM self-review packet written by the
  `review` command before final presentation.
- `handbook-package.json`: manifest for sections and image assets.

Downloaded specification PDFs and extracted text belong under `source/` and must
not be committed to the repository.

## Required Preflight

Do not start syllabus download or handbook writing until the user has confirmed:

1. subject selection: board, qualification level, subject, and code if known.
   If the user only gives an exam board and subject, resolve official
   candidates first. If several official candidates match, return those choices
   and wait for the user to choose one instead of guessing;
2. exam year when the provider needs it, especially Cambridge pages with
   multiple syllabus year ranges;
3. output language: `en` or `zh-CN`;
4. writing style: `formal`, `friendly`, `life`, `story`, `detective`, or
   `adventure`.

Do not ask for an image model during preflight. The base handbook should run
first, then the visual pass should count how many complex infographic briefs are
needed. Tell the user that count after generation. The user may then provide an
image model, API, Skill, script, designer workflow, or generated asset directory.
If a callable route exists, run it after the base handbook is generated and
import or attach the reviewed outputs automatically. Do not make the user move
files by hand. If they provide none, leave complex infographics as pending
visual jobs, show the `visual_###` IDs that need generation, and do not present
those slots as final reviewed visuals.

The same "base first, review before final" rule applies to concept
explanations. The base generator writes `concepts/concept_jobs.json` and
`concepts/concept_jobs.md` from the current topic title and official source
points. The Agent/LLM must then write the final student-facing concept
explanations for each job, save them as `concepts/concept_explanations.json`,
import them with `scripts/import_concept_explanations.py`, and rerun validation
before presenting the handbook as final.

Recommended external models for complex text+diagram infographics include GPT
Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast. They are recommendations,
not guaranteed built-in capabilities. For custom image providers, record the
model name, endpoint URL, and the API-key environment variable name. Do not
collect or store the raw API key.

Before any real image provider is used after the base guide run, verify at least
one concrete capability:
a named image-generation Skill installed for this run, an existing generation or
import script path, an asset directory with files matching visual IDs, or a
`custom` provider with model name, endpoint URL, API-key environment variable
name, and the environment variable actually set. If this gate is not satisfied,
do not ask the user to pick from model names and do not pass recommended model
labels to the base generator. Use `prompt-queue`, write pending visual jobs for
complex visuals, and leave the final result marked as needing image review.

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
- 2-3 source-bound concept explanations that say what the concept is, what
  relationship or boundary it describes, and why it matters for this syllabus
  point;
- key syllabus points kept in structured review data, not as a substitute for
  concept explanation;
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
- run the anti-template language pass before finalizing student-facing text:
  remove safe formulaic transitions such as `In conclusion`, `Overall`, `总之`,
  and `值得注意的是`; leave remaining suspicious AI-style phrasing as validation
  warnings for review.

## Visual Workflow

Do not make the handbook text-only by default.

After the source-bound topic guide and examples are drafted, run a second pass
to decide which items need visuals:

- `text-ok`: no image needed;
- `svg-basic`: deterministic SVG is enough;
- `infographic`: create a source-bound visual brief and prompt queue entry;
  render it only after a reviewed raster asset exists.

Good SVG cases include number lines, simple graphs, pH scales, particle models,
energy profiles, and basic geometry. Good infographic cases include lab
apparatus, complex geometry, circuits, economics diagrams, business workflows,
and text-heavy single-language charts.

For SVG-safe chart, axis, curve, table, and simple geometry cases, use the
scientific-vector fallback in `references/scientific_vector_fallback.md`. This
adapts the `nature-figure` idea of a figure contract to revision guides: state
the learning claim, evidence/label requirements, and review risk before drawing.
Keep SVG text editable and record `fallback_route:
scripted-scientific-vector` in `images/visual_manifest.json`. Do not use this
route for dense educational posters or rich infographics that need a real image
model or reviewed imported asset.

If a richer infographic is needed, keep a prompt queue with:

- topic title;
- focus point;
- source syllabus points;
- asset route/status: `deterministic-svg`, `external-generation-required`, or a
  reviewed generated/imported asset;
- prompt;
- review status.

Do not claim that an infographic has been generated until a callable route has
produced or imported an image and the asset is saved under `images/`.

## Source And Accuracy Rules

- Use the public qualification page for discovery metadata.
- Use the downloaded course specification PDF as the source of truth for
  detailed syllabus content.
- Prefer detailed reference codes such as `N1`, `A13`, `G20`, or `S18` when the
  PDF exposes them.
- Do not copy past-paper questions, mark schemes, or large passages from the PDF.
- Generate original worked examples that stay inside the extracted syllabus
  points.
- Do not maintain per-subject hard-coded concept-explanation libraries. The
  final concept text must be generated from the current topic title and source
  points for that run, not copied from a Mathematics, Chemistry, Economics, or
  Physics template.
- Treat a guide as incomplete if the detailed topic extraction, source snippets,
  examples, visuals, HTML, or validation report are missing.

## Validation Checklist

Before presenting a handbook, confirm:

- topic count is detailed enough for the source PDF;
- every topic has a guide block and worked example;
- every topic has a reviewed concept explanation imported from
  `concepts/concept_explanations.json`;
- `validation.json.review_summary.pending_concept_explanations` is `0`;
- every topic has a source snippet or a manual-review warning;
- visual briefs exist for visual topics;
- `sections/` and `images/` are present;
- `validation.json` has no `error` issues;
- PDF export succeeded or the user is told why it was skipped.

Then run `python -m intl_exam_guide review --out <output-dir>`, read
`final-review-packet.json`, and perform an Agent/LLM review over the rendered
excerpt, validation issues, source/topic summary, and visual status. Validation
is not enough by itself. The packet must include an `agent_self_review` verdict;
if `agent_self_review.must_not_present_as_final` is true, present the output as
a draft or blocked run, not as final.
