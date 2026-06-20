from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.localization import (
    zh_point_label,
    zh_point_labels,
    zh_topic_reference,
    zh_visual_trigger,
    zh_visual_type,
)
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile


def build_visual_brief(
    topic: Topic,
    guide: TopicGuide,
    run_options: GuideRunOptions,
    subject_area: str | None = None,
) -> VisualBrief | None:
    points = topic.points[:4] or [topic.title]
    focus = points[0]
    visual_type, complexity, trigger = choose_visual_type(topic, points, subject_area)
    if complexity == "text-ok":
        return None
    provider = choose_provider_for_visual(complexity, run_options)
    if run_options.output_language == "en":
        visible_focus = focus
        visible_points = points
        visible_visual_type = visual_type
        visible_trigger = trigger
        prompt = (
            f"Create a student-friendly International GCSE revision visual for '{topic.title}'. "
            f"Focus on the syllabus point '{focus}'. Visual type: {visual_type}. "
            "Combine a clear diagram or infographic with concise English labels. "
            "Use original educational styling, not copyrighted characters or copied exam-paper art. "
            "Do not add facts beyond these source syllabus points: "
            f"{'; '.join(points)}. Leave space for a short question and answer frame."
        )
    else:
        visible_focus = zh_point_label(focus)
        visible_points = zh_point_labels(points)
        visible_visual_type = zh_visual_type(visual_type)
        visible_trigger = zh_visual_trigger(trigger)
        prompt = (
            f"为“{zh_topic_reference(topic)}”制作一张适合学生复习的国际课程图文学习图。"
            f"聚焦：“{visible_focus}”。图形类型：{visible_visual_type}。"
            "画面需要把清晰图解或信息图与简短中文标签结合起来；公式、单位和必要符号保持准确。"
            "使用原创教育风格，不使用受版权保护的角色，也不要复制考试卷图片。"
            "不要添加超出这些来源大纲点的事实；官方英文来源仅用于结构化复核，不出现在学生可见标签中。"
            f"可见标签围绕：{'；'.join(visible_points)}。预留一个简短题目和答题框架的位置。"
        )
    return VisualBrief(
        topic_title=topic.title,
        focus_point=visible_focus,
        trigger=visible_trigger,
        visual_type=visible_visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )

