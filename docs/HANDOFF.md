# Agent Handoff / 后续 Agent 接手说明

Last updated: 2026-06-18

This file is the first place a new agent should read before continuing work on
this repository.

## Source Of Truth

- GitHub repository: `https://github.com/mianbaofang/igcse-a-level-revision-guide`
- GitHub Pages: `https://mianbaofang.github.io/igcse-a-level-revision-guide/`
- Local repository in Ethan's Codex workspace:
  `C:\Users\Ethan\Documents\Codex\2026-06-14\igcse-skill-skill-github-skill-igcse\work\igcse-a-level-revision-guide`
- Local generated outputs:
  `C:\Users\Ethan\Documents\Codex\2026-06-14\igcse-skill-skill-github-skill-igcse\outputs`
- Installed local Skill:
  `C:\Users\Ethan\.agents\skills\igcse-a-level-revision-guide`
- Deprecated compatibility Skill:
  `C:\Users\Ethan\.agents\skills\igcse-revision-guide`

The compatibility Skill should remain a thin redirect only. Do not restore the
old `REFERENCES/` or `EXAMPLES/` workflow under `igcse-revision-guide`.

## What This Project Is

This is an open-source Codex Skill and Python pipeline for generating
student-friendly, image-rich revision handbooks for OxfordAQA International GCSE
and International AS-A-level subjects.

The user-facing promise is simple:

1. give an agent the Skill link;
2. ask for a subject revision/study handbook;
3. confirm subject, output language, image route, and explanation style;
4. let the agent fetch the OxfordAQA syllabus, plan the handbook, generate
   examples and visuals, render HTML, export PDF, and validate the result.

Current provider support is OxfordAQA only. Pearson Edexcel and Cambridge
International / CAIE are roadmap providers for the China-market version. Do not
claim support for all UK exam boards.

## Current State

- Repository name and links use `mianbaofang/igcse-a-level-revision-guide`.
- GitHub Pages is configured from `main` / `docs`.
- Public homepage: `docs/index.html`.
- Public intro animation: `docs/project-intro-animation.html`,
  `docs/project-intro-animation.mp4`, and `docs/assets/intro-animation-preview.gif`.
- README and Chinese README now describe ordinary agent usage first, not CLI usage.
- The three public screenshots are examples of final handbook quality, not a
  subject support limit and not a user-facing release workflow.
- SenseNova is named as **SenseNova U1 Fast** for user-facing model guidance;
  the machine option remains `sensenova-u1-fast`.
- Raw API keys must never be committed, pasted into docs, or printed in logs.

## Important Docs

- `README.md`: public English project entry.
- `README.zh-CN.md`: public Chinese project entry.
- `skill/SKILL.md`: the compact Skill instruction that other agents install.
- `skill/references/revision_guide_spec.md`: handbook contract and required
  output behavior.
- `skill/references/oxfordaqa.md`: OxfordAQA provider notes and quality gates.
- `docs/PROJECT_DETAILS.md`: architecture, MVP scope, provider roadmap.
- `docs/IMAGE_MODEL_GUIDE.md`: SVG vs image-model routing and provider guidance.
- `docs/ACCURACY_POLICY.md`: source, copyright, and student-safety rules.
- `docs/EXAMPLES.md`: developer examples and sample verification.
- `docs/RELEASE_CHECKLIST.md`: release checks before GitHub publication.

If a future agent only reads three files, read this file, `README.md`, and
`skill/SKILL.md`.

## Current Output Samples

The local `outputs/` folder contains generated sample guides and verification
artifacts. The most important samples are:

- `outputs/mathematics-9260-sample/guide.html`
- `outputs/mathematics-9260-sample/guide.pdf`
- `outputs/economics-9214-sample/guide.html`
- `outputs/economics-9214-sample/guide.pdf`
- `outputs/chemistry-9202-sample/guide.html`
- `outputs/chemistry-9202-sample/guide.pdf`
- `outputs/repo-home-preview.html`
- `outputs/project-intro-animation.html`
- `outputs/igcse-a-level-revision-guide-source.zip`

Generated guide folders are large and are not committed to Git. Treat them as
local release artifacts.

## Validation Commands

From the repository root:

```powershell
python -m pytest -q
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ..\..\outputs
python scripts/verify_release_samples.py --outputs-root ..\..\outputs
```

If the current Python environment does not have test dependencies installed,
install the package in editable development mode first:

```powershell
python -m pip install -e ".[dev]"
```

Before committing or pushing, run at least:

```powershell
git diff --check
python scripts/scan_for_raw_keys.py . ..\..\outputs
```

## Image Generation Rules

- Ask the user before starting a real guide run if the image route is not
  confirmed.
- Use deterministic SVG only for simple structure diagrams and source-bound
  concept maps.
- Use user-selected image providers for complex infographics, for example
  `gpt-image-2`, `qwen-image-pro`, `sensenova-u1-fast`, or `custom`.
- If the provider is custom, record model name, endpoint URL, and environment
  variable name for the key. Do not record the raw key.
- Every generated image should keep provider/model, prompt, source topic,
  caption, alt text, and review status metadata.

## Known Follow-Up Priorities

1. Improve PDF section segmentation for command words, assessment objectives,
   appendices, and version history.
2. Add synthetic provider fixtures and tests so parser changes do not depend on
   downloaded official PDFs.
3. Add deeper subject-aware authoring adapters for worked examples, with
   review gates.
4. Add richer SVG templates for common Maths, Science, Economics, and Business
   diagram types.
5. Implement proper image-provider adapter interfaces rather than treating
   provider images as external/imported assets.
6. Add visual regression checks for generated HTML and public homepage assets.
7. Add Pearson Edexcel provider after OxfordAQA fixtures and validation are
   stable.
8. Add Cambridge International / CAIE provider after Edexcel or as a separate
   provider module with its own source model.

## Do Not Do

- Do not commit downloaded OxfordAQA PDFs, past papers, mark schemes, or copied
  question content.
- Do not describe the project as supporting all IGCSE/A-Level providers.
- Do not mix Chinese and English labels in student-facing guide bodies unless
  the user explicitly requests bilingual output.
- Do not use generated images as factual sources. Images explain source-bound
  content; they do not create syllabus facts.
- Do not push private API keys, generated key logs, or provider credentials.

## 中文快速交接

下一个 agent 优先看：

1. `docs/HANDOFF.md`
2. `README.zh-CN.md`
3. `skill/SKILL.md`
4. `skill/references/revision_guide_spec.md`

当前项目已经开源到：

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide
```

当前公开主页：

```text
https://mianbaofang.github.io/igcse-a-level-revision-guide/
```

用户侧理解方式：

```text
把 Skill 链接给 agent -> 让 agent 安装 -> 用户说“帮我生成某科复习手册”
-> agent 先确认科目、语言、生图方式、讲解风格 -> 自动生成 HTML/PDF。
```

核心逻辑不能变：先根据 OxfordAQA 官方大纲生成知识点和例题，再二次判断哪些内容
需要图文结合；简单图用 SVG，复杂信息图用用户选择的生图模型。
