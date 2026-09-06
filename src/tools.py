"""Strict pixel-native drawing and ASCII authoring primitives.

Structural lines reject one-pixel widths.  Every color is resolved through the
named project palette, and every primitive rejects accidental canvas clipping.
Single pixels remain available only for texture, dithering, eyes, and sparks.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .palette import SYMBOLS, rgba

TRANSPARENT = (0, 0, 0, 0)


@dataclass(frozen=True)
class Anchor:
    horizontal: str = "center"
    vertical: str = "bottom"

    def __post_init__(self) -> None:
        if self.horizontal not in {"left", "center", "right"}:
            raise ValueError(f"invalid horizontal anchor: {self.horizontal}")
        if self.vertical not in {"top", "center", "bottom"}:
            raise ValueError(f"invalid vertical anchor: {self.vertical}")


def new_canvas(width: int, height: int, fill: str | None = None) -> Image.Image:
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise ValueError(f"canvas dimensions must be positive integers, got {width}x{height}")
    return Image.new("RGBA", (width, height), TRANSPARENT if fill is None else rgba(fill))


def _check_box(image: Image.Image, x: int, y: int, width: int, height: int, label: str) -> None:
    if width <= 0 or height <= 0:
        raise ValueError(f"{label} dimensions must be positive, got {width}x{height}")
    if x < 0 or y < 0 or x + width > image.width or y + height > image.height:
        raise ValueError(
            f"{label} ({x}, {y}, {width}, {height}) clips {image.width}x{image.height} canvas"
        )


def pixel(image: Image.Image, x: int, y: int, color: str) -> None:
    """Place one non-structural detail pixel, rejecting clipping."""
    _check_box(image, x, y, 1, 1, "pixel")
    image.putpixel((x, y), rgba(color))


def rect(image: Image.Image, x: int, y: int, width: int, height: int, color: str) -> None:
    _check_box(image, x, y, width, height, "rectangle")
    ImageDraw.Draw(image).rectangle((x, y, x + width - 1, y + height - 1), fill=rgba(color))


def outline_rect(
    image: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str,
    thickness: int = 2,
) -> None:
    _check_box(image, x, y, width, height, "outline")
    if thickness < 1 or thickness * 2 > min(width, height):
        raise ValueError(f"invalid outline thickness {thickness} for {width}x{height}")
    draw = ImageDraw.Draw(image)
    for inset in range(thickness):
        draw.rectangle(
            (x + inset, y + inset, x + width - 1 - inset, y + height - 1 - inset),
            outline=rgba(color),
        )


def line(
    image: Image.Image,
    points: Sequence[tuple[int, int]],
    color: str,
    width: int = 2,
) -> None:
    """Draw a structural polyline; one-pixel limbs and shafts are forbidden."""
    if len(points) < 2:
        raise ValueError("line requires at least two points")
    if width < 2:
        raise ValueError("structural line width must be at least 2px")
    for x, y in points:
        if not (0 <= x < image.width and 0 <= y < image.height):
            raise ValueError(f"line point {(x, y)} clips {image.size} canvas")
    ImageDraw.Draw(image).line(points, fill=rgba(color), width=width, joint="curve")


def texture_line(
    image: Image.Image,
    points: Sequence[tuple[int, int]],
    color: str,
) -> None:
    """Draw a one-pixel non-structural crack, mortar seam, or glint."""
    if len(points) < 2:
        raise ValueError("texture line requires at least two points")
    for x, y in points:
        if not (0 <= x < image.width and 0 <= y < image.height):
            raise ValueError(f"texture line point {(x, y)} clips {image.size} canvas")
    ImageDraw.Draw(image).line(points, fill=rgba(color), width=1)


def polygon(image: Image.Image, points: Sequence[tuple[int, int]], color: str) -> None:
    if len(points) < 3:
        raise ValueError("polygon requires at least three points")
    for x, y in points:
        if not (0 <= x < image.width and 0 <= y < image.height):
            raise ValueError(f"polygon point {(x, y)} clips {image.size} canvas")
    ImageDraw.Draw(image).polygon(points, fill=rgba(color))


def ellipse(image: Image.Image, x: int, y: int, width: int, height: int, color: str) -> None:
    _check_box(image, x, y, width, height, "ellipse")
    ImageDraw.Draw(image).ellipse((x, y, x + width - 1, y + height - 1), fill=rgba(color))




def dither_disc(
    image: Image.Image,
    center_x: int,
    center_y: int,
    radius: int,
    rings: Sequence[tuple[float, str, int]],
) -> None:
    """Draw palette-safe concentric colors with sparse outer falloff.

    Each ring is ``(radius_fraction, color, dither_period)``.  Fractions may be
    supplied in any order; the 1.0 outer ring is required.
    """
    if radius <= 0:
        raise ValueError("disc radius must be positive")
    if not rings:
        raise ValueError("disc requires at least one ring")
    if center_x - radius < 0 or center_y - radius < 0 or center_x + radius >= image.width or center_y + radius >= image.height:
        raise ValueError(f"dither disc centered at {(center_x, center_y)} clips {image.size} canvas")
    ordered = sorted(rings, key=lambda item: item[0])
    if ordered[-1][0] != 1.0 or any(not 0 < fraction <= 1 or period < 1 for fraction, _, period in ordered):
        raise ValueError("light rings need increasing 0..1 fractions, a 1.0 outer ring, and positive periods")
    resolved = [(fraction, rgba(name), period) for fraction, name, period in ordered]
    radius_sq = radius * radius
    for yy in range(center_y - radius, center_y + radius + 1):
        for xx in range(center_x - radius, center_x + radius + 1):
            distance_sq = (xx - center_x) ** 2 + (yy - center_y) ** 2
            if distance_sq > radius_sq:
                continue
            distance = distance_sq ** 0.5 / radius
            for fraction, value, period in resolved:
                if distance <= fraction:
                    if period <= 1 or (xx + yy * 3) % period == 0:
                        image.putpixel((xx, yy), value)
                    break




def validate_map(rows: Sequence[str], symbols: Mapping[str, str | None] = SYMBOLS) -> tuple[int, int]:
    if not rows:
        raise ValueError("pixel map cannot be empty")
    if not rows[0]:
        raise ValueError("pixel map rows cannot be empty")
    width = len(rows[0])
    for symbol in symbols:
        if len(symbol) != 1:
            raise ValueError(f"pixel-map legend key {symbol!r} is not one character")
    for row_index, row in enumerate(rows):
        if not isinstance(row, str):
            raise TypeError(f"pixel map row {row_index} is not a string")
        if len(row) != width:
            raise ValueError(
                f"pixel map row {row_index} has {len(row)} cells; expected rectangular width {width}"
            )
        unknown = sorted(set(row).difference(symbols))
        if unknown:
            raise ValueError(f"undefined pixel-map symbols in row {row_index}: {unknown}")
    return width, len(rows)


def draw_map(
    image: Image.Image,
    x: int,
    y: int,
    rows: Sequence[str],
    symbols: Mapping[str, str | None] = SYMBOLS,
) -> Image.Image:
    width, height = validate_map(rows, symbols)
    _check_box(image, x, y, width, height, "pixel map")
    for row_index, row in enumerate(rows):
        for column_index, symbol in enumerate(row):
            color_name = symbols[symbol]
            if color_name is not None:
                image.putpixel((x + column_index, y + row_index), rgba(color_name))
    return image


def map_sprite(
    rows: Sequence[str],
    size: tuple[int, int] | None = None,
    anchor: Anchor = Anchor(),
    symbols: Mapping[str, str | None] = SYMBOLS,
) -> Image.Image:
    map_width, map_height = validate_map(rows, symbols)
    if size is None:
        size = (map_width, map_height)
    width, height = size
    if map_width > width or map_height > height:
        raise ValueError(f"{map_width}x{map_height} map does not fit {width}x{height} canvas")
    if anchor.horizontal == "left":
        x = 0
    elif anchor.horizontal == "right":
        x = width - map_width
    else:
        x = (width - map_width) // 2
    if anchor.vertical == "top":
        y = 0
    elif anchor.vertical == "bottom":
        y = height - map_height
    else:
        y = (height - map_height) // 2
    return draw_map(new_canvas(width, height), x, y, rows, symbols)


def blit(destination: Image.Image, source: Image.Image, x: int, y: int) -> None:
    _check_box(destination, x, y, source.width, source.height, "blit")
    destination.alpha_composite(source, (x, y))


def nearest(image: Image.Image, scale: int) -> Image.Image:
    if type(scale) is not int or scale <= 0:
        raise ValueError(f"scale must be a positive integer, got {scale!r}")
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def pixel_values(image: Image.Image):
    """Return a flat pixel view without Pillow's deprecated ``getdata`` API."""
    modern = getattr(image, "get_flattened_data", None)
    return modern() if modern is not None else image.getdata()




def alpha_volume(image: Image.Image) -> int:
    return sum(1 for pixel_value in pixel_values(image) if pixel_value[3] != 0)


