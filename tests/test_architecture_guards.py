from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_html_renderer_stays_below_monolith_limit():
    html_renderer = REPO_ROOT / "src" / "intl_exam_guide" / "rendering" / "html.py"

    line_count = len(html_renderer.read_text(encoding="utf-8").splitlines())

    assert line_count <= 1000


def test_svg_and_styles_are_split_out_of_html_renderer():
    rendering_dir = REPO_ROOT / "src" / "intl_exam_guide" / "rendering"

    assert (rendering_dir / "svg_templates.py").exists()
    assert (rendering_dir / "styles.py").exists()
