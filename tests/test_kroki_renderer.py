from __future__ import annotations

from pathlib import Path
from typing import Any

from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.kroki import (
    kroki_graphviz_source,
    normalize_kroki_svg_title,
    render_kroki_svg_asset,
)


def test_render_kroki_svg_asset_posts_graphviz_source(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    calls: dict[str, object] = {}

    class FakeResponse:
        headers = {"Content-Type": "image/svg+xml"}

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'<?xml version="1.0"?><svg><text>Accounting Records Flow</text></svg>'

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        calls["url"] = request.full_url
        calls["method"] = request.get_method()
        calls["data"] = request.data
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "intl_exam_guide.rendering.kroki.urllib.request.urlopen",
        fake_urlopen,
    )
    brief = VisualBrief(
        topic_title="Accounting records",
        focus_point="Use source documents, books of prime entry and ledger accounts.",
        trigger="accounting records need a precise source-to-ledger flow diagram",
        visual_type="source-document to book-of-prime-entry and ledger flow diagram",
        complexity="svg-basic",
        image_provider="kroki",
        prompt="",
        source_points=["Use source documents, books of prime entry and ledger accounts."],
    )

    output_path = tmp_path / "visual.svg"
    render_kroki_svg_asset(brief, output_path, base_url="https://kroki.test", timeout=3)

    assert calls["url"] == "https://kroki.test/graphviz/svg"
    assert calls["method"] == "POST"
    assert b"Accounting Records Flow - Accounting records" in calls["data"]
    assert b"digraph G" not in calls["data"]
    assert b"digraph Accounting_Records_Flow" in calls["data"]
    assert b"Source document" in calls["data"]
    assert calls["timeout"] == 3
    assert output_path.read_text(encoding="utf-8").startswith("<?xml")


def test_kroki_graphviz_uses_hierarchy_layout_for_organisation_structure() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="Organisation structure",
            focus_point="reporting lines",
            trigger="hierarchy",
            visual_type="organisation structure hierarchy",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Understand organisation structure and reporting lines."],
        )
    )

    assert "rankdir=TB" in source
    assert "n1 -> n2" in source
    assert "n2 -> n3" in source
    assert "n2 -> n4" in source


def test_kroki_graphviz_uses_stakeholder_star_map() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="Stakeholders",
            focus_point="stakeholder influence",
            trigger="map",
            visual_type="stakeholder influence map",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Explain stakeholder influence."],
        )
    )

    assert "Stakeholder Influence Map" in source
    assert "n1 -> n2 [dir=both]" in source
    assert "n1 -> n5 [dir=both]" in source


def test_kroki_graphviz_uses_segmentation_map_layout() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="3.5.2 - Market segmentation",
            focus_point="customer groups",
            trigger="map",
            visual_type="customer segmentation map",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Identify market segments."],
        )
    )

    assert "Customer Segmentation Map - Market segmentation" in source
    assert 'label="segments"' in source
    assert 'label="target"' in source


def test_kroki_graphviz_uses_quality_checkpoint_loop() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="3.3.3 - The concept of quality",
            focus_point="quality control",
            trigger="checkpoint",
            visual_type="quality assurance checkpoint diagram",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Explain quality assurance."],
        )
    )

    assert "Quality Checkpoint Loop - The concept of quality" in source
    assert "n4 -> n2" in source
    assert 'label="improve"' in source


def test_kroki_graphviz_prioritises_operations_before_quality_checkpoint() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="3.3.1 - Production processes",
            focus_point="production process",
            trigger="flow",
            visual_type="operations flow and quality checkpoint diagram",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Describe production processes."],
        )
    )

    assert "Operations Flow - Production processes" in source
    assert "Quality Checkpoint Loop" not in source


def test_normalize_kroki_svg_title_replaces_graphviz_id_title() -> None:
    payload = b'<svg><title>G</title><g id="node1"></g></svg>'

    normalized = normalize_kroki_svg_title(payload, "Stakeholder Influence Map - Stakeholders")

    assert b"<title>Stakeholder Influence Map - Stakeholders</title>" in normalized
    assert b"<title>G</title>" not in normalized


def test_kroki_graphviz_uses_comparison_clusters() -> None:
    source = kroki_graphviz_source(
        VisualBrief(
            topic_title="Business ownership comparison",
            focus_point="sole trader and limited company",
            trigger="comparison",
            visual_type="business ownership comparison",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="",
            source_points=["Compare ownership structures."],
        )
    )

    assert "subgraph cluster_left" in source
    assert "subgraph cluster_right" in source
    assert 'label="compare"' in source
