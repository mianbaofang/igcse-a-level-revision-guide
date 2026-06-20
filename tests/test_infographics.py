from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.infographics import render_infographic_required


def sample_visual(provider: str = "prompt-queue") -> VisualBrief:
    return VisualBrief(
        topic_title="Bonding",
        focus_point="ionic bonding and properties",
        trigger="spatial structure and property links need a labelled visual",
        visual_type="bonding and structure infographic",
        complexity="infographic",
        image_provider=provider,
        prompt="Create a labelled bonding infographic anchored to the syllabus point.",
        source_points=["Describe ionic bonding."],
    )


def test_render_generated_infographic_branch():
    html = render_infographic_required(
        "Bonding",
        sample_visual("gpt-image-2"),
        {
            "file": "visual_001_bonding.png",
            "asset_status": "generated",
            "image_provider": "gpt-image-2",
        },
        "page 12",
        "en",
    )

    assert "generated-infographic" in html
    assert "Generated Infographic" in html
    assert "visual_001_bonding.png" in html
    assert "gpt-image-2 - reviewed visual asset" in html
    assert "Infographic Queue" not in html


def test_render_svg_fallback_branch():
    html = render_infographic_required(
        "Bonding",
        sample_visual(),
        {
            "file": "visual_001_bonding.svg",
            "asset_status": "svg-fallback-needs-review",
            "image_provider": "deterministic-svg",
        },
        "page 12",
        "en",
    )

    assert "svg-fallback" in html
    assert "SVG Fallback - Review Needed" in html
    assert "visual_001_bonding.svg" in html
    assert "External image brief" in html
    assert "Generated Infographic" not in html


def test_render_pending_infographic_branch():
    html = render_infographic_required(
        "Bonding",
        sample_visual("ask-user-infographic"),
        None,
        "page 12",
        "en",
    )

    assert "infographic-required" in html
    assert "Infographic Queue" in html
    assert "external infographic generation pending" in html
    assert "Prompt queue" in html
    assert "bonding and structure infographic" in html
