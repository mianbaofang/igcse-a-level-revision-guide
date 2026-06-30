from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from html import escape as html_escape, unescape as html_unescape
import json
import os
from pathlib import Path
import re

from pypdf import PdfReader

from intl_exam_guide.auditing.content_quality import (
    student_visible_text_issues,
    topic_title_quality_issues,
)
from intl_exam_guide.auditing.concept_jobs import CONCEPT_REVIEW_FILE, reviewed_concept_titles
from intl_exam_guide.models import GuidePlan, PracticeItem, Topic, VisualBrief
from intl_exam_guide.planning.anti_ai_language import has_ai_language_smell
from intl_exam_guide.planning.guide_plan import is_scope_exclusion_topic
from intl_exam_guide.planning.localization import zh_teachable_topic_title, zh_topic_keyword_label
from intl_exam_guide.rendering.html import display_topic_titles
from intl_exam_guide.rendering.visual_assets import (
    PENDING_ASSET_STATUSES,
    has_renderable_infographic,
    has_renderable_svg_fallback,
    is_raster_asset,
    load_visual_manifest,
)


@dataclass
class ValidationIssue:
    severity: str
    message: str


BILINGUAL_LABEL_PATTERNS = [
    "Chinese / English",
    "中文 / English",
    "图文学习页 / Visual Guide",
    "复习路线 / Study Roadmap",
    "例题 / Worked Example",
]
BILINGUAL_SLASH_PATTERN = re.compile(
    r"(?:[\u4e00-\u9fff][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[A-Za-z]"
    r"|[A-Za-z][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[\u4e00-\u9fff])"
)
ENCODING_ARTIFACT_PATTERN = re.compile(r"\ufffd|\?{3,}")
SVG_REPETITION_MIN_FILES = 12
SVG_REPETITION_MAX_UNIQUE_RATIO = 0.6
SVG_REPETITION_MAX_REPEAT_RATIO = 0.25
SVG_REPETITION_MIN_REPEAT = 10
PDF_PAGE_HEADROOM = 24
PDF_MAX_PAGES_PER_TOPIC = 2.0
PDF_ABSOLUTE_MAX_PAGES = 260
PDF_MAX_MIB_HEADROOM = 24
PDF_MAX_MIB_PER_VISUAL = 0.75
PDF_ABSOLUTE_MAX_MIB = 120
IMAGE_PROMPT_PACKAGING_PATTERNS = [
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
    r"\bcourse\s+code\s*[·:,-]?\s*\d+\b",
    r"\bcode\s*[·:,-]?\s*\d+\b",
    r"课程代码\s*[·:：,-]?\s*\d+",
    r"国际课程",
    r"官方英文来源",
]
SVG_SAFE_VISUAL_TERMS = {
    "axis",
    "bar",
    "chart",
    "circle",
    "accounting",
    "coordinate",
    "curve",
    "data",
    "demand",
    "distance-time",
    "energy",
    "flow",
    "force",
    "fraction",
    "function",
    "geometry",
    "graph",
    "ledger",
    "line",
    "market",
    "mechanics",
    "motion",
    "number",
    "particle",
    "ph",
    "probability",
    "ratio",
    "reconciliation",
    "scatter",
    "statement",
    "statistics",
    "supply",
    "table",
    "tree",
    "triangle",
    "venn",
    "vector",
    "angle",
    "图",
    "坐标",
    "曲线",
    "数轴",
    "函数",
    "几何",
    "三角",
    "角",
    "圆",
    "统计",
    "概率",
    "表",
    "数据",
    "韦恩",
    "树",
    "力",
    "运动",
    "动量",
    "碰撞",
    "能量",
    "粒子",
    "比例",
}
ZH_FORBIDDEN_TEMPLATE_PHRASES = [
    "How to Study",
    "Study Roadmap",
    "One-Sentence Essence",
    "Everyday Analogy",
    "Worked Example",
    "Try First",
    "Solution",
    "Check",
    "Exam Pitfall",
    "Source anchor",
    "Concept Map",
    "Visual Worked Example",
    "Generated Infographic",
    "Infographic Queue",
    "Local SVG draft",
    "Why not SVG",
    "Prompt queue",
    "Output language: English",
    "官方大纲要求",
]


def validate_plan(
    plan: GuidePlan,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
    output_dir: Path | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_preflight_and_source(plan))
    issues.extend(validate_topic_coverage(plan))
    issues.extend(validate_guides(plan))
    issues.extend(validate_practice(plan))
    issues.extend(validate_visual_briefs(plan))
    issues.extend(validate_qualification_notes(plan))
    if html_path:
        issues.extend(validate_html_output(plan, html_path))
    if pdf_path:
        if not pdf_path.exists():
            issues.append(ValidationIssue("warning", f"PDF output is missing: {pdf_path}"))
        else:
            issues.extend(validate_pdf_output(plan, pdf_path))
    if output_dir:
        issues.extend(validate_output_package(plan, output_dir))
    return issues


