from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide
from intl_exam_guide.planning.visual_routing import (
    build_visual_brief,
    choose_provider_for_visual,
    choose_visual_type,
)


def route(title: str, points: list[str], subject: str | None) -> tuple[str, str, str]:
    return choose_visual_type(Topic(title=title, points=points), points, subject)


def guide() -> TopicGuide:
    return TopicGuide(
        topic_title="Topic",
        essence="Explain the idea.",
        analogy="Use a simple analogy.",
        mini_worked_example="Apply it once.",
        worked_solution_steps=["Read", "Plan", "Answer", "Check"],
        pitfall="Avoid guessing.",
        checklist=["Explain", "Apply", "Check"],
        diagram_brief="Show the flow.",
    )


def options(language: str = "en", provider: str = "prompt-queue") -> GuideRunOptions:
    return GuideRunOptions(
        requested_subject="Accounting",
        image_provider=provider,
        explanation_style="friendly",
        output_language=language,
        image_model="reviewed-model",
    )


def test_build_visual_brief_returns_none_for_text_only_generic_topic():
    brief = build_visual_brief(
        Topic(title="Portfolio review", points=["creative annotation"]),
        guide(),
        options(),
        "Art and Design",
    )

    assert brief is None


def test_build_visual_brief_keeps_english_visible_fields():
    brief = build_visual_brief(
        Topic(title="3.1 Source documents", points=["source document ledger"]),
        guide(),
        options(),
        "Accounting",
    )

    assert brief is not None
    assert brief.focus_point == "source document ledger"
    assert brief.visual_type == "source-document to book-of-prime-entry and ledger flow infographic"
    assert brief.trigger == "accounting records are clearer as a source-to-ledger flow"
    assert brief.image_provider == "external-generation-required"


def test_build_visual_brief_localizes_chinese_visual_fields():
    brief = build_visual_brief(
        Topic(title="3.1 Source documents", points=["source document ledger"]),
        guide(),
        options(language="zh-CN"),
        "Accounting",
    )

    assert brief is not None
    assert brief.focus_point == "原始凭证与发票"
    assert brief.visual_type == "会计记录流程图"
    assert brief.trigger == "场景、因果和流程需要用箭头串起来。"
    assert brief.image_provider == "external-generation-required"


def test_choose_provider_for_visual_covers_svg_custom_and_passthrough_routes():
    assert choose_provider_for_visual("svg-basic", options()) == "deterministic-svg"
    assert choose_provider_for_visual("infographic", options(provider="custom")) == "custom:reviewed-model"
    assert choose_provider_for_visual("infographic", options(provider="reviewed-assets")) == "reviewed-assets"


def test_accounting_visual_routes_cover_ratio_and_default_process_branches():
    ratio_type, ratio_complexity, _ = route("Ratio analysis", ["liquidity profitability"], "Accounting")
    default_type, default_complexity, _ = route("Ethics overview", ["stewardship and responsibility"], "Accounting")

    assert ratio_complexity == "infographic"
    assert "ratio-analysis" in ratio_type
    assert default_complexity == "infographic"
    assert default_type == "accounting process infographic with records and statement effects"


def test_economics_visual_routes_cover_policy_business_and_default_branches():
    cases = [
        ("Macroeconomics", ["government inflation trade exchange imports exports"], "policy and trade"),
        ("Production resources", ["land labour capital enterprise factors"], "factors of production"),
        ("Business finance", ["business revenue profit cash"], "business case-study"),
        ("Economics concepts", ["consumer welfare incentives"], "scenario infographic"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Economics")

        assert complexity == "infographic"
        assert expected in visual_type


def test_chemistry_visual_routes_cover_structure_calculation_and_no_match_paths():
    bonding_type, bonding_complexity, _ = route("Bonding", ["ionic covalent metallic structure"], "Chemistry")
    calculation_type, calculation_complexity, _ = route("Electrolysis", ["electrolysis moles concentration"], "Chemistry")
    fallback_type, fallback_complexity, _ = route("Chemistry overview", ["safe laboratory conduct"], "Chemistry")

    assert bonding_complexity == "infographic"
    assert "bonding and structure" in bonding_type
    assert calculation_complexity == "infographic"
    assert "chemistry calculation" in calculation_type
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"


def test_mathematics_visual_routes_cover_remaining_infographic_branches():
    cases = [
        ("Construction", ["locus bearings constructions"], "geometry construction"),
        ("Calculus", ["calculus tangent gradient"], "calculus graph"),
        ("Mensuration", ["circle volume surface trigonometry"], "geometry or mensuration"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "infographic"
        assert expected in visual_type


def test_generic_and_unmatched_routes_cover_data_and_text_only_paths():
    data_type, data_complexity, _ = route("Data handling", ["tables graphs measurement"], None)
    maths_data_type, maths_data_complexity, _ = route("Data handling", ["data tables measurements"], "Mathematics")
    fallback_type, fallback_complexity, _ = route("Creative portfolio", ["annotation process"], None)

    assert data_complexity == "svg-basic"
    assert data_type == "data table and graph interpretation visual"
    assert maths_data_complexity == "svg-basic"
    assert maths_data_type == "data table and graph interpretation visual"
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"
