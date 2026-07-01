from intl_exam_guide.models import Topic
from intl_exam_guide.subjects import (
    PRIORITY_SUBJECT_PACKS,
    build_subject_review_job,
    build_subject_writing_job,
    resolve_subject_pack,
)


def test_priority_subject_packs_cover_market_core_subjects():
    assert set(PRIORITY_SUBJECT_PACKS) == {
        "accounting",
        "biology",
        "chemistry",
        "economics",
        "mathematics",
        "physics",
    }


def test_resolve_subject_pack_uses_declared_subject_before_generic_fallback():
    pack = resolve_subject_pack(
        "Accounting",
        Topic(title="Bank reconciliation", points=["cash book and bank statement"]),
        "cash book bank statement reconciliation",
    )

    assert pack.name == "accounting"
    assert pack.priority is True
    assert "ledger or statement step" in pack.practice_focus


def test_subject_writing_and_review_jobs_define_non_template_contracts():
    pack = resolve_subject_pack(
        "Mathematics",
        Topic(title="P1.1 - Algebra: Surds", points=["Use and manipulate surds."]),
        "Use and manipulate surds.",
    )

    writing_job = build_subject_writing_job(
        job_id="concept_001",
        topic_title="P1.1 - Algebra: Surds",
        student_title="根式",
        source_points=["Use and manipulate surds."],
        output_language="zh-CN",
        pack=pack,
    )
    review_job = build_subject_review_job(
        writing_job_id="concept_001",
        topic_title="P1.1 - Algebra: Surds",
        output_language="zh-CN",
        pack=pack,
    )

    assert writing_job["contract_version"] == "v0.4-pedagogy-mvp"
    assert writing_job["subject_pack"] == "mathematics"
    assert "what relationship or boundary it describes" in writing_job["must_answer"]
    assert "borrow another subject's template" in writing_job["must_not"]
    assert review_job["id"] == "concept_001_review"
    assert "specific enough" in " ".join(review_job["questions"])
