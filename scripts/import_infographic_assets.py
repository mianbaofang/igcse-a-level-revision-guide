from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import externally generated infographic assets into visual_manifest.json."
    )
    parser.add_argument("output_dir", help="A generated guide output directory.")
    parser.add_argument(
        "--asset-dir",
        required=True,
        help="Directory containing generated raster images named with manifest IDs, e.g. visual_001.png.",
    )
    parser.add_argument("--provider", default="external-provider")
    parser.add_argument("--status", default="reviewed-generated")
    parser.add_argument("--force", action="store_true", help="Replace existing generated files.")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Do not fail when some pending infographic IDs have no matching image.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    asset_dir = Path(args.asset_dir).resolve()
    images_dir = output_dir / "images"
    manifest_path = images_dir / "visual_manifest.json"
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}", file=sys.stderr)
        return 1
    if not asset_dir.is_dir():
        print(f"asset directory not found: {asset_dir}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        print("visual_manifest.json must contain a list", file=sys.stderr)
        return 1

    imported = 0
    missing: list[str] = []
    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("complexity") != "infographic":
            continue
        visual_id = str(entry.get("id") or "")
        if not visual_id:
            continue
        existing_file = str(entry.get("file") or "")
        if existing_file and (images_dir / existing_file).exists() and not args.force:
            continue
        source = find_asset(asset_dir, visual_id)
        if not source:
            missing.append(visual_id)
            continue
        target = images_dir / source.name
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        entry["file"] = source.name
        entry["asset_status"] = args.status
        entry["generated_by"] = args.provider
        imported += 1

    if missing and not args.allow_partial:
        print(
            json.dumps(
                {
                    "ok": False,
                    "imported": imported,
                    "missing": missing,
                    "hint": "Use --allow-partial to import only matching assets.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "imported": imported,
                "missing": missing,
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def find_asset(asset_dir: Path, visual_id: str) -> Path | None:
    candidates = [
        path
        for path in asset_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in RASTER_EXTENSIONS
        and (path.stem == visual_id or path.stem.startswith(f"{visual_id}_"))
    ]
    return sorted(candidates)[0] if candidates else None


if __name__ == "__main__":
    raise SystemExit(main())