def validate_preflight_and_source(plan: GuidePlan) -> list[ValidationIssue]:
    qualification = plan.qualification
    options = plan.run_options
    issues: list[ValidationIssue] = []

    if not options.requested_subject.strip():
        issues.append(ValidationIssue("error", "Missing preflight subject selection."))
    if options.explanation_style not in {"formal", "friendly", "life", "story", "detective", "adventure"}:
        issues.append(ValidationIssue("error", "Missing or unsupported explanation style selection."))
    if options.output_language not in {"en", "zh-CN"}:
        issues.append(ValidationIssue("error", "Missing or unsupported output language selection."))
    if options.image_provider not in {"prompt-queue", "deterministic-svg", "custom"}:
        issues.append(ValidationIssue("error", "Missing or unsupported image-provider selection."))
    if options.image_provider == "custom":
        issues.extend(validate_custom_image_provider(options))

    if not qualification.source.page_url:
        issues.append(ValidationIssue("error", "Missing source qualification page URL."))
    if not qualification.source.provider:
        issues.append(ValidationIssue("error", "Missing source provider name."))
    if not qualification.source.specification_url:
        issues.append(ValidationIssue("error", "Missing specification PDF URL."))
    if not qualification.source.specification_sha256:
        issues.append(ValidationIssue("warning", "Specification PDF hash was not recorded."))
    if not qualification.topics:
        issues.append(ValidationIssue("error", "No syllabus topics were extracted."))
    if qualification.source.specification_path and len(qualification.topics) < 6:
        issues.append(
            ValidationIssue(
                "error",
                f"Only {len(qualification.topics)} syllabus topics were extracted from a downloaded specification PDF.",
            )
        )
    if qualification.source.specification_path and any(
        topic.title.lower().startswith("content unit ") for topic in qualification.topics
    ):
        issues.append(
            ValidationIssue(
                "error",
                "Downloaded specification fell back to generic Content unit topics; "
                "the syllabus parser needs a more precise provider-specific match.",
            )
        )
    if (
        (qualification.source.provider == "cambridge" or qualification.provider == "cambridge")
        and qualification.source.syllabus_year_range
        and not qualification.source.selected_exam_year
    ):
        issues.append(
            ValidationIssue(
                "error",
                "Cambridge syllabus range is present but selected exam year was not recorded.",
            )
        )
    if not qualification.assessments:
        severity = "error" if qualification.source.specification_path else "warning"
        issues.append(ValidationIssue(severity, "No assessment papers were extracted."))
    if is_as_only_plan(plan):
        for paper in qualification.assessments:
            if is_a_level_only_title(paper.title):
                issues.append(
                    ValidationIssue(
                        "error",
                        f"AS-only guide includes an A-level assessment: {paper.title}",
                    )
                )
        for topic in qualification.topics:
            if is_a_level_only_title(topic.title):
                issues.append(
                    ValidationIssue(
                        "error",
                        f"AS-only guide includes an A-level topic: {topic.title}",
                    )
                )
    teachable_topics = handbook_topics(plan)
    if len(plan.practice_items) < len(teachable_topics):
        issues.append(ValidationIssue("warning", "Practice coverage is below one item per topic."))
    if len(plan.topic_guides) != len(teachable_topics):
        issues.append(ValidationIssue("error", "Topic guide coverage does not match topic count."))
    if not plan.visual_briefs:
        issues.append(ValidationIssue("warning", "No topics were selected for visual explanation."))
    return issues


def validate_custom_image_provider(options: object) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not getattr(options, "image_model", None):
        issues.append(ValidationIssue("error", "Custom image provider is missing a model name."))
    if not getattr(options, "image_endpoint_url", None):
        issues.append(ValidationIssue("error", "Custom image provider is missing an endpoint URL."))
    api_key_env = getattr(options, "image_api_key_env", None)
    if not api_key_env:
        issues.append(
            ValidationIssue(
                "error",
                "Custom image provider is missing an API-key environment variable name.",
            )
        )
    elif not os.environ.get(api_key_env):
        issues.append(
            ValidationIssue(
                "error",
                f"Custom image provider environment variable is not set: {api_key_env}",
            )
        )
    return issues


def handbook_topics(plan: GuidePlan) -> list[Topic]:
    return [topic for topic in plan.qualification.topics if not is_scope_exclusion_topic(topic)]


def validate_topic_coverage(plan: GuidePlan) -> list[ValidationIssue]:
    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    practice_topics = {item.topic_title for item in plan.practice_items}
    issues: list[ValidationIssue] = []
    for topic in handbook_topics(plan):
        if is_fragment_topic_title(topic):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Syllabus topic title looks like a parser fragment, not a teachable unit: {topic.title}",
                )
            )
        if topic.title not in guide_topics:
            issues.append(ValidationIssue("error", f"Missing authored guide block for topic: {topic.title}"))
        if topic.title not in practice_topics:
            issues.append(ValidationIssue("error", f"Missing practice item for topic: {topic.title}"))
        if not topic.points:
            issues.append(ValidationIssue("error", f"Syllabus topic has no extracted body points: {topic.title}"))
        if not topic.source_snippets:
            issues.append(ValidationIssue("warning", f"No PDF source snippet matched for topic: {topic.title}"))
        elif all(is_contents_or_index_snippet(snippet) for snippet in topic.source_snippets):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Topic source snippets look like contents/index pages, not syllabus body: {topic.title}",
                )
            )
    return issues


def validate_guides(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for guide in plan.topic_guides:
        required = [
            guide.essence,
            guide.analogy,
            guide.mini_worked_example,
            guide.pitfall,
            guide.diagram_brief,
        ]
        if any(not value.strip() for value in required):
            issues.append(ValidationIssue("error", f"Incomplete topic guide block: {guide.topic_title}"))
        if len(guide.worked_solution_steps) < 4:
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Worked example has fewer than 4 public steps: {guide.topic_title}",
                )
            )
        if len(guide.checklist) < 3:
            issues.append(ValidationIssue("warning", f"Checklist is too short: {guide.topic_title}"))
        if has_ai_language_smell(
            [
                guide.essence,
                guide.analogy,
                guide.mini_worked_example,
                guide.pitfall,
                guide.diagram_brief,
                *guide.worked_solution_steps,
                *guide.checklist,
            ],
            plan.run_options.output_language,
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Topic guide contains formulaic AI-style wording: {guide.topic_title}",
                )
            )
        if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
            [
                guide.essence,
                guide.analogy,
                guide.mini_worked_example,
                guide.pitfall,
                guide.diagram_brief,
                *guide.worked_solution_steps,
                *guide.checklist,
            ]
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Chinese topic guide contains generic syllabus placeholder text: {guide.topic_title}",
                )
            )
        if has_encoding_artifacts(
            [
                guide.essence,
                guide.analogy,
                guide.mini_worked_example,
                guide.pitfall,
                guide.diagram_brief,
                *guide.worked_solution_steps,
                *guide.checklist,
            ]
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Topic guide contains encoding replacement artifacts: {guide.topic_title}",
                )
            )
    issues.extend(validate_checklist_diversity(plan))
    return issues


