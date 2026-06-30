from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.localization import (
    is_generic_zh_label,
    zh_point_label,
    zh_point_labels,
    zh_visual_trigger,
    zh_visual_type,
)
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile


SUBJECT_PROMPT_LABELS = {
    "accounting": ("accounting", "会计"),
    "biology": ("biology", "生物"),
    "chemistry": ("chemistry", "化学"),
    "economics": ("economics and business", "经济与商业"),
    "generic": ("this subject", "本学科"),
    "mathematics": ("mathematics", "数学"),
    "physics": ("physics", "物理"),
}

COURSE_PACKAGING_PATTERNS = [
    r"\b(?:Oxford\s*)?AQA\b",
    r"\bOxfordAQA\b",
    r"\bPearson\b",
    r"\bEdexcel\b",
    r"\bCambridge\b",
    r"\bCAIE\b",
    r"\bInternational\s+(?:GCSE|AS(?:[-\s]A[-\s]level|[-\s]A-level|\s+Level)?|A[-\s]level)\b",
    r"\bIGCSE\b",
    r"\bGCSE\b",
    r"\bAS[-\s]A[-\s]level\b",
    r"\bAS[-\s]A-level\b",
    r"\bAS\s+Level\b",
    r"\bA[-\s]level\b",
    r"\bA\s+Level\b",
    r"\bAS\s+unit\s+[A-Z]?\d+\b",
    r"\bcourse\s+code\s*[·:,-]?\s*\d+\b",
    r"\bcode\s*[·:,-]?\s*\d+\b",
    r"课程代码\s*[·:：,-]?\s*\d+",
    r"国际课程",
    r"官方英文来源",
    r"AS\s*[A-Z]?\d+",
]


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
    else:
        visible_focus = zh_point_label(focus)
        visible_points = [
            label for label in zh_point_labels(points) if not is_generic_zh_label(label)
        ]
        if not visible_points:
            visible_points = ["本节核心概念"]
        if is_generic_zh_label(visible_focus):
            visible_focus = visible_points[0]
        visible_visual_type = zh_visual_type(visual_type)
        visible_trigger = zh_visual_trigger(trigger)
    prompt = build_content_only_image_prompt(
        topic=topic,
        points=points,
        subject_area=subject_area,
        language=run_options.output_language,
        focus=visible_focus,
        visual_type=visible_visual_type,
        visible_points=visible_points,
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


def build_content_only_image_prompt(
    *,
    topic: Topic,
    points: list[str],
    subject_area: str | None,
    language: str,
    focus: str,
    visual_type: str,
    visible_points: list[str],
) -> str:
    """Build the prompt submitted to image models without board/source packaging."""

    subject = subject_prompt_label(subject_area, topic, points, language)
    clean_focus = clean_prompt_phrase(focus)
    clean_type = clean_prompt_phrase(visual_type)
    label_clause = prompt_label_clause(visible_points, language)
    if language == "en":
        return (
            "Create a concise educational visual. "
            f"Topic: {subject}: {clean_focus}. "
            f"Visual task: {clean_type}. "
            "Show only the diagrams, formulas, and short labels needed for this topic. "
            "Do not add institutional logos, course-cover headers, badges, footers, "
            f"or watermarks.{label_clause} Leave a small practice frame."
        )
    return (
        "制作一张中文学习信息图。"
        f"主题：{subject}：{clean_focus}。"
        f"图形任务：{clean_type}。"
        "只呈现该主题需要的图形、公式和简短中文标签；"
        "不要添加机构标识、课程封面、页眉页脚、徽章或水印。"
        f"{label_clause}留出一个简短练习框。"
    )


def subject_prompt_label(
    subject_area: str | None,
    topic: Topic,
    points: list[str],
    language: str,
) -> str:
    profile = resolve_subject_profile(subject_area, topic, f"{topic.title} {' '.join(points)}")
    index = 1 if language != "en" else 0
    return SUBJECT_PROMPT_LABELS[profile.example_domain][index]


def prompt_label_clause(visible_points: list[str], language: str) -> str:
    labels = [clean_prompt_phrase(label) for label in visible_points[:3]]
    labels = [label for label in labels if label and not is_generic_zh_label(label)]
    if not labels:
        return ""
    if language == "en":
        return f" Short labels may include: {', '.join(labels)}."
    return f"可用短标签：{'、'.join(labels)}。"


def clean_prompt_phrase(text: str) -> str:
    phrase = " ".join(text.split())
    phrase = re.sub(
        r"^(?:students|candidates|learners)\s+(?:should|must|are expected to)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    phrase = re.sub(
        r"^(?:be able to|understand|describe|explain|apply)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    for pattern in COURSE_PACKAGING_PATTERNS:
        phrase = re.sub(pattern, "", phrase, flags=re.IGNORECASE)
    phrase = re.sub(r"\s{2,}", " ", phrase).strip(" -:：,，;；")
    return phrase or "core concept visual"


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

    if is_scope_exclusion_text(text):
        return "scope note for text explanation", "text-ok", "exam-scope exclusions should be kept as notes, not visuals"

    if profile.example_domain == "accounting":
        title_text = topic.title.lower()
        ratio_terms = ["ratio", "liquidity", "profitability", "analysis"]
        statement_terms = [
            "statement",
            "statements",
            "profit",
            "position",
            "partnership",
            "company",
            "manufacturing",
            "non-profit",
        ]
        if any(has(word) for word in ["depreciation", "receivables", "payables", "irrecoverable", "accruals", "prudence", "concepts"]):
            return "text explanation with optional table", "text-ok", "adjustments are safer as source-bound explanation unless a statement layout is required"
        if any(term in title_text for term in ratio_terms) or (
            any(has(word) for word in ratio_terms)
            and not any(has(word) for word in statement_terms)
        ):
            return "text explanation with optional table", "text-ok", "ratio formula and interpretation topics are clearer as worked calculations"
        if any(
            has(word)
            for word in [
                "source",
                "document",
                "documents",
                "journal",
                "journals",
                "ledger",
                "ledgers",
                "book",
                "books",
                "prime",
                "original",
            ]
        ) or has_phrase("double entry"):
            return "source-document to book-of-prime-entry and ledger flow diagram", "svg-basic", "accounting records need a precise source-to-ledger flow diagram"
        if any(has(word) for word in ["trial", "balance", "control", "reconciliation", "bank", "error", "errors", "suspense"]):
            return "verification and reconciliation workflow diagram", "svg-basic", "verification topics need a precise comparison and correction flow"
        if any(has(word) for word in statement_terms):
            return "financial-statement layout and calculation diagram", "svg-basic", "financial statements need a precise layout that can be drawn as editable SVG"
        return "text explanation with optional table", "text-ok", "accounting point can be explained without a custom visual"

    if profile.example_domain == "economics":
        title_text = topic.title.lower()
        if any(
            marker in text
            for marker in [
                "ppc",
                "production possibility",
                "ped",
                "pes",
                "elasticity",
                "market failure",
                "government intervention",
                "taxation",
                "monetary policy",
                "supply-side policy",
                "economic growth",
                "recession",
                "inflation",
                "price changes",
                "wage determination",
                "differences in wages",
                "demand for factors",
            ]
        ):
            return "text explanation with optional mini case", "text-ok", "economic calculations, causes, and policies are clearer as source-bound text"
        if (
            any(
                phrase in title_text
                for phrase in [
                    "demand curve",
                    "supply curve",
                    "market equilibrium",
                    "market disequilibrium",
                    "foreign exchange rate",
                ]
            )
            or has_phrase("demand curve")
            or has_phrase("supply curve")
            or has_phrase("market equilibrium")
            or has_phrase("market disequilibrium")
            or has_phrase("foreign exchange rate")
        ):
            return "demand-supply curve and market diagram", "svg-basic", "market relationships need precise curve axes and labels"
        if "price mechanism" in title_text:
            return "text explanation with optional mini case", "text-ok", "price mechanism can be explained as coordinated incentives without a separate curve"
        if any(has(word) for word in ["factor", "factors", "land", "labour", "capital", "enterprise", "production"]):
            return "text explanation with optional mini case", "text-ok", "production factors can be classified in text without a custom image"
        if any(has(word) for word in ["scarcity", "choice", "choices", "opportunity", "cost", "costs", "allocation"]):
            return "text explanation with optional mini case", "text-ok", "economic choice can be explained as a source-bound trade-off sentence"
        if any(has(word) for word in ["sector", "sectors", "primary", "secondary", "tertiary"]):
            return "text explanation with optional mini case", "text-ok", "sector classification is usually clear as a short case list"
        if any(has(word) for word in ["money", "bank", "financial", "interest"]):
            return "text explanation with optional mini case", "text-ok", "financial roles can be explained without a custom image unless a flow is explicitly requested"
        if any(has(word) for word in ["government", "inflation", "growth", "employment", "trade", "exchange", "imports", "exports"]):
            return "text explanation with optional mini case", "text-ok", "macroeconomic trade-offs are safer as text unless a specific diagram is named"
        if any(has(word) for word in ["business", "revenue", "profit", "profits", "cash"]):
            return "text explanation with optional mini case", "text-ok", "business cases can be handled with source-bound text and calculations"
        return "text explanation with optional mini case", "text-ok", "economic point can be explained without a custom visual"

    if profile.example_domain == "chemistry":
        if any(has(word) for word in ["bond", "bonds", "bonding", "ionic", "covalent", "metallic", "structure", "structures"]):
            return "bonding and structure model", "infographic", "bonding and structure relationships need visual spatial explanation"
        if any(has(word) for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude", "carboxylic"]):
            return "organic structure and reaction pathway infographic", "infographic", "organic structures and pathways need labelled visual representation"
        if any(has(word) for word in ["electrolysis", "reactivity"]):
            return "chemistry process infographic", "infographic", "electrolysis and reactivity need linked apparatus, particles, and observations"
        if any(has(word) for word in ["chromatography", "purity", "pure", "mixture", "mixtures", "separation"]):
            return "chromatography and purity method diagram", "svg-basic", "separation methods need a precise labelled method diagram"
        if any(has(word) for word in ["solid", "liquid", "liquids", "particle", "particles", "atom", "atoms"]):
            return "particle model with labelled states", "svg-basic", "state changes are clearer with particle arrangement and movement"
        if (
            has_phrase("gas test")
            or has_phrase("gas tests")
            or any(has(word) for word in ["splint", "limewater", "ammonia", "oxygen", "hydrogen", "chlorine"])
        ):
            return "common gas tests observation chart", "svg-basic", "gas tests need a structured observation and conclusion chart"
        if any(has(word) for word in ["acid", "acids", "base", "bases", "alkali", "alkalis", "salt", "salts", "ph"]):
            return "pH scale and preparation flow diagram", "svg-basic", "scales and preparation flow are clearer as diagrams"
        if any(has(word) for word in ["rate", "rates", "equilibrium", "haber"]):
            return "reaction-rate graph and particle explanation", "svg-basic", "rate topics need a precise graph before any richer illustration"
        if any(has(word) for word in ["energy", "exothermic", "endothermic"]):
            return "reaction energy profile diagram", "svg-basic", "energy profile curves are visual by nature"
        if any(has(word) for word in ["mole", "moles", "molar", "concentration", "concentrations"]):
            return "text explanation with worked calculation", "text-ok", "quantity topics are clearer as worked calculations than as separate images"

    if profile.example_domain == "physics":
        if has_phrase("distance-time") or has_phrase("speed-time") or has_phrase("velocity-time"):
            return "distance-time motion graph visual", "svg-basic", "motion graphs need axes and labelled line segments"
        if any(has(word) for word in ["force", "forces", "newton", "acceleration", "motion"]):
            return "force and motion diagram", "svg-basic", "force questions need precise arrows and labels"
        if any(has(word) for word in ["circuit", "electricity", "current", "voltage"]):
            return "circuit and measurement infographic", "infographic", "circuits need component placement and measurement labels"
        return "text explanation with optional diagram", "text-ok", "physics point can be explained without a custom visual unless a graph, force diagram, or circuit is central"

    if profile.example_domain == "mathematics":
        if any(has(word) for word in ["surd", "surds", "rationalisation", "rationalization"]):
            return "text explanation with no custom visual", "text-ok", "surds are clearer as worked algebra steps than as a separate image"
        if has_phrase("laws of indices") or has_phrase("rational exponents"):
            return "text explanation with no custom visual", "text-ok", "index laws are clearer as worked algebra steps than as a separate image"
        if (
            has_phrase("number line")
            or has_phrase("fraction bar")
            or has_phrase("ratio diagram")
            or any(
                has(word)
                for word in [
                    "percentage",
                    "percentages",
                    "decimal",
                    "decimals",
                    "ratio",
                    "proportion",
                    "bounds",
                    "rounding",
                ]
            )
        ):
            return "number line, fraction bar, and ratio visual", "svg-basic", "number work is clearer with position, part-whole, and proportion diagrams"
        if has_phrase("number of possible outcomes will be finite") or (
            has_phrase("calculation of probabilities") and has("formula") and has("tables")
        ) or (
            has_phrase("assigning probabilities") and has_phrase("relative frequencies")
        ):
            return "text explanation with no custom visual", "text-ok", "probability formula and finite-outcome topics are clearer as worked calculations"
        if (
            has("venn")
            or has("subset")
            or has("subsets")
            or has("union")
            or has("complement")
            or has_phrase("set notation")
        ):
            return "set notation and Venn diagram", "svg-basic", "set notation needs regions and symbol labels"
        if any(has(word) for word in ["matrix", "matrices", "vector", "vectors", "transformation", "transformations"]):
            return "transformation, matrix, or vector infographic", "infographic", "multi-step geometry movement and vector reasoning need a richer labelled visual"
        if any(has(word) for word in ["construction", "constructions", "locus", "loci", "bearing", "bearings"]):
            return "geometry construction or bearings infographic", "infographic", "construction and bearings diagrams need precise labels and step annotations"
        if any(
            has(word)
            for word in [
                "histogram",
                "histograms",
                "cumulative",
                "scatter",
                "statistics",
                "statistical",
                "chart",
                "charts",
                "data",
                "table",
                "tables",
                "measurement",
                "measurements",
            ]
        ) or (
            has_phrase("probability distributions")
            and not any(has(word) for word in ["mean", "variance", "deductions", "conditions"])
        ) or (
            has_phrase("binomial distribution")
            and not any(has(word) for word in ["mean", "variance", "deductions", "conditions", "calculation"])
        ):
            return "statistics chart visual", "svg-basic", "statistical chart topics need the exact chart structure"
        if has_phrase("probability tree") or any(has(word) for word in ["tree", "venn"]):
            return "probability tree or Venn visual", "svg-basic", "probability diagrams need branches or regions"
        if any(has(word) for word in ["trigonometry", "trigonometric", "sine", "cosine", "radian", "radians"]):
            if not any(
                phrase in text
                for phrase in [
                    "sine and cosine rules",
                    "area of a triangle",
                    "sine, cosine and tangent functions",
                    "graphs, symmetries and periodicity",
                ]
            ):
                return "text explanation with no custom visual", "text-ok", "trigonometric formula topics can be taught with worked steps unless graph or triangle structure is central"
            return "trigonometry circle or graph visual", "svg-basic", "trigonometric ratios and graphs need angle or curve structure"
        if any(has(word) for word in ["tangent", "gradient", "area", "regions", "curve", "curves", "x-axis"]):
            return "calculus graph and area annotation", "svg-basic", "calculus graph reasoning needs annotated graph features"
        if has_phrase("conditions for two straight lines") or has_phrase("product of the gradients"):
            return "text explanation with no custom visual", "text-ok", "parallel and perpendicular gradient rules are clearer as short worked algebra steps"
        if has_phrase("using algebraic methods"):
            return "text explanation with no custom visual", "text-ok", "algebraic intersection methods are clearer as equation-solving steps"
        if any(has(word) for word in ["graph", "graphs", "sketch", "coordinate", "coordinates"]):
            return "function graph or coordinate visual", "svg-basic", "graphs and coordinate geometry are visual by nature"
        if has_phrase("translation of circles"):
            return "text explanation with no custom visual", "text-ok", "circle translations can be taught by coordinate changes without a separate image"
        if any(has(word) for word in ["circle", "circles", "triangle", "triangles", "angle", "angles", "pythagoras"]):
            return "simple labelled geometry diagram", "svg-basic", "geometry shape relationships need labels"
        if has_phrase("distance-time") or has_phrase("speed-time") or has_phrase("velocity-time"):
            return "motion graph visual", "svg-basic", "motion graphs need axes and labelled line segments"
        if any(has(word) for word in ["force", "forces", "newton"]):
            if any(
                phrase in text
                for phrase in [
                    "force of gravity",
                    "normal reactions",
                    "resistive forces",
                    "tensions in strings",
                    "thrusts in rods",
                ]
            ):
                return "text explanation with no custom visual", "text-ok", "individual force definitions can be taught with notation and worked examples"
            if not (has("newton") or has_phrase("connected particle")):
                return "text explanation with no custom visual", "text-ok", "individual force definitions can be taught with notation and worked examples"
            return "mechanics force or collision diagram", "svg-basic", "mechanics questions need arrows, bodies, or before-after states"
        if any(has(word) for word in ["momentum", "impulse", "collision", "collisions"]):
            if not (has("collision") or has("collisions") or has_phrase("conservation of momentum") or has_phrase("direct impact")):
                return "text explanation with no custom visual", "text-ok", "momentum and impulse definitions can be taught with equations unless before-after states are central"
            return "mechanics before-after collision infographic", "infographic", "collisions and momentum conservation need context-specific before-after states, not a generic SVG"
        return "text explanation with no custom visual", "text-ok", "symbolic mathematics can be taught with worked steps instead of a separate image"

    if profile.example_domain == "generic":
        if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
            return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
        return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

    if (
        has("venn")
        or has("sets")
        or has("subset")
        or has("subsets")
        or has("union")
        or has("complement")
        or has_phrase("set notation")
    ):
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
    if any(
        has(word)
        for word in [
            "calculus",
            "derivative",
            "differentiation",
            "integral",
            "integration",
            "tangent",
            "gradient",
            "area",
            "regions",
            "x-axis",
        ]
    ):
        return "calculus graph and area annotation infographic", "infographic", "calculus, area, and graph reasoning need carefully annotated graph features"

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

def is_scope_exclusion_text(text: str) -> bool:
    text = text.rsplit(":", 1)[-1]
    exclusion_phrases = [
        "will not be set",
        "will not be assessed",
        "is not required",
        "are not required",
        "not required",
        "not be required",
        "not expected",
        "outside the scope",
    ]
    if not any(phrase in text for phrase in exclusion_phrases):
        return False
    learning_terms = [
        "restricted to",
        "include",
        "includes",
        "including",
        "to include",
        "use of",
        "application of",
        "applications of",
    ]
    return not any(term in text for term in learning_terms)

def choose_provider_for_visual(complexity: str, run_options: GuideRunOptions) -> str:
    if complexity == "svg-basic":
        return "deterministic-svg"
    if run_options.image_provider in {"prompt-queue", "deterministic-svg"}:
        return "external-generation-required"
    if run_options.image_provider == "custom":
        return f"custom:{run_options.image_model or 'model-not-set'}"
    return run_options.image_provider
