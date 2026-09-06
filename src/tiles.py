"""Seamless terrain and modular gothic architectural tiles."""
from __future__ import annotations


from PIL import Image

from .tools import ellipse, line, new_canvas, outline_rect, pixel, polygon, rect, texture_line


def stone_floor(cracked: bool = False) -> Image.Image:
    image = new_canvas(16, 16, "stone_dark")
    rect(image, 0, 0, 16, 3, "stone_light")
    rect(image, 0, 3, 16, 8, "stone_mid")
    rect(image, 0, 11, 16, 5, "stone_dark")
    texture_line(image, ((0, 7), (15, 7)), "stone_shadow")
    texture_line(image, ((7, 0), (7, 7)), "stone_shadow")
    texture_line(image, ((3, 8), (3, 15)), "stone_shadow")
    for x, y in ((2, 2), (11, 4), (5, 10), (13, 12)):
        pixel(image, x, y, "stone_highlight" if y < 7 else "stone_light")
    if cracked:
        texture_line(image, ((11, 1), (9, 5), (12, 8), (8, 12), (9, 15)), "stone_shadow")
        texture_line(image, ((9, 5), (5, 6), (3, 9)), "stone_shadow")
    return image


def brick_wall(mossy: bool = False) -> Image.Image:
    image = new_canvas(16, 16, "brick_shadow")
    rows = ((0, 0), (5, 4), (10, 0))
    for row_index, (y, offset) in enumerate(rows):
        for x in range(offset - 8, 17, 8):
            left = max(0, x + 1)
            right = min(16, x + 8)
            if right <= left:
                continue
            color = "brick_mid" if (row_index + x // 8) % 2 == 0 else "brick_dark"
            rect(image, left, y, right - left, 4, color)
            if right - left >= 3:
                rect(image, left, y, right - left, 1, "brick_light")
    for y in (4, 9, 14): rect(image, 0, y, 16, 1, "brick_shadow")
    if mossy:
        for x, y in ((1, 3), (2, 4), (10, 8), (11, 9), (14, 10), (5, 13), (6, 14)):
            rect(image, x, y, 2, 2, "moss_dark" if y % 2 else "moss_mid")
    return image


def cobble() -> Image.Image:
    image = new_canvas(16, 16, "stone_shadow")
    stones = ((0, 1, 6, 5), (7, 0, 8, 6), (2, 7, 7, 5), (10, 7, 6, 6), (0, 13, 8, 3), (9, 14, 7, 2))
    for index, (x, y, width, height) in enumerate(stones):
        rect(image, x, y, width, height, "stone_mid" if index % 3 else "stone_dark")
        if width >= 3: rect(image, x, y, width, 1, "stone_light")
        if height >= 3: rect(image, x, y, 1, height, "stone_highlight" if index == 1 else "stone_light")
    return image


def platform() -> Image.Image:
    image = new_canvas(16, 16, "stone_shadow")
    rect(image, 0, 0, 16, 3, "stone_highlight")
    rect(image, 0, 3, 16, 4, "stone_mid")
    rect(image, 0, 7, 16, 2, "stone_dark")
    for x in (1, 8):
        polygon(image, ((x, 9), (x + 6, 9), (x + 4, 15), (x + 2, 15)), "stone_dark")
        rect(image, x + 2, 10, 2, 5, "stone_mid")
    return image


def stairs() -> Image.Image:
    image = new_canvas(16, 16, "stone_shadow")
    for index in range(4):
        x = index * 4
        y = 12 - index * 4
        rect(image, x, y, 16 - x, 4, "stone_mid")
        rect(image, x, y, 16 - x, 2, "stone_light")
        if y + 3 < 16: rect(image, x, y + 3, 16 - x, 1, "stone_dark")
    return image


def pillar() -> Image.Image:
    image = new_canvas(16, 32, "night_shadow")
    rect(image, 1, 0, 14, 5, "stone_dark"); rect(image, 3, 1, 10, 2, "stone_light")
    rect(image, 3, 5, 10, 22, "stone_mid"); rect(image, 4, 5, 3, 22, "stone_light"); rect(image, 10, 5, 3, 22, "stone_shadow")
    rect(image, 1, 27, 14, 5, "stone_dark"); rect(image, 3, 27, 10, 2, "stone_highlight")
    return image


def column() -> Image.Image:
    image = new_canvas(16, 32, "night_shadow")
    polygon(image, ((2, 0), (14, 0), (12, 5), (4, 5)), "stone_mid")
    rect(image, 4, 5, 8, 21, "stone_dark")
    for x, color in ((5, "stone_light"), (8, "stone_mid"), (10, "stone_shadow")):
        rect(image, x, 5, 2, 21, color)
    polygon(image, ((4, 26), (12, 26), (15, 31), (1, 31)), "stone_mid")
    rect(image, 2, 29, 12, 2, "stone_highlight")
    return image


def arch_half(left: bool) -> Image.Image:
    image = new_canvas(16, 16, "night_shadow")
    if left:
        polygon(image, ((0, 0), (15, 0), (15, 4), (12, 5), (9, 8), (7, 12), (6, 15), (0, 15)), "stone_dark")
        line(image, ((14, 2), (10, 6), (7, 11), (5, 15)), "stone_light", 2)
        rect(image, 0, 0, 16, 2, "stone_mid")
    else:
        polygon(image, ((0, 0), (15, 0), (15, 15), (9, 15), (8, 12), (6, 8), (3, 5), (0, 4)), "stone_dark")
        line(image, ((1, 2), (5, 6), (8, 11), (10, 15)), "stone_light", 2)
        rect(image, 0, 0, 16, 2, "stone_mid")
    return image


def arch_keystone() -> Image.Image:
    image = new_canvas(16, 16, "night_shadow")
    polygon(image, ((0, 6), (5, 4), (8, 0), (11, 4), (15, 6), (15, 10), (11, 8), (8, 4), (5, 8), (0, 10)), "stone_dark")
    line(image, ((1, 6), (5, 5), (8, 1), (11, 5), (14, 6)), "stone_highlight", 2)
    polygon(image, ((6, 4), (8, 1), (10, 4), (9, 8), (7, 8)), "stone_mid")
    return image


def lancet_window() -> Image.Image:
    image = new_canvas(16, 32, "stone_dark")
    polygon(image, ((3, 30), (3, 12), (8, 2), (13, 12), (13, 30)), "night_shadow")
    polygon(image, ((5, 29), (5, 13), (8, 6), (11, 13), (11, 29)), "moon_shadow")
    polygon(image, ((6, 27), (6, 14), (8, 9), (9, 15), (9, 27)), "moon_dark")
    rect(image, 7, 11, 2, 18, "stone_shadow")
    rect(image, 4, 20, 8, 2, "stone_shadow")
    rect(image, 0, 30, 16, 2, "stone_light")
    return image


def rose_window() -> Image.Image:
    image = new_canvas(32, 32, "stone_dark")
    ellipse(image, 2, 2, 28, 28, "stone_shadow")
    ellipse(image, 5, 5, 22, 22, "moon_shadow")
    ellipse(image, 9, 9, 14, 14, "teal_dark")
    ellipse(image, 13, 13, 6, 6, "gold_mid")
    for end in ((16, 4), (27, 16), (16, 27), (4, 16), (8, 8), (24, 8), (24, 24), (8, 24)):
        line(image, ((16, 16), end), "stone_dark", 2)
    for x, y in ((13, 6), (21, 9), (24, 17), (19, 23), (10, 22), (6, 15), (9, 9)):
        rect(image, x, y, 3, 3, "crimson_mid" if (x + y) % 2 else "teal_mid")
    return image


def door() -> Image.Image:
    image = new_canvas(16, 32, "stone_dark")
    polygon(image, ((2, 31), (2, 10), (8, 2), (14, 10), (14, 31)), "ink")
    polygon(image, ((4, 31), (4, 11), (8, 5), (12, 11), (12, 31)), "wood_dark")
    rect(image, 5, 13, 3, 18, "wood_mid"); rect(image, 9, 13, 2, 18, "wood_shadow")
    rect(image, 4, 18, 8, 2, "iron_dark"); rect(image, 9, 21, 2, 2, "gold_mid")
    return image


def trim() -> Image.Image:
    image = new_canvas(16, 16, "stone_dark")
    rect(image, 0, 0, 16, 3, "stone_light"); rect(image, 0, 13, 16, 3, "stone_shadow")
    for x in (1, 9):
        ellipse(image, x, 4, 7, 7, "stone_mid")
        rect(image, x + 2, 6, 3, 3, "night_shadow")
    rect(image, 0, 11, 16, 2, "stone_highlight")
    return image


def balcony() -> Image.Image:
    image = new_canvas(16, 16)
    rect(image, 0, 0, 16, 3, "stone_light")
    for x in (1, 7, 13):
        rect(image, x, 3, 3, 10, "stone_dark")
        polygon(image, ((x, 3), (x + 1, 1), (x + 2, 3)), "stone_highlight")
    rect(image, 0, 12, 16, 4, "stone_shadow"); rect(image, 0, 12, 16, 2, "stone_mid")
    return image


def spikes() -> Image.Image:
    image = new_canvas(16, 16)
    for x in (0, 5, 10):
        polygon(image, ((x, 13), (x + 3, 2), (x + 5, 13)), "iron_mid")
        line(image, ((x + 3, 4), (x + 3, 12)), "iron_highlight", 2)
    rect(image, 0, 13, 16, 3, "stone_dark")
    return image


def chain() -> Image.Image:
    image = new_canvas(8, 16)
    for index, y in enumerate((0, 5, 10)):
        x = 1 if index % 2 == 0 else 3
        outline_rect(image, x, y, 4, 6, "iron_mid", 1)
    return image


def roof() -> Image.Image:
    image = new_canvas(16, 16, "night_shadow")
    for row, y in enumerate((0, 5, 10)):
        offset = -3 if row % 2 else 0
        for x in range(offset, 16, 6):
            left = max(0, x)
            width = min(5, 16 - left)
            if width < 2: continue
            polygon(image, ((left, y), (left + width - 1, y), (left + max(1, width // 2), min(15, y + 5))), "night_light" if row == 0 else "night_mid")
            if width >= 3: texture_line(image, ((left, y), (left + width - 1, y)), "moon_shadow")
    return image


def portcullis() -> Image.Image:
    image = new_canvas(16, 32)
    for x in (1, 6, 11):
        rect(image, x, 0, 4, 27, "iron_dark"); rect(image, x + 1, 0, 2, 25, "iron_mid")
        polygon(image, ((x, 26), (x + 2, 31), (x + 4, 26)), "iron_light")
    rect(image, 0, 7, 16, 3, "iron_shadow"); rect(image, 0, 20, 16, 3, "iron_shadow")
    return image


def vine() -> Image.Image:
    image = new_canvas(16, 16)
    line(image, ((2, 0), (5, 4), (4, 8), (9, 11), (8, 15)), "moss_dark", 2)
    for x, y, direction in ((4, 4, 1), (5, 8, -1), (8, 11, 1)):
        polygon(image, ((x, y), (x + direction * 5, y - 2), (x + direction * 3, y + 2)), "moss_mid")
    return image


def rubble() -> Image.Image:
    image = new_canvas(16, 16)
    polygons = (
        (((0, 12), (3, 7), (7, 9), (8, 15)), "stone_dark"),
        (((5, 14), (9, 5), (13, 8), (15, 15)), "stone_mid"),
        (((11, 15), (13, 10), (15, 11), (15, 15)), "stone_light"),
    )
    for points, color in polygons: polygon(image, points, color)
    rect(image, 8, 8, 3, 2, "stone_highlight"); rect(image, 2, 11, 3, 2, "stone_light")
    return image


def ceiling() -> Image.Image:
    image = new_canvas(16, 16, "night_shadow")
    rect(image, 0, 0, 16, 4, "stone_shadow"); rect(image, 0, 3, 16, 3, "stone_mid")
    polygon(image, ((0, 6), (5, 6), (8, 15), (11, 6), (15, 6), (15, 9), (12, 9), (8, 15), (4, 9), (0, 9)), "stone_dark")
    line(image, ((1, 6), (5, 7), (8, 14), (11, 7), (15, 6)), "stone_light", 2)
    return image


def build_tile_assets() -> dict[str, Image.Image]:
    return {
        "tile_stone_floor": stone_floor(), "tile_stone_floor_cracked": stone_floor(True),
        "tile_brick_wall": brick_wall(), "tile_brick_wall_moss": brick_wall(True),
        "tile_cobble": cobble(), "tile_platform": platform(), "tile_stairs": stairs(),
        "tile_pillar": pillar(), "tile_column": column(), "tile_arch_left": arch_half(True),
        "tile_arch_right": arch_half(False), "tile_arch_keystone": arch_keystone(),
        "tile_lancet_window": lancet_window(), "tile_rose_window": rose_window(),
        "tile_door": door(), "tile_trim": trim(), "tile_balcony": balcony(),
        "tile_spikes": spikes(), "tile_chain": chain(), "tile_roof": roof(),
        "tile_portcullis": portcullis(), "tile_vine": vine(), "tile_rubble": rubble(),
        "tile_ceiling": ceiling(),
    }
