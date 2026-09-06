"""Compute the canonical aggregate digest from PNG files already on disk."""
from __future__ import annotations

from pathlib import Path

from .generate import OUT, aggregate_digest
from .spec import ASSET_SPECS


def disk_digest(output_dir: Path = OUT) -> tuple[int, str]:
    expected = {f"{spec.name}.png" for spec in ASSET_SPECS}
    actual = {path.name for path in output_dir.glob("*.png")}
    if actual != expected:
        raise ValueError(f"PNG inventory mismatch; missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    encoded = {name: (output_dir / name).read_bytes() for name in sorted(actual)}
    return len(encoded), aggregate_digest(encoded)


def main() -> int:
    count, digest = disk_digest()
    print(f"disk assets: {count}")
    print(f"aggregate digest: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
