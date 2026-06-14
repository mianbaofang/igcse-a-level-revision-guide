from __future__ import annotations

import html
from pathlib import Path

from intl_exam_guide.models import (
    GuidePlan,
    PracticeItem,
    Qualification,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)


def render_html(plan: GuidePlan, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qualification = plan.qualification
    parts = [
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        f"<title>{escape(qualification.title)} Revision Guide</title>",
        f"<style>{stylesheet()}</style></head><body>",
        render_cover(qualification),
        render_source_note(qualification),
        render_language_policy(),
        render_summary(qualification),
        render_assessments(qualification),
        render_topic_map(qualification.topics),
        render_revision_stages(plan.revision_stages),
        render_topics(
            qualification.topics,
            plan.topic_guides,
            plan.practice_items,
            plan.visual_briefs,
        ),
        render_diagram_briefs(plan.diagram_briefs),
        render_final_checklist(qualification, len(plan.practice_items)),
        "</body></html>",
    ]
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def render_cover(qualification: Qualification) -> str:
    qtype = "International GCSE" if qualification.qualification_type == "international_gcse" else "International AS/A-level"
    return f"""
<section class="cover">
  <div class="kicker">{escape(qtype)} Revision Guide / 复习指南</div>
  <h1>{escape(qualification.title)}</h1>
  <p class="subtitle">Source-traceable final revision guide generated from OxfordAQA public syllabus materials.</p>
  <div class="cover-grid">
    <div><span>Code</span><strong>{escape(qualification.code or "Unknown")}</strong></div>
    <div><span>Topics</span><strong>{len(qualification.topics)}</strong></div>
    <div><span>Assessment papers</span><strong>{len(qualification.assessments)}</strong></div>
  </div>
</section>
"""


def render_source_note(qualification: Qualification) -> str:
    listing_note = render_listing_note(qualification)
    return f"""
<section class="band source">
  <h2>适用对象与来源 / Audience and Sources</h2>
  <p>{escape(qualification.audience_note)}</p>
  {listing_note}
  <ul>
    <li>Qualification page: <a href="{escape(qualification.page_url)}">{escape(qualification.page_url)}</a></li>
    <li>Specification PDF: {link_or_missing(qualification.source.specification_url)}</li>
    <li>PDF SHA-256: <code>{escape(qualification.source.specification_sha256 or "not downloaded")}</code></li>
  </ul>
</section>
"""


def render_language_policy() -> str:
    return """
<section class="band language-policy">
  <h2>语言策略 / Language Policy</h2>
  <ul class="plain">
    <li>Official qualification titles, topic titles, paper titles, syllabus points, and source snippets are kept in English from OxfordAQA.</li>
    <li>Template navigation labels are bilingual: Chinese first, then English.</li>
    <li>Chinese topic translations should be added only from a reviewed glossary or subject-specialist authoring pass.</li>
  </ul>
</section>
"""


def render_listing_note(qualification: Qualification) -> str:
    source = qualification.source
    if not source.listing_group_label and not source.listing_subject:
        return ""
    pieces = []
    if source.listing_subject:
        pieces.append(f"Subject group: {escape(source.listing_subject)}")
    if source.listing_group_label:
        pieces.append(f"Website group: {escape(source.listing_group_label)}")
    if source.listing_style_class:
        pieces.append(f"Detected class: {escape(source.listing_style_class)}")
    return f"<p class=\"listing-note\">{' · '.join(pieces)}</p>"


def render_summary(qualification: Qualification) -> str:
    items = "\n".join(f"<li>{escape(item)}</li>" for item in qualification.summary[:5])
    return f"""
<section class="band">
  <h2>课程定位 / Course Position</h2>
  <ul class="plain">{items}</ul>
</section>
"""


def render_assessments(qualification: Qualification) -> str:
    cards = []
    for paper in qualification.assessments:
        details = "".join(f"<li>{escape(item)}</li>" for item in paper.details[:8])
        cards.append(f"<article class=\"assessment\"><h3>{escape(paper.title)}</h3><ul>{details}</ul></article>")
    body = "\n".join(cards) if cards else "<p class=\"warning\">No assessment structure was extracted. Review the source page manually.</p>"
    return f"<section class=\"band\"><h2>考试结构 / Assessment Structure</h2><div class=\"assessment-grid\">{body}</div></section>"


def render_topic_map(topics: list[Topic]) -> str:
    rows = []
    for index, topic in enumerate(topics, start=1):
        points = ", ".join(topic.points[:4]) if topic.points else "Use the specification text for detailed statements."
        rows.append(
            "<tr>"
            f"<td>{index}</td><td>{escape(topic.title)}</td><td>{escape(points)}</td>"
            "<td>概念边界 -> 例题 -> 错题回看</td>"
            "</tr>"
        )
    return f"""
<section class="band">
  <h2>知识地图 / Knowledge Map</h2>
  <table><thead><tr><th>#</th><th>Topic / 官方主题</th><th>Official syllabus points / 官方大纲要点</th><th>Revision route / 复习路径</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>
"""


def render_revision_stages(stages: list[str]) -> str:
    items = "".join(f"<li>{escape(stage)}</li>" for stage in stages)
    return f"<section class=\"band\"><h2>三阶段复习法 / Three-Stage Revision</h2><ol class=\"stage-list\">{items}</ol></section>"


def render_topics(
    topics: list[Topic],
    topic_guides: list[TopicGuide],
    practice_items: list[PracticeItem],
    visual_briefs: list[VisualBrief],
) -> str:
    grouped: dict[str, list[PracticeItem]] = {}
    for item in practice_items:
        grouped.setdefault(item.topic_title, []).append(item)
    guides = {guide.topic_title: guide for guide in topic_guides}
    visuals = {brief.topic_title: brief for brief in visual_briefs}

    sections = []
    for index, topic in enumerate(topics, start=1):
        guide = guides.get(topic.title)
        points = "".join(f"<li>{escape(point)}</li>" for point in topic.points)
        if not points:
            points = "<li>Use the official specification text to expand this topic into teachable sub-points.</li>"
        examples = "\n".join(render_practice(item) for item in grouped.get(topic.title, [])[:2])
        guide_block = render_topic_guide(guide) if guide else ""
        diagram_block = render_topic_diagram(topic, guide, index) if guide else ""
        visual = visuals.get(topic.title)
        visual_block = render_visual_example(topic, guide, visual, index) if guide and visual else ""
        source_block = render_source_snippets(topic.source_snippets)
        sections.append(
            f"""
<section class="topic">
  <h2>T{index}. {escape(topic.title)}</h2>
  <p class="language-note">官方大纲标题保留英文原文 / Official syllabus title retained in English.</p>
  <div class="topic-grid">
    <div>
      <h3>官方边界 / Official Boundary</h3>
      <ul>{points}</ul>
    </div>
    <div class="logic-card">
      <h3>学习逻辑 / Study Logic</h3>
      <p><strong>一句话目标 / One-line goal:</strong> 先判断本 topic 在考什么，再把每个 syllabus point 变成可解释、可计算或可评价的动作。</p>
      <p><strong>常见失分点 / Common mark-loss point:</strong> 只背关键词但没有回应 command word；只写结论但没有把题干信息用进去。</p>
    </div>
  </div>
  {guide_block}
  {diagram_block}
  {visual_block}
  {render_story_modes(topic, guide) if guide else ""}
  {source_block}
  <div class="practice-block">{examples}</div>
</section>
"""
        )
    return "\n".join(sections)


def render_topic_guide(guide: TopicGuide) -> str:
    steps = "".join(f"<li>{escape(step)}</li>" for step in guide.worked_solution_steps)
    checklist = "".join(f"<li>{escape(item)}</li>" for item in guide.checklist)
    return f"""
<div class="guide-grid">
  <article class="essence"><h3>{render_icon("target")}<span>一句话本质 / One-Sentence Essence</span></h3><p>{escape(guide.essence)}</p></article>
  <article class="analogy"><h3>{render_icon("bridge")}<span>生活化类比 / Everyday Analogy</span></h3><p>{escape(guide.analogy)}</p></article>
  <article class="worked"><h3>{render_icon("steps")}<span>Mini Worked Example / 小例题推导</span></h3><p>{escape(guide.mini_worked_example)}</p><ol>{steps}</ol></article>
  <article class="pitfall"><h3>{render_icon("alert")}<span>考试陷阱 / Exam Pitfall</span></h3><p>{escape(guide.pitfall)}</p><ul>{checklist}</ul></article>
</div>
"""


def render_topic_diagram(topic: Topic, guide: TopicGuide, index: int) -> str:
    points = topic.points[:4] or guide.checklist[:4] or [topic.title]
    branches = []
    branch_positions = [(510, 62), (510, 126), (510, 190), (510, 254)]
    colors = ["#1354a5", "#1f7a5b", "#b83246", "#d99a24"]
    for number, point in enumerate(points[:4]):
        x, y = branch_positions[number]
        color = colors[number % len(colors)]
        label = svg_multiline_text(point, x + 18, y + 3, max_chars=26, line_height=16)
        branches.append(
            f"""
<line x1="300" y1="160" x2="{x}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
<circle cx="{x}" cy="{y}" r="8" fill="{color}"/>
<rect x="{x + 14}" y="{y - 25}" width="238" height="54" rx="12" fill="#ffffff" stroke="{color}" opacity="0.98"/>
{label}
"""
        )

    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = (
        f"Source: p.{source.page} - {source.matched_term}" if source else "Source: review required"
    )
    return f"""
<figure class="topic-diagram" aria-label="Concept map for {escape(topic.title)}">
  <figcaption>Concept map / 图文解释</figcaption>
  <svg viewBox="0 0 820 320" role="img" aria-labelledby="diagram-title-{index}">
    <title id="diagram-title-{index}">Concept map for {escape(topic.title)}</title>
    <rect x="0" y="0" width="820" height="320" rx="18" fill="#f7f9fc"/>
    <rect x="24" y="24" width="310" height="272" rx="18" fill="#124f9b"/>
    <text x="52" y="68" fill="#ffe4a9" font-size="13" font-weight="800">TOPIC {index}</text>
    {svg_multiline_text(topic.title, 52, 112, max_chars=20, line_height=28, size=24, weight=800, fill="#ffffff")}
    <text x="52" y="260" fill="#dceaff" font-size="13">{escape(source_label)}</text>
    {''.join(branches)}
  </svg>
</figure>
"""


def render_visual_example(
    topic: Topic,
    guide: TopicGuide,
    visual: VisualBrief,
    index: int,
) -> str:
    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = (
        f"p.{source.page} - {source.matched_term}" if source else "source review required"
    )
    model_note = (
        "Local SVG draft"
        if visual.image_provider == "deterministic-svg"
        else f"Image model slot: {visual.image_provider}"
    )
    return f"""
<figure class="visual-example" aria-label="Visual worked example for {escape(topic.title)}">
  <figcaption>{render_icon("visual")}<span>Visual worked example / 图形例题</span></figcaption>
  <div class="visual-grid">
    {render_topic_visual_svg(visual, index)}
    <div class="visual-notes">
      <div class="visual-model">{escape(model_note)}</div>
      <div class="visual-source">Source anchor: {escape(source_label)}</div>
      <p class="visual-question">Use the diagram to explain or apply: <strong>{escape(visual.focus_point)}</strong>.</p>
      <ol>
        <li>Label the visual feature that matches the syllabus point.</li>
        <li>Connect the label to one precise syllabus term.</li>
        <li>Finish with a sentence that answers the command word.</li>
      </ol>
      <details class="visual-prompt">
        <summary>Image prompt / 生图提示词</summary>
        <p>{escape(visual.prompt)}</p>
      </details>
    </div>
  </div>
</figure>
"""


def render_topic_visual_svg(visual: VisualBrief, index: int) -> str:
    text = visual.visual_type.lower()
    if any(word in text for word in ["number line", "fraction", "ratio"]):
        return render_number_svg(index)
    if any(word in text for word in ["function graph", "equation-balance", "algebra"]):
        return render_algebra_svg(index)
    if any(word in text for word in ["statistics chart", "probability"]):
        return render_statistics_svg(index)
    if any(
        word in text
        for word in ["geometry diagram", "triangle", "trigonometry", "pythagoras", "transformation"]
    ):
        return render_triangle_svg(index)
    if any(word in text for word in ["rate", "equilibrium"]):
        return render_rate_svg(index)
    if any(word in text for word in ["energy", "exothermic", "endothermic"]):
        return render_energy_svg(index)
    if any(word in text for word in ["acid", "base", "salt", "ph"]):
        return render_ph_svg(index)
    if any(word in text for word in ["solid", "liquid", "particle", "atom"]):
        return render_particles_svg(index)
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        return render_bonding_svg(index)
    if any(word in text for word in ["organic", "hydrocarbon", "carbon"]):
        return render_organic_svg(index)
    if any(
        word in text
        for word in ["chemical analysis", "chromatography", "identification of common gases", "identification of ions"]
    ):
        return render_analysis_svg(index)
    return render_particles_svg(index)


def render_story_modes(topic: Topic, guide: TopicGuide) -> str:
    focus = topic.points[0] if topic.points else guide.topic_title
    return f"""
<div class="story-modes" aria-label="Narrative explanation styles for {escape(topic.title)}">
  <article>
    <h3>{render_icon("life")}<span>生活场景 / Life Scene</span></h3>
    <p>把 <strong>{escape(topic.title)}</strong> 当成身边的一件事来理解：先找现象，再用 <strong>{escape(focus)}</strong> 解释它为什么发生。</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>侦探推理 / Detective Mode</span></h3>
    <p>像破案一样答题：线索是题干数据，证据是 syllabus term，结论必须回到 command word。</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>动漫闯关感 / Anime Quest</span></h3>
    <p>把知识点拆成任务：解锁术语、避开常见陷阱、用一句检查句完成本关。默认使用原创冒险语气，不复刻具体 IP。</p>
  </article>
</div>
"""


def render_number_svg(index: int) -> str:
    ticks = []
    labels = []
    for value in range(-3, 4):
        x = 104 + (value + 3) * 56
        ticks.append(f'<path d="M{x} 170v16" stroke="#172033" stroke-width="3"/>')
        labels.append(
            f'<text x="{x - 7}" y="212" font-size="17" font-weight="800" fill="#172033">{value}</text>'
        )
    fraction_segments = []
    for number in range(4):
        color = "#1354a5" if number < 3 else "#edf4ff"
        fraction_segments.append(
            f'<rect x="{456 + number * 42}" y="112" width="42" height="56" fill="{color}" stroke="#172033" stroke-width="2"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Number line, fraction bar, and ratio diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="70" fill="#1354a5" font-size="23" font-weight="800">Number sense</text>
  <path d="M88 178h368" stroke="#172033" stroke-width="4" marker-end="url(#numarrow-{index})"/>
  <defs><marker id="numarrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {''.join(ticks)}
  {''.join(labels)}
  <circle cx="328" cy="178" r="10" fill="#b83246"/>
  <text x="92" y="246" font-size="16" fill="#5b677a">position helps compare negative numbers, decimals, and bounds</text>
  <text x="454" y="94" font-size="19" font-weight="800" fill="#b83246">3 / 4</text>
  {''.join(fraction_segments)}
  <text x="454" y="198" font-size="16" fill="#5b677a">fraction bar: part-whole</text>
  <rect x="456" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="522" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="596" y="238" width="58" height="40" rx="8" fill="#fff1f3" stroke="#b83246" stroke-width="3"/>
  <text x="462" y="304" font-size="18" font-weight="800" fill="#1f7a5b">2</text>
  <text x="598" y="304" font-size="18" font-weight="800" fill="#b83246">1</text>
  <text x="508" y="304" font-size="16" fill="#5b677a">ratio blocks</text>
</svg>
"""


def render_algebra_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Function graph and equation balance</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Algebra links symbols to shapes</text>
  <rect x="58" y="92" width="282" height="210" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M96 262V118M96 262h210" stroke="#172033" stroke-width="4"/>
  <path d="M100 244C130 228 160 204 190 174C226 138 256 126 302 126" fill="none" stroke="#b83246" stroke-width="5"/>
  <path d="M97 207h208M145 262V120M195 262V120M245 262V120" stroke="#d7deea" stroke-width="2"/>
  <text x="110" y="136" font-size="18" font-weight="800" fill="#b83246">graph of a rule</text>
  <text x="248" y="286" font-size="17" font-weight="800">x</text>
  <text x="76" y="130" font-size="17" font-weight="800">y</text>
  <rect x="396" y="104" width="260" height="178" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <path d="M526 138v88M448 226h156" stroke="#172033" stroke-width="5" stroke-linecap="round"/>
  <path d="M468 154l-42 72h84z" fill="#edf4ff" stroke="#1354a5" stroke-width="3"/>
  <path d="M584 154l-42 72h84z" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <text x="436" y="205" font-size="25" font-weight="800" fill="#1354a5">x + 3</text>
  <text x="564" y="205" font-size="25" font-weight="800" fill="#1f7a5b">7</text>
  <text x="430" y="82" font-size="18" font-weight="800" fill="#d99a24">equation balance</text>
  <text x="418" y="314" font-size="16" fill="#5b677a">transform both sides, then check the solution</text>
</svg>
"""


def render_statistics_svg(index: int) -> str:
    points = [(420, 230), (448, 202), (480, 214), (510, 172), (548, 156), (580, 126)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#b83246"/>' for x, y in points)
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Statistics chart and probability visual</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Data becomes evidence</text>
  <rect x="72" y="98" width="250" height="178" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M112 246V120M112 246h168" stroke="#172033" stroke-width="4"/>
  <rect x="132" y="198" width="26" height="48" fill="#1354a5"/>
  <rect x="174" y="166" width="26" height="80" fill="#1f7a5b"/>
  <rect x="216" y="134" width="26" height="112" fill="#d99a24"/>
  <text x="116" y="292" font-size="16" fill="#5b677a">chart: compare and describe</text>
  <rect x="376" y="98" width="260" height="178" rx="14" fill="#fffaf1" stroke="#d99a24"/>
  <path d="M420 246V120M420 246h178" stroke="#172033" stroke-width="4"/>
  {dots}
  <path d="M420 236L588 124" stroke="#1f7a5b" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="432" y="288" font-size="16" fill="#5b677a">scatter graph: trend and outliers</text>
  <path d="M116 318h74M190 318l58-34M190 318l58 34" stroke="#172033" stroke-width="3" fill="none"/>
  <text x="68" y="324" font-size="15" font-weight="800" fill="#b83246">probability branch</text>
</svg>
"""


def render_particles_svg(index: int) -> str:
    dots = []
    for row in range(3):
        for col in range(4):
            dots.append(f'<circle cx="{92 + col * 22}" cy="{102 + row * 22}" r="7" fill="#1354a5"/>')
    liquid = [
        '<circle cx="330" cy="118" r="8" fill="#1f7a5b"/>',
        '<circle cx="356" cy="132" r="8" fill="#1f7a5b"/>',
        '<circle cx="315" cy="150" r="8" fill="#1f7a5b"/>',
        '<circle cx="372" cy="164" r="8" fill="#1f7a5b"/>',
        '<circle cx="342" cy="176" r="8" fill="#1f7a5b"/>',
    ]
    gas = [
        '<circle cx="535" cy="92" r="8" fill="#b83246"/>',
        '<circle cx="606" cy="125" r="8" fill="#b83246"/>',
        '<circle cx="558" cy="180" r="8" fill="#b83246"/>',
    ]
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Particle model diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="48" y="58" fill="#b83246" font-size="20" font-weight="800">Particle model</text>
  <rect x="70" y="82" width="130" height="130" rx="14" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="290" y="82" width="130" height="130" rx="14" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="510" y="82" width="130" height="130" rx="14" fill="#fff1f3" stroke="#e5aab4"/>
  {''.join(dots)}
  {''.join(liquid)}
  {''.join(gas)}
  <path d="M220 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <path d="M440 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <defs><marker id="arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
  <text x="92" y="250" font-size="22" font-weight="800" fill="#1354a5">solid</text>
  <text x="322" y="250" font-size="22" font-weight="800" fill="#1f7a5b">liquid</text>
  <text x="552" y="250" font-size="22" font-weight="800" fill="#b83246">gas</text>
  <text x="70" y="292" font-size="16" fill="#5b677a">arrangement and movement explain state changes</text>
</svg>
"""


def render_triangle_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Right triangle diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M160 270h380L160 90z" fill="#ffffff" stroke="#111827" stroke-width="5"/>
  <path d="M160 244h26v26" fill="none" stroke="#111827" stroke-width="4"/>
  <text x="126" y="92" font-size="38" font-weight="800">A</text>
  <text x="550" y="292" font-size="38" font-weight="800">B</text>
  <text x="126" y="292" font-size="38" font-weight="800">C</text>
  <text x="304" y="308" font-size="30" font-weight="700">5 cm</text>
  <text x="72" y="190" font-size="30" font-weight="700">12 cm</text>
  <text x="360" y="174" font-size="30" font-weight="700">13 cm</text>
</svg>
"""


def render_rate_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Rate of reaction graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M95 275V70M95 275h520" stroke="#172033" stroke-width="4"/>
  <path d="M100 260C180 150 255 100 410 94C500 91 565 91 615 91" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M100 260C170 190 250 160 420 156C505 154 570 154 615 154" fill="none" stroke="#d99a24" stroke-width="6"/>
  <text x="118" y="66" font-size="18" font-weight="800" fill="#b83246">product formed</text>
  <text x="548" y="306" font-size="18" font-weight="800" fill="#1f7a5b">time</text>
  <text x="430" y="88" font-size="18" fill="#1354a5">faster rate</text>
  <text x="430" y="150" font-size="18" fill="#9b6a10">slower rate</text>
</svg>
"""


def render_energy_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Reaction energy profile</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M90 280V70M90 280h540" stroke="#172033" stroke-width="4"/>
  <path d="M120 245C230 245 235 88 350 88C465 88 470 185 600 185" fill="none" stroke="#b83246" stroke-width="6"/>
  <path d="M145 245h92M505 185h92" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M350 98v135" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="120" y="270" font-size="17" font-weight="800">reactants</text>
  <text x="500" y="210" font-size="17" font-weight="800">products</text>
  <text x="365" y="160" font-size="18" fill="#9b6a10">activation energy</text>
  <text x="110" y="62" font-size="18" font-weight="800" fill="#b83246">energy</text>
</svg>
"""


def render_ph_svg(index: int) -> str:
    segments = []
    colors = ["#b83246", "#d45c3f", "#d99a24", "#95b84a", "#1f7a5b", "#217c9b", "#1354a5"]
    for i, color in enumerate(colors):
        segments.append(f'<rect x="{84 + i * 76}" y="146" width="76" height="54" fill="{color}"/>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">pH scale and salt preparation</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="88" font-size="24" font-weight="800" fill="#1354a5">pH scale</text>
  {''.join(segments)}
  <text x="86" y="226" font-size="18" font-weight="800">0</text>
  <text x="300" y="226" font-size="18" font-weight="800">7</text>
  <text x="590" y="226" font-size="18" font-weight="800">14</text>
  <text x="94" y="130" font-size="18" fill="#b83246">acid</text>
  <text x="312" y="130" font-size="18" fill="#1f7a5b">neutral</text>
  <text x="548" y="130" font-size="18" fill="#1354a5">alkali</text>
</svg>
"""


def render_organic_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Hydrocarbon chain diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="82" font-size="24" font-weight="800" fill="#1354a5">hydrocarbon model</text>
  <path d="M178 178h100h100h100" stroke="#172033" stroke-width="5"/>
  <g fill="#1354a5" stroke="#172033" stroke-width="3">
    <circle cx="178" cy="178" r="32"/><circle cx="278" cy="178" r="32"/>
    <circle cx="378" cy="178" r="32"/><circle cx="478" cy="178" r="32"/>
  </g>
  <g fill="#ffffff" font-size="24" font-weight="800" text-anchor="middle">
    <text x="178" y="187">C</text><text x="278" y="187">C</text>
    <text x="378" y="187">C</text><text x="478" y="187">C</text>
  </g>
  <text x="160" y="272" font-size="18" fill="#5b677a">structure helps explain reactions and properties</text>
</svg>
"""


def render_analysis_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Chromatography diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="140" y="72" width="170" height="235" rx="18" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <path d="M170 250h110" stroke="#1354a5" stroke-width="4"/>
  <path d="M225 250V98" stroke="#172033" stroke-width="3"/>
  <circle cx="225" cy="223" r="11" fill="#b83246"/>
  <circle cx="225" cy="178" r="11" fill="#d99a24"/>
  <circle cx="225" cy="130" r="11" fill="#1f7a5b"/>
  <path d="M430 96h105M430 154h105M430 212h105" stroke="#d7deea" stroke-width="4"/>
  <text x="430" y="88" font-size="18" font-weight="800" fill="#1f7a5b">separated spots</text>
  <text x="430" y="246" font-size="18" fill="#5b677a">compare position and colour</text>
</svg>
"""


def render_bonding_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Bonding and structure diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="74" font-size="24" font-weight="800" fill="#1354a5">bonding model</text>
  <rect x="74" y="104" width="150" height="150" rx="16" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="285" y="104" width="150" height="150" rx="16" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="496" y="104" width="150" height="150" rx="16" fill="#fff1f3" stroke="#e5aab4"/>
  <g fill="#1354a5"><circle cx="124" cy="150" r="16"/><circle cx="174" cy="150" r="16"/><circle cx="124" cy="202" r="16"/><circle cx="174" cy="202" r="16"/></g>
  <g fill="#ffffff" font-size="15" font-weight="800" text-anchor="middle"><text x="124" y="155">+</text><text x="174" y="155">-</text><text x="124" y="207">-</text><text x="174" y="207">+</text></g>
  <g stroke="#172033" stroke-width="4"><path d="M332 178h56"/><path d="M360 150v56"/></g>
  <g fill="#1f7a5b"><circle cx="332" cy="178" r="18"/><circle cx="388" cy="178" r="18"/><circle cx="360" cy="150" r="18"/><circle cx="360" cy="206" r="18"/></g>
  <g fill="#b83246"><circle cx="542" cy="150" r="16"/><circle cx="600" cy="150" r="16"/><circle cx="542" cy="204" r="16"/><circle cx="600" cy="204" r="16"/></g>
  <path d="M526 176h90M571 132v92" stroke="#d99a24" stroke-width="3" stroke-dasharray="6 6"/>
  <text x="116" y="286" font-size="20" font-weight="800" fill="#1354a5">ionic</text>
  <text x="315" y="286" font-size="20" font-weight="800" fill="#1f7a5b">covalent</text>
  <text x="530" y="286" font-size="20" font-weight="800" fill="#b83246">metallic</text>
</svg>
"""


def render_practice(item: PracticeItem) -> str:
    frame = "".join(f"<li>{escape(step)}</li>" for step in item.answer_frame)
    solution = "".join(f"<li>{escape(step)}</li>" for step in item.public_solution_steps)
    checkpoints = "".join(f"<li>{escape(point)}</li>" for point in item.answer_checkpoints)
    source = render_source_snippets(item.source_snippets, compact=True)
    return f"""
<article class="practice">
  <h3>{render_icon("practice")}<span>{escape(item.topic_title)} - practice card / 练习卡</span></h3>
  <div class="practice-meta">
    <span>{render_icon("command")}Command: {escape(item.command_word)}</span>
    <span>{render_icon("level")}Difficulty: {escape(item.difficulty)}</span>
    <span>{render_icon("focus")}Focus: {escape(item.focus_point)}</span>
  </div>
  <p class="practice-question">{escape(item.question)}</p>
  <h4>{render_icon("frame")}Answer frame / 答题框架</h4>
  <ol>{frame}</ol>
  <h4>{render_icon("steps")}Public solution steps / 公开解题步骤</h4>
  <ol>{solution}</ol>
  <h4>{render_icon("check")}Answer checkpoints / 答案检查点</h4>
  <ul>{checkpoints}</ul>
  {source}
</article>
"""


def render_icon(name: str) -> str:
    paths = {
        "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
        "bridge": '<path d="M4 15c3-7 13-7 16 0"/><path d="M4 15h16"/><path d="M8 15v-3"/><path d="M16 15v-3"/>',
        "steps": '<path d="M5 18h4v-4h4v-4h4V6h2"/><path d="M5 18h14"/>',
        "alert": '<path d="M12 4 3 20h18L12 4z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
        "practice": '<path d="M6 4h9l3 3v13H6z"/><path d="M14 4v4h4"/><path d="M9 13h6"/><path d="M9 17h4"/>',
        "command": '<path d="M7 8h10"/><path d="M7 12h7"/><path d="M7 16h4"/>',
        "level": '<path d="M5 17h3v-5H5z"/><path d="M11 17h3V7h-3z"/><path d="M17 17h3V4h-3z"/>',
        "focus": '<circle cx="12" cy="12" r="7"/><path d="M12 9v3l2 2"/>',
        "frame": '<rect x="5" y="6" width="14" height="12" rx="2"/><path d="M8 10h8"/><path d="M8 14h6"/>',
        "check": '<path d="m5 12 4 4 10-10"/>',
        "visual": '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m7 17 4-4 3 3 2-2 2 3"/>',
        "life": '<path d="M4 12 12 5l8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-5h4v5"/>',
        "detective": '<circle cx="11" cy="11" r="5"/><path d="m15 15 5 5"/><path d="M8 11h6"/>',
        "quest": '<path d="M12 3 4 7v6c0 5 3.5 7.5 8 8 4.5-.5 8-3 8-8V7z"/><path d="M9 12l2 2 4-5"/>',
    }
    path = paths.get(name, paths["target"])
    return (
        '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{path}</svg>'
    )


def render_diagram_briefs(briefs: list[str]) -> str:
    items = "".join(f"<li>{escape(brief)}</li>" for brief in briefs[:12])
    return f"""
<section class="band">
  <h2>图文解释规划 / Diagram Plan</h2>
  <p>These diagram briefs are intentionally source-bounded. A future image or illustration adapter should render them without adding unsourced syllabus claims.</p>
  <ul>{items}</ul>
</section>
"""


def render_final_checklist(qualification: Qualification, practice_count: int) -> str:
    topics = len(qualification.topics)
    return f"""
<section class="band final">
  <h2>质量检查清单 / Quality Checklist</h2>
  <ul>
    <li>Every topic from the public syllabus summary appears in the guide: {topics} topics.</li>
    <li>Every generated practice item is an original frame, not copied from past papers: {practice_count} items.</li>
    <li>Before giving this to a child, a subject specialist should add or approve worked examples for each topic.</li>
    <li>Confirm the downloaded PDF hash and qualification version before each exam season.</li>
  </ul>
</section>
"""


def render_source_snippets(snippets: list[SourceSnippet], compact: bool = False) -> str:
    if not snippets:
        return "<p class=\"warning\">No page-level source snippet was matched for this section. Review manually.</p>"
    css_class = "source-snippets compact" if compact else "source-snippets"
    items = []
    for snippet in snippets:
        text = snippet.text
        if compact and len(text) > 220:
            text = f"{text[:220].rstrip()}..."
        items.append(
            "<li>"
            f"<strong>p.{snippet.page}</strong> "
            f"<span>{escape(snippet.matched_term)}</span>"
            f"<blockquote>{escape(text)}</blockquote>"
            "</li>"
        )
    return f"<div class=\"{css_class}\"><h3>Source check / 来源核对</h3><ul>{''.join(items)}</ul></div>"


def link_or_missing(value: str | None) -> str:
    if not value:
        return "<span class=\"warning\">missing</span>"
    return f"<a href=\"{escape(value)}\">{escape(value)}</a>"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def svg_multiline_text(
    value: str,
    x: int,
    y: int,
    max_chars: int,
    line_height: int,
    size: int = 12,
    weight: int = 700,
    fill: str = "#172033",
) -> str:
    lines = wrap_words(value, max_chars=max_chars)[:3]
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}">{"".join(tspans)}</text>'
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    words = value.replace("/", " / ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
    if current:
        lines.append(current)
    return lines or [value[:max_chars]]


def stylesheet() -> str:
    return """
:root {
  --ink: #172033;
  --muted: #5b677a;
  --paper: #fffaf1;
  --blue: #1354a5;
  --red: #b83246;
  --green: #1f7a5b;
  --gold: #d99a24;
  --line: #d7deea;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background: #eef2f7;
  font: 15px/1.65 "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
a { color: var(--blue); }
.cover {
  min-height: 92vh;
  padding: 54px 8vw;
  color: white;
  background:
    linear-gradient(90deg, #124f9b 0 72%, #b83246 72% 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-bottom: 12px solid var(--gold);
}
.kicker { color: #ffe4a9; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
h1 { max-width: 920px; font-size: 52px; line-height: 1.05; margin: 18px 0; letter-spacing: 0; }
.subtitle { max-width: 760px; font-size: 19px; color: #f7f1e6; }
.cover-grid { display: grid; grid-template-columns: repeat(3, minmax(140px, 1fr)); gap: 12px; max-width: 760px; margin-top: 30px; }
.cover-grid div { border: 1px solid rgba(255,255,255,.32); padding: 16px; background: rgba(255,255,255,.1); }
.cover-grid span { display: block; color: #ffe4a9; font-size: 12px; text-transform: uppercase; }
.cover-grid strong { display: block; font-size: 26px; margin-top: 4px; }
.band, .topic {
  margin: 0 auto;
  padding: 34px 8vw;
  background: white;
  border-bottom: 1px solid var(--line);
}
.source { background: var(--paper); }
.listing-note { padding: 10px 12px; background: #ffffff; border-left: 4px solid var(--gold); }
.language-policy { background: #f7fbff; }
.language-note { margin: -8px 0 16px; color: var(--muted); font-size: 13px; }
h2 { margin: 0 0 16px; font-size: 28px; line-height: 1.15; color: var(--blue); letter-spacing: 0; }
h3 { margin: 0 0 10px; font-size: 17px; color: var(--red); letter-spacing: 0; }
h4 { margin: 12px 0 6px; font-size: 14px; color: var(--blue); letter-spacing: 0; }
.icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  vertical-align: -4px;
  margin-right: 6px;
}
.guide-grid h3,
.practice h3,
.practice h4,
.story-modes h3,
.visual-example figcaption {
  display: flex;
  align-items: center;
  gap: 6px;
}
ul, ol { padding-left: 22px; }
li { margin: 5px 0; }
code { overflow-wrap: anywhere; color: var(--red); }
table { width: 100%; border-collapse: collapse; margin-top: 14px; }
th { background: var(--blue); color: #fff; text-align: left; }
th, td { border: 1px solid var(--line); padding: 10px 12px; vertical-align: top; }
.assessment-grid, .topic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.assessment, .logic-card, .practice {
  border: 1px solid var(--line);
  border-left: 5px solid var(--gold);
  padding: 16px;
  background: #fbfcff;
}
.guide-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.guide-grid article {
  border: 1px solid var(--line);
  padding: 14px;
  background: white;
}
.essence { border-left: 5px solid var(--gold) !important; }
.analogy { border-left: 5px solid var(--green) !important; }
.worked { border-left: 5px solid var(--blue) !important; }
.pitfall { border-left: 5px solid var(--red) !important; }
.topic:nth-of-type(odd) { background: #fbfcff; }
.practice-block { margin-top: 16px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.practice-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }
.practice-meta span {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  background: #edf4ff;
  color: var(--blue);
  font-size: 12px;
  font-weight: 800;
}
.practice-question { font-weight: 700; }
.visual-example {
  margin: 18px 0 0;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--red);
}
.visual-example figcaption {
  margin-bottom: 12px;
  color: var(--red);
  font-weight: 800;
}
.visual-grid {
  display: grid;
  grid-template-columns: minmax(0, .58fr) minmax(240px, .42fr);
  gap: 16px;
  align-items: stretch;
}
.visual-svg {
  display: block;
  width: 100%;
  height: auto;
}
.visual-notes {
  border: 1px solid var(--line);
  padding: 16px;
  background: #fbfcff;
}
.visual-model,
.visual-source {
  display: inline-block;
  margin: 0 6px 12px 0;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.visual-model { background: #edf4ff; color: var(--blue); }
.visual-source { background: #fff3d8; color: #8a5f11; }
.visual-question {
  margin: 0 0 10px;
  font-weight: 700;
}
.visual-prompt {
  margin-top: 12px;
  padding: 10px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.visual-prompt summary {
  cursor: pointer;
  color: var(--red);
  font-weight: 800;
}
.visual-prompt p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.story-modes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.story-modes article {
  border: 1px solid var(--line);
  padding: 14px;
  background: #ffffff;
}
.story-modes article:nth-child(1) { border-left: 5px solid var(--green); }
.story-modes article:nth-child(2) { border-left: 5px solid var(--blue); }
.story-modes article:nth-child(3) { border-left: 5px solid var(--gold); }
.story-modes p { margin: 0; }
.topic-diagram {
  margin: 16px 0 0;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--green);
}
.topic-diagram figcaption {
  margin-bottom: 10px;
  color: var(--green);
  font-weight: 800;
}
.topic-diagram svg {
  display: block;
  width: 100%;
  height: auto;
}
.source-snippets { margin-top: 14px; padding: 14px; background: #fffaf1; border: 1px solid #efd7a0; }
.source-snippets h3 { color: var(--green); }
.source-snippets blockquote { margin: 6px 0 8px; color: var(--muted); font-size: 13px; }
.source-snippets.compact { background: transparent; border: 0; padding: 0; }
.source-snippets.compact h3 { font-size: 13px; margin-top: 10px; }
.source-snippets.compact blockquote { display: none; }
.stage-list li { padding: 10px 12px; background: #f3f7fb; border-left: 4px solid var(--green); }
.warning { color: var(--red); font-weight: 700; }
.final { background: #f4fff9; }
@media (max-width: 760px) {
  h1 { font-size: 38px; }
  .cover-grid, .assessment-grid, .topic-grid, .practice-block, .guide-grid, .visual-grid, .story-modes { grid-template-columns: 1fr; }
}
@media print {
  body { background: white; }
  .cover { min-height: 270mm; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .band, .topic { break-inside: avoid; padding: 22px 10mm; }
  a { color: inherit; text-decoration: none; }
}
"""
