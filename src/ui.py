"""Background silhouettes and coherent gothic HUD components."""
from __future__ import annotations

from PIL import Image

from .tools import TRANSPARENT, ellipse, new_canvas, outline_rect, polygon, rect


def moon() -> Image.Image:
    image = new_canvas(32, 32)
    ellipse(image, 3, 2, 27, 27, "moon_light")
    # Transparent offset cutout forms a crescent that composites on any sky.
    clear = TRANSPARENT
    for y in range(2, 26):
        for x in range(12, 31):
            if ((x - 19) / 11) ** 2 + ((y - 12) / 11) ** 2 <= 1:
                image.putpixel((x, y), clear)
    for x, y, width, height in ((7, 8, 4, 3), (8, 19, 3, 2), (13, 24, 3, 2)):
        rect(image, x, y, width, height, "moon_mid")
    return image


def cloud() -> Image.Image:
    image = new_canvas(48, 20)
    ellipse(image, 1, 8, 18, 10, "night_mid"); ellipse(image, 11, 3, 23, 15, "night_light")
    ellipse(image, 27, 7, 19, 11, "night_mid"); rect(image, 5, 12, 38, 7, "night_mid")
    rect(image, 12, 9, 21, 4, "moon_shadow"); rect(image, 5, 17, 38, 2, "night_dark")
    return image


def castle_silhouette() -> Image.Image:
    image = new_canvas(96, 48)
    rect(image, 0, 31, 96, 17, "night_shadow")
    towers = ((3, 16, 13), (23, 22, 12), (60, 20, 13), (79, 13, 14))
    for x, top, width in towers:
        rect(image, x, top, width, 31 - top, "night_shadow")
        polygon(image, ((x - 2, top), (x + width // 2, max(1, top - 11)), (x + width + 1, top)), "night_shadow")
        rect(image, x + 4, top + 7, 3, 8, "night_mid")
    rect(image, 34, 15, 28, 23, "night_shadow")
    polygon(image, ((32, 15), (48, 1), (64, 15)), "night_shadow")
    polygon(image, ((43, 37), (43, 27), (48, 21), (53, 27), (53, 37)), "night_mid")
    for x in (35, 42, 51, 58): rect(image, x, 11, 3, 5, "night_shadow")
    return image


def ui_corner() -> Image.Image:
    image = new_canvas(8, 8)
    polygon(image, ((0, 0), (8 - 1, 0), (8 - 1, 2), (4, 2), (2, 4), (2, 7), (0, 7)), "gold_dark")
    rect(image, 0, 0, 6, 2, "gold_light"); rect(image, 0, 0, 2, 6, "gold_mid")
    rect(image, 2, 2, 3, 3, "stone_light")
    return image


def ui_edge_horizontal() -> Image.Image:
    image = new_canvas(8, 8)
    rect(image, 0, 0, 8, 2, "gold_light"); rect(image, 0, 2, 8, 3, "gold_dark")
    for x in (1, 5): rect(image, x, 2, 2, 2, "stone_light")
    return image


def ui_edge_vertical() -> Image.Image:
    image = new_canvas(8, 8)
    rect(image, 0, 0, 2, 8, "gold_light"); rect(image, 2, 0, 3, 8, "gold_dark")
    for y in (1, 5): rect(image, 2, y, 2, 2, "stone_light")
    return image


def heart(full: bool) -> Image.Image:
    image = new_canvas(8, 8)
    polygon(image, ((0, 2), (2, 0), (4, 2), (6, 0), (7, 2), (7, 4), (4, 7), (1, 4)), "crimson_dark" if full else "iron_dark")
    if full:
        polygon(image, ((1, 2), (2, 1), (4, 3), (6, 1), (7, 3), (4, 6), (2, 4)), "crimson_mid")
        rect(image, 2, 1, 2, 2, "crimson_light")
    else:
        polygon(image, ((2, 2), (3, 3), (4, 4), (5, 2), (6, 2), (6, 3), (4, 5), (2, 3)), "night_shadow")
    return image


def segmented_bar(fill: str, highlight: str) -> Image.Image:
    image = new_canvas(96, 10, "ink")
    rect(image, 1, 1, 94, 8, "stone_dark"); rect(image, 3, 3, 90, 4, "night_shadow")
    for x in range(4, 92, 6):
        rect(image, x, 3, 5, 4, fill); rect(image, x, 3, 5, 1, highlight)
    rect(image, 1, 1, 94, 1, "gold_dark")
    return image


def subweapon_frame() -> Image.Image:
    image = new_canvas(24, 24)
    polygon(image, ((4, 0), (20, 0), (24 - 1, 4), (23, 20), (20, 23), (4, 23), (0, 20), (0, 4)), "gold_dark")
    polygon(image, ((5, 2), (19, 2), (21, 5), (21, 19), (19, 21), (5, 21), (2, 19), (2, 5)), "stone_light")
    rect(image, 5, 5, 14, 14, "night_shadow")
    for x, y in ((3, 3), (19, 3), (3, 19), (19, 19)): rect(image, x, y, 2, 2, "gold_light")
    return image


def boss_bar() -> Image.Image:
    image = new_canvas(128, 12, "ink")
    rect(image, 1, 1, 126, 10, "gold_shadow")
    polygon(image, ((2, 6), (6, 2), (122, 2), (126, 6), (122, 10), (6, 10)), "stone_dark")
    rect(image, 8, 4, 112, 5, "night_shadow")
    for x in range(9, 119, 5):
        rect(image, x, 4, 4, 5, "crimson_dark"); rect(image, x, 4, 4, 2, "crimson_light")
    rect(image, 61, 3, 6, 7, "gold_mid")
    return image


def build_ui_assets() -> dict[str, Image.Image]:
    return {
        "bg_moon": moon(), "bg_cloud": cloud(), "bg_castle_silhouette": castle_silhouette(),
        "ui_corner": ui_corner(), "ui_edge_horizontal": ui_edge_horizontal(),
        "ui_edge_vertical": ui_edge_vertical(), "ui_heart_full": heart(True),
        "ui_heart_empty": heart(False), "ui_hp_bar": segmented_bar("crimson_mid", "crimson_light"),
        "ui_mana_bar": segmented_bar("teal_mid", "teal_light"),
        "ui_subweapon_frame": subweapon_frame(), "ui_boss_bar": boss_bar(),
    }
