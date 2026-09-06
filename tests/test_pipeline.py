from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.digest import disk_digest
from src.generate import aggregate_digest, build_all, png_bytes, write_native_assets
from src.palette import PALETTE, SYMBOLS, validate_palette
from src.spec import ANIMATIONS, ASSET_SPECS, ASSET_SPECS_BY_NAME, validate_spec
from src.tools import line, new_canvas, validate_map
from src.validate import animation_errors, asset_errors, palette_violations, validate


class PixelMapContractTests(unittest.TestCase):
    def test_rejects_undefined_map_symbol(self) -> None:
        with self.assertRaisesRegex(ValueError, "undefined pixel-map symbols"):
            validate_map(("kkk", "k~k"), SYMBOLS)

    def test_rejects_ragged_map(self) -> None:
        with self.assertRaisesRegex(ValueError, "rectangular width"):
            validate_map(("kkkk", "kkk"), SYMBOLS)

    def test_rejects_empty_map(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            validate_map((), SYMBOLS)

    def test_rejects_multi_character_legend_tokens(self) -> None:
        with self.assertRaisesRegex(ValueError, "not one character"):
            validate_map(("..",), {"..": None})

    def test_structural_lines_require_two_pixels(self) -> None:
        image = new_canvas(8, 8)
        with self.assertRaisesRegex(ValueError, "at least 2px"):
            line(image, ((1, 1), (6, 6)), "stone_mid", 1)


class SpecificationTests(unittest.TestCase):
    def test_palette_and_manifest_definitions_are_self_consistent(self) -> None:
        self.assertEqual(validate_palette(), [])
        self.assertEqual(validate_spec(), [])
        self.assertEqual(len(PALETTE), len(set(PALETTE.values())))

    def test_builders_match_exact_inventory_and_dimensions(self) -> None:
        assets = build_all()
        self.assertEqual(tuple(assets), tuple(spec.name for spec in ASSET_SPECS))
        for name, image in assets.items():
            self.assertEqual(image.mode, "RGBA", name)
            self.assertEqual(image.size, ASSET_SPECS_BY_NAME[name].size, name)


class DeterminismTests(unittest.TestCase):
    def test_two_independent_builds_have_identical_bytes_and_digest(self) -> None:
        first = {f"{name}.png": png_bytes(image) for name, image in build_all().items()}
        second = {f"{name}.png": png_bytes(image) for name, image in build_all().items()}
        self.assertEqual(first, second)
        self.assertEqual(aggregate_digest(first), aggregate_digest(second))

    def test_clean_writer_removes_stale_output(self) -> None:
        assets = build_all()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            (output / "stale.png").write_bytes(b"stale")
            (output / "notes.txt").write_text("also stale", encoding="utf-8")
            digest, manifest = write_native_assets(assets, output)
            expected = {f"{name}.png" for name in assets} | {"manifest.json"}
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            self.assertEqual(digest, manifest["aggregate_sha256"])
            self.assertEqual(disk_digest(output), (len(assets), digest))

    def test_end_to_end_native_validation_in_temporary_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            write_native_assets(build_all(), output)
            report = validate(output, Path(temporary) / "unused-sheets", check_reviews=False)
            self.assertTrue(report.ok, "\n".join(report.errors))
            self.assertEqual(report.native_count, len(ASSET_SPECS))


class FailureDetectionTests(unittest.TestCase):
    def test_palette_violation_is_reported(self) -> None:
        spec = ASSET_SPECS_BY_NAME["hero_idle_0"]
        image = build_all()[spec.name].copy()
        image.putpixel((0, 0), (1, 2, 3, 255))
        self.assertEqual(palette_violations(image), {(1, 2, 3)})
        self.assertTrue(any("outside" in error for error in asset_errors(spec.name, image, spec)))

    def test_dimension_violation_is_reported(self) -> None:
        spec = ASSET_SPECS_BY_NAME["pickup_heart_big"]
        image = new_canvas(spec.size[0] + 1, spec.size[1])
        image.putpixel((0, 0), (*PALETTE["crimson_mid"], 255))
        errors = asset_errors(spec.name, image, spec)
        self.assertTrue(any("dimensions" in error for error in errors))

    def test_partial_alpha_and_hidden_rgb_are_reported(self) -> None:
        spec = ASSET_SPECS_BY_NAME["pickup_heart_small"]
        image = build_all()[spec.name].copy()
        image.putpixel((0, 0), (9, 8, 7, 128))
        errors = asset_errors(spec.name, image, spec)
        self.assertTrue(any("binary" in error for error in errors))
        image.putpixel((0, 0), (9, 8, 7, 0))
        errors = asset_errors(spec.name, image, spec)
        self.assertTrue(any("hidden RGB" in error for error in errors))

    def test_non_rgba_mode_is_reported(self) -> None:
        spec = ASSET_SPECS_BY_NAME["ui_hp_bar"]
        image = Image.new("RGB", spec.size)
        self.assertEqual(asset_errors(spec.name, image, spec), [f"{spec.name}: mode RGB, expected RGBA"])


class AnimationContractTests(unittest.TestCase):
    def test_authored_animations_meet_regional_and_volume_contracts(self) -> None:
        errors, metrics = animation_errors(build_all())
        self.assertEqual(errors, [])
        self.assertEqual(tuple(metric.name for metric in metrics), tuple(spec.name for spec in ANIMATIONS))
        for spec, metric in zip(ANIMATIONS, metrics):
            self.assertLessEqual(metric.volume_drift, spec.maximum_volume_drift)
            self.assertGreaterEqual(min(metric.total_diffs), spec.minimum_total_diff)
            for region in spec.regions:
                self.assertGreaterEqual(min(metric.regional_alpha_diffs[region.name]), region.minimum_alpha_diff)

    def test_translated_or_duplicate_walk_pose_is_rejected(self) -> None:
        assets = build_all()
        assets["hero_walk_1"] = assets["hero_walk_0"].copy()
        errors, _ = animation_errors(assets)
        self.assertTrue(any("hero_walk" in error and "adjacent pair" in error for error in errors), errors)
        self.assertTrue(any("hero_walk/legs" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
