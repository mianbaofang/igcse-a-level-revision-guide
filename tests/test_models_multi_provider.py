"""Synthetic model tests for multi-provider data fields (Phase 2).

These tests prove the upgraded models can store Cambridge syllabus year ranges
and Edexcel modular/unit structures, and that old JSON without the new fields
still loads via from_dict.
"""

from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceRecord,
    Topic,
)


def _base_qualification(**overrides) -> Qualification:
    defaults = dict(
        title="International GCSE Example (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Example",
        page_url="https://example.test/",
        summary=[],
        topics=[Topic(title="Atomic structure", points=["Atoms"])],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/",
            specification_url="https://example.test/spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students.",
    )
    defaults.update(overrides)
    return Qualification(**defaults)


def test_cambridge_year_range_roundtrip():
    qualification = _base_qualification(
        provider="cambridge",
        qualification_family="Cambridge IGCSE",
        selected_exam_year="2027",
        source=SourceRecord(
            provider="cambridge",
            page_url="https://www.cambridgeinternational.org/igcse-chemistry-0620/",
            specification_url="https://www.cambridgeinternational.org/Images/697205-2026-2028-syllabus.pdf",
            specification_sha256="deadbeef",
            syllabus_year_range="2026-2028",
            selected_exam_year="2027",
            first_teaching="September 2024",
            first_assessment="2026",
            issue_version="2026-2028 syllabus",
        ),
        route_tags=["Core", "Supplement"],
    )
    data = qualification.to_dict()
    assert data["source"]["syllabus_year_range"] == "2026-2028"
    assert data["source"]["selected_exam_year"] == "2027"
    assert data["selected_exam_year"] == "2027"
    assert data["route_tags"] == ["Core", "Supplement"]

    restored = Qualification.from_dict(data)
    assert restored.source.syllabus_year_range == "2026-2028"
    assert restored.source.selected_exam_year == "2027"
    assert restored.selected_exam_year == "2027"
    assert restored.route_tags == ["Core", "Supplement"]
    assert restored.provider == "cambridge"


def test_edexcel_unit_structure_roundtrip():
    unit_paper = AssessmentPaper(
        title="Unit 1: Structure and calculation",
        details=["Written exam", "1 hour 30 minutes", "80 marks"],
        code="XFM1/01",
        duration="1 hour 30 minutes",
        marks="80",
        weighting="33.3%",
        route_tags=["modular", "Foundation", "Higher"],
    )
    qualification = _base_qualification(
        provider="pearson",
        qualification_family="Edexcel International GCSE",
        assessments=[unit_paper],
        route_tags=["modular"],
        command_words=["Calculate", "Explain", "Compare"],
        assessment_objectives=["AO1", "AO2", "AO3"],
    )
    data = qualification.to_dict()
    assert data["assessments"][0]["code"] == "XFM1/01"
    assert data["assessments"][0]["route_tags"] == ["modular", "Foundation", "Higher"]

    restored = Qualification.from_dict(data)
    assert restored.assessments[0].code == "XFM1/01"
    assert restored.assessments[0].duration == "1 hour 30 minutes"
    assert restored.assessments[0].marks == "80"
    assert restored.assessments[0].weighting == "33.3%"
    assert restored.assessments[0].route_tags == ["modular", "Foundation", "Higher"]
    assert restored.command_words == ["Calculate", "Explain", "Compare"]
    assert restored.assessment_objectives == ["AO1", "AO2", "AO3"]


def test_old_json_without_new_fields_loads_with_defaults():
    """A legacy qualification dict (pre-Phase-2) must still load."""
    legacy = {
        "title": "International GCSE Chemistry (9202)",
        "code": "9202",
        "qualification_type": "international_gcse",
        "subject_area": "Chemistry",
        "page_url": "https://example.test/chemistry/",
        "summary": [],
        "topics": [{"title": "Bonding", "points": ["ionic"]}],
        "assessments": [{"title": "Paper 1", "details": ["1 hour"]}],
        "source": {
            "provider": "oxfordaqa",
            "page_url": "https://example.test/chemistry/",
            "specification_url": "https://example.test/spec.pdf",
        },
        "audience_note": "International GCSE linear qualification for international students.",
    }
    restored = Qualification.from_dict(legacy)
    assert restored.title == "International GCSE Chemistry (9202)"
    assert restored.provider is None
    assert restored.selected_exam_year is None
    assert restored.route_tags == []
    assert restored.command_words == []
    assert restored.assessment_objectives == []
    assert restored.assessments[0].code is None
    assert restored.assessments[0].route_tags == []
    assert restored.source.syllabus_year_range is None
    assert restored.source.selected_exam_year is None
