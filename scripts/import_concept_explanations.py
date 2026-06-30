from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import LLM-reviewed concept explanations into a generated guide."
    )
    parser.add_argument("output_dir", help="A generated guide output directory.")
    parser.add_argument("--concept-file", required=True, help="JSON file with topic_title and explanations.")
    parser.add_argument("--force", action="store_true", help="Replace existing concept explanations.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    concept_file = Path(args.concept_file).resolve()
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        print(f"missing guide plan: {plan_path}", file=sys.stderr)
        return 1
    if not concept_file.exists():
        print(f"missing concept file: {concept_file}", file=sys.stderr)
        return 1

    from intl_exam_guide.models import GuidePlan

    plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
    explanations = load_concept_explanations(concept_file)
    imported, missing = apply_concept_explanations(plan, explanations, force=args.force)
    if missing:
        print(
            json.dumps(
                {"ok": False, "imported": imported, "missing": missing},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    plan_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    (concepts_dir / "concept_explanations.json").write_text(
        json.dumps(explanations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rerender_result = rerender_handbook(output_dir)
    print(
        json.dumps(
            {
                "ok": True,
                "imported": imported,
                "concept_explanations": str(concepts_dir / "concept_explanations.json"),
                "rerender": rerender_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print("Review the updated handbook with:")
    print(f"python -m intl_exam_guide review --out {output_dir}")
    return 0


def load_concept_explanations(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("concept_explanations", data) if isinstance(data, dict) else data
    if isinstance(entries, dict):
        return [
            {"topic_title": title, "explanations": explanations}
            for title, explanations in entries.items()
        ]
    if not isinstance(entries, list):
        raise ValueError("concept file must contain a list or mapping")
    return [entry for entry in entries if isinstance(entry, dict)]


def apply_concept_explanations(
    plan: object,
    explanations: list[dict[str, object]],
    force: bool = False,
) -> tuple[int, list[str]]:
    guides = {guide.topic_title: guide for guide in getattr(plan, "topic_guides", [])}
    imported = 0
    missing: list[str] = []
    for entry in explanations:
        topic_title = str(entry.get("topic_title") or "")
        values = entry.get("explanations")
        if not topic_title or not isinstance(values, list):
            continue
        clean_values = [str(value).strip() for value in values if str(value).strip()]
        if len(clean_values) < 2:
            continue
        guide = guides.get(topic_title)
        if not guide:
            missing.append(topic_title)
            continue
        guide.checklist = clean_values[:4]
        imported += 1
    return imported, missing


def rerender_handbook(output_dir: Path) -> dict[str, object]:
    try:
        from intl_exam_guide.models import GuidePlan
        from intl_exam_guide.rendering.handbook_package import write_handbook_package
        from intl_exam_guide.rendering.html import render_html
        from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf

        plan_path = output_dir / "guide-plan.json"
        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
        write_handbook_package(plan, output_dir)
        html_path = render_html(
            plan,
            output_dir / "guide.html",
            output_dir / "images" / "visual_manifest.json",
        )
        result: dict[str, object] = {
            "rerendered": True,
            "html": str(html_path),
            "sections": str(output_dir / "sections"),
        }
        pdf_path = output_dir / "guide.pdf"
        if pdf_path.exists():
            try:
                export_pdf(html_path, pdf_path)
                result["pdf"] = str(pdf_path)
            except PdfExportError as exc:
                result["pdf_error"] = str(exc)
        return result
    except Exception as exc:  # pragma: no cover - defensive script boundary
        return {"rerendered": False, "reason": str(exc)}


if __name__ == "__main__":
    raise SystemExit(main())
