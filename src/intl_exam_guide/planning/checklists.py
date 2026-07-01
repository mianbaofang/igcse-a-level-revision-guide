from __future__ import annotations

import re

from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import zh_topic_reference
from intl_exam_guide.planning.source_points import clean_source_point, is_syllabus_shell


def build_checklist(
    points: list[str],
    output_language: str,
    source_text: str | None = None,
    topic_title: str | None = None,
) -> list[str]:
    label = clean_label(points[0] if points else "this syllabus point")
    source_points = [clean_label(point) for point in points if clean_label(point)]
    primary_point = source_points[0] if source_points else label
    secondary_point = next((point for point in source_points[1:] if point != primary_point), "")
    context = " ".join([source_text or "", *points]).lower()
    unit_context = topic_context(topic_title or source_text or "", output_language)
    if output_language == "en":
        return [
            f"Core content in {unit_context}: {primary_point}.",
            relationship_sentence(context, label, secondary_point, output_language),
            boundary_sentence(context, label, output_language),
        ]
    return [
        f"核心内容：{unit_context} - {primary_point}。",
        relationship_sentence(context, label, secondary_point, output_language),
        boundary_sentence(context, label, output_language),
    ]


def clean_label(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", clean_source_point(value)).strip().rstrip(".。")
    return "" if is_syllabus_shell(cleaned) else cleaned


def topic_context(value: str, output_language: str) -> str:
    cleaned = clean_label(value)
    if not cleaned:
        return "this syllabus unit" if output_language == "en" else "本节"
    if output_language == "zh-CN":
        return zh_topic_reference(Topic(title=cleaned))
    return cleaned[:90]


def relationship_sentence(
    context: str,
    label: str,
    secondary_point: str,
    output_language: str,
) -> str:
    if output_language == "en":
        if secondary_point:
            return f"Relationship to understand: connect {label} with {secondary_point} without importing adjacent topics."
        if has_calculation_context(context):
            return f"Relationship to understand: translate the wording into the {label} quantity, formula, or graph relationship."
        return f"Relationship to understand: explain what {label} describes and why the source point treats it as a unit."
    if secondary_point:
        return f"需要说清的关系：把“{label}”与“{secondary_point}”连起来，但不引入相邻章节内容。"
    if has_calculation_context(context):
        return f"需要说清的关系：把题目文字翻译成“{label}”对应的量、公式或图像关系。"
    return f"需要说清的关系：解释“{label}”描述的对象、条件或边界，以及为什么它在本节单独成点。"


def has_calculation_context(context: str) -> bool:
    return any(
        marker in context
        for marker in (
            "calculate",
            "calculation",
            "equation",
            "formula",
            "graph",
            "gradient",
            "probability",
            "ratio",
            "rate",
            "solve",
        )
    )


def boundary_sentence(context: str, label: str, output_language: str) -> str:
    has_explicit_limit = any(
        marker in context
        for marker in (
            "restricted",
            "only",
            "will not",
            "not required",
            "not be required",
            "simple problems",
        )
    )
    if output_language == "en":
        if has_explicit_limit:
            return (
                "The boundary matters here: include the conditions named in the source point "
                "and leave out content it explicitly excludes."
            )
        return f"It is central because later examples first translate the question into the {label} relationship."
    if has_explicit_limit:
        return "边界也要清楚：只处理课纲写出的限制条件，明确排除或未要求的内容不展开。"
    return f"它之所以重要，是因为后面的例题要先把题目条件翻译成“{label}”对应的关系。"
