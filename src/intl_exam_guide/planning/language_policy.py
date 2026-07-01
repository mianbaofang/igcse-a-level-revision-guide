from __future__ import annotations

from dataclasses import replace

from intl_exam_guide.models import GuideRunOptions

LANGUAGE_CHOICES = {"en", "zh-CN", "zh-TW", "ja"}


def handbook_body_language(_selected_language: str) -> str:
    """Student handbook prose follows the exam language: English."""

    return "en"


def glossary_language(selected_language: str) -> str | None:
    selected = (selected_language or "en").strip()
    if selected == "en" or selected not in LANGUAGE_CHOICES:
        return None
    return selected


def language_mode_label(selected_language: str) -> str:
    support = glossary_language(selected_language)
    if not support:
        return "English"
    return f"English with {support} glossary"


def with_body_language_options(options: GuideRunOptions) -> GuideRunOptions:
    if options.output_language == "en":
        return options
    return replace(options, output_language="en")
