from __future__ import annotations

import re

from intl_exam_guide.models import GuidePlan, PracticeItem, Qualification, Topic, TopicGuide, VisualBrief


def build_guide_plan(
    qualification: Qualification,
    questions_per_topic: int = 2,
    image_provider: str | None = None,
) -> GuidePlan:
    topic_guides: list[TopicGuide] = []
    practice_items: list[PracticeItem] = []
    visual_briefs: list[VisualBrief] = []
    diagram_briefs: list[str] = []

    for topic in qualification.topics:
        points = topic.points[:4]
        if not points:
            points = [topic.title]
        guide = build_topic_guide(topic, qualification.qualification_type)
        topic_guides.append(guide)
        visual = build_visual_brief(topic, guide, image_provider)
        if visual:
            visual_briefs.append(visual)
        diagram_briefs.append(guide.diagram_brief)
        for number in range(questions_per_topic):
            focus = points[number % len(points)]
            command_word = choose_command_word(number, qualification.qualification_type)
            difficulty = choose_difficulty(number)
            practice_items.append(
                PracticeItem(
                    topic_title=topic.title,
                    command_word=command_word,
                    difficulty=difficulty,
                    focus_point=focus,
                    question=(
                        f"{command_word.title()} how the syllabus idea '{focus}' could be used in "
                        f"an exam question on '{topic.title}'. Use a short scenario, one precise "
                        "syllabus term, and a final checking sentence."
                    ),
                    answer_frame=[
                        f"Line 1: answer the command word '{command_word}'.",
                        f"Line 2: state the relevant idea from the syllabus point '{focus}'.",
                        "Line 3: apply the idea to the given situation or data.",
                        "Line 4: check units, wording, and whether the answer addresses the command word.",
                    ],
                    public_solution_steps=[
                        f"Read the command word: {command_word}.",
                        f"Select the source-bound focus point: {focus}.",
                        "Write one sentence that defines or names the relevant idea.",
                        "Write one sentence that applies the idea to the scenario or data.",
                        "Finish with a checking sentence that matches the wording of the question.",
                    ],
                    answer_checkpoints=[
                        "Uses the command word directly.",
                        f"Mentions the focus point: {focus}.",
                        "Links the point to the scenario instead of only listing a memorised fact.",
                    ],
                    source_points=points,
                    source_snippets=topic.source_snippets[:2],
                )
            )

    revision_stages = build_revision_stages(qualification.qualification_type)
    return GuidePlan(
        qualification=qualification,
        topic_guides=topic_guides,
        practice_items=practice_items,
        visual_briefs=visual_briefs,
        diagram_briefs=diagram_briefs,
        revision_stages=revision_stages,
    )


def build_topic_guide(topic: Topic, qualification_type: str) -> TopicGuide:
    points = topic.points[:5] or [topic.title]
    primary = points[0]
    level_hint = "AS/A-level unit" if qualification_type == "international_as_a_level" else "GCSE topic"
    return TopicGuide(
        topic_title=topic.title,
        essence=(
            f"This {level_hint} is bounded by the official syllabus points around "
            f"'{primary}'. Start by turning each point into a definition, a process, "
            "or an application task."
        ),
        analogy=(
            f"Think of '{topic.title}' as a small toolkit: each syllabus point is one tool, "
            "and exam questions ask the student to choose the right tool for the command word."
        ),
        mini_worked_example=(
            f"Mini example: a question asks the student to explain or apply '{primary}' in a short "
            "scenario. The student should identify the command word, name the relevant idea, "
            "apply it to the scenario, and finish with a checking sentence."
        ),
        worked_solution_steps=[
            "Underline the command word: state, describe, explain, calculate, compare, evaluate, or suggest.",
            f"Select the matching syllabus point: {primary}.",
            "Use one precise term from the syllabus and connect it to the data or context in the question.",
            "Check that the final sentence answers the exact wording of the prompt.",
        ],
        pitfall=(
            "A common pitfall is writing a memorised fact without linking it to the command word. "
            "Train the student to ask: what action does this question want me to perform?"
        ),
        checklist=[
            *[f"Can explain: {point}" for point in points[:4]],
            "Can answer at least one original exam-style prompt without looking at notes.",
            "Can name one common mistake and how to avoid it.",
        ],
        diagram_brief=(
            f"Draw a clean concept map for '{topic.title}' with the central title in the middle, "
            f"branches for {', '.join(points[:4])}, and one short exam-action label on each branch."
        ),
        source_snippets=topic.source_snippets[:3],
    )


