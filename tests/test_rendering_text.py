from intl_exam_guide.models import Qualification, SourceRecord
from intl_exam_guide.rendering.text import html_escape, subject_display_name


def qualification(title: str, subject_area: str | None = None) -> Qualification:
    return Qualification(
        title=title,
        code=None,
        qualification_type="international_gcse",
        subject_area=subject_area,
        page_url="https://example.test/course",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(provider="synthetic", page_url="https://example.test/course"),
        audience_note="For learners.",
    )


def test_subject_display_name_maps_supported_subjects_from_area_or_title():
    expectations = [
        ("International GCSE Mathematics", None, "数学"),
        ("International GCSE Chemistry", None, "化学"),
        ("International GCSE Economics", None, "经济学"),
        ("International GCSE Accounting", None, "会计学"),
        ("International GCSE Business", None, "商务"),
        ("International GCSE Physics", None, "物理"),
        ("International GCSE Biology", None, "生物"),
        ("International GCSE Computer Science", None, "计算机科学"),
        ("International GCSE English", None, "英语"),
        ("International GCSE Any Title", "Maths", "数学"),
    ]

    for title, subject_area, expected in expectations:
        assert subject_display_name(qualification(title, subject_area)) == expected


def test_subject_display_name_falls_back_to_generic_course_label():
    assert subject_display_name(qualification("International GCSE Geography")) == "本课程"


def test_html_escape_quotes_ampersands_and_tags():
    assert html_escape('"A&B" <topic>') == "&quot;A&amp;B&quot; &lt;topic&gt;"
