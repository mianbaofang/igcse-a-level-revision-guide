from dataclasses import replace

from intl_exam_guide.models import SourceSnippet, VisualBrief
from intl_exam_guide.visuals import VisualSpec, spec_hash


def sample_visual_brief() -> VisualBrief:
    return VisualBrief(
        topic_title="Bonding",
        focus_point="ionic bonding and properties",
        trigger="spatial structure and property links need a labelled visual",
        visual_type="bonding and structure infographic",
        complexity="infographic",
        image_provider="prompt-queue",
        prompt="Create a labelled bonding infographic anchored to the syllabus point.",
        source_points=["Describe ionic bonding."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should describe ionic bonding.",
                matched_term="ionic bonding",
            )
        ],
    )


def test_visual_spec_from_brief_copies_the_visual_contract():
    brief = sample_visual_brief()

    spec = VisualSpec.from_brief(brief, visual_id="visual_007")

    assert spec.visual_id == "visual_007"
    assert spec.topic_title == "Bonding"
    assert spec.focus_point == "ionic bonding and properties"
    assert spec.renderer_id == "prompt-queue"
    assert spec.source_points == ("Describe ionic bonding.",)
    assert spec.source_pages == (12,)
    assert spec.source_terms == ("ionic bonding",)

    brief.source_points.append("mutated after adaptation")
    assert spec.source_points == ("Describe ionic bonding.",)


def test_spec_hash_is_stable_for_equal_specs_and_changes_with_contract():
    spec = VisualSpec.from_brief(sample_visual_brief(), visual_id="visual_001")
    same_spec = VisualSpec.from_brief(sample_visual_brief(), visual_id="visual_009")
    changed_spec = replace(spec, prompt="Create a different visual.")

    assert spec.spec_hash() == spec_hash(spec)
    assert spec.spec_hash() == same_spec.spec_hash()
    assert len(spec.spec_hash()) == 64
    assert spec.spec_hash() != changed_spec.spec_hash()