def choose_visual_type(
    topic: Topic,
    points: list[str],
    subject_area: str | None = None,
) -> tuple[str, str, str]:
    text = f"{topic.title} {' '.join(points)}".lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    has = tokens.__contains__
    has_phrase = text.__contains__
    profile = resolve_subject_profile(subject_area, topic, text)

    if profile.example_domain == "accounting":
        if any(has(word) for word in ["source", "document", "documents", "journal", "ledger", "ledgers", "entry", "entries"]):
            return "source-document to book-of-prime-entry and ledger flow infographic", "infographic", "accounting records are clearer as a source-to-ledger flow"
        if any(has(word) for word in ["trial", "balance", "control", "reconciliation", "bank", "error", "errors", "suspense"]):
            return "verification and reconciliation workflow infographic", "infographic", "verification topics need step-by-step comparison and correction flow"
        if any(has(word) for word in ["depreciation", "receivables", "payables", "irrecoverable", "accruals", "prudence", "concepts"]):
            return "accounting adjustment and concept-effect infographic", "infographic", "adjustments need linked record, statement, and profit effects"
        if any(has(word) for word in ["statement", "statements", "profit", "position", "partnership", "company", "manufacturing", "non-profit"]):
            return "financial-statement layout and calculation infographic", "infographic", "financial statements need layout plus calculation path"
        if any(has(word) for word in ["ratio", "liquidity", "profitability", "analysis"]):
            return "ratio-analysis formula and interpretation infographic", "infographic", "ratios need formula, substitution, and interpretation together"
        return "accounting process infographic with records and statement effects", "infographic", "accounting ideas are clearer with documents, accounts, and statement effects linked"

    if profile.example_domain == "economics":
        if any(has(word) for word in ["demand", "supply", "market", "price", "equilibrium", "elasticity"]):
            return "demand-supply curve and market scenario infographic", "infographic", "market relationships need curve shifts plus context labels"
        if any(has(word) for word in ["factor", "factors", "land", "labour", "capital", "enterprise", "production"]):
            return "factors of production scenario infographic", "infographic", "production resources are clearer as a labelled real-world scenario"
        if any(has(word) for word in ["scarcity", "choice", "choices", "opportunity", "cost", "costs", "allocation"]):
            return "choice and opportunity-cost flow infographic", "infographic", "economic choice is clearer as a trade-off flow"
        if any(has(word) for word in ["sector", "sectors", "primary", "secondary", "tertiary"]):
            return "economic sectors production-chain infographic", "infographic", "sector classification works best as a chain from raw material to service"
        if any(has(word) for word in ["money", "bank", "financial", "interest"]):
            return "money and banking flow infographic", "infographic", "financial roles are clearer as flows between savers, banks, and borrowers"
        if any(has(word) for word in ["government", "inflation", "growth", "employment", "trade", "exchange", "imports", "exports"]):
            return "policy and trade cause-effect infographic", "infographic", "macroeconomic relationships need cause-effect arrows and trade-offs"
        if any(has(word) for word in ["business", "revenue", "profit", "profits", "cash"]):
            return "business case-study canvas with icons and flow arrows", "infographic", "business/accounting cases benefit from icon flow and statement layout"
        return "scenario infographic with curve or flow chart", "infographic", "economic relationships are clearer as curves, flows, or scenarios"

    if profile.example_domain == "chemistry":
        if any(has(word) for word in ["chromatography", "purity", "pure", "mixture", "mixtures", "separation"]):
            return "chromatography and purity lab-method infographic", "infographic", "separation methods and purity checks need a labelled apparatus/process visual"
        if any(has(word) for word in ["gas", "gases", "splint", "limewater", "ammonia", "oxygen", "hydrogen"]):
            return "common gas tests observation infographic", "infographic", "gas tests need apparatus, observation, and conclusion labels"
        if any(has(word) for word in ["solid", "liquid", "liquids", "particle", "particles", "atom", "atoms"]):
            return "particle model with labelled states", "svg-basic", "state changes are clearer with particle arrangement and movement"
        if any(has(word) for word in ["bond", "bonds", "bonding", "ionic", "covalent", "metallic", "structure", "structures"]):
            return "bonding and structure model", "infographic", "bonding and structure relationships need visual spatial explanation"
        if any(has(word) for word in ["acid", "acids", "base", "bases", "alkali", "alkalis", "salt", "salts", "ph"]):
            return "pH scale and preparation flow diagram", "svg-basic", "scales and preparation flow are clearer as diagrams"
        if any(has(word) for word in ["rate", "rates", "equilibrium", "haber"]):
            return "reaction-rate graph and particle explanation", "infographic", "rate and equilibrium need graph plus particle interpretation"
        if any(has(word) for word in ["energy", "exothermic", "endothermic"]):
            return "reaction energy profile diagram", "svg-basic", "energy profile curves are visual by nature"
        if any(has(word) for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude", "carboxylic"]):
            return "organic structure and reaction pathway infographic", "infographic", "organic structures and pathways need labelled visual representation"
        if any(has(word) for word in ["electrolysis", "reactivity", "mole", "moles", "molar", "concentration", "concentrations"]):
            return "chemistry calculation and process infographic", "infographic", "chemistry process and quantity topics need linked formula, particles, and observations"

    if profile.example_domain == "generic":
        if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
            return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
        return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

    if any(has(word) for word in ["set", "sets", "subset", "subsets", "venn", "union", "intersection"]):
        return "set notation and Venn diagram infographic", "infographic", "set notation needs Venn regions and symbol labels, not a generic statistics chart"
    if any(
        has(word)
        for word in [
            "number",
            "numbers",
            "fraction",
            "fractions",
            "percentage",
            "percentages",
            "decimal",
            "decimals",
            "ratio",
            "proportion",
        ]
    ):
        return "number line, fraction bar, and ratio visual", "svg-basic", "number work is clearer with position, part-whole, and proportion diagrams"

    if any(has(word) for word in ["matrix", "matrices", "vector", "vectors", "transformation", "transformations"]):
        return "transformation, matrix, or vector infographic", "infographic", "multi-step geometry movement and vector reasoning need a richer labelled visual"
    if any(has(word) for word in ["construction", "constructions", "locus", "loci", "bearing", "bearings"]):
        return "geometry construction or bearings infographic", "infographic", "construction and bearings diagrams need precise labels and step annotations"
    if any(has(word) for word in ["histogram", "histograms", "cumulative", "sampling", "population"]):
        return "statistics method infographic", "infographic", "statistical representations need the exact chart type instead of a generic SVG"
    if any(has(word) for word in ["calculus", "tangent", "gradient"]):
        return "calculus graph annotation infographic", "infographic", "calculus and gradient reasoning need carefully annotated graph features"

    if any(
        has(word)
        for word in [
            "algebra",
            "function",
            "functions",
            "equation",
            "equations",
            "inequality",
            "inequalities",
            "sequence",
            "sequences",
        ]
    ):
        return "function graph and equation-balance visual", "svg-basic", "algebra is clearer when symbols connect to graphs and transformations"
    if any(
        has(word)
        for word in [
            "triangle",
            "triangles",
            "angle",
            "angles",
            "pythagoras",
        ]
    ):
        return "simple labelled triangle or angle diagram", "svg-basic", "simple geometry can be drawn accurately with deterministic SVG"
    if any(has(word) for word in ["geometry", "geometric", "measure", "measures", "mensuration", "trigonometry", "circle", "circles", "volume", "surface"]):
        return "geometry or mensuration infographic", "infographic", "non-trivial geometry needs diagrams that match the exact shape and labels"
    if any(
        has(word)
        for word in [
            "probability",
            "statistics",
            "statistical",
            "chart",
            "charts",
            "scatter",
            "correlation",
            "distribution",
            "distributions",
        ]
    ):
        return "statistics chart and probability visual", "svg-basic", "statistics and probability are clearer with charts, tables, and chance diagrams"
    if has_phrase("distance-time") or any(has(word) for word in ["speed", "distance"]):
        return "distance-time graph visual", "svg-basic", "distance-time graphs can be drawn safely with deterministic axes and a labelled line"
    if any(has(word) for word in ["force", "forces", "motion"]):
        return "force and motion infographic", "infographic", "force and motion questions need context-specific arrows and labels"
    if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
        return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
    return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

def choose_provider_for_visual(complexity: str, run_options: GuideRunOptions) -> str:
    if complexity == "svg-basic":
        return "deterministic-svg"
    if run_options.image_provider in {"prompt-queue", "deterministic-svg"}:
        return "external-generation-required"
    if run_options.image_provider == "custom":
        return f"custom:{run_options.image_model or 'model-not-set'}"
    return run_options.image_provider
