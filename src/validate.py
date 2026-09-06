"""Validate every native, manifest, palette, animation, and review contract."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from .generate import OUT, SHEETS, aggregate_digest, build_all, build_manifest, png_bytes, sha256
from .palette import PALETTE, PALETTE_NAME, RAMPS, validate_palette
from .spec import ANIMATIONS, ASSET_SPECS, REVIEW_FILES, AnimationSpec, AssetSpec, validate_spec
from .tools import TRANSPARENT, alpha_volume, pixel_values


@dataclass(frozen=True)
class AnimationMetrics:
    name: str
    volumes: tuple[int, ...]
    volume_drift: float
    total_diffs: tuple[int, ...]
    regional_alpha_diffs: dict[str, tuple[int, ...]]


@dataclass(frozen=True)
class ValidationReport:
    errors: tuple[str, ...]
    digest: str
    animations: tuple[AnimationMetrics, ...]
    native_count: int
    review_count: int

    @property
    def ok(self) -> bool:
        return not self.errors


def palette_violations(image: Image.Image) -> set[tuple[int, int, int]]:
    allowed = set(PALETTE.values())
    if image.mode != "RGBA":
        return set()
    return {pixel[:3] for pixel in pixel_values(image) if pixel[3] and pixel[:3] not in allowed}


def asset_errors(
    name: str,
    image: Image.Image,
    spec: AssetSpec,
    expected_png: bytes | None = None,
) -> list[str]:
    errors: list[str] = []
    if image.mode != "RGBA":
        return [f"{name}: mode {image.mode}, expected RGBA"]
    if image.size != spec.size:
        errors.append(f"{name}: dimensions {image.size}, expected {spec.size}")
    pixels = list(pixel_values(image))
    alphas = {pixel[3] for pixel in pixels}
    opaque_count = sum(alpha != 0 for alpha in (pixel[3] for pixel in pixels))
    if opaque_count == 0:
        errors.append(f"{name}: image is fully transparent")
    if not alphas.issubset({0, 255}):
        errors.append(f"{name}: alpha must be binary 0/255, found {sorted(alphas)}")
    hidden_rgb = {pixel for pixel in pixels if pixel[3] == 0 and pixel != TRANSPARENT}
    if hidden_rgb:
        errors.append(f"{name}: transparent pixels contain hidden RGB values")
    if spec.alpha == "opaque" and alphas != {255}:
        errors.append(f"{name}: opaque asset contains transparency")
    if spec.alpha == "sprite" and 0 not in alphas:
        errors.append(f"{name}: sprite lacks transparent padding")
    bad_colors = palette_violations(image)
    if bad_colors:
        errors.append(f"{name}: colors outside {PALETTE_NAME}: {sorted(bad_colors)[:5]}")
    if expected_png is not None and png_bytes(image) != expected_png:
        errors.append(f"{name}: decoded image does not match deterministic PNG bytes")
    return errors


def _pixel_diff(first: Image.Image, second: Image.Image) -> int:
    if first.size != second.size or first.mode != second.mode:
        raise ValueError("frame diff requires equal modes and dimensions")
    return sum(left != right for left, right in zip(pixel_values(first), pixel_values(second)))


def _regional_alpha_diff(first: Image.Image, second: Image.Image, box: tuple[int, int, int, int]) -> int:
    left, top, right, bottom = box
    difference = 0
    first_alpha = first.getchannel("A")
    second_alpha = second.getchannel("A")
    for y in range(top, bottom):
        for x in range(left, right):
            difference += first_alpha.getpixel((x, y)) != second_alpha.getpixel((x, y))
    return difference


def _frame_pairs(frame_count: int, loop: bool) -> tuple[tuple[int, int], ...]:
    pairs = [(index, index + 1) for index in range(frame_count - 1)]
    if loop and frame_count > 2:
        pairs.append((frame_count - 1, 0))
    return tuple(pairs)


def animation_metrics(assets: dict[str, Image.Image], animation: AnimationSpec) -> AnimationMetrics:
    frames = [assets[name] for name in animation.frames]
    volumes = tuple(alpha_volume(frame) for frame in frames)
    average = sum(volumes) / len(volumes)
    drift = (max(volumes) - min(volumes)) / average if average else 1.0
    pairs = _frame_pairs(len(frames), animation.loop)
    total_diffs = tuple(_pixel_diff(frames[left], frames[right]) for left, right in pairs)
    regional = {
        region.name: tuple(_regional_alpha_diff(frames[left], frames[right], region.box) for left, right in pairs)
        for region in animation.regions
    }
    return AnimationMetrics(animation.name, volumes, drift, total_diffs, regional)


def animation_errors(assets: dict[str, Image.Image]) -> tuple[list[str], tuple[AnimationMetrics, ...]]:
    errors: list[str] = []
    metrics: list[AnimationMetrics] = []
    for animation in ANIMATIONS:
        metric = animation_metrics(assets, animation)
        metrics.append(metric)
        if not metric.volumes or min(metric.volumes) == 0:
            errors.append(f"{animation.name}: empty animation frame")
        if metric.volume_drift > animation.maximum_volume_drift:
            errors.append(
                f"{animation.name}: pixel-volume drift {metric.volume_drift:.3f} exceeds "
                f"{animation.maximum_volume_drift:.3f}; volumes={list(metric.volumes)}"
            )
        for pair_index, difference in enumerate(metric.total_diffs):
            if difference < animation.minimum_total_diff:
                errors.append(
                    f"{animation.name}: adjacent pair {pair_index} changes {difference} pixels; "
                    f"minimum is {animation.minimum_total_diff}"
                )
        for region in animation.regions:
            differences = metric.regional_alpha_diffs[region.name]
            for pair_index, difference in enumerate(differences):
                if difference < region.minimum_alpha_diff:
                    errors.append(
                        f"{animation.name}/{region.name}: pair {pair_index} changes {difference} silhouette pixels; "
                        f"minimum is {region.minimum_alpha_diff}"
                    )
    return errors, tuple(metrics)


def _component_sizes(image: Image.Image) -> list[int]:
    alpha = image.getchannel("A")
    remaining = {(x, y) for y in range(image.height) for x in range(image.width) if alpha.getpixel((x, y))}
    sizes: list[int] = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        size = 1
        while stack:
            x, y = stack.pop()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
                    size += 1
        sizes.append(size)
    return sorted(sizes, reverse=True)


def _hero_silhouette_errors(assets: dict[str, Image.Image]) -> list[str]:
    errors: list[str] = []
    for name, image in assets.items():
        if not name.startswith("hero_") or name == "hero_reference":
            continue
        sizes = _component_sizes(image)
        volume = sum(sizes)
        if not sizes or sizes[0] / volume < 0.98:
            errors.append(f"{name}: silhouette has detached structural components {sizes[:6]}")
    return errors


def _load_rgba(path: Path) -> Image.Image:
    with Image.open(path) as opened:
        opened.load()
        return opened.copy()


def _validate_review_artifacts(sheets_dir: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    if not sheets_dir.exists():
        return [f"review directory missing: {sheets_dir}"], 0
    if not sheets_dir.is_dir():
        return [f"review path is not a directory: {sheets_dir}"], 0
    files = {path.name for path in sheets_dir.iterdir()}
    missing, stale = REVIEW_FILES - files, files - REVIEW_FILES
    if missing:
        errors.append(f"review artifacts missing: {sorted(missing)}")
    if stale:
        errors.append(f"stale review artifacts: {sorted(stale)}")
    scene_path = sheets_dir / "scene.png"
    if scene_path.exists():
        from .scene import SCENE_SIZE

        scene = _load_rgba(scene_path)
        if scene.mode != "RGBA":
            errors.append(f"scene: mode {scene.mode}, expected RGBA")
        if scene.size != SCENE_SIZE:
            errors.append(f"scene: dimensions {scene.size}, expected {SCENE_SIZE}")
        if set(pixel[3] for pixel in pixel_values(scene)) != {255}:
            errors.append("scene: composed screenshot must be fully opaque")
        bad_colors = palette_violations(scene)
        if bad_colors:
            errors.append(f"scene: colors outside {PALETTE_NAME}: {sorted(bad_colors)[:5]}")
    for animation in ANIMATIONS:
        gif_path = sheets_dir / f"{animation.name}.gif"
        if not gif_path.exists():
            continue
        with Image.open(gif_path) as gif:
            frame_count = getattr(gif, "n_frames", 1)
            if frame_count != len(animation.frames):
                errors.append(f"{animation.name}.gif: {frame_count} frames, expected {len(animation.frames)}")
    return errors, len(files)


def validate(
    output_dir: Path = OUT,
    sheets_dir: Path = SHEETS,
    *,
    check_reviews: bool = True,
) -> ValidationReport:
    errors = validate_palette() + validate_spec()

    # Build twice in memory before looking at disk.  This detects nondeterminism
    # even when stale output happens to match one of the builds.
    first_assets = build_all()
    second_assets = build_all()
    first_encoded = {f"{name}.png": png_bytes(image) for name, image in first_assets.items()}
    second_encoded = {f"{name}.png": png_bytes(image) for name, image in second_assets.items()}
    for filename in first_encoded:
        if first_encoded[filename] != second_encoded[filename]:
            errors.append(f"{filename}: two independent in-memory builds differ")

    expected_files = set(first_encoded) | {"manifest.json"}
    if output_dir.exists() and not output_dir.is_dir():
        errors.append(f"native output path is not a directory: {output_dir}")
        actual_files: set[str] = set()
    else:
        actual_files = {path.name for path in output_dir.iterdir()} if output_dir.exists() else set()
    missing, stale = expected_files - actual_files, actual_files - expected_files
    if missing:
        errors.append(f"native outputs missing: {sorted(missing)}")
    if stale:
        errors.append(f"stale native outputs: {sorted(stale)}")

    actual_encoded: dict[str, bytes] = {}
    for spec in ASSET_SPECS:
        filename = f"{spec.name}.png"
        path = output_dir / filename
        if not path.exists():
            continue
        data = path.read_bytes()
        actual_encoded[filename] = data
        expected_data = first_encoded[filename]
        if data != expected_data:
            errors.append(f"{spec.name}: PNG bytes differ from deterministic build")
        try:
            image = _load_rgba(path)
        except Exception as exc:  # Pillow gives precise decoder errors in the message.
            errors.append(f"{spec.name}: cannot decode PNG: {exc}")
            continue
        errors.extend(asset_errors(spec.name, image, spec, expected_data))

    expected_manifest = build_manifest(first_encoded)
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        try:
            actual_manifest: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"manifest.json: cannot read exact manifest: {exc}")
        else:
            if actual_manifest != expected_manifest:
                errors.append("manifest.json: content differs from exact generated manifest")
            if isinstance(actual_manifest, dict) and isinstance(actual_manifest.get("assets"), list):
                for record in actual_manifest["assets"]:
                    if not isinstance(record, dict) or "file" not in record or "sha256" not in record:
                        errors.append("manifest.json: malformed asset hash record")
                        break
                    filename = record["file"]
                    if filename in actual_encoded and record["sha256"] != sha256(actual_encoded[filename]):
                        errors.append(f"manifest.json: hash mismatch for {filename}")

    deterministic_digest = aggregate_digest(first_encoded)
    if len(actual_encoded) == len(first_encoded):
        disk_digest = aggregate_digest(actual_encoded)
        if disk_digest != deterministic_digest:
            errors.append(f"disk aggregate {disk_digest} differs from deterministic build {deterministic_digest}")

    animation_error_list, metrics = animation_errors(first_assets)
    errors.extend(animation_error_list)
    errors.extend(_hero_silhouette_errors(first_assets))

    review_count = 0
    if check_reviews:
        review_errors, review_count = _validate_review_artifacts(sheets_dir)
        errors.extend(review_errors)

    return ValidationReport(tuple(errors), deterministic_digest, metrics, len(first_assets), review_count)


def main() -> int:
    report = validate()
    print(f"validated {report.native_count} native assets and {report.review_count} review artifacts")
    print(f"palette: {PALETTE_NAME} ({len(PALETTE)} colors, {len(RAMPS)} hue-shifted ramps)")
    for metric in report.animations:
        regions = "; ".join(f"{name}={list(values)}" for name, values in metric.regional_alpha_diffs.items())
        print(
            f"{metric.name}: volumes={list(metric.volumes)} drift={metric.volume_drift:.3f} "
            f"diffs={list(metric.total_diffs)}; {regions}"
        )
    print(f"aggregate digest: {report.digest}")
    for error in report.errors:
        print(f"ERROR: {error}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
