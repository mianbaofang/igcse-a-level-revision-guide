# IGCSE & A-Level AI Revision Guide Skill

<p align="center">
  <img src="docs/assets/hero.svg" alt="IGCSE & A-Level AI Revision Guide Skill hero" width="100%">
</p>

<p align="center">
  <a href="README.zh-CN.md">中文 README</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/">Project site</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">Intro video</a>
  ·
  <a href="docs/PROJECT_DETAILS.md">Project details</a>
  ·
  <a href="docs/SKILL_EXPLAINED.md">Skill explained</a>
  ·
  <a href="docs/IMAGE_MODEL_GUIDE.md">Image models</a>
  ·
  <a href="docs/EXAMPLES.md">Examples</a>
  ·
  <a href="docs/ACCURACY_POLICY.md">Accuracy policy</a>
  ·
  <a href="docs/RELEASE_CHECKLIST.md">Release checklist</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-1454A5">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-B83246">
  <img alt="PDF ready" src="https://img.shields.io/badge/PDF-ready-1F7A5B">
  <img alt="OxfordAQA" src="https://img.shields.io/badge/provider-OxfordAQA-D99A24">
</p>

IGCSE & A-Level AI Revision Guide Skill is a Codex Skill for turning an OxfordAQA
International GCSE or International AS-A-level subject into a printable,
image-rich revision guide.

For parents, students, tutors, and teachers: you do **not** need to install
Python, run commands, or understand the codebase. Give the Skill link to your
Codex/agent, ask it to install the Skill, then request a subject guide in plain
language. After you confirm the subject, output language, image model, and
explanation style, the agent returns an HTML/PDF guide with explanations,
worked examples, infographics, and review questions.

## Start Here: Use the Skill

Send this link to your Codex/agent:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

Then say:

```text
请安装这个 Skill，然后帮我生成 OxfordAQA Chemistry International GCSE 复习手册，并导出 PDF。
```

After installation, normal prompts are enough:

```text
帮我生成 OxfordAQA Biology International GCSE 学习手册。
帮我生成 Chemistry 9202 复习手册，并导出 PDF。
帮我生成 OxfordAQA Business International AS-A-level revision guide。
```

Before generation starts, the agent must confirm four choices with you:

1. **Subject**: exam board, level, subject, and code if known, for example
   OxfordAQA International GCSE Chemistry 9202.
2. **Output language**: choose English (`en`) or Simplified Chinese (`zh-CN`).
   The generated handbook uses one selected language for its own labels and
   explanations instead of bilingual `Chinese / English` labels.
3. **Infographic/image route**: choose `gpt-image-2`, `qwen-image-pro`,
   `sensenova-u1-fast`, `custom`, or explicitly choose `prompt-queue` for a dry
   run. For a custom model/API, provide only the model name, endpoint URL, and
   the environment variable name that stores the API key. Do not paste raw keys
   into chat or commit them.
4. **Explanation style**: `formal`, `friendly`, `life`, `story`, `detective`, or
   `adventure`.

Once those choices are confirmed, the Skill starts the real workflow: turn the
selected OxfordAQA course requirements into teachable topic units, decide where
visual explanation is needed, generate or queue the right graphics, and render
an HTML/PDF guide with topic maps, worked examples, practice cards, answer
checkpoints, and final revision questions.

Current scope is intentionally narrow: OxfordAQA is implemented now. Pearson
Edexcel and Cambridge International / CAIE are planned next for the China-market
roadmap.

## 24-Second Intro

<p align="center">
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">
    <img src="docs/assets/intro-animation-preview.gif" alt="IGCSE & A-Level AI Revision Guide Skill intro animation preview" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">Open the live HTML intro</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.mp4">Play or download the MP4</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/">Open the project home page</a>
</p>

## Why This Exists

This project began at home. My son is taking his International GCSE exams this
year after moving from a Chinese public-school path into an international
curriculum. In less than a year, the classroom language shifted from Chinese to
English, while the exam clock kept moving. The knowledge itself can be learned;
the hard part is reorganizing it under a new language, a new exam style, and real
time pressure.

So I turned AI into a revision skill: take the chosen course, break the
knowledge into understandable structures, examples, diagrams, checkpoints, and
reviewable practice. The goal is not to let AI learn for a child. The goal is to
lower the noise around learning so a student can face schoolwork with more calm
and control.

The promise is simple: make revision more readable, more visual, and easier to
review. The official syllabus and validation checks stay behind the scenes as
safety rails, so the guide can be helpful without drifting into unsupported
claims.

## What It Produces