def build_visual_brief(
    topic: Topic,
    guide: TopicGuide,
    image_provider: str | None,
) -> VisualBrief | None:
    points = topic.points[:4] or [topic.title]
    focus = points[0]
    visual_type, complexity, trigger = choose_visual_type(topic, points)
    if complexity == "text-ok":
        return None
    provider = image_provider or choose_default_provider(complexity)
    prompt = (
        f"Create a student-friendly International GCSE revision visual for '{topic.title}'. "
        f"Focus on the syllabus point '{focus}'. Visual type: {visual_type}. "
        "Combine a clear diagram or infographic with short bilingual labels where useful. "
        "Use original educational styling, not copyrighted characters or copied exam-paper art. "
        "Do not add facts beyond these source syllabus points: "
        f"{'; '.join(points)}. Leave space for a short question and answer frame."
    )
    return VisualBrief(
        topic_title=topic.title,
        focus_point=focus,
        trigger=trigger,
        visual_type=visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def choose_visual_type(topic: Topic, points: list[str]) -> tuple[str, str, str]:
    text = f"{topic.title} {' '.join(points)}".lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    has = tokens.__contains__
    has_phrase = text.__contains__
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
            "geometry",
            "geometric",
            "measure",
            "measures",
            "mensuration",
            "trigonometry",
            "triangle",
            "triangles",
            "angle",
            "angles",
            "circle",
            "circles",
            "construction",
            "constructions",
            "transformation",
            "transformations",
            "vector",
            "vectors",
            "matrix",
            "matrices",
        ]
    ):
        return "geometry diagram with triangle, angle, and transformation cues", "svg-basic", "geometry questions need labelled shapes, lengths, angles, and movement"
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
    if any(has(word) for word in ["solid", "liquid", "liquids", "particle", "particles", "atom", "atoms"]):
        return "particle model with labelled states", "svg-basic", "state changes are clearer with particle arrangement and movement"
    if any(has(word) for word in ["bond", "bonds", "bonding", "ionic", "covalent", "metallic"]):
        return "bonding and structure model", "infographic", "bonding and structure relationships need visual spatial explanation"
    if any(has(word) for word in ["analysis", "chromatography", "identification"]):
        return "lab method or chromatography infographic", "infographic", "experimental methods and observations are easier as labelled process diagrams"
    if any(has(word) for word in ["acid", "acids", "base", "bases", "salt", "salts", "ph"]):
        return "pH scale and preparation flow diagram", "svg-basic", "scales and preparation flow are clearer as diagrams"
    if any(has(word) for word in ["rate", "rates", "equilibrium"]):
        return "reaction-rate graph and particle explanation", "infographic", "rate and equilibrium need graph plus particle interpretation"
    if any(has(word) for word in ["energy", "exothermic", "endothermic"]):
        return "reaction energy profile diagram", "svg-basic", "energy profile curves are visual by nature"
    if any(has(word) for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers"]):
        return "organic structure and reaction pathway infographic", "infographic", "organic structures and pathways need labelled visual representation"
    if any(has(word) for word in ["force", "forces", "motion", "speed", "distance"]) or has_phrase("distance-time"):
        return "motion graph and force diagram", "infographic", "force and motion questions need graph or arrow-based visual reasoning"
    if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
        return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
    if any(has(word) for word in ["market", "demand", "supply", "economics", "economic", "economy"]):
        return "scenario infographic with curve or flow chart", "infographic", "economic relationships are clearer as curves, flows, or scenarios"
    if any(has(word) for word in ["account", "accounting", "business", "cash", "profit", "profits"]):
        return "business case-study canvas with icons and flow arrows", "infographic", "business/accounting cases benefit from icon flow and statement layout"
    return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"


def choose_default_provider(complexity: str) -> str:
    if complexity == "svg-basic":
        return "deterministic-svg"
    return "ask-user: gpt-image-2 | qwen-image-pro | sensenova-u1-fast | custom"


def build_revision_stages(qualification_type: str) -> list[str]:
    if qualification_type == "international_as_a_level":
        return [
            "Stage 1 - Unit map: separate AS and A2 or modular units before mixing questions.",
            "Stage 2 - Build: turn each unit point into a short explanation, one application prompt, and one pitfall.",
            "Stage 3 - Test: practise by unit first, then combine units once command words and source boundaries are secure.",
        ]
    return [
        "Stage 1 - Linear map: learn the full-course topic boundaries before doing mixed papers.",
        "Stage 2 - Build: turn each syllabus point into a one-page note, one worked example, and one pitfall.",
        "Stage 3 - Test: practise mixed end-of-course questions, review errors, and update the checklist weekly.",
    ]


def choose_command_word(number: int, qualification_type: str) -> str:
    if qualification_type == "international_as_a_level":
        words = ["explain", "analyse", "compare", "evaluate"]
    else:
        words = ["state", "describe", "explain", "suggest"]
    return words[number % len(words)]


def choose_difficulty(number: int) -> str:
    return ["core", "standard", "stretch"][number % 3]