def validate_checklist_diversity(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    topics_by_combo: dict[tuple[str, ...], list[str]] = {}
    for guide in plan.topic_guides:
        combo = tuple(item.strip() for item in guide.checklist[:3])
        if len(combo) == 3 and all(combo):
            topics_by_combo.setdefault(combo, []).append(guide.topic_title)

    exact_duplicates = [
        (combo, titles)
        for combo, titles in topics_by_combo.items()
        if len(titles) > 1
    ]
    if exact_duplicates:
        combo, titles = max(exact_duplicates, key=lambda item: len(item[1]))
        preview = " / ".join(combo)[:180]
        topic_preview = "; ".join(titles[:3])
        issues.append(
            ValidationIssue(
                "error",
                f"Checklist mastery requirements are duplicated across topics: {len(titles)} topics share "
                f"'{preview}' ({topic_preview}).",
            )
        )

    if len(plan.topic_guides) < 12:
        return issues
    combos = Counter({combo: len(titles) for combo, titles in topics_by_combo.items()})
    repeated = [
        (combo, count)
        for combo, count in combos.items()
        if combo and count > max(4, int(len(plan.topic_guides) * 0.12))
    ]
    if not repeated:
        return issues
    combo, count = max(repeated, key=lambda item: item[1])
    preview = " / ".join(combo)[:180]
    issues.append(
        ValidationIssue(
            "error",
            f"Checklist mastery requirements are too repetitive: {count} topics share '{preview}'.",
        )
    )
    return issues


def validate_practice(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for item in plan.practice_items:
        issues.extend(validate_practice_item(plan, item))
    for topic_title in duplicate_practice_question_topics(plan.practice_items):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice items repeat the same question for topic: {topic_title}",
            )
        )
    return issues


def validate_practice_item(plan: GuidePlan, item: PracticeItem) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    topic_title = getattr(item, "topic_title", "")
    if not item.command_word.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a command word: {topic_title}"))
    if not item.difficulty.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a difficulty: {topic_title}"))
    if not item.focus_point.strip():
        issues.append(ValidationIssue("error", f"Practice item is missing a focus point: {topic_title}"))
    if len(item.public_solution_steps) < 4:
        issues.append(ValidationIssue("error", f"Practice item has too few solution steps: {topic_title}"))
    if len(item.answer_checkpoints) < 3:
        issues.append(ValidationIssue("error", f"Practice item has too few answer checkpoints: {topic_title}"))
    if not item.source_points:
        issues.append(ValidationIssue("error", f"Practice item has no source points: {topic_title}"))
    if is_placeholder_practice_question(item.question):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice item is an authoring frame, not a concrete worked example: {topic_title}",
            )
        )
    if is_cross_subject_borrowed_practice(item.question, plan.qualification.subject_area):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice item appears to borrow a different subject template: {topic_title}",
            )
        )
    if has_ai_language_smell(
        [
            item.question,
            *item.answer_frame,
            *item.public_solution_steps,
            *item.answer_checkpoints,
        ],
        plan.run_options.output_language,
    ):
        issues.append(
            ValidationIssue(
                "warning",
                f"Practice item contains formulaic AI-style wording: {topic_title}",
            )
        )
    if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
        [
            item.question,
            item.command_word,
            item.focus_point,
            *item.public_solution_steps,
            *item.answer_checkpoints,
            *item.source_points,
        ]
    ):
        issues.append(
            ValidationIssue(
                "error",
                f"Chinese practice item contains generic syllabus placeholder text: {topic_title}",
            )
        )
    if has_encoding_artifacts(
        [
            item.question,
            item.command_word,
            item.focus_point,
            *item.answer_frame,
            *item.public_solution_steps,
            *item.answer_checkpoints,
            *item.source_points,
        ]
    ):
        issues.append(
            ValidationIssue(
                "error",
                f"Practice item contains encoding replacement artifacts: {topic_title}",
            )
        )
    return issues


def validate_visual_briefs(plan: GuidePlan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for brief in plan.visual_briefs:
        if not brief.focus_point.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing a focus point: {brief.topic_title}"))
        if not brief.visual_type.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing a visual type: {brief.topic_title}"))
        if not brief.trigger.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing the selection reason: {brief.topic_title}"))
        if not brief.image_provider.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing an image provider: {brief.topic_title}"))
        if not brief.prompt.strip():
            issues.append(ValidationIssue("error", f"Visual brief is missing an image prompt: {brief.topic_title}"))
        elif has_image_prompt_course_packaging(brief.prompt):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Visual image prompt includes board or course packaging: {brief.topic_title}",
                )
            )
        if plan.run_options.output_language == "zh-CN" and has_zh_placeholder_text(
            [brief.focus_point, brief.visual_type, brief.trigger, brief.prompt]
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Chinese visual brief contains generic syllabus placeholder text: {brief.topic_title}",
                )
            )
        if has_encoding_artifacts([brief.focus_point, brief.visual_type, brief.trigger, brief.prompt]):
            issues.append(
                ValidationIssue(
                    "error",
                    f"Visual brief contains encoding replacement artifacts: {brief.topic_title}",
                )
            )
        if brief.complexity == "svg-basic" and not is_svg_safe_visual_brief(brief):
            issues.append(
                ValidationIssue(
                    "error",
                    f"SVG visual brief is not in the SVG-safe scope: {brief.topic_title}",
                )
            )
    return issues


def has_image_prompt_course_packaging(prompt: str) -> bool:
    return any(
        re.search(pattern, prompt, flags=re.IGNORECASE)
        for pattern in IMAGE_PROMPT_PACKAGING_PATTERNS
    )


def has_encoding_artifacts(values: Sequence[str]) -> bool:
    return any(ENCODING_ARTIFACT_PATTERN.search(value) for value in values)


def is_svg_safe_visual_brief(brief: VisualBrief) -> bool:
    text = f"{brief.visual_type} {brief.trigger}".lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    for term in SVG_SAFE_VISUAL_TERMS:
        normalized = term.lower()
        if re.search(r"[\u4e00-\u9fff]", normalized):
            if normalized in text:
                return True
        elif " " in normalized or "-" in normalized:
            if normalized in text:
                return True
        elif normalized in tokens:
            return True
    return False


