from __future__ import annotations

import json
import re
from pathlib import Path

from intl_exam_guide.auditing.concept_jobs import write_concept_jobs
from intl_exam_guide.auditing.visual_jobs import build_visual_jobs, visual_jobs_markdown
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.html import (
    render_cover,
    render_reference_appendix,
    render_student_overview,
    subject_display_name,
    render_topic_map,
    render_topic_nav,
    render_topic_visual_svg,
    render_topics,
    stylesheet,
)
from intl_exam_guide.rendering.visual_assets import (
    build_visual_asset_lookup,
    has_renderable_infographic,
    is_raster_asset,
    load_visual_manifest,
    scientific_vector_route,
    visual_asset_key_from_brief,
)

PRINT_RASTER_MAX_WIDTH = 1600
PRINT_RASTER_JPEG_QUALITY = 88
PRINT_RASTER_MIN_BYTES = 1_000_000
VISUAL_ASSET_EXTENSIONS = {".jpg", ".jpeg", ".png", ".svg", ".webp"}


def write_handbook_package(plan: GuidePlan, output_dir: Path) -> dict[str, object]:
    """Write the modular handbook artifacts expected by the original Skill."""
    sections_dir = output_dir / "sections"
    images_dir = output_dir / "images"
    sections_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    image_files = write_visual_assets(plan, images_dir)
    concept_jobs = write_concept_jobs(plan, output_dir)
    visual_assets = build_visual_asset_lookup(load_visual_manifest(images_dir))
    section_files = write_sections(plan, sections_dir, visual_assets)

    manifest: dict[str, object] = {
        "sections_dir": str(sections_dir),
        "images_dir": str(images_dir),
        "run_options": plan.run_options.__dict__,
        "section_files": [path.name for path in section_files],
        "image_files": [path.name for path in image_files],
        "concept_jobs": len(concept_jobs),
    }
    (output_dir / "handbook-package.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def write_sections(
    plan: GuidePlan,
    sections_dir: Path,
    visual_assets: dict[str, dict[str, object]] | None = None,
) -> list[Path]:
    qualification = plan.qualification
    language = plan.run_options.output_language
    html_lang = "zh-CN" if language == "zh-CN" else "en"
    page_title = (
        f"{qualification.title} Revision Guide"
        if language == "en"
        else f"{subject_display_name(qualification)}学习复习手册"
    )
    sections: list[tuple[str, str]] = [
        (
            "00_css.txt",
            "\n".join(
                [
                    f'<!doctype html><html lang="{html_lang}"><head><meta charset="utf-8">',
                    f"<title>{page_title}</title>",
                    f"<style>{stylesheet()}</style></head><body>",
                ]
            ),
        ),
        ("01_cover.txt", render_cover(qualification, plan.run_options)),
        (
            "02_study_overview.txt",
            render_student_overview(qualification, plan.revision_stages, plan.run_options),
        ),
        ("03_topic_map.txt", render_topic_map(qualification.topics, language, plan.topic_guides)),
        ("03_topic_navigation.txt", render_topic_nav(qualification.topics, language, plan.topic_guides)),
        (
            "04_topic_guides_and_examples.txt",
            render_topics(
                qualification.topics,
                plan.topic_guides,
                plan.practice_items,
                plan.visual_briefs,
                visual_assets,
                language,
                plan.run_options.explanation_style,
            ),
        ),
        (
            "05_source_appendix.txt",
            render_reference_appendix(qualification, len(plan.practice_items), language) + "\n</body></html>",
        ),
    ]

    written: list[Path] = []
    for name, content in sections:
        path = sections_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def write_visual_assets(plan: GuidePlan, images_dir: Path) -> list[Path]:
    existing_entries = load_visual_manifest(images_dir)
    existing_by_key = build_visual_asset_lookup(existing_entries)
    for old_svg in images_dir.glob("*.svg"):
        old_svg.unlink()
    manifest = []
    written: list[Path] = []
    for index, brief in enumerate(plan.visual_briefs, start=1):
        key = visual_asset_key_from_brief(brief)
        previous = existing_by_key.get(key, {})
        filename = None
        asset_status = "external-generation-required"
        if has_renderable_infographic(previous, images_dir):
            filename = str(previous.get("file"))
            asset_status = str(previous.get("asset_status") or "generated")
            written.append(images_dir / filename)
        elif brief.complexity == "svg-basic":
            filename = f"visual_{index:03d}_{slugify(brief.topic_title)}.svg"
            path = images_dir / filename
            path.write_text(
                render_topic_visual_svg(brief, index, plan.run_options.output_language).strip(),
                encoding="utf-8",
            )
            written.append(path)
            asset_status = "svg-draft"
        else:
            filename = None
            asset_status = "external-generation-required"
        entry = {
            **previous,
            **{
                "id": f"visual_{index:03d}",
                "key": key,
                "file": filename,
                "asset_status": asset_status,
                "topic_title": brief.topic_title,
                "focus_point": brief.focus_point,
                "visual_type": brief.visual_type,
                "complexity": brief.complexity,
                "image_provider": brief.image_provider,
                "fallback_route": (
                    scientific_vector_route(brief.visual_type)
                    if brief.complexity == "svg-basic"
                    else "no-svg-complex-infographic"
                ),
                "prompt": brief.prompt,
                "source_points": brief.source_points,
                "source_pages": [snippet.page for snippet in brief.source_snippets],
            },
        }
        manifest.append(entry)

    optimize_raster_assets_for_pdf(manifest, images_dir)
    final_written = [
        images_dir / str(entry["file"])
        for entry in manifest
        if entry.get("file") and (images_dir / str(entry["file"])).exists()
    ]
    cleanup_unreferenced_visual_assets(
        images_dir,
        {path.name for path in final_written},
    )

    (images_dir / "visual_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    jobs = build_visual_jobs(manifest)
    (images_dir / "infographic_jobs.json").write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (images_dir / "infographic_jobs.md").write_text(
        visual_jobs_markdown(jobs),
        encoding="utf-8",
    )
    return final_written


def cleanup_unreferenced_visual_assets(
    images_dir: Path,
    referenced_files: set[str],
) -> None:
    for path in images_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in VISUAL_ASSET_EXTENSIONS:
            continue
        if path.name not in referenced_files:
            path.unlink(missing_ok=True)


def optimize_raster_assets_for_pdf(
    manifest: list[dict[str, object]],
    images_dir: Path,
) -> list[Path]:
    try:
        from PIL import Image, ImageOps
    except ModuleNotFoundError:
        return []

    optimized: list[Path] = []
    for entry in manifest:
        filename = str(entry.get("file") or "")
        if not is_raster_asset(filename):
            continue
        source = images_dir / filename
        if not source.exists():
            continue
        try:
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image)
                width, height = image.size
                if source.stat().st_size < PRINT_RASTER_MIN_BYTES and width <= PRINT_RASTER_MAX_WIDTH:
                    continue
                image.thumbnail(
                    (PRINT_RASTER_MAX_WIDTH, PRINT_RASTER_MAX_WIDTH),
                    Image.Resampling.LANCZOS,
                )
                if image.mode not in {"RGB", "L"}:
                    image = image.convert("RGB")
                target = unique_print_asset_path(images_dir, source.stem)
                image.save(
                    target,
                    "JPEG",
                    quality=PRINT_RASTER_JPEG_QUALITY,
                    optimize=True,
                    progressive=True,
                )
        except (OSError, ValueError):
            continue
        if target.stat().st_size >= source.stat().st_size:
            target.unlink(missing_ok=True)
            continue
        entry["source_file"] = filename
        entry["file"] = target.name
        entry["asset_optimized_for_pdf"] = True
        optimized.append(target)
    return optimized


def unique_print_asset_path(images_dir: Path, stem: str) -> Path:
    target = images_dir / f"{stem}-print.jpg"
    if not target.exists():
        return target
    index = 2
    while True:
        candidate = images_dir / f"{stem}-print-{index}.jpg"
        if not candidate.exists():
            return candidate
        index += 1


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:54] or "topic"
