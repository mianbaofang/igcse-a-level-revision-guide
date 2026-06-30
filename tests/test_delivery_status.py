import json

from intl_exam_guide.cli import main
from intl_exam_guide.validation.checks import ValidationIssue, delivery_status_from_issues


def test_delivery_status_blocks_errors_before_image_warnings():
    assert (
        delivery_status_from_issues(
            [ValidationIssue("error", "bad")],
            {"pending_infographic_assets": 10},
        )
        == "blocked_errors"
    )


def test_delivery_status_marks_pending_infographics_as_draft():
    assert delivery_status_from_issues([], {"pending_infographic_assets": 2}) == "draft_needs_image_review"


def test_delivery_status_marks_pending_concepts_before_images():
    assert (
        delivery_status_from_issues(
            [],
            {"pending_concept_explanations": 2, "pending_infographic_assets": 2},
        )
        == "draft_needs_concept_review"
    )


def test_delivery_status_ready_when_clean_and_no_pending_infographics():
    assert (
        delivery_status_from_issues(
            [],
            {"pending_concept_explanations": 0, "pending_infographic_assets": 0},
        )
        == "ready"
    )


def test_validation_json_contains_delivery_status(tmp_path):
    output_dir = tmp_path / "demo"

    result = main(
        [
            "demo",
            "--out",
            str(output_dir),
            "--image-provider",
            "deterministic-svg",
            "--explanation-style",
            "friendly",
            "--language",
            "en",
            "--skip-pdf",
        ]
    )

    assert result == 0
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["delivery_status"] == "draft_needs_concept_review"
    assert validation["review_summary"]["concept_jobs"] == validation["review_summary"]["topic_guides"]
    assert validation["review_summary"]["pending_concept_explanations"] == validation["review_summary"]["topic_guides"]
