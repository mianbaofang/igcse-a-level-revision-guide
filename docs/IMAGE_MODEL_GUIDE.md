# Image Model Guide / 生图模型建议

## English

The guide generator should not depend on image generation for its core factual
output. The current MVP uses deterministic SVG concept maps because they are
easy to trace back to syllabus points.

For many subjects, richer illustrations are still useful:

- science lab apparatus and safety layouts;
- maths geometry diagrams and step-by-step annotated figures;
- biology structures and process diagrams;
- chemistry particle or reaction sketches;
- physics force, circuit, wave, and energy-transfer diagrams;
- economics curves, flow diagrams, and scenario posters;
- bilingual infographics that help students bridge Chinese explanation and
  English exam language.

Use image generation as a user-selected illustration adapter, not as the source
of truth. The generator should first create source-bound knowledge points and
practice examples, then analyze which items need visual explanation. Simple
visuals can use SVG; complex infographics should ask the user for a provider.

The guide should also support lively explanation styles. A model-generated
visual can be paired with a life-scene story, detective-style reasoning, or an
anime-quest style mission. These modes should use original framing by default
and should not copy protected characters, dialogue, or fictional worlds.

## Recommended Providers

| Provider | Best use | Notes |
|---|---|---|
| OpenAI `gpt-image-2` | Default high-quality provider for Codex/OpenAI workflows, visual explanations, edits, and polished guide illustrations. | Official OpenAI docs list text and image input, image output, flexible sizes, and image generation/edit endpoints. Check cost, moderation, and organization verification requirements. |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | Chinese/English text-heavy infographics, poster-like layouts, PPT-style visual explanations, and China-market experiments. | Treat API availability, provider endpoint, license, and deployment constraints as configurable. |
| SenseNova U1 / SenseNova-U1-8B-MoT variants | Open-source or local experiments, dense visual communication, interleaved image-text, and fast infographic drafts. | Use as an experimental provider until this project has its own visual benchmark set. The official repo describes 8-step inference variants and infographic-focused checkpoints. |

Do not hard-code one provider. Use a provider interface so schools, tutors, or
agents can choose based on availability, cost, privacy, and language quality.

## Suggested Architecture

Use this as the integration flow:

```text
official specification
  -> extracted syllabus points
  -> deterministic guide plan
  -> visual-need analysis
  -> SVG if simple, or ask user for image provider if complex
  -> visual_brief prompt queue
  -> reviewed illustration asset
  -> HTML/PDF guide
```

Recommended interface:

```text
generate_illustration(
  topic_id,
  topic_title,
  source_snippet_ids,
  visual_type,
  required_labels,
  forbidden_claims,
  language_policy,
  output_size
)
```

Each generated image should store:

- model/provider name;
- prompt;
- source topic and source snippets;
- generation time;
- caption and alt text;
- review status;
- whether it is safe for student-facing use.

## Routing Rules

- Use deterministic SVG for knowledge maps, topic dependency diagrams, and
  source-bound structure.
- Use `gpt-image-2` when the user wants polished guide illustrations and the
  OpenAI stack is available.
- Use Qwen-Image-2.0 or Qwen Image 2.0 Pro when Chinese typography or bilingual
  infographic layout is the main evaluation point.
- Use SenseNova U1 variants for open-source, local, or low-latency experiments.
- Do not recreate official exam paper diagrams, mark scheme diagrams, or
  copyrighted textbook illustrations.
- Do not add labels, mechanisms, equations, or facts that are absent from the
  extracted specification unless a subject expert reviews them.

## Prompt Template

```text
Create an educational illustration for an OxfordAQA International GCSE revision
guide.

Topic: {topic_title}
Source-bound learning point: {source_point}
Visual type: {visual_type}
Required labels: {required_labels}
Language policy: official syllabus terms in English; optional Chinese scaffold
labels only when reviewed.

Make it clear, printable, student-friendly, and suitable for a revision guide.
Do not add new syllabus facts, named examples, equations, or exam claims beyond
the source point.
```

## 中文

复习手册的核心事实不应该依赖生图模型。当前 MVP 使用确定性 SVG 知识地图，是因为
它们更容易追溯到 syllabus points。

但很多知识点确实需要更好的视觉解释，例如：

- Science 实验装置和安全布局；
- Biology 结构图和过程图；
- Chemistry 粒子模型、反应过程示意图；
- Physics 力、电路、波、能量转移图；
- Economics 曲线图、流程图、场景信息图；
- 帮助学生从中文理解过渡到英文考试表达的双语信息图。

生图应该是用户选择的插图层，不是事实来源。生成器应先根据大纲生成基础知识点和
例题，再分析哪些知识点或例题需要图文结合讲解。简单图用 SVG；复杂信息图再让用户
选择 provider。

## 推荐模型

| Provider | 适合场景 | 备注 |
|---|---|---|
| OpenAI `gpt-image-2` | Codex/OpenAI 工作流里的默认高质量方案，适合复习手册插图、视觉解释和编辑。 | OpenAI 官方文档说明它支持文本和图像输入、图像输出、灵活尺寸，并支持生成和编辑接口。注意成本、内容审核和组织验证要求。 |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | 中文/英文文字较多的信息图、海报式解释、PPT 风格知识图、国内场景实验。 | API、服务商、许可和部署限制应做成配置，不要写死。 |
| SenseNova U1 / SenseNova-U1-8B-MoT variants | 开源、本地、快速信息图草稿、密集图文表达实验。 | 在本项目建立自己的视觉基准前，建议作为实验性 provider。官方仓库提到 8-step 推理变体和 infographic checkpoints。 |

不要把项目绑定到单一 provider。更好的做法是设计一个 provider interface，让学校、
老师、家长或 agent 按可用性、成本、隐私和中英文排版质量来选择。

## 生成边界

- 知识地图、topic 依赖关系和 source-bound 结构优先用确定性 SVG。
- 需要精美插图且 OpenAI 环境可用时，优先用 `gpt-image-2`。
- 需要中文排版或双语信息图时，可以评估 Qwen-Image-2.0 / Qwen Image 2.0 Pro。
- 需要开源、本地或低延迟实验时，可以评估 SenseNova U1 variants。
- 不要复刻官方真题图、mark scheme 图或教材版权插图。
- 不要让图片添加 specification 中没有的标签、机制、公式或考试结论，除非经过学科老师复核。
