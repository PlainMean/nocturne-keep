"""Deterministic native build, manifest, review sheets, animations, and scene."""
from __future__ import annotations

import hashlib
import io
import json
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from textwrap import shorten

from PIL import Image, ImageDraw, ImageFont

from .hero import build_hero_assets
from .palette import PALETTE_NAME, rgba
from .spec import ANIMATIONS, ASSET_SPECS, ASSET_SPECS_BY_NAME, REVIEW_FILES, AssetSpec, validate_spec
from .sprites import build_sprite_assets
from .tiles import build_tile_assets
from .tools import blit, nearest, new_canvas, rect
from .ui import build_ui_assets

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SHEETS = ROOT / "sheets"
PNG_OPTIONS = {"format": "PNG", "optimize": False, "compress_level": 9}


def png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, **PNG_OPTIONS)
    return buffer.getvalue()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def aggregate_digest(entries: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in sorted(entries):
        name_bytes = name.encode("utf-8")
        data = entries[name]
        digest.update(len(name_bytes).to_bytes(4, "big"))
        digest.update(name_bytes)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def build_all() -> dict[str, Image.Image]:
    errors = validate_spec()
    if errors:
        raise ValueError("invalid asset specification: " + "; ".join(errors))
    groups = (build_hero_assets(), build_sprite_assets(), build_tile_assets(), build_ui_assets())
    assets: dict[str, Image.Image] = {}
    for group in groups:
        overlap = set(assets).intersection(group)
        if overlap:
            raise ValueError(f"duplicate asset builders: {sorted(overlap)}")
        assets.update(group)
    expected = set(ASSET_SPECS_BY_NAME)
    actual = set(assets)
    if actual != expected:
        raise ValueError(f"builder/spec mismatch; missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    for name, image in assets.items():
        spec = ASSET_SPECS_BY_NAME[name]
        if image.mode != "RGBA":
            raise ValueError(f"{name}: builder returned {image.mode}, expected RGBA")
        if image.size != spec.size:
            raise ValueError(f"{name}: builder returned {image.size}, expected {spec.size}")
    # Reorder by the manifest.  Dict insertion order is part of deterministic
    # sheet layout and manifest serialization.
    return {spec.name: assets[spec.name] for spec in ASSET_SPECS}


def _safe_clean(directory: Path) -> None:
    resolved = directory.resolve()
    if resolved in {Path("/").resolve(), ROOT.resolve(), ROOT.parent.resolve()}:
        raise ValueError(f"refusing to clean unsafe directory: {resolved}")
    if directory.exists():
        if not directory.is_dir():
            raise ValueError(f"output path is not a directory: {directory}")
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def build_manifest(encoded: Mapping[str, bytes]) -> dict[str, object]:
    digest = aggregate_digest(encoded)
    records = []
    for spec in ASSET_SPECS:
        filename = f"{spec.name}.png"
        records.append({
            "name": spec.name,
            "file": filename,
            "width": spec.size[0],
            "height": spec.size[1],
            "category": spec.category,
            "alpha": spec.alpha,
            "description": spec.description,
            "sha256": sha256(encoded[filename]),
        })
    return {
        "schema": 2,
        "palette": PALETTE_NAME,
        "asset_count": len(records),
        "aggregate_sha256": digest,
        "assets": records,
    }


def write_native_assets(
    assets: Mapping[str, Image.Image],
    output_dir: Path = OUT,
) -> tuple[str, dict[str, object]]:
    _safe_clean(output_dir)
    encoded = {f"{name}.png": png_bytes(image) for name, image in assets.items()}
    for filename, data in encoded.items():
        (output_dir / filename).write_bytes(data)
    manifest = build_manifest(encoded)
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return str(manifest["aggregate_sha256"]), manifest


def _checker(width: int, height: int, cell: int = 8) -> Image.Image:
    image = new_canvas(width, height, "night_shadow")
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            color = "night_dark" if (x // cell + y // cell) % 2 == 0 else "ink"
            rect(image, x, y, min(cell, width - x), min(cell, height - y), color)
    return image


def _font() -> ImageFont.ImageFont:
    return ImageFont.load_default()


def _contact_sheet(assets: Mapping[str, Image.Image], specs: Sequence[AssetSpec], columns: int) -> Image.Image:
    cell_width, cell_height, margin = 148, 124, 10
    rows = (len(specs) + columns - 1) // columns
    sheet = _checker(columns * cell_width + margin * 2, rows * cell_height + margin * 2)
    draw = ImageDraw.Draw(sheet)
    font = _font()
    for index, spec in enumerate(specs):
        row_index, column_index = divmod(index, columns)
        image = assets[spec.name]
        max_scale = max(1, min(4, (cell_width - 16) // image.width, 76 // image.height))
        enlarged = nearest(image, max_scale)
        cell_x = margin + column_index * cell_width
        cell_y = margin + row_index * cell_height
        x = cell_x + (cell_width - enlarged.width) // 2
        y = cell_y + 3 + (78 - enlarged.height) // 2
        blit(sheet, enlarged, x, y)
        label = spec.name.replace("_", " ")
        draw.text((cell_x + 4, cell_y + 84), shorten(label, width=23, placeholder="…"), fill=rgba("gold_light"), font=font)
        draw.text((cell_x + 4, cell_y + 99), f"{image.width}x{image.height} · {spec.alpha}", fill=rgba("stone_highlight"), font=font)
        draw.text((cell_x + 4, cell_y + 111), shorten(spec.description, width=24, placeholder="…"), fill=rgba("moon_mid"), font=font)
    return sheet


def make_contact_sheets(assets: Mapping[str, Image.Image], sheets_dir: Path = SHEETS) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for category in ("hero", "enemies", "props", "items", "tiles", "ui"):
        specs = [spec for spec in ASSET_SPECS if spec.category == category]
        columns = 5 if category in {"hero", "enemies", "props"} else 6
        path = sheets_dir / f"{category}.png"
        _contact_sheet(assets, specs, columns).save(path, **PNG_OPTIONS)
        paths[category] = path
    all_path = sheets_dir / "all.png"
    _contact_sheet(assets, ASSET_SPECS, 8).save(all_path, **PNG_OPTIONS)
    paths["all"] = all_path
    return paths


def _animation_strip(
    assets: Mapping[str, Image.Image],
    animation_name: str,
    sheets_dir: Path,
    scale: int = 4,
) -> tuple[Path, Path]:
    animation = next(item for item in ANIMATIONS if item.name == animation_name)
    frames = [assets[name] for name in animation.frames]
    frame_width, frame_height = frames[0].size
    panel_width = frame_width * scale + 18
    sheet_width = panel_width * len(frames) + 10
    sheet_height = frame_height * scale + 48
    strip = _checker(sheet_width, sheet_height)
    draw = ImageDraw.Draw(strip)
    font = _font()
    gif_frames: list[Image.Image] = []
    for index, (name, frame, delta) in enumerate(zip(animation.frames, frames, animation.frame_deltas)):
        enlarged = nearest(frame, scale)
        x = 5 + index * panel_width + (panel_width - enlarged.width) // 2
        blit(strip, enlarged, x, 5)
        draw.text((7 + index * panel_width, frame_height * scale + 10), f"{index}: {name.rsplit('_', 1)[-1]}", fill=rgba("gold_light"), font=font)
        draw.text((7 + index * panel_width, frame_height * scale + 24), shorten(delta, width=24, placeholder="…"), fill=rgba("moon_mid"), font=font)
        gif_frames.append(enlarged)
    strip_path = sheets_dir / f"{animation_name}_strip.png"
    strip.save(strip_path, **PNG_OPTIONS)
    gif_path = sheets_dir / f"{animation_name}.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=animation.durations_ms,
        loop=0 if animation.loop else 1,
        disposal=2,
        optimize=False,
    )
    return strip_path, gif_path


def make_review_artifacts(assets: Mapping[str, Image.Image], sheets_dir: Path = SHEETS) -> dict[str, Path]:
    _safe_clean(sheets_dir)
    paths = make_contact_sheets(assets, sheets_dir)
    for animation in ANIMATIONS:
        strip, gif = _animation_strip(assets, animation.name, sheets_dir)
        paths[f"{animation.name}_strip"] = strip
        paths[animation.name] = gif
    from .scene import render

    scene_path = sheets_dir / "scene.png"
    render(assets).save(scene_path, **PNG_OPTIONS)
    paths["scene"] = scene_path
    actual = {path.name for path in sheets_dir.iterdir() if path.is_file()}
    if actual != REVIEW_FILES:
        raise ValueError(f"review inventory mismatch; missing={sorted(REVIEW_FILES - actual)}, extra={sorted(actual - REVIEW_FILES)}")
    return paths


def generate() -> tuple[dict[str, Image.Image], str]:
    """Replace both generated directories with one complete coherent build."""
    assets = build_all()
    digest, _ = write_native_assets(assets, OUT)
    make_review_artifacts(assets, SHEETS)
    return assets, digest


def main() -> int:
    assets, digest = generate()
    print(f"generated {len(assets)} native assets with {PALETTE_NAME}")
    print(f"aggregate digest: {digest}")
    print(f"native output: {OUT}")
    print(f"review artifacts: {len(REVIEW_FILES)} in {SHEETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
