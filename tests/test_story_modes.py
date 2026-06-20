from intl_exam_guide.rendering.story_modes import chinese_story_lines, english_story_lines


def test_english_story_lines_are_topic_aware_for_accounting():
    lines = english_story_lines("Source documents", "purchase invoice", 1)
    combined = " ".join(lines).lower()

    assert "small shop" in combined
    assert "audit trail" in combined
    assert "source document" in combined


def test_chinese_story_lines_are_topic_aware_for_economics():
    lines = chinese_story_lines("Demand and supply", "市场价格", 2)
    combined = " ".join(lines)

    assert "商店排队" in combined
    assert "曲线" in combined
    assert "激励变化" in combined


def test_story_lines_fall_back_to_index_variants_without_cross_subject_terms():
    lines = english_story_lines("Portfolio annotation", "visual balance", 2)
    combined = " ".join(lines).lower()

    assert "school, shop, lab, or household decision" in combined
    assert "audit trail" not in combined
    assert "curve" not in combined