| Mathematics | Economics | Chemistry |
|---|---|---|
| <img src="docs/assets/sample-math-guide.png" alt="Mathematics sample guide with visual worked example" width="100%"> | <img src="docs/assets/sample-economics-guide.png" alt="Economics sample guide with infographic" width="100%"> | <img src="docs/assets/sample-chemistry-guide.png" alt="Chemistry sample guide with infographic" width="100%"> |

## Visual And Narrative Modes

The guide should not read like a sleepy syllabus extract. The renderer now has
three layers:

- **Deterministic SVG basics** for concept maps, particle models, pH scales,
  energy curves, and other reproducible diagrams.
- **User-selected infographic image models** for complex geometry, lab
  apparatus, circuits, economics charts, and text-heavy visuals in the selected
  output language.
- **Narrative explanation templates** such as life-scene analogies, detective
  reasoning, and anime-quest style study missions. These use original framing by
  default and should not copy protected characters or worlds.

The AI analyzes which topic points and practice examples need visual
explanation. Those selected items carry a `visual_brief`: what diagram is
needed, whether SVG is enough, which image provider the user selected when an
infographic is needed, and the prompt queue for producing reviewed charts.

## Optional Image Generation

The current MVP uses deterministic SVG drafts for simple visual needs. When the
AI marks a point as needing a richer infographic, lab apparatus, single-language
visual, or visual explanation, the agent should ask the user to choose an image
provider before generating complex charts.

Recommended starting points:

- **OpenAI `gpt-image-2`** as a high-quality option when the OpenAI stack is
  available.
- **Qwen-Image-2.0 / Qwen Image 2.0 Pro** for Chinese/English text-heavy
  infographic experiments.
- **SenseNova U1 Fast** for fast infographic drafts and local/provider
  experiments.

See [Image Model Guide](docs/IMAGE_MODEL_GUIDE.md). Images explain the selected
topic; they must not invent extra exam claims or unsupported facts.

## Developer Quick Start

This section is only for developers who want to run or modify the Python engine
directly. Normal Skill users can skip it.

Run the offline synthetic demo first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m intl_exam_guide demo --out ./outputs/demo-science --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf
```

Then run a real OxfordAQA public qualification:

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --language en --image-provider qwen-image-pro --explanation-style friendly --out ./outputs/chemistry-9202
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m intl_exam_guide demo --out .\outputs\demo-science --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf
python -m intl_exam_guide generate --query chemistry --level igcse --language en --image-provider qwen-image-pro --explanation-style friendly --out .\outputs\chemistry-9202
```

Run from a checkout without installing:

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level a-level --language en --image-provider prompt-queue --explanation-style detective --out ./outputs/chemistry-9620
```

## What It Generates

```text
outputs/chemistry-9202/
  guide.html                 print-friendly student guide
  guide.pdf                  PDF export when Chrome/Edge or Playwright is available
  sections/                  modular handbook source fragments for review/rebuild
  images/                    SVG drafts, infographic assets, and visual_manifest.json
  run-options.json           confirmed subject, language, image route, and writing style
  guide-plan.json            structured guide plan and practice cards
  qualification.json         extracted qualification metadata
  validation.json            quality gate report
  handbook-package.json      manifest for sections and visual assets
  source/                    optional local reference cache, do not commit
