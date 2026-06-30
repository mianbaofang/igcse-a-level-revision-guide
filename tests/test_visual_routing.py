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
    assert brief.visual_type == "source-document to book-of-prime-entry and ledger flow diagram"
    assert brief.trigger == "accounting records need a precise source-to-ledger flow diagram"
    assert brief.image_provider == "deterministic-svg"


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
    assert brief.image_provider == "deterministic-svg"


def test_image_prompt_keeps_board_and_course_packaging_out_of_model_prompt():
    brief = build_visual_brief(
        Topic(
            title="OxfordAQA 9660 P1.3 - Trigonometry",
            points=[
                "OxfordAQA International AS Level students should understand "
                "sine, cosine and tangent functions",
            ],
        ),
        guide(),
        options(),
        "Mathematics",
    )

    assert brief is not None
    assert "Topic: mathematics:" in brief.prompt
    assert "sine, cosine and tangent functions" in brief.prompt
    assert "institutional logos" in brief.prompt
    for leaked in ["Oxford", "AQA", "International", "AS Level", "9660"]:
        assert leaked not in brief.prompt


def test_chinese_image_prompt_is_content_only_not_source_metadata():
    brief = build_visual_brief(
        Topic(
            title="OxfordAQA 9660 P1.3 - Trigonometry",
            points=[
                "OxfordAQA International AS unit P1 sine, cosine and tangent functions",
            ],
        ),
        guide(),
        options(language="zh-CN"),
        "Mathematics",
    )

    assert brief is not None
    assert "主题：数学：" in brief.prompt
    assert "机构标识" in brief.prompt
    assert "正弦" in brief.prompt
    for leaked in ["Oxford", "AQA", "International", "9660", "国际课程", "官方英文来源"]:
        assert leaked not in brief.prompt


def test_choose_provider_for_visual_covers_svg_custom_and_passthrough_routes():
    assert choose_provider_for_visual("svg-basic", options()) == "deterministic-svg"
    assert choose_provider_for_visual("infographic", options(provider="custom")) == "custom:reviewed-model"
    assert choose_provider_for_visual("infographic", options(provider="reviewed-assets")) == "reviewed-assets"


def test_math_visual_routing_does_not_treat_ordinary_set_as_venn():
    visual_type, complexity, trigger = route(
        "P1.4 - Integration: Questions involving regions partially above and below the x-axis",
        ["Questions involving regions partially above and below the x-axis will not be set."],
        "Mathematics",
    )

    assert "Venn" not in visual_type
    assert "set notation" not in visual_type
    assert complexity == "text-ok"
    assert "exclusions" in trigger


def test_accounting_visual_routes_cover_ratio_and_default_text_branch():
    ratio_type, ratio_complexity, _ = route("Ratio analysis", ["liquidity profitability"], "Accounting")
    default_type, default_complexity, _ = route("Ethics overview", ["stewardship and responsibility"], "Accounting")

    assert ratio_complexity == "text-ok"
    assert ratio_type == "text explanation with optional table"
    assert default_complexity == "text-ok"
    assert default_type == "text explanation with optional table"


def test_accounting_visual_routes_do_not_overdraw_adjustments_or_ratios():
    depreciation_type, depreciation_complexity, _ = route(
        "2.5 - Depreciation",
        ["Record accounting entries for depreciation and non-current assets."],
        "Accounting",
    )
    ratio_type, ratio_complexity, _ = route(
        "4.4 - The calculation and interpretation of accounting ratios",
        ["Calculate ratios using financial statements and interpret liquidity and profitability."],
        "Accounting",
    )

    assert depreciation_complexity == "text-ok"
    assert depreciation_type == "text explanation with optional table"
    assert ratio_complexity == "text-ok"
    assert ratio_type == "text explanation with optional table"


def test_economics_visual_routes_only_draw_named_curve_topics():
    visual_type, complexity, _ = route(
        "Market equilibrium",
        ["demand supply price equilibrium"],
        "Economics",
    )

    assert complexity == "svg-basic"
    assert "demand-supply" in visual_type

    for title, points in [
        ("Macroeconomics", ["government inflation trade exchange imports exports"]),
        ("Production resources", ["land labour capital enterprise factors"]),
        ("Business finance", ["business revenue profit cash"]),
    ]:
        visual_type, complexity, _ = route(title, points, "Economics")

        assert complexity == "text-ok"
        assert visual_type == "text explanation with optional mini case"

    default_type, default_complexity, _ = route(
        "Economics concepts",
        ["consumer welfare incentives"],
        "Economics",
    )
    assert default_complexity == "text-ok"
    assert default_type == "text explanation with optional mini case"


def test_economics_visual_routes_do_not_draw_every_market_word():
    text_only_cases = [
        (
            "Shifts of a PPC",
            [
                "causes and consequences of shifts of a PPC in terms of an economy's growth",
                "market forces of demand and supply, market equilibrium and disequilibrium",
            ],
        ),
        ("Price changes", ["causes and consequences of price changes"]),
        ("Calculation of PED", ["calculation of price elasticity of demand"]),
        ("Market failure", ["causes and consequences of market failure"]),
        ("Taxation", ["fiscal policy taxation and government aims"]),
        ("Causes of inflation", ["causes and consequences of inflation"]),
        ("Wage determination", ["reasons for differences in wages"]),
    ]

    for title, points in text_only_cases:
        visual_type, complexity, _ = route(title, points, "Economics")

        assert complexity == "text-ok"
        assert visual_type == "text explanation with optional mini case"


def test_chemistry_visual_routes_cover_structure_calculation_and_no_match_paths():
    bonding_type, bonding_complexity, _ = route("Bonding", ["ionic covalent metallic structure"], "Chemistry")
    calculation_type, calculation_complexity, _ = route("Electrolysis", ["electrolysis moles concentration"], "Chemistry")
    fallback_type, fallback_complexity, _ = route("Chemistry overview", ["safe laboratory conduct"], "Chemistry")

    assert bonding_complexity == "infographic"
    assert "bonding and structure" in bonding_type
    assert calculation_complexity == "infographic"
    assert "chemistry process" in calculation_type
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"


def test_chemistry_visual_routes_do_not_overmatch_generic_gas_or_structure_words():
    states_type, states_complexity, _ = route(
        "3.1.1 - Solids, liquids and gases",
        ["The three states of matter are solid, liquid and gas; particles are arranged differently."],
        "Chemistry",
    )
    bonding_type, bonding_complexity, _ = route(
        "3.2.1 - Chemical bonds",
        ["Ionic, covalent and metallic bonding and structure."],
        "Chemistry",
    )
    reactivity_type, reactivity_complexity, _ = route(
        "3.3.1.1 - The reactivity series",
        ["Reactivity of metals with water, oxygen and dilute acids."],
        "Chemistry",
    )

    assert states_complexity == "svg-basic"
    assert "particle model" in states_type
    assert bonding_complexity == "infographic"
    assert "bonding and structure" in bonding_type
    assert reactivity_complexity == "infographic"
    assert "chemistry process" in reactivity_type


def test_mathematics_visual_routes_cover_remaining_infographic_branches():
    cases = [
        ("Construction", ["locus bearings constructions"], "geometry construction"),
        ("Matrices", ["vectors matrices transformations"], "matrix"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "infographic"
        assert expected in visual_type


def test_mathematics_visual_routes_use_svg_only_for_exact_diagrams():
    cases = [
        ("Calculus", ["calculus tangent gradient"], "calculus graph"),
        ("Circle", ["equation of a circle"], "geometry"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "svg-basic"
        assert expected in visual_type


def test_as_math_symbolic_topics_do_not_get_unnecessary_visuals():
    cases = [
        (
            "P1.1 - Algebra: Use and manipulation of surds",
            ["Use and manipulation of surds. To include simplification and rationalisation of the denominator of a fraction."],
        ),
        (
            "P1.1 - Algebra: Application of the Factor Theorem",
            ["Application of the Factor Theorem and Remainder Theorem."],
        ),
        (
            "P1.5 - Sequences and series: Arithmetic series",
            ["Arithmetic series."],
        ),
    ]

    for title, points in cases:
        _, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "text-ok"


def test_as_math_trigonometry_is_not_misrouted_as_calculus_tangent():
    visual_type, complexity, trigger = route(
        "PP1.2 - Trigonometry: Sine, cosine and tangent functions",
        ["Sine, cosine and tangent functions."],
        "Mathematics",
    )

    assert complexity == "svg-basic"
    assert "trigonometry" in visual_type
    assert "calculus" not in visual_type
    assert "angle" in trigger or "curve" in trigger


def test_scope_exclusion_notes_are_text_only_visuals():
    visual_type, complexity, trigger = route(
        "M1.4 - Momentum: Knowledge of Newton's law of restitution is not required",
        ["Knowledge of Newton's law of restitution is not required."],
        "Mathematics",
    )

    assert complexity == "text-ok"
    assert visual_type == "scope note for text explanation"
    assert "exclusions" in trigger


def test_as_math_formula_topics_stay_text_only_after_visual_tightening():
    cases = [
        (
            "P1.2 - Coordinate geometry: Conditions for two straight lines to be parallel or perpendicular to each other",
            ["Conditions for two straight lines to be parallel or perpendicular to each other."],
        ),
        (
            "PP1.2 - Trigonometry: Degree and radian measure",
            ["Degree and radian measure."],
        ),
        (
            "S1.3 - Bernoulli and binomial distributions: Mean and variance of a Bernoulli",
            ["Mean and variance of a Bernoulli distribution."],
        ),
        (
            "S1.2 - Discrete random variables: The number of possible outcomes will be finite",
            ["The number of possible outcomes will be finite."],
        ),
        (
            "S1.1 - Further probability: Assigning probabilities to events using relative frequencies or equally likely outcomes",
            ["Assigning probabilities to events using relative frequencies or equally likely outcomes."],
        ),
        (
            "S1.3 - Bernoulli and binomial distributions: Calculation of probabilities using formula and tables",
            ["Calculation of probabilities using formula and tables."],
        ),
        (
            "M1.3 - Forces and Newton's Laws: Normal Reactions",
            ["Normal Reactions."],
        ),
        (
            "M1.4 - Momentum and impulse: Concept of momentum",
            ["Concept of momentum."],
        ),
    ]

    for title, points in cases:
        _, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "text-ok"


def test_as_math_keeps_svg_for_graphs_and_forces_but_queues_collisions():
    cases = [
        (
            "PP1.2 - Trigonometry: Their graphs, symmetries and periodicity",
            ["Their graphs, symmetries and periodicity."],
            "svg-basic",
        ),
        (
            "M1.3 - Forces and Newton's Laws: Newton's three laws of motion",
            ["Newton's three laws of motion."],
            "svg-basic",
        ),
        (
            "M1.4 - Momentum and impulse: Direct impact with a fixed surface",
            ["Direct impact with a fixed surface."],
            "infographic",
        ),
        (
            "M1.4 - Momentum and impulse: The principle of conservation of momentum applied to two particles",
            ["The principle of conservation of momentum applied to two particles."],
            "infographic",
        ),
    ]

    for title, points, expected_complexity in cases:
        visual_type, complexity, trigger = route(title, points, "Mathematics")

        assert complexity == expected_complexity
        if expected_complexity == "infographic":
            assert "collision" in visual_type
            assert "generic SVG" in trigger


def test_generic_and_unmatched_routes_cover_data_and_text_only_paths():
    data_type, data_complexity, _ = route("Data handling", ["tables graphs measurement"], None)
    maths_data_type, maths_data_complexity, _ = route("Data handling", ["data tables measurements"], "Mathematics")
    fallback_type, fallback_complexity, _ = route("Creative portfolio", ["annotation process"], None)

    assert data_complexity == "svg-basic"
    assert data_type == "data table and graph interpretation visual"
    assert maths_data_complexity == "svg-basic"
    assert maths_data_type == "statistics chart visual"
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"