def validate_qualification_notes(plan: GuidePlan) -> list[ValidationIssue]:
    qualification = plan.qualification
    issues: list[ValidationIssue] = []
    if qualification.qualification_type == "international_gcse":
        if (
            qualification.source.listing_qualification_type
            and qualification.source.listing_qualification_type != "international_gcse"
        ):
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with International GCSE type."))
        if "international students" not in qualification.audience_note.lower():
            issues.append(
                ValidationIssue(
                    "warning",
                    "GCSE audience note does not explicitly mention international students.",
                )
            )
        if (
            "outside the uk" not in qualification.audience_note.lower()
            and "outside the united kingdom" not in qualification.audience_note.lower()
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "GCSE audience note does not explain that the course is for use outside the UK.",
                )
            )
        if "linear" not in " ".join([qualification.audience_note, *qualification.summary]).lower():
            issues.append(
                ValidationIssue("warning", "GCSE guide does not mention the linear qualification structure.")
            )
    if qualification.qualification_type == "international_as_a_level":
        if (
            qualification.source.listing_qualification_type
            and qualification.source.listing_qualification_type != "international_as_a_level"
        ):
            issues.append(ValidationIssue("error", "Source listing metadata conflicts with AS-A-level type."))
        if (
            (qualification.provider or qualification.source.provider) != "cambridge"
            and "modular" not in " ".join([qualification.audience_note, *qualification.summary]).lower()
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "AS-A-level guide does not mention the modular qualification structure.",
                )
            )
    return issues


def validate_html_output(plan: GuidePlan, html_path: Path) -> list[ValidationIssue]:
    if not html_path.exists():
        return [ValidationIssue("error", f"HTML output is missing: {html_path}")]

    html = html_path.read_text(encoding="utf-8", errors="replace")
    options = plan.run_options
    issues: list[ValidationIssue] = []
    if has_encoding_artifacts([html]):
        issues.append(ValidationIssue("error", "HTML output contains encoding replacement artifacts."))
    for message in student_visible_text_issues(html, options.output_language):
        issues.append(ValidationIssue("error", message))
    rendered_titles = rendered_topic_titles(html)
    for message in topic_title_quality_issues(rendered_titles, options.output_language):
        issues.append(ValidationIssue("error", message))
    for label in mixed_language_label_matches(html):
        issues.append(
            ValidationIssue(
                "error",
                f"HTML contains a bilingual mixed-language label: {label}",
            )
        )
    expected_markers = display_topic_titles(
        handbook_topics(plan),
        options.output_language,
        plan.topic_guides,
    )
    for marker in expected_markers:
        if marker not in html and html_escape(marker) not in html:
            issues.append(ValidationIssue("error", f"Topic missing from HTML: {marker}"))
    issues.extend(validate_html_language(options.output_language, html))
    issues.extend(validate_html_visual_and_diagram_blocks(plan, html))
    issues.extend(validate_html_topic_map_mastery(html, options.output_language))
    return issues


def validate_html_topic_map_mastery(html: str, language: str) -> list[ValidationIssue]:
    section_heading = "Study Roadmap" if language == "en" else "复习路线"
    section_match = re.search(
        rf"<section\b[^>]*>\s*<h2>{re.escape(section_heading)}</h2>(.*?)</section>",
        html,
        flags=re.S,
    )
    if not section_match:
        return []
    issues: list[ValidationIssue] = []
    cells_by_title: dict[str, list[str]] = {}
    cells_by_mastery: dict[str, list[str]] = {}
    for row in re.findall(r"<tr>(.*?)</tr>", section_match.group(1), flags=re.S):
        cells = [
            normalize_html_cell(cell)
            for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        ]
        if len(cells) < 3:
            continue
        title = cells[1]
        mastery = cells[2]
        if title:
            cells_by_title.setdefault(title, []).append(mastery)
        if mastery:
            cells_by_mastery.setdefault(mastery, []).append(title)
    duplicated_titles = [
        (title, mastery_values)
        for title, mastery_values in cells_by_title.items()
        if len(mastery_values) > 1
    ]
    if duplicated_titles:
        title, mastery_values = max(duplicated_titles, key=lambda item: len(item[1]))
        issues.append(
            ValidationIssue(
                "error",
                "Topic map knowledge-unit title is duplicated across topics: "
                f"{len(mastery_values)} rows share '{title}' ({'; '.join(mastery_values[:3])}).",
            )
        )
    duplicated = [
        (mastery, titles)
        for mastery, titles in cells_by_mastery.items()
        if len(titles) > 1
    ]
    if not duplicated:
        return issues
    mastery, titles = max(duplicated, key=lambda item: len(item[1]))
    issues.append(
        ValidationIssue(
            "error",
            "Topic map mastery summary is duplicated across topics: "
            f"{len(titles)} topics share '{mastery[:180]}' ({'; '.join(titles[:3])}).",
        )
    )
    return issues