```

## Supported Scope

| Provider / exam board | International GCSE | International AS-A-level | Status |
|---|---:|---:|---|
| OxfordAQA / Oxford International AQA Examinations | yes | yes | MVP implemented |
| Pearson Edexcel | planned | planned | China-market roadmap |
| Cambridge International / CAIE | planned | planned | China-market roadmap |
| Other UK boards, including OCR, WJEC/Eduqas, and CCEA | no | no | outside current scope |

The current implementation is for OxfordAQA, not the whole AQA UK portfolio and
not every A-level awarding organisation. This boundary is intentional: in
mainland China, the practical international-school roadmap is OxfordAQA,
Pearson Edexcel, and Cambridge International.

Within OxfordAQA, subjects are not registered one by one. Any discovered
International GCSE or International AS-A-level qualification page should use the
same provider/parser pipeline. Specialist subject profiles only improve example
and visual choices; unprofiled subjects fall back to syllabus-aligned generic
examples instead of borrowing another subject's template.

OxfordAQA's subject index lists International GCSE and International AS-A-level
qualification pages. The public subject page also explains that International
GCSEs are linear, while International AS-A-levels are modular. The generator
keeps that difference in the guide instead of forcing one structure onto both.
On subject pages, the provider records the website listing group too:
`btn--type-8` is treated as the blue International GCSE listing and
`btn--type-7` as the red International AS-A-level listing.

The current discovery audit found 17 subject pages and 48 qualification links:
31 International GCSE listings and 17 International AS-A-level listings, with no
unknown listing types.

The parser audit also opened all 48 discovered qualification pages and found no
missing topic extraction, assessment extraction, specification link, or
blue/red listing conflict.

Official source anchors used for this scope:

- [OxfordAQA](https://www.oxfordaqa.com/) for the current provider and
  International GCSE / International AS-A-level subject pages.
- [Pearson Edexcel International Advanced Levels](https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels.html)
  for the planned Pearson provider family.
- [Cambridge International facts and figures](https://www.cambridgeinternational.org/about-us/facts-and-figures/)
  for the planned Cambridge International / CAIE provider family.

## Language Policy

Generated guides use the output language selected before generation:

- `en` mode keeps the student-facing handbook in English.
- `zh-CN` mode keeps the student-facing handbook in Simplified Chinese.
- Template labels, explanation frames, worked examples, and generated image
  prompts follow one selected language instead of bilingual labels.
- In `zh-CN` mode, raw English topic headings and syllabus bullet points stay in
  structured files or a separated review appendix; the topic map and
  student-facing topic body remain Chinese.

This prevents the generator from producing half-Chinese, half-English handbook
pages.

## Guide Generation Model

The generator separates course intake from creative teaching:

1. **Course intake**: find the selected OxfordAQA course and read its current requirements.
2. **Topic planning**: turn the course into teachable topic blocks, examples, and review tasks.
3. **Visual decision**: decide whether each concept needs no image, simple SVG, or a richer infographic model.
4. **Student guide writing**: keep the chosen language and explanation style consistent across the handbook.
5. **Rendering**: build the HTML guide and PDF export.
6. **Validation**: warn when topics, examples, visuals, or output files are incomplete.

Current worked examples are original practice items, not copied past-paper
questions. Each card records a command word, difficulty, focus point, solution
steps, and answer checkpoints.

## Agent Workflow

Most users do not need the command line. Give the Skill link to an AI agent,
then ask for a subject guide in plain language, for example:

```text
Install this Skill, then generate a Chinese OxfordAQA International GCSE
Mathematics 9260 revision handbook with visual worked examples and PDF output.
```

The agent should confirm four choices before it starts:

- subject and qualification;
- output language;
- image route for complex infographics;
- explanation style.

After that, the agent handles discovery, syllabus reading, guide writing,
visual generation, HTML rendering, PDF export, and final checks.

## Public Samples

The homepage shows Mathematics, Economics, and Chemistry screenshots only as
visual examples of the final handbook quality. They are not a fixed publishing
process and they are not the subject support limit. Any supported OxfordAQA
qualification should follow the same syllabus-to-handbook workflow.

## Codex Skill

This repository also includes a compact Codex skill wrapper in `skill/`.

<p align="center">
  <img src="docs/assets/skill-system.svg" alt="Skill system diagram" width="100%">
</p>

The skill keeps the agent workflow concise and pushes deterministic operations
into the Python package. See [Skill explained](docs/SKILL_EXPLAINED.md).

## Copyright and Source Policy

Do not commit downloaded OxfordAQA PDFs, past papers, mark schemes, or copied
question content to this repository. Generated examples should use original
explanations, original practice cards, and only the minimum review metadata
needed to check where the guide came from.

Families should confirm exam entry routes, subject availability, and local exam
arrangements with their school or exam centre.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py .
```

## Repository Layout

```text
src/intl_exam_guide/
  providers/      website-specific discovery and parsing
  parsing/        PDF text extraction
  planning/       source-safe guide and practice planning
  rendering/      HTML and PDF rendering
  validation/     completeness and safety checks
skill/            Codex skill wrapper
docs/             project, skill, accuracy, and research notes
tests/            parser and pipeline tests
```

## README Presentation References

These repositories are not comparable education or syllabus-generation tools.
They were used only as references for open-source README presentation patterns:
badges, hero imagery, quick start placement, documentation navigation, trust
messaging, and contribution links.

The README structure was informed by presentation patterns from projects such as
[Open WebUI](https://github.com/open-webui/open-webui),
[uv](https://github.com/astral-sh/uv),
[Ruff](https://github.com/astral-sh/ruff),
[RAGFlow](https://github.com/infiniflow/ragflow), and
[awesome-readme](https://github.com/matiassingers/awesome-readme). See
[README research notes](docs/README_RESEARCH.md).

## License

MIT.
