"""Render the best scene screenshot without rebuilding native outputs."""
from __future__ import annotations

from src.generate import PNG_OPTIONS, SHEETS, build_all
from src.scene import render


def main() -> int:
    SHEETS.mkdir(parents=True, exist_ok=True)
    image = render(build_all())
    path = SHEETS / "scene.png"
    image.save(path, **PNG_OPTIONS)
    print(f"saved {path} {image.size} {image.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())