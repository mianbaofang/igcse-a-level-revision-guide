import os

from intl_exam_guide.models import AssessmentPaper, Qualification, SourceRecord, SourceSnippet, Topic
from intl_exam_guide.planning.guide_plan import (
    build_guide_plan,
    build_topic_guide,
    build_revision_stages,
    build_run_options,
    normalize_image_provider,
)


def sample_accounting_qualification() -> Qualification:
    return Qualification(
        title="International GCSE Accounting (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=["Example qualification."],
        topics=[
            Topic(
                title="2.1 - Source documents and ledgers",
                points=[
                    "Source documents include purchase invoices and sales invoices.",
                    "Ledger entries record the double entry effect of transactions.",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Source documents include purchase invoices and sales invoices.",
                        matched_term="Source documents",
                    )
                ],
            )
        ],
        assessments=[AssessmentPaper(title="Paper 1", details=["1 hour 30 minutes"])],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/accounting/",
            specification_url="https://example.test/accounting-spec.pdf",
        ),
        audience_note="Example only.",
    )


def test_build_guide_plan_creates_guides_practice_and_visual_briefs():
    plan = build_guide_plan(
        sample_accounting_qualification(),
        questions_per_topic=2,
        image_provider="prompt-queue",
        explanation_style="detective",
        output_language="en",
        requested_subject="accounting",
    )

    assert plan.run_options.requested_subject == "accounting"
    assert plan.run_options.image_provider == "prompt-queue"
    assert len(plan.topic_guides) == 1
    assert len(plan.practice_items) == 2
    assert len(plan.visual_briefs) == 1
    assert plan.visual_briefs[0].image_provider == "deterministic-svg"
    question = plan.practice_items[0].question.lower()
    assert "invoice" in question
    assert "source document" in question
    assert "accounting record" in question
    assert len({item.question for item in plan.practice_items}) == 2


def test_build_run_options_normalizes_invalid_choices_without_bilingual_mode():
    qualification = sample_accounting_qualification()

    options = build_run_options(
        qualification=qualification,
        requested_subject=None,
        image_provider="sensenova-u1-fast",
        explanation_style="unknown-style",
        output_language="fr",
        exam_year=None,
        image_model=None,
        image_endpoint_url=None,
        image_api_key_env=None,
    )

    assert options.requested_subject == qualification.title
    assert options.image_provider == "prompt-queue"
    assert options.explanation_style == "friendly"
    assert options.output_language == "en"


def test_custom_image_provider_requires_all_custom_fields_and_environment(monkeypatch):
    monkeypatch.delenv("SCHOOL_IMAGE_KEY", raising=False)

    assert (
        normalize_image_provider(
            "custom",
            "school-model",
            "https://images.example.test/v1/images/generations",
            "SCHOOL_IMAGE_KEY",
        )
        == "prompt-queue"
    )

    monkeypatch.setenv("SCHOOL_IMAGE_KEY", "test-value")

    assert (
        normalize_image_provider(
            "custom",
            "school-model",
            "https://images.example.test/v1/images/generations",
            "SCHOOL_IMAGE_KEY",
        )
        == "custom"
    )
    assert os.environ["SCHOOL_IMAGE_KEY"] == "test-value"


def test_chinese_revision_stages_are_readable_text():
    stages = build_revision_stages("international_as_a_level", "zh-CN")

    assert stages == [
        "第 1 阶段 - 单元地图：先分清 AS、A2 或模块单元，再做综合题。",
        "第 2 阶段 - 建构：把每个单元点整理成短讲解、一道应用题和一个易错点。",
        "第 3 阶段 - 测试：先按单元练，再把不同单元放在一起做综合练习。",
    ]
    assert not any(" / " in stage for stage in stages)


def test_chinese_concept_explanation_is_source_bound_not_subject_hardcoded():
    guide = build_topic_guide(
        Topic(
            title="2.3 - Market failure: External costs and benefits",
            points=[
                "External costs and benefits. Candidates should understand how third parties are affected."
            ],
        ),
        "international_gcse",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert len(guide.checklist) >= 3
    assert "概念草稿" not in checklist
    assert "核心内容" in checklist
    assert "需要说清的关系" in checklist
    assert "市场" in checklist or "External" not in checklist
    assert "本节核心主题" not in checklist
    assert "带情境或数据的小题" not in checklist
    assert "常见错误" not in checklist


def test_chinese_concept_explanation_avoids_math_template_for_accounting_topic():
    guide = build_topic_guide(
        Topic(
            title="3.1 - Accounting: Bank reconciliation",
            points=[
                "Bank reconciliation statements including unpresented cheques and outstanding lodgements."
            ],
        ),
        "international_gcse",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "银行对账" in checklist
    assert "二次方程" not in checklist
    assert "牛顿" not in checklist


def test_chinese_momentum_concept_explanation_is_not_collision_template():
    guide = build_topic_guide(
        Topic(
            title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): Concept of momentum",
            points=["Concept of momentum."],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "动量概念" in checklist or "动量" in checklist
    assert "碰前" not in checklist


def test_chinese_checklist_filters_untranslated_secondary_point_placeholders():
    guide = build_topic_guide(
        Topic(
            title="P1.1 - Algebra: Solution of linear and quadratic inequalities",
            points=[
                "Solution of linear and quadratic inequalities.",
                "eg 2 2xx + /greaterthanorequalangled6",
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    visible_text = " ".join([*guide.checklist, guide.diagram_brief])

    assert "一次与二次不等式求解" in visible_text
    assert "本节核心主题" not in visible_text


def test_chinese_concept_explanation_does_not_cross_wire_ambiguous_source_notes():
    guide = build_topic_guide(
        Topic(
            title="P1.3 - Differentiation: Applications of differentiation",
            points=[
                "Applications of differentiation to gradients, tangents and normals, "
                "maxima and minima and stationary points, increasing and decreasing functions.",
                "Questions will not be set requiring the determination of or knowledge of "
                "points of inflection.",
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "微分" in checklist
    assert "集合与韦恩图" not in checklist


def test_chinese_newton_laws_explanation_is_not_overwritten_by_resistive_forces():
    guide = build_topic_guide(
        Topic(
            title="M1.3 - Forces and Newton’s Laws: Newton’ s three laws of motion",
            points=[
                "Newton’ s three laws of motion. Restricted to dynamics in a straight line "
                "on the horizontal or motion vertically including resistive forces."
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "牛顿" in checklist
    assert "掌握：阻力" not in checklist


def test_chinese_concept_explanation_is_not_action_checklist():
    guide = build_topic_guide(
        Topic(
            title="P1.3 - Differentiation: The derivative of f (x) as the gradient of the tangent",
            points=["The derivative of f (x) as the gradient of the tangent."],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "概念草稿" not in checklist
    assert "导数" in checklist
    assert "核心内容" in checklist
    assert "需要说清的关系" in checklist
    assert "会识别" not in checklist
    assert "会操作" not in checklist
    assert "会检查" not in checklist
