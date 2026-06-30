from intl_exam_guide.auditing.content_quality import (
    student_visible_text_issues,
    topic_title_quality_issues,
)


def test_student_visible_text_rejects_generic_chinese_placeholders():
    text = "能解释：考点要求 1。不看笔记也能完成至少一道原创考试风格练习。"

    assert student_visible_text_issues(text, "zh-CN") == [
        "student-facing Chinese text contains generic placeholder: 考点要求 1",
        "student-facing Chinese text contains generic practice frame: 不看笔记也能完成至少一道原创考试风格练习",
    ]


def test_student_visible_text_rejects_chinese_core_topic_fallback():
    assert student_visible_text_issues("复习路线 本节核心主题 1", "zh-CN") == [
        "student-facing Chinese text contains generic placeholder: 本节核心主题 1"
    ]


def test_topic_title_quality_rejects_repeated_module_only_titles():
    titles = ["第 P1 节", "第 P1 节", "第 P1 节", "第 PP1 节"]

    assert topic_title_quality_issues(titles, "zh-CN") == [
        "student-facing topic titles are too repetitive: 2 unique titles for 4 topics",
        "student-facing topic title is module-only and not teachable: 第 P1 节",
        "student-facing topic title is module-only and not teachable: 第 PP1 节",
    ]
