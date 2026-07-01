from __future__ import annotations

import re

from intl_exam_guide.models import Topic


SHELL_PATTERNS = [
    r"^candidates should have an understanding of:?$",
    r"^students should be able to:?$",
    r"^learners should be able to:?$",
    r"^[a-z]\)\s*understand the significance of the following accounting$",
    r"^[a-z]\)\s*(?:explain|describe|understand|state|identify|apply|prepare|calculate)\s+(?:the\s+)?(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)?(?:\s+of)?\s*:?$",
    r"^[a-z]\)\s*(?:explain|describe|understand|state|identify|apply|prepare|calculate)\s+(?:the\s+)?[a-z ]{0,25}:$",
]


def visible_source_points(topic: Topic, limit: int = 5) -> list[str]:
    """Return source points suitable for student-facing guide text."""

    cleaned = [clean_source_point(point) for point in topic.points]
    visible = merge_wrapped_source_points([point for point in cleaned if point and not is_syllabus_shell(point)])
    if visible:
        return visible[:limit]
    title = clean_topic_title(topic.title)
    return [title] if title else [topic.title]


def choose_focus_point(topic: Topic, number: int = 0) -> str:
    points = visible_source_points(topic)
    return points[number % len(points)]


def clean_source_point(point: str) -> str:
    text = " ".join(point.split()).strip()
    action_words = r"(?:understand|identify|explain|describe|state|apply|prepare|calculate|distinguish)"
    text = re.sub(r"^[a-z]\)\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+significance\s+of\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+causes\s+of\s+(.+)$", r"causes of \1", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of(?:\s+the)?\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+between\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r"\bStudents will be expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents may be required to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents should be familiar with\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bLearners should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bCandidates should have an understanding of\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    return text.rstrip(".")


def merge_wrapped_source_points(points: list[str]) -> list[str]:
    merged: list[str] = []
    for raw in points:
        point = raw.strip()
        if not point:
            continue
        if merged and should_merge_with_next(merged[-1], point):
            merged[-1] = f"{merged[-1]} {point}".strip()
        else:
            merged.append(point)
    return merged


def should_merge_with_next(previous: str, current: str) -> bool:
    prev = previous.strip().lower()
    cur = current.strip()
    if not prev or not cur:
        return False
    if prev.endswith((",", ";", ":")):
        return True
    if prev.split()[-1] in {"and", "or", "for", "of", "the", "in", "to", "with", "capital", "raw", "provision"}:
        return True
    if cur and cur[0].islower() and prev.endswith((" other", "non-current", "books", "open")):
        return True
    return False


def clean_topic_title(title: str) -> str:
    text = title.rsplit(":", 1)[-1]
    text = re.sub(r"^\s*[A-Z]{0,3}\d+(?:\.\d+)*\s*[-–]\s*", "", text).strip()
    return text or title.strip()


def is_syllabus_shell(point: str) -> bool:
    text = clean_source_point(point).strip(" .")
    if not text:
        return True
    lower = text.lower()
    if any(re.fullmatch(pattern, lower) for pattern in SHELL_PATTERNS):
        return True
    if lower in {
        "concepts:",
        "the following accounting",
        "the following accounting:",
    }:
        return True
    return False