def normalize_html_cell(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", html_unescape(text)).strip()


def rendered_topic_titles(html: str) -> list[str]:
    titles: list[str] = []
    topic_sections = re.findall(
        r'<section\b[^>]*class="[^"]*\btopic\b[^"]*"[^>]*>(.*?)</section>',
        html,
        flags=re.S,
    )
    for section in topic_sections:
        match = re.search(r"<h2[^>]*>(.*?)</h2>", section, flags=re.S)
        if not match:
            continue
        title = re.sub(r"<[^>]+>", "", match.group(1))
        title = re.sub(r"\s+", " ", title).strip()
        if title:
            titles.append(title)
    return titles


def validate_html_language(output_language: str, html: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if output_language == "en":
        if re.search(r"[\u4e00-\u9fff]", html):
            issues.append(
                ValidationIssue(
                    "error",
                    "English output contains Chinese characters in the student-facing HTML.",
                )
            )
        required_phrases = [
            "How to Study",
            "Study Roadmap",
            "One-Sentence Essence",
            "Method",
            "Worked Example",
            "Solution",
            "Check",
            "Exam Pitfall",
            "Source anchor",
        ]
    else:
        for phrase in ZH_FORBIDDEN_TEMPLATE_PHRASES:
            if phrase in html:
                issues.append(
                    ValidationIssue(
                        "error",
                        f"Chinese output contains an English template phrase: {phrase}",
                    )
                )
        required_phrases = [
            "怎么用这本手册",
            "复习路线",
            "一句话本质",
            "解题套路",
            "例题",
            "解题步骤",
            "检查答案",
            "考试陷阱",
            "来源依据",
        ]
    for phrase in required_phrases:
        if phrase not in html:
            issues.append(ValidationIssue("error", f"HTML missing required section phrase: {phrase}"))
    return issues


def validate_html_visual_and_diagram_blocks(plan: GuidePlan, html: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if plan.visual_briefs:
        visual_markers = (
            [
                "Visual Worked Example",
                "Infographic Queue",
                "Generated Infographic",
                "SVG Fallback - Review Needed",
            ]
            if plan.run_options.output_language == "en"
            else ["图形例题", "信息图生成队列", "已生成信息图", "SVG 兜底图 - 需要复核"]
        )
        if not any(marker in html for marker in visual_markers):
            issues.append(ValidationIssue("error", "HTML missing required visual explanation block."))
    return issues


def validate_output_package(plan: GuidePlan, output_dir: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sections_dir = output_dir / "sections"
    images_dir = output_dir / "images"
    concepts_dir = output_dir / "concepts"
    package_manifest = output_dir / "handbook-package.json"
    if not sections_dir.exists():
        issues.append(ValidationIssue("error", f"Sections directory is missing: {sections_dir}"))
    else:
        section_count = len(list(sections_dir.glob("*.txt")))
        if section_count < 5:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Sections directory has only {section_count} section files.",
                )
            )
    if not images_dir.exists():
        issues.append(ValidationIssue("error", f"Images directory is missing: {images_dir}"))
    elif plan.visual_briefs:
        issues.extend(validate_image_assets(plan, images_dir))
    if not (output_dir / "run-options.json").exists():
        issues.append(ValidationIssue("error", "Run options file is missing from output directory."))
    if not package_manifest.exists():
        issues.append(ValidationIssue("error", f"Handbook package manifest is missing: {package_manifest}"))
    review_path = concepts_dir / CONCEPT_REVIEW_FILE
    _concept_jobs, _reviewed_concepts, pending_concepts = concept_review_counts(plan, output_dir)
    if plan.topic_guides and not (concepts_dir / "concept_jobs.json").exists():
        issues.append(
            ValidationIssue(
                "warning",
                "Concept explanation jobs are missing. Rebuild the package so concepts/concept_jobs.json "
                "is available for the LLM/Agent concept-writing pass.",
            )
        )
    if pending_concepts:
        issues.append(
            ValidationIssue(
                "warning",
                f"{pending_concepts}/{len(plan.topic_guides)} topic concept explanations still need "
                f"LLM/Agent review. Write them from concepts/concept_jobs.json, save {review_path.name}, and import with "
                f"scripts/import_concept_explanations.py before final delivery.",
            )
        )
    return issues


def validate_pdf_output(plan: GuidePlan, pdf_path: Path) -> list[ValidationIssue]:
    summary = pdf_quality_summary(plan, pdf_path)
    if summary.get("read_error"):
        return [
            ValidationIssue(
                "error",
                f"PDF output could not be inspected: {summary['read_error']}",
            )
        ]

    page_count = summary_int(summary, "pdf_pages")
    max_pages = summary_int(summary, "pdf_max_recommended_pages")
    size_mib = summary_float(summary, "pdf_size_mib")
    max_mib = summary_float(summary, "pdf_max_recommended_mib")
    blank_text_pages = summary_int(summary, "pdf_blank_text_pages")
    blank_limit = max(2, int(page_count * 0.03))
    issues: list[ValidationIssue] = []
    if page_count <= 0:
        issues.append(ValidationIssue("error", f"PDF output has no pages: {pdf_path}"))
    if page_count > max_pages:
        issues.append(
            ValidationIssue(
                "error",
                f"PDF output has {page_count} pages, above the recommended maximum "
                f"of {max_pages} for {len(handbook_topics(plan))} handbook topics.",
            )
        )
    if max_mib and size_mib > max_mib:
        issues.append(
            ValidationIssue(
                "error",
                f"PDF output is {size_mib:.1f} MiB, above the recommended maximum "
                f"of {max_mib:.1f} MiB.",
            )
        )
    if blank_text_pages > blank_limit:
        issues.append(
            ValidationIssue(
                "error",
                f"PDF output has {blank_text_pages} pages with almost no extractable text.",
            )
        )
    return issues


def pdf_quality_summary(plan: GuidePlan, pdf_path: Path) -> dict[str, object]:
    try:
        reader = PdfReader(str(pdf_path))
        page_text_lengths: list[int] = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except (KeyError, ValueError, TypeError):
                text = ""
            page_text_lengths.append(len(text.strip()))
    except (OSError, ValueError, KeyError) as exc:
        return {"read_error": str(exc)}

    page_count = len(page_text_lengths)
    blank_text_pages = sum(1 for length in page_text_lengths if length < 20)
    max_pages = pdf_recommended_max_pages(plan)
    size_mib = pdf_path.stat().st_size / (1024 * 1024)
    max_mib = pdf_recommended_max_mib(plan)
    return {
        "pdf_pages": page_count,
        "pdf_max_recommended_pages": max_pages,
        "pdf_size_mib": round(size_mib, 2),
        "pdf_max_recommended_mib": round(max_mib, 2),
        "pdf_blank_text_pages": blank_text_pages,
        "pdf_average_text_chars": (
            int(sum(page_text_lengths) / page_count) if page_count else 0
        ),
    }


def pdf_recommended_max_pages(plan: GuidePlan) -> int:
    topic_count = max(1, len(handbook_topics(plan)))
    dynamic_limit = int(topic_count * PDF_MAX_PAGES_PER_TOPIC) + PDF_PAGE_HEADROOM
    return max(PDF_PAGE_HEADROOM, min(PDF_ABSOLUTE_MAX_PAGES, dynamic_limit))


def pdf_recommended_max_mib(plan: GuidePlan) -> float:
    visual_count = max(1, len(plan.visual_briefs))
    dynamic_limit = PDF_MAX_MIB_HEADROOM + visual_count * PDF_MAX_MIB_PER_VISUAL
    return min(PDF_ABSOLUTE_MAX_MIB, dynamic_limit)


def validate_image_assets(plan: GuidePlan, images_dir: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    svg_briefs = [brief for brief in plan.visual_briefs if brief.complexity == "svg-basic"]
    infographic_briefs = [brief for brief in plan.visual_briefs if brief.complexity == "infographic"]
    manifest_path = images_dir / "visual_manifest.json"
    manifest_entries = load_visual_manifest(images_dir)
    svg_safe_asset_count = count_renderable_svg_safe_assets(manifest_entries, images_dir)
    if svg_safe_asset_count < len(svg_briefs):
        issues.append(
            ValidationIssue(
                "error",
                f"Images directory has {svg_safe_asset_count} renderable assets for "
                f"{len(svg_briefs)} SVG-safe visual briefs.",
            )
        )
    if not manifest_path.exists():
        issues.append(ValidationIssue("error", "Visual manifest is missing from images directory."))
    for entry in manifest_entries:
        filename = entry.get("file")
        if filename and not (images_dir / str(filename)).exists():
            issues.append(
                ValidationIssue(
                    "error",
                    f"Visual manifest references a missing image file: {filename}",
                )
            )
    if infographic_briefs:
        issues.extend(validate_infographic_assets(infographic_briefs, manifest_entries, images_dir))
    issues.extend(validate_svg_repetition(images_dir))
    return issues


def count_renderable_svg_safe_assets(
    manifest_entries: list[dict[str, object]],
    images_dir: Path,
) -> int:
    count = 0
    for entry in manifest_entries:
        if str(entry.get("complexity")) != "svg-basic":
            continue
        filename = str(entry.get("file") or "")
        if not filename or not (images_dir / filename).exists():
            continue
        if filename.lower().endswith(".svg") or has_renderable_infographic(entry, images_dir):
            count += 1
    return count


def validate_infographic_assets(
    infographic_briefs: Sequence[VisualBrief],
    manifest_entries: list[dict[str, object]],
    images_dir: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    generated = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic" and has_renderable_infographic(entry, images_dir)
    )
    svg_fallbacks = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic" and has_renderable_svg_fallback(entry, images_dir)
    )
    pending_external_generation = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic"
        and str(entry.get("asset_status", "")).lower() in PENDING_ASSET_STATUSES
    )
    if pending_external_generation:
        fallback_note = (
            f"; {svg_fallbacks} SVG fallback assets were written for draft review"
            if svg_fallbacks
            else ""
        )
        issues.append(
            ValidationIssue(
                "warning",
                f"{pending_external_generation} infographic briefs are queued for external image generation or review"
                f"{fallback_note}. See images/infographic_jobs.md and import reviewed assets with "
                "scripts/import_infographic_assets.py.",
            )
        )
    selected_or_generated = len(infographic_briefs) - pending_external_generation
    if generated < selected_or_generated:
        issues.append(
            ValidationIssue(
                "warning",
                f"{generated}/{selected_or_generated} selected infographic briefs have generated raster assets.",
            )
        )
    return issues


def validate_svg_repetition(images_dir: Path) -> list[ValidationIssue]:
    summary = svg_repetition_summary(images_dir)
    total = summary_int(summary, "svg_files")
    if total < SVG_REPETITION_MIN_FILES:
        return []

    issues: list[ValidationIssue] = []
    unique_titles = summary_int(summary, "svg_unique_titles")
    max_title_repeats = summary_int(summary, "svg_max_title_repeats")
    if is_svg_repetition_problem(total, unique_titles, max_title_repeats):
        issues.append(
            ValidationIssue(
                "warning",
                "SVG visual titles are too repetitive: "
                f"{unique_titles}/{total} unique titles; {max_title_repeats} use "
                f'"{summary["svg_most_common_title"]}". '
                "Use topic-specific SVG titles or reviewed infographic assets before final delivery.",
            )
        )

    unique_structures = summary_int(summary, "svg_unique_structures")
    max_structure_repeats = summary_int(summary, "svg_max_structure_repeats")
    if is_svg_repetition_problem(total, unique_structures, max_structure_repeats):
        issues.append(
            ValidationIssue(
                "warning",
                "SVG visual structures are too repetitive: "
                f"{unique_structures}/{total} unique shape layouts; {max_structure_repeats} share one layout. "
                "Add subject/topic-specific vector templates or import reviewed infographic assets.",
            )
        )
    return issues


def is_svg_repetition_problem(total: int, unique_count: int, max_repeats: int) -> bool:
    if max_repeats / total > SVG_REPETITION_MAX_REPEAT_RATIO:
        return True
    if max_repeats >= SVG_REPETITION_MIN_REPEAT:
        return True
    unique_ratio = unique_count / total
    return unique_ratio < 0.35 and max_repeats >= max(5, int(total * 0.2))


def svg_repetition_summary(images_dir: Path) -> dict[str, object]:
    svg_paths = sorted(images_dir.glob("*.svg"))
    titles: list[str] = []
    structures: list[str] = []
    for path in svg_paths:
        svg = path.read_text(encoding="utf-8", errors="replace")
        titles.append(extract_svg_title(svg) or path.stem)
        structures.append(svg_structure_fingerprint(svg))

    title_counts = Counter(titles)
    structure_counts = Counter(structures)
    most_common_title, max_title_repeats = most_common_counter_item(title_counts)
    _most_common_structure, max_structure_repeats = most_common_counter_item(structure_counts)
    return {
        "svg_files": len(svg_paths),
        "svg_unique_titles": len(title_counts),
        "svg_max_title_repeats": max_title_repeats,
        "svg_most_common_title": most_common_title,
        "svg_unique_structures": len(structure_counts),
        "svg_max_structure_repeats": max_structure_repeats,
    }


def extract_svg_title(svg: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", svg, flags=re.I | re.S)
    if not match:
        return ""
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return html_unescape(title)


def svg_structure_fingerprint(svg: str) -> str:
    text = re.sub(r"<title\b[^>]*>.*?</title>", "", svg, flags=re.I | re.S)
    text = re.sub(r"<text\b[^>]*>.*?</text>", "<text/>", text, flags=re.I | re.S)
    text = re.sub(r"<tspan\b[^>]*>.*?</tspan>", "<tspan/>", text, flags=re.I | re.S)
    text = re.sub(r'\baria-labelledby="[^"]*"', 'aria-labelledby=""', text)
    text = re.sub(r"\baria-labelledby='[^']*'", "aria-labelledby=''", text)
    text = re.sub(r'\bid="[^"]*"', 'id=""', text)
    text = re.sub(r"\bid='[^']*'", "id=''", text)
    text = re.sub(r"url\(#.*?\)", "url(#id)", text)
    return re.sub(r"\s+", " ", text).strip()


def most_common_counter_item(counter: Counter[str]) -> tuple[str, int]:
    if not counter:
        return "", 0
    return counter.most_common(1)[0]


def is_placeholder_practice_question(question: str) -> bool:
    text = question.lower()
    return (
        ("how the syllabus idea" in text and "could be used in an exam question" in text)
        or "answer an original short exam-style question" in text
        or "identify the relevant evidence, choose the correct method or definition" in text
        or "完成一道原创练习" in question
        or "先找关键信息，再选择方法" in question
        or "围绕“考点要求" in question
    )


def is_as_only_plan(plan: GuidePlan) -> bool:
    return "level-scope:as" in getattr(plan.qualification, "route_tags", [])


def is_a_level_only_title(title: str) -> bool:
    lower = title.lower()
    return (
        lower.startswith("a-level ")
        or lower.startswith("international a-level ")
        or re.match(r"^(p2|s2|m2)\b", lower) is not None
        or re.search(r"\bunit (p2|s2|m2)\b", lower) is not None
    )


def is_fragment_topic_title(topic: object) -> bool:
    title = getattr(topic, "title", "").strip()
    points = [str(point).strip().lower() for point in getattr(topic, "points", [])]
    lower = title.lower()
    if re.search(r"\s-\s\d+$", title):
        return True
    if lower.endswith("students will be required to demonstrate"):
        return True
    if points and all(point in {"students will be required to demonstrate"} for point in points):
        return True
    return False


def has_zh_placeholder_text(values: list[str]) -> bool:
    placeholder_patterns = [
        r"官方大纲要求",
        r"本单元第\s*\d+\s*个细分要求",
        r"第\s*\d+\s*个细分要求",
        r"知识单元\s*\d+",
        r"知识点\s*\d+",
    ]
    return any(
        re.search(pattern, value)
        for value in values
        for pattern in placeholder_patterns
    )


def duplicate_practice_question_topics(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    questions_by_topic: dict[str, set[str]] = {}
    counts_by_topic: dict[str, int] = {}
    for item in items:
        topic_title = getattr(item, "topic_title", "")
        question = normalize_practice_question(getattr(item, "question", ""))
        if not topic_title or not question:
            continue
        questions_by_topic.setdefault(topic_title, set()).add(question)
        counts_by_topic[topic_title] = counts_by_topic.get(topic_title, 0) + 1
    return [
        topic_title
        for topic_title, count in counts_by_topic.items()
        if len(questions_by_topic.get(topic_title, set())) < count
    ]


def normalize_practice_question(question: str) -> str:
    text = re.sub(
        r"^(Case file: |Real-life prompt: |Warm-up prompt: |Exam-style prompt: "
        r"|Story prompt: |Checkpoint challenge: |案件线索：|生活场景题：|热身题："
        r"|考试题：|故事题：|闯关挑战：)",
        "",
        question,
    )
    return re.sub(r"\s+", " ", text).strip().lower()


def is_contents_or_index_snippet(snippet: object) -> bool:
    text = getattr(snippet, "text", "").lower()
    page = getattr(snippet, "page", 999)
    syllabus_body_markers = [
        "content additional information",
        "students should",
        "prepare and",
        "understand",
        "calculate",
        "explain",
    ]
    if any(marker in text for marker in syllabus_body_markers):
        return False
    contents_markers = [
        "contents",
        "specification at a glance",
        "scheme of assessment",
        "general administration",
    ]
    return page <= 3 or sum(marker in text for marker in contents_markers) >= 2


def is_cross_subject_borrowed_practice(question: str, subject_area: str | None) -> bool:
    area = (subject_area or "").lower()
    if any(term in area for term in ["math", "mathematics", "further mathematics"]):
        return False
    question_lower = question.lower()
    borrowed_math_markers = [
        "mean and range",
        "median and range",
        "right-angled triangle",
        "find the hypotenuse",
        "solve 3(",
        "nth term",
        "straight line y =",
        "drink is mixed using juice and water in the ratio",
    ]
    return any(marker in question_lower for marker in borrowed_math_markers)


def mixed_language_label_matches(html: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html)
    matches: list[str] = []
    for pattern in BILINGUAL_LABEL_PATTERNS:
        if pattern in html:
            matches.append(pattern)
    for match in BILINGUAL_SLASH_PATTERN.finditer(text):
        label = " ".join(match.group(0).split())
        if label not in matches:
            matches.append(label)
    return matches


def expected_topic_marker(topic_title: str, index: int, output_language: str) -> str:
    if output_language == "en":
        return topic_title
    return zh_teachable_topic_title(topic_title, index)


def localized_topic_marker(topic_title: str) -> str | None:
    label = zh_topic_keyword_label(topic_title)
    if label:
        return label
    if re.search(r"[\u4e00-\u9fff]", topic_title):
        return topic_title[:32]
    return None


def issues_to_dict(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [asdict(issue) for issue in issues]


def concept_review_counts(plan: GuidePlan, output_dir: Path) -> tuple[int, int, int]:
    concepts_dir = output_dir / "concepts"
    concept_jobs_path = concepts_dir / "concept_jobs.json"
    concept_jobs = 0
    if concept_jobs_path.exists():
        try:
            concept_jobs_data = json.loads(concept_jobs_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            concept_jobs_data = []
        if isinstance(concept_jobs_data, list):
            concept_jobs = len(concept_jobs_data)

    guide_titles = {guide.topic_title for guide in plan.topic_guides}
    reviewed_titles = reviewed_concept_titles(output_dir)
    reviewed_concept_explanations = len(guide_titles & reviewed_titles)
    pending_concept_explanations = max(0, len(plan.topic_guides) - reviewed_concept_explanations)
    return concept_jobs, reviewed_concept_explanations, pending_concept_explanations


def delivery_status_from_issues(
    issues: list[ValidationIssue],
    summary: dict[str, object],
) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "blocked_errors"
    if summary_int(summary, "pending_concept_explanations"):
        return "draft_needs_concept_review"
    if summary_int(summary, "pending_infographic_assets"):
        return "draft_needs_image_review"
    return "ready"


def summary_int(summary: dict[str, object], key: str, default: int = 0) -> int:
    value = summary.get(key, default)
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def summary_float(summary: dict[str, object], key: str, default: float = 0.0) -> float:
    value = summary.get(key, default)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def review_summary(
    plan: GuidePlan,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, object]:
    qualification = plan.qualification
    teachable_topics = handbook_topics(plan)
    topic_titles = {topic.title for topic in teachable_topics}
    practice_topics = {item.topic_title for item in plan.practice_items}
    guide_topics = {guide.topic_title for guide in plan.topic_guides}
    topics_with_source = sum(1 for topic in qualification.topics if topic.source_snippets)
    teachable_topics_with_source = sum(1 for topic in teachable_topics if topic.source_snippets)
    svg_safe_visuals = sum(1 for brief in plan.visual_briefs if brief.complexity == "svg-basic")
    infographic_visuals = sum(1 for brief in plan.visual_briefs if brief.complexity == "infographic")
    html = ""
    if html_path and html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
    section_files = 0
    image_files = 0
    generated_infographic_assets = 0
    svg_fallback_assets = 0
    pending_infographic_assets = 0
    concept_jobs = 0
    reviewed_concept_explanations = 0
    pending_concept_explanations = 0
    pdf_summary: dict[str, object] = {
        "pdf_pages": 0,
        "pdf_max_recommended_pages": pdf_recommended_max_pages(plan),
        "pdf_size_mib": 0.0,
        "pdf_max_recommended_mib": round(pdf_recommended_max_mib(plan), 2),
        "pdf_blank_text_pages": 0,
        "pdf_average_text_chars": 0,
    }
    svg_summary = {
        "svg_files": 0,
        "svg_unique_titles": 0,
        "svg_max_title_repeats": 0,
        "svg_most_common_title": "",
        "svg_unique_structures": 0,
        "svg_max_structure_repeats": 0,
    }
    has_visual_manifest = False
    has_package_manifest = False
    if output_dir:
        sections_dir = output_dir / "sections"
        images_dir = output_dir / "images"
        section_files = len(list(sections_dir.glob("*.txt"))) if sections_dir.exists() else 0
        if images_dir.exists():
            image_files = len(
                [
                    path
                    for path in images_dir.iterdir()
                    if path.suffix.lower() == ".svg" or is_raster_asset(path.name)
                ]
            )
            svg_summary = svg_repetition_summary(images_dir)
            manifest_entries = load_visual_manifest(images_dir)
            generated_infographic_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and has_renderable_infographic(entry, images_dir)
            )
            svg_fallback_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and has_renderable_svg_fallback(entry, images_dir)
            )
            pending_infographic_assets = sum(
                1
                for entry in manifest_entries
                if entry.get("complexity") == "infographic"
                and str(entry.get("asset_status", "")).lower() in PENDING_ASSET_STATUSES
            )
        has_visual_manifest = (images_dir / "visual_manifest.json").exists()
        has_package_manifest = (output_dir / "handbook-package.json").exists()
        concept_jobs, reviewed_concept_explanations, pending_concept_explanations = concept_review_counts(
            plan,
            output_dir,
        )
    if pdf_path and pdf_path.exists():
        pdf_summary = {**pdf_summary, **pdf_quality_summary(plan, pdf_path)}
    return {
        "requested_subject": plan.run_options.requested_subject,
        "provider": qualification.provider or qualification.source.provider,
        "source_provider": qualification.source.provider,
        "qualification_family": qualification.qualification_family or qualification.source.qualification_family,
        "specification_sha256": qualification.source.specification_sha256,
        "syllabus_year_range": qualification.source.syllabus_year_range,
        "selected_exam_year": qualification.selected_exam_year or qualification.source.selected_exam_year,
        "image_provider": plan.run_options.image_provider,
        "explanation_style": plan.run_options.explanation_style,
        "output_language": plan.run_options.output_language,
        "topics": len(teachable_topics),
        "source_topics": len(qualification.topics),
        "scope_exclusion_topics": len(qualification.topics) - len(teachable_topics),
        "assessments": len(qualification.assessments),
        "topic_guides": len(plan.topic_guides),
        "concept_jobs": concept_jobs,
        "reviewed_concept_explanations": reviewed_concept_explanations,
        "pending_concept_explanations": pending_concept_explanations,
        "visual_briefs": len(plan.visual_briefs),
        "svg_safe_visuals": svg_safe_visuals,
        "infographic_visuals": infographic_visuals,
        "generated_infographic_assets": generated_infographic_assets,
        "svg_fallback_assets": svg_fallback_assets,
        "pending_infographic_assets": pending_infographic_assets,
        "practice_cards": len(plan.practice_items),
        "topics_with_practice": len(topic_titles & practice_topics),
        "topics_with_guides": len(topic_titles & guide_topics),
        "topics_with_pdf_source_snippets": teachable_topics_with_source,
        "source_topics_with_pdf_source_snippets": topics_with_source,
        "topic_diagrams_in_html": html.count('class="topic-diagram"') if html else 0,
        "visual_examples_in_html": html.count('<figure class="visual-example') if html else 0,
        "has_html": bool(html_path and html_path.exists()),
        "has_pdf": bool(pdf_path and pdf_path.exists()),
        **pdf_summary,
        "section_files": section_files,
        "image_files": image_files,
        **svg_summary,
        "has_visual_manifest": has_visual_manifest,
        "has_package_manifest": has_package_manifest,
        "has_listing_metadata": bool(
            qualification.source.listing_qualification_type
            or qualification.source.listing_group_label
        ),
        "listing_group_label": qualification.source.listing_group_label,
        "audience_note_mentions_international_students": "international students"
        in qualification.audience_note.lower(),
        "audience_note_mentions_outside_uk": (
            "outside the uk" in qualification.audience_note.lower()
            or "outside the united kingdom" in qualification.audience_note.lower()
        ),
        "qualification_structure": qualification.qualification_type,
    }
