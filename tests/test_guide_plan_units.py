import os

from intl_exam_guide.models import AssessmentPaper, Qualification, SourceRecord, SourceSnippet, Topic
from intl_exam_guide.planning.guide_plan import (
    build_guide_plan,
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
    assert plan.visual_briefs[0].image_provider == "external-generation-required"
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
