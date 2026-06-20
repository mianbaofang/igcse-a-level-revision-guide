from __future__ import annotations

import html

from intl_exam_guide.models import Qualification


def subject_display_name(qualification: Qualification) -> str:
    source = f"{qualification.subject_area or ''} {qualification.title}".lower()
    subject_map = [
        ("mathematics", "数学"),
        ("maths", "数学"),
        ("chemistry", "化学"),
        ("economics", "经济学"),
        ("accounting", "会计学"),
        ("business", "商务"),
        ("physics", "物理"),
        ("biology", "生物"),
        ("computer science", "计算机科学"),
        ("english", "英语"),
    ]
    for key, label in subject_map:
        if key in source:
            return label
    return "本课程"


def html_escape(value: str) -> str:
    return html.escape(value, quote=True)
