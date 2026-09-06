"""Data-driven enemy, prop, sub-weapon, and pickup builders."""
from __future__ import annotations

from collections.abc import Sequence

from PIL import Image

from .tools import Anchor, ellipse, line, map_sprite, new_canvas, outline_rect, polygon, rect, texture_line


def _limb(image: Image.Image, points: Sequence[tuple[int, int]], fill: str, outer: int = 5, inner: int = 3) -> None:
    line(image, points, "ink", outer)
    line(image, points, fill, inner)


def _eye(image: Image.Image, x: int, y: int, color: str = "eye") -> None:
    rect(image, x, y, 2, 2, color)


def _flame(image: Image.Image, center_x: int, top: int, height: int = 9) -> None:
    polygon(image, ((center_x, top), (center_x + 4, top + 4), (center_x + 2, top + height),
                    (center_x - 3, top + height - 1), (center_x - 4, top + 4)), "flame_shadow")
    polygon(image, ((center_x + 1, top + 1), (center_x + 3, top + 5), (center_x + 1, top + height - 1),
                    (center_x - 2, top + height - 2), (center_x - 2, top + 4)), "flame_orange")
    rect(image, center_x, top + 4, 2, max(2, height - 5), "flame_white")


def zombie() -> Image.Image:
    image = new_canvas(32, 40)
    _limb(image, ((12, 26), (10, 32), (8, 38)), "undead_dark")
    _limb(image, ((19, 26), (21, 32), (23, 38)), "undead_mid")
    rect(image, 5, 36, 8, 3, "leather_shadow"); rect(image, 20, 36, 8, 3, "leather_shadow")
    polygon(image, ((8, 14), (20, 12), (25, 18), (22, 29), (9, 29), (6, 20)), "ink")
    polygon(image, ((10, 15), (20, 14), (23, 19), (20, 27), (10, 27), (8, 20)), "moss_dark")
    rect(image, 9, 19, 13, 3, "moss_mid"); rect(image, 11, 24, 5, 3, "undead_dark")
    _limb(image, ((21, 16), (26, 21), (30, 22)), "undead_mid")
    _limb(image, ((9, 17), (5, 22), (3, 27)), "moss_dark")
    ellipse(image, 9, 5, 13, 12, "undead_shadow"); ellipse(image, 11, 6, 10, 9, "undead_mid")
    rect(image, 9, 5, 12, 4, "wood_dark"); rect(image, 11, 5, 8, 2, "wood_light")
    _eye(image, 17, 9); rect(image, 15, 13, 5, 2, "ink")
    return image


def skeleton() -> Image.Image:
    image = new_canvas(32, 40)
    ellipse(image, 10, 3, 12, 11, "bone_shadow"); ellipse(image, 12, 4, 8, 8, "bone_mid")
    rect(image, 13, 12, 6, 4, "bone_dark"); rect(image, 12, 7, 3, 3, "ink"); rect(image, 18, 7, 3, 3, "ink")
    _limb(image, ((15, 15), (14, 25), (12, 31)), "bone_mid", 4, 2)
    for y, width in ((17, 11), (20, 13), (23, 11)):
        rect(image, 16 - width // 2, y, width, 2, "bone_mid")
    rect(image, 14, 17, 2, 9, "ink")
    _limb(image, ((10, 18), (6, 25), (5, 31)), "bone_dark", 4, 2)
    _limb(image, ((22, 18), (26, 24), (27, 30)), "bone_mid", 4, 2)
    _limb(image, ((13, 27), (10, 33), (8, 38)), "bone_dark", 4, 2)
    _limb(image, ((18, 27), (21, 33), (24, 38)), "bone_mid", 4, 2)
    rect(image, 5, 37, 7, 2, "bone_shadow"); rect(image, 22, 37, 7, 2, "bone_shadow")
    return image


def bat(upstroke: bool) -> Image.Image:
    image = new_canvas(32, 24)
    if upstroke:
        polygon(image, ((14, 10), (9, 7), (5, 2), (2, 3), (4, 12), (10, 15)), "purple_shadow")
        polygon(image, ((18, 10), (23, 7), (27, 2), (30, 3), (28, 12), (22, 15)), "purple_shadow")
        polygon(image, ((13, 11), (9, 9), (6, 5), (6, 12), (11, 16)), "purple_mid")
        polygon(image, ((19, 11), (23, 9), (26, 5), (26, 12), (21, 16)), "purple_mid")
    else:
        polygon(image, ((14, 10), (9, 8), (3, 10), (1, 15), (8, 19), (13, 16)), "purple_shadow")
        polygon(image, ((18, 10), (23, 8), (29, 10), (31, 15), (24, 19), (19, 16)), "purple_shadow")
        polygon(image, ((12, 12), (8, 11), (4, 14), (9, 17), (14, 15)), "purple_mid")
        polygon(image, ((20, 12), (24, 11), (28, 14), (23, 17), (18, 15)), "purple_mid")
    polygon(image, ((13, 8), (16, 5), (19, 8), (21, 15), (16, 20), (11, 15)), "ink")
    ellipse(image, 13, 8, 7, 9, "leather_mid"); _eye(image, 14, 10); _eye(image, 18, 10)
    polygon(image, ((13, 8), (12, 4), (15, 7)), "leather_light"); polygon(image, ((19, 8), (20, 4), (17, 7)), "leather_light")
    return image


def medusa_head() -> Image.Image:
    image = new_canvas(28, 24)
    for points in (
        ((11, 8), (6, 4), (2, 6)), ((12, 7), (10, 2), (7, 1)), ((15, 7), (17, 2), (20, 1)),
        ((17, 8), (22, 4), (26, 6)), ((10, 11), (5, 12), (2, 16)), ((18, 11), (23, 12), (26, 16)),
    ):
        line(image, points, "moss_mid", 3)
        ex, ey = points[-1]; rect(image, max(0, ex - 1), max(0, ey - 1), 3, 2, "moss_light")
    ellipse(image, 8, 6, 13, 15, "skin_shadow"); ellipse(image, 10, 8, 10, 11, "skin_mid")
    polygon(image, ((8, 8), (12, 5), (19, 7), (21, 11), (18, 10), (14, 7), (10, 11)), "moss_dark")
    _eye(image, 11, 12); _eye(image, 17, 12); rect(image, 13, 16, 5, 2, "crimson_dark")
    return image


def ghost() -> Image.Image:
    image = new_canvas(32, 32)
    polygon(image, ((16, 2), (23, 5), (27, 12), (26, 22), (30, 27), (23, 25),
                    (19, 30), (15, 26), (10, 30), (9, 24), (3, 26), (6, 18), (5, 11), (10, 5)), "ghost_shadow")
    polygon(image, ((16, 4), (22, 7), (24, 13), (22, 22), (18, 26), (15, 22),
                    (11, 26), (11, 20), (8, 17), (8, 11), (12, 6)), "ghost_mid")
    polygon(image, ((15, 5), (20, 8), (21, 13), (18, 15), (11, 14), (10, 10)), "ghost_light")
    rect(image, 11, 10, 3, 3, "night_shadow"); rect(image, 18, 10, 3, 3, "night_shadow")
    rect(image, 13, 16, 7, 2, "ghost_dark")
    return image


def raven() -> Image.Image:
    image = new_canvas(28, 24)
    polygon(image, ((12, 10), (7, 5), (1, 3), (3, 10), (9, 15)), "purple_shadow")
    polygon(image, ((15, 10), (20, 5), (27, 6), (23, 13), (18, 16)), "purple_dark")
    polygon(image, ((8, 7), (4, 5), (5, 10), (11, 14)), "purple_mid")
    polygon(image, ((11, 8), (18, 8), (21, 14), (17, 19), (10, 17), (8, 12)), "ink")
    polygon(image, ((18, 9), (25, 11), (19, 13)), "gold_dark"); _eye(image, 16, 10)
    line(image, ((12, 17), (10, 21)), "iron_dark", 2); line(image, ((16, 18), (17, 22)), "iron_dark", 2)
    return image


def axe_knight() -> Image.Image:
    image = new_canvas(40, 40)
    _limb(image, ((17, 27), (15, 34), (13, 38)), "iron_dark", 6, 4)
    _limb(image, ((24, 27), (26, 34), (28, 38)), "iron_mid", 6, 4)
    rect(image, 9, 36, 9, 3, "iron_shadow"); rect(image, 25, 36, 9, 3, "iron_shadow")
    polygon(image, ((11, 13), (28, 13), (33, 21), (29, 31), (11, 31), (7, 21)), "ink")
    polygon(image, ((13, 15), (27, 15), (30, 21), (27, 28), (13, 28), (10, 21)), "crimson_dark")
    rect(image, 12, 19, 17, 4, "iron_mid"); rect(image, 14, 19, 7, 2, "iron_highlight")
    ellipse(image, 13, 3, 15, 14, "iron_shadow"); rect(image, 15, 5, 11, 9, "iron_mid")
    rect(image, 14, 9, 13, 3, "ink"); _eye(image, 23, 9)
    _limb(image, ((29, 16), (34, 21), (35, 29)), "crimson_mid", 6, 3)
    line(image, ((35, 8), (35, 33)), "wood_mid", 3)
    polygon(image, ((34, 6), (27, 3), (25, 8), (28, 13), (35, 10)), "iron_light")
    rect(image, 28, 5, 6, 2, "iron_highlight")
    return image


def fleaman() -> Image.Image:
    image = new_canvas(24, 24)
    ellipse(image, 8, 3, 9, 8, "skin_shadow"); rect(image, 10, 5, 6, 5, "skin_mid"); _eye(image, 14, 6)
    polygon(image, ((7, 10), (16, 9), (20, 14), (16, 18), (8, 17), (4, 14)), "crimson_dark")
    rect(image, 9, 11, 8, 4, "crimson_mid")
    _limb(image, ((8, 15), (4, 19), (2, 22)), "skin_dark", 4, 2)
    _limb(image, ((16, 15), (20, 18), (22, 21)), "skin_mid", 4, 2)
    _limb(image, ((10, 17), (8, 21)), "leather_dark", 4, 2)
    _limb(image, ((15, 17), (17, 22)), "leather_dark", 4, 2)
    return image


def hunchback() -> Image.Image:
    image = new_canvas(32, 32)
    _limb(image, ((13, 23), (10, 29)), "leather_dark"); _limb(image, ((20, 23), (23, 29)), "leather_dark")
    polygon(image, ((6, 10), (13, 4), (24, 8), (29, 17), (24, 26), (8, 25), (3, 18)), "ink")
    polygon(image, ((8, 11), (14, 6), (23, 9), (26, 17), (22, 23), (9, 23), (5, 17)), "crimson_shadow")
    polygon(image, ((8, 11), (17, 7), (24, 12), (21, 15), (12, 14)), "crimson_mid")
    ellipse(image, 10, 9, 11, 10, "skin_shadow"); rect(image, 12, 11, 8, 6, "skin_mid"); _eye(image, 18, 12)
    _limb(image, ((22, 17), (27, 21), (29, 25)), "skin_dark")
    return image


def werewolf() -> Image.Image:
    image = new_canvas(36, 36)
    _limb(image, ((14, 25), (10, 31), (6, 34)), "undead_dark", 6, 3)
    _limb(image, ((22, 25), (26, 31), (31, 34)), "undead_mid", 6, 3)
    polygon(image, ((9, 11), (17, 7), (27, 12), (29, 22), (23, 28), (12, 27), (6, 20)), "ink")
    polygon(image, ((11, 13), (18, 9), (25, 13), (27, 21), (22, 25), (13, 25), (8, 20)), "undead_dark")
    polygon(image, ((12, 10), (8, 3), (16, 7)), "undead_mid"); polygon(image, ((22, 9), (26, 3), (27, 13)), "undead_mid")
    polygon(image, ((13, 7), (22, 7), (28, 13), (23, 18), (14, 17), (9, 13)), "undead_mid")
    polygon(image, ((20, 12), (30, 14), (23, 17)), "undead_light"); _eye(image, 18, 11)
    _limb(image, ((10, 16), (5, 22), (2, 28)), "undead_dark", 5, 3)
    _limb(image, ((26, 16), (31, 22), (34, 28)), "undead_mid", 5, 3)
    rect(image, 0, 27, 5, 3, "bone_light"); rect(image, 31, 27, 5, 3, "bone_light")
    return image


def bone_knight() -> Image.Image:
    image = new_canvas(40, 40)
    # Spear and shield establish the silhouette before the skeleton interior.
    line(image, ((34, 2), (34, 38)), "iron_light", 3)
    polygon(image, ((4, 16), (13, 13), (18, 17), (17, 29), (10, 35), (4, 29)), "iron_shadow")
    polygon(image, ((7, 17), (13, 16), (16, 19), (15, 28), (10, 32), (7, 28)), "crimson_dark")
    ellipse(image, 18, 3, 12, 11, "bone_shadow"); ellipse(image, 20, 4, 8, 8, "bone_mid")
    rect(image, 21, 7, 2, 3, "ink"); rect(image, 26, 7, 2, 3, "ink")
    _limb(image, ((24, 14), (24, 27)), "bone_mid", 4, 2)
    for y in (17, 20, 23): rect(image, 19, y, 11, 2, "bone_mid")
    _limb(image, ((21, 26), (20, 33), (18, 38)), "bone_dark", 4, 2)
    _limb(image, ((27, 26), (29, 33), (31, 38)), "bone_mid", 4, 2)
    _limb(image, ((28, 17), (33, 21), (34, 26)), "bone_mid", 4, 2)
    return image


def giant_bat() -> Image.Image:
    image = new_canvas(48, 32)
    polygon(image, ((21, 13), (15, 8), (7, 3), (1, 5), (5, 14), (1, 24), (12, 21), (20, 18)), "purple_shadow")
    polygon(image, ((27, 13), (33, 8), (41, 3), (47, 5), (43, 14), (47, 24), (36, 21), (28, 18)), "purple_shadow")
    polygon(image, ((20, 15), (13, 11), (7, 7), (9, 15), (5, 21), (15, 19)), "purple_mid")
    polygon(image, ((28, 15), (35, 11), (41, 7), (39, 15), (43, 21), (33, 19)), "purple_mid")
    polygon(image, ((19, 9), (24, 5), (29, 9), (32, 21), (24, 29), (16, 21)), "ink")
    ellipse(image, 19, 10, 11, 14, "leather_mid"); _eye(image, 20, 13); _eye(image, 27, 13)
    polygon(image, ((19, 10), (17, 4), (22, 8)), "leather_light"); polygon(image, ((29, 10), (31, 4), (26, 8)), "leather_light")
    return image


def gargoyle() -> Image.Image:
    image = new_canvas(36, 36)
    polygon(image, ((11, 13), (4, 8), (2, 22), (10, 18), (13, 27)), "stone_shadow")
    polygon(image, ((25, 13), (32, 8), (34, 22), (26, 18), (23, 27)), "stone_shadow")
    polygon(image, ((9, 15), (14, 9), (23, 9), (28, 17), (24, 28), (12, 28)), "ink")
    polygon(image, ((12, 15), (16, 11), (22, 11), (25, 17), (22, 25), (14, 25)), "stone_mid")
    polygon(image, ((14, 10), (12, 3), (18, 8)), "stone_light"); polygon(image, ((22, 10), (25, 3), (25, 13)), "stone_light")
    _eye(image, 15, 14); _eye(image, 21, 14)
    _limb(image, ((14, 25), (10, 32), (6, 34)), "stone_dark", 5, 3)
    _limb(image, ((22, 25), (26, 32), (31, 34)), "stone_mid", 5, 3)
    return image


def merman() -> Image.Image:
    image = new_canvas(32, 36)
    line(image, ((27, 2), (27, 34)), "iron_light", 3)
    line(image, ((23, 5), (27, 2), (31, 5)), "iron_light", 2)
    _limb(image, ((13, 24), (10, 31), (8, 34)), "teal_dark", 5, 3)
    _limb(image, ((20, 24), (22, 31), (25, 34)), "teal_mid", 5, 3)
    polygon(image, ((8, 12), (20, 10), (25, 16), (23, 27), (10, 27), (6, 18)), "ink")
    polygon(image, ((10, 13), (19, 12), (22, 16), (21, 24), (11, 24), (8, 18)), "teal_mid")
    for x, y in ((11, 17), (16, 15), (19, 19), (13, 22)): rect(image, x, y, 3, 2, "teal_light")
    ellipse(image, 10, 3, 12, 11, "teal_dark"); polygon(image, ((13, 4), (21, 5), (25, 9), (20, 11), (12, 10)), "teal_mid")
    _eye(image, 18, 7); _limb(image, ((21, 14), (25, 19), (27, 23)), "teal_light", 5, 3)
    return image


def armor_lord() -> Image.Image:
    image = new_canvas(40, 44)
    _limb(image, ((15, 31), (13, 38), (11, 42)), "iron_dark", 7, 4)
    _limb(image, ((25, 31), (27, 38), (29, 42)), "iron_mid", 7, 4)
    rect(image, 6, 40, 11, 3, "iron_shadow"); rect(image, 25, 40, 11, 3, "iron_shadow")
    polygon(image, ((7, 14), (14, 10), (27, 10), (34, 15), (36, 27), (29, 34), (11, 34), (4, 27)), "ink")
    polygon(image, ((10, 15), (15, 12), (26, 12), (31, 16), (33, 26), (27, 31), (13, 31), (7, 26)), "iron_mid")
    rect(image, 8, 20, 25, 4, "gold_dark"); rect(image, 13, 20, 15, 2, "gold_light")
    ellipse(image, 12, 1, 17, 15, "iron_shadow"); rect(image, 14, 4, 13, 10, "iron_mid")
    polygon(image, ((13, 4), (20, 0), (28, 4)), "iron_light"); rect(image, 13, 9, 15, 3, "ink"); _eye(image, 24, 9)
    _limb(image, ((8, 17), (3, 23), (3, 31)), "iron_dark", 7, 4)
    _limb(image, ((32, 17), (37, 23), (37, 31)), "iron_mid", 7, 4)
    return image


def warg() -> Image.Image:
    image = new_canvas(40, 28)
    polygon(image, ((7, 10), (16, 5), (29, 8), (36, 13), (32, 21), (17, 22), (8, 18), (2, 15)), "ink")
    polygon(image, ((9, 11), (17, 7), (28, 10), (33, 13), (30, 19), (17, 20), (9, 17), (4, 15)), "undead_dark")
    polygon(image, ((29, 9), (34, 4), (35, 12)), "undead_mid"); polygon(image, ((23, 9), (26, 3), (30, 10)), "undead_mid")
    polygon(image, ((30, 12), (39, 14), (32, 18)), "undead_light"); _eye(image, 31, 11)
    _limb(image, ((12, 19), (8, 25), (4, 26)), "undead_dark", 5, 3)
    _limb(image, ((19, 20), (17, 25), (14, 26)), "undead_mid", 5, 3)
    _limb(image, ((27, 19), (31, 24), (36, 25)), "undead_mid", 5, 3)
    return image


def phantom() -> Image.Image:
    image = new_canvas(32, 40)
    polygon(image, ((16, 2), (23, 7), (28, 18), (25, 29), (30, 37), (21, 34),
                    (16, 39), (11, 34), (3, 37), (7, 28), (4, 18), (9, 7)), "ink")
    polygon(image, ((16, 5), (21, 8), (25, 18), (22, 30), (16, 35), (10, 30), (7, 18), (11, 8)), "purple_shadow")
    polygon(image, ((12, 10), (20, 9), (23, 16), (20, 21), (12, 21), (9, 16)), "night_shadow")
    rect(image, 12, 14, 3, 3, "ghost_light"); rect(image, 19, 14, 3, 3, "ghost_light")
    polygon(image, ((8, 23), (16, 26), (24, 23), (21, 32), (16, 35), (11, 31)), "purple_dark")
    return image


def succubus() -> Image.Image:
    image = new_canvas(40, 40)
    polygon(image, ((14, 15), (8, 8), (1, 7), (5, 18), (2, 28), (12, 23)), "purple_shadow")
    polygon(image, ((26, 15), (32, 8), (39, 7), (35, 18), (38, 28), (28, 23)), "purple_shadow")
    polygon(image, ((15, 14), (20, 10), (25, 14), (28, 25), (23, 34), (16, 34), (12, 25)), "ink")
    polygon(image, ((17, 15), (20, 12), (23, 15), (25, 25), (22, 31), (17, 31), (15, 25)), "crimson_dark")
    ellipse(image, 15, 3, 11, 11, "skin_shadow"); ellipse(image, 17, 5, 8, 8, "skin_mid")
    polygon(image, ((15, 6), (17, 1), (21, 5), (25, 1), (26, 8), (21, 5)), "purple_dark")
    _eye(image, 22, 7)
    _limb(image, ((16, 31), (13, 36), (10, 38)), "skin_dark", 4, 2)
    _limb(image, ((23, 31), (26, 36), (30, 38)), "skin_mid", 4, 2)
    return image


def reaper() -> Image.Image:
    image = new_canvas(48, 48)
    # Scythe is a continuous 3px shaft with a broad crescent, never a hairline.
    line(image, ((38, 5), (32, 42)), "wood_light", 3)
    polygon(image, ((37, 6), (43, 2), (47, 3), (42, 8), (35, 13), (28, 12), (34, 9)), "iron_light")
    polygon(image, ((13, 8), (24, 4), (33, 11), (35, 25), (31, 36), (37, 44),
                    (27, 41), (22, 47), (17, 41), (8, 44), (12, 34), (7, 25)), "ink")
    polygon(image, ((15, 10), (23, 7), (30, 12), (32, 25), (28, 35), (23, 41),
                    (17, 37), (11, 40), (15, 31), (10, 24)), "purple_shadow")
    polygon(image, ((17, 11), (26, 10), (30, 17), (27, 23), (16, 23), (12, 17)), "night_shadow")
    rect(image, 16, 16, 3, 3, "ghost_light"); rect(image, 25, 16, 3, 3, "ghost_light")
    _limb(image, ((30, 22), (35, 27), (34, 33)), "bone_dark", 5, 3)
    return image


# ---------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------
def candle() -> Image.Image:
    image = new_canvas(16, 24); _flame(image, 8, 1, 8)
    rect(image, 5, 9, 7, 11, "bone_mid"); rect(image, 6, 9, 2, 8, "bone_light")
    rect(image, 9, 12, 3, 3, "bone_dark"); rect(image, 3, 20, 11, 3, "gold_dark"); rect(image, 5, 20, 7, 1, "gold_light")
    return image


def candelabrum() -> Image.Image:
    image = new_canvas(24, 32)
    for x in (5, 12, 19): _flame(image, x, 1 if x == 12 else 4, 7)
    line(image, ((5, 11), (5, 15), (12, 18), (19, 15), (19, 11)), "gold_mid", 3)
    line(image, ((12, 9), (12, 28)), "gold_dark", 3)
    rect(image, 7, 28, 11, 3, "gold_dark"); rect(image, 9, 28, 7, 1, "gold_light")
    return image


def wall_sconce() -> Image.Image:
    image = new_canvas(16, 20); _flame(image, 8, 1, 7)
    rect(image, 6, 8, 5, 6, "bone_mid"); line(image, ((8, 14), (12, 17), (14, 17)), "iron_mid", 3)
    rect(image, 12, 12, 3, 8, "iron_dark"); return image


def torch() -> Image.Image:
    image = new_canvas(16, 24); _flame(image, 8, 1, 10)
    polygon(image, ((4, 10), (12, 10), (10, 15), (6, 15)), "iron_mid")
    line(image, ((8, 14), (8, 22)), "wood_mid", 3); rect(image, 5, 21, 7, 2, "iron_dark")
    return image


def brazier() -> Image.Image:
    image = new_canvas(24, 24); _flame(image, 12, 1, 10)
    polygon(image, ((3, 10), (21, 10), (18, 17), (6, 17)), "stone_shadow")
    polygon(image, ((5, 11), (19, 11), (17, 15), (7, 15)), "stone_mid")
    line(image, ((9, 16), (8, 22)), "iron_dark", 3); line(image, ((15, 16), (16, 22)), "iron_dark", 3)
    rect(image, 5, 21, 14, 3, "stone_dark"); return image


def iron_gate() -> Image.Image:
    image = new_canvas(32, 40)
    for x in (3, 9, 15, 21, 27):
        polygon(image, ((x, 0), (x + 2, 4), (x + 4, 0), (x + 4, 37), (x, 37)), "iron_dark")
        rect(image, x + 1, 5, 2, 30, "iron_mid")
    rect(image, 1, 12, 30, 4, "iron_shadow"); rect(image, 1, 27, 30, 4, "iron_shadow")
    for x in range(3, 28, 6): rect(image, x, 13, 4, 2, "iron_light")
    return image


def gargoyle_statue() -> Image.Image:
    image = new_canvas(24, 32)
    polygon(image, ((7, 10), (4, 4), (10, 8)), "stone_light"); polygon(image, ((17, 10), (20, 4), (14, 8)), "stone_light")
    ellipse(image, 6, 7, 13, 11, "stone_mid"); rect(image, 8, 11, 3, 2, "ink"); rect(image, 15, 11, 3, 2, "ink")
    polygon(image, ((5, 17), (19, 17), (21, 26), (16, 28), (12, 23), (8, 28), (3, 26)), "stone_dark")
    rect(image, 1, 27, 22, 4, "stone_shadow"); rect(image, 3, 27, 18, 2, "stone_light"); return image


def sarcophagus() -> Image.Image:
    image = new_canvas(24, 40)
    polygon(image, ((8, 1), (16, 1), (21, 8), (19, 36), (15, 39), (9, 39), (5, 36), (3, 8)), "stone_shadow")
    polygon(image, ((9, 3), (15, 3), (19, 9), (17, 34), (14, 37), (10, 37), (7, 34), (5, 9)), "stone_mid")
    ellipse(image, 8, 6, 8, 8, "stone_highlight"); rect(image, 10, 15, 4, 13, "stone_light")
    line(image, ((7, 18), (12, 23), (17, 18)), "stone_highlight", 2); rect(image, 7, 32, 10, 2, "stone_dark")
    return image


def crate() -> Image.Image:
    image = new_canvas(20, 20); rect(image, 1, 1, 18, 18, "wood_dark"); outline_rect(image, 1, 1, 18, 18, "iron_shadow", 2)
    polygon(image, ((4, 3), (7, 3), (16, 16), (13, 16)), "wood_light")
    polygon(image, ((13, 3), (16, 3), (7, 16), (4, 16)), "wood_mid")
    rect(image, 8, 8, 4, 4, "iron_mid"); return image


def barrel() -> Image.Image:
    image = new_canvas(20, 24)
    polygon(image, ((5, 1), (15, 1), (18, 5), (18, 19), (15, 23), (5, 23), (2, 19), (2, 5)), "wood_shadow")
    rect(image, 4, 3, 12, 18, "wood_mid"); rect(image, 5, 3, 3, 18, "wood_light")
    for y in (4, 11, 18): rect(image, 2, y, 16, 3, "iron_dark")
    return image


def hanging_chain() -> Image.Image:
    image = new_canvas(12, 32)
    for index, y in enumerate(range(1, 25, 5)):
        x = 3 if index % 2 == 0 else 5
        outline_rect(image, x, y, 5, 7, "iron_mid", 1)
    return image


def banner() -> Image.Image:
    image = new_canvas(20, 36); line(image, ((2, 3), (18, 3)), "gold_mid", 3)
    polygon(image, ((4, 5), (16, 5), (16, 29), (13, 34), (10, 30), (7, 35), (4, 30)), "crimson_shadow")
    polygon(image, ((6, 6), (14, 6), (14, 27), (10, 30), (6, 28)), "crimson_mid")
    polygon(image, ((10, 10), (13, 17), (10, 24), (7, 17)), "gold_mid"); rect(image, 9, 14, 3, 7, "gold_light")
    return image


def bookshelf() -> Image.Image:
    image = new_canvas(32, 40); rect(image, 1, 1, 30, 39, "wood_shadow"); outline_rect(image, 1, 1, 30, 39, "iron_shadow", 2)
    for y in (12, 25, 36): rect(image, 3, y, 26, 3, "wood_light")
    colors = ("crimson_dark", "navy_mid", "moss_dark", "purple_mid", "bone_dark", "teal_dark")
    for shelf, base_y in enumerate((4, 15, 28)):
        x = 4
        for index, width in enumerate((3, 4, 3, 5, 3)):
            height = 7 + ((index + shelf) % 3)
            rect(image, x, base_y + 8 - height, width, height, colors[(index + shelf) % len(colors)])
            x += width + 1
    return image


def altar() -> Image.Image:
    image = new_canvas(32, 24); rect(image, 2, 8, 28, 5, "stone_mid"); rect(image, 4, 13, 24, 9, "stone_dark")
    rect(image, 6, 13, 4, 7, "stone_light"); rect(image, 22, 13, 4, 7, "stone_shadow")
    polygon(image, ((12, 8), (16, 2), (20, 8)), "gold_dark"); rect(image, 15, 3, 3, 6, "gold_light")
    rect(image, 1, 21, 30, 3, "stone_shadow"); return image


def coffin() -> Image.Image:
    image = new_canvas(24, 40)
    polygon(image, ((8, 1), (16, 1), (21, 9), (19, 31), (15, 39), (9, 39), (5, 31), (3, 9)), "ink")
    polygon(image, ((9, 3), (15, 3), (19, 10), (17, 30), (14, 36), (10, 36), (7, 30), (5, 10)), "wood_dark")
    polygon(image, ((12, 8), (15, 15), (13, 15), (13, 28), (10, 28), (10, 15), (8, 15)), "gold_dark")
    rect(image, 11, 9, 3, 18, "gold_mid"); return image


def chandelier() -> Image.Image:
    image = new_canvas(40, 24); line(image, ((20, 0), (20, 8)), "iron_mid", 3)
    line(image, ((5, 14), (12, 18), (20, 19), (28, 18), (35, 14)), "iron_dark", 3)
    line(image, ((20, 7), (12, 16)), "iron_mid", 2); line(image, ((20, 7), (28, 16)), "iron_mid", 2)
    for x in (5, 13, 27, 35):
        rect(image, x - 1, 10, 3, 6, "bone_mid"); _flame(image, x, 3, 7)
    return image


def breakable_wall() -> Image.Image:
    image = new_canvas(32, 32)
    for y, offset in ((2, 2), (10, -5), (18, 2), (26, -5)):
        for x in range(offset, 32, 12):
            if x < 0: continue
            width = min(10, 30 - x)
            if width > 0: rect(image, x, y, width, 6, "brick_mid" if (x + y) % 3 else "brick_dark")
    line(image, ((17, 1), (14, 9), (18, 15), (12, 22), (15, 30)), "ink", 2)
    texture_line(image, ((14, 9), (7, 12), (3, 17)), "brick_shadow")
    texture_line(image, ((18, 15), (26, 17), (30, 22)), "brick_shadow")
    return image


def throne() -> Image.Image:
    image = new_canvas(28, 40)
    polygon(image, ((6, 2), (22, 2), (25, 7), (23, 30), (19, 32), (9, 32), (5, 29), (3, 7)), "wood_shadow")
    polygon(image, ((8, 5), (20, 5), (22, 9), (20, 27), (8, 27), (6, 9)), "crimson_shadow")
    polygon(image, ((10, 7), (18, 7), (19, 24), (9, 24)), "crimson_mid")
    polygon(image, ((14, 8), (17, 14), (14, 21), (11, 14)), "gold_mid")
    rect(image, 2, 25, 24, 6, "wood_dark"); rect(image, 5, 30, 5, 10, "wood_shadow"); rect(image, 18, 30, 5, 10, "wood_shadow")
    return image


# ---------------------------------------------------------------------------
# ASCII-authored sub-weapons and pickups.  Maps are strict and never padded.
# ---------------------------------------------------------------------------
def _ascii(rows: tuple[str, ...], size: tuple[int, int]) -> Image.Image:
    return map_sprite(rows, size, Anchor("center", "center"))


def dagger() -> Image.Image:
    return _ascii((
        "..........JJ", "........JJJJ", "......JJJJ..", "....JJJJ....", "..JJJJ......", "JJJJ........",
        ".yy.........", "yyyy........", ".GG.........", ".GG.........", "............", "............",
    ), (16, 16))


def axe() -> Image.Image:
    return _ascii((
        "...JJJJJ....", ".JJJJJJJJ...", "JJJQQQJJJ...", "JJQQQQQJJ...", ".JJQQQJJ....", "...JJJJ.....",
        "....ccc.....", "....ccc.....", "...ccccc....", "..ccc.ccc...", ".ccc...ccc..", "............",
    ), (16, 16))


def holy_water() -> Image.Image:
    return _ascii((
        "....JJJJ....", "...JJJJJJ...", "...QQQQQQ...", "..QQ{{{{QQ..", ".QQ{{}}{{QQ.", ".QQ{{{{{{QQ.",
        ".QQ]{{{{]QQ.", "..QQ{{{{QQ..", "...QQQQQQ...", "....QQQQ....", "....QQQQ....", "............",
    ), (16, 18))


def cross() -> Image.Image:
    return _ascii((
        "....yyyy....", "....yYYy....", "....yYYy....", ".yyyYYYYyyy.", ".yYYYYYYYYy.", ".yyyYYYYyyy.",
        "....yYYy....", "....yYYy....", "....yYYy....", "....yyyy....", "............", "............",
    ), (16, 16))


def stopwatch() -> Image.Image:
    return _ascii((
        "....JJJJ....", "...JJyyJJ...", "....yyyy....", "..JJJJJJJJ..", ".JJhhhhhhJJ.", ".JhhyyhhhhJ.",
        ".JhhhyyhhhJ.", ".JhhhhhhhhJ.", ".JJhhhhhhJJ.", "..JJJJJJJJ..", "....Q..Q....", "............",
    ), (16, 18))


def bible() -> Image.Image:
    return _ascii((
        ".kkkkkkkkkkkkkk.", "kxxxxxxxxxxxxxxk", "kxvvvvvvvvvvvvxk", "kxvvvyyyyvvvvvxk", "kxvvvYyyYvvvvvxk",
        "kxvyyyyyyyyyyvxk", "kxvvvYyyYvvvvvxk", "kxvvvyyyyvvvvvxk", "kxvvvvvvvvvvvvxk", "kxxxxxxxxxxxxxxk",
        ".kkkkkkkkkkkkkk.", "................",
    ), (20, 18))


def heart(big: bool) -> Image.Image:
    rows = (
        "...VV...VV...", "..VVVV.VVVV..", ".VVVVVVVVVVV.", ".VVVvvvvvVVV.", "..VVvvvvvVV..", "...VvvvvvV...",
        "....VvvvV....", ".....VvV.....", "......V......", ".............", ".............", ".............",
    ) if big else (
        "............", "....VV.VV...", "...VVVVVVV..", "...VVvvVVV..", "....VvvvV...", ".....VvV....",
        "......V.....", "............", "............", "............", "............", "............",
    )
    return _ascii(rows, (16, 16))


def meat() -> Image.Image:
    return _ascii((
        "..zz......zz..", ".zZZz....zZZz.", "..zzVVVVzz....", "...VVVVVVVV...", "..VVvvvvVVVV..", ".VVvvvvvvvvVV.",
        ".VVvvvvvvVVVV.", "..VVVVVVVVV...", "...VVVVVV.....", "..............",
    ), (18, 16))


def gold_pickup() -> Image.Image:
    return _ascii((
        "....yyyy....", "..yyYYYYyy..", ".yYYYYYYYYy.", ".yYYyyyyYYy.", ".yYyyyyyyYy.", ".yYYyyyyYYy.",
        "..yYYYYYYy..", "...yyyyyy...", "..GGGGGGGG..", ".GGyyyyyyGG.", "..GGGGGGGG..", "............",
    ), (16, 16))


def potion(color_dark: str, color_mid: str, color_light: str) -> Image.Image:
    image = new_canvas(16, 20)
    rect(image, 5, 1, 6, 4, "iron_mid"); rect(image, 6, 1, 4, 2, "iron_highlight")
    polygon(image, ((4, 4), (12, 4), (15, 9), (14, 17), (11, 19), (5, 19), (2, 17), (1, 9)), "iron_shadow")
    polygon(image, ((5, 6), (11, 6), (13, 10), (12, 16), (10, 17), (6, 17), (4, 16), (3, 10)), color_dark)
    rect(image, 5, 9, 7, 6, color_mid); rect(image, 6, 9, 3, 4, color_light)
    return image


def whip_upgrade() -> Image.Image:
    image = new_canvas(20, 18); line(image, ((4, 13), (2, 9), (4, 4), (9, 2), (15, 4), (17, 9), (14, 14), (9, 15)), "leather_light", 3)
    rect(image, 7, 13, 7, 3, "gold_dark"); rect(image, 9, 13, 4, 2, "gold_light"); return image


def armor_pickup() -> Image.Image:
    image = new_canvas(18, 20)
    polygon(image, ((4, 2), (8, 1), (10, 1), (14, 2), (17, 7), (15, 17), (9, 19), (3, 17), (1, 7)), "iron_shadow")
    polygon(image, ((5, 4), (8, 3), (10, 3), (13, 4), (15, 8), (13, 15), (9, 17), (5, 15), (3, 8)), "iron_mid")
    rect(image, 5, 7, 8, 3, "iron_highlight"); rect(image, 8, 5, 3, 11, "iron_dark"); return image


def rosary() -> Image.Image:
    image = new_canvas(18, 18)
    for x, y in ((5, 3), (9, 2), (13, 4), (15, 8), (13, 12), (9, 14), (5, 12), (3, 8)):
        rect(image, x - 1, y - 1, 3, 3, "gold_mid")
    rect(image, 8, 12, 3, 6, "gold_dark"); rect(image, 6, 14, 7, 3, "gold_light"); return image


def mana() -> Image.Image:
    image = new_canvas(16, 18)
    polygon(image, ((8, 0), (14, 6), (11, 16), (8, 17), (5, 16), (2, 6)), "teal_shadow")
    polygon(image, ((8, 2), (12, 7), (10, 14), (8, 16), (6, 14), (4, 7)), "teal_mid")
    polygon(image, ((8, 3), (9, 12), (7, 14), (6, 7)), "teal_light"); return image


def build_sprite_assets() -> dict[str, Image.Image]:
    return {
        "enemy_zombie": zombie(), "enemy_skeleton": skeleton(),
        "enemy_bat_0": bat(True), "enemy_bat_1": bat(False),
        "enemy_medusa_head": medusa_head(), "enemy_ghost": ghost(), "enemy_raven": raven(),
        "enemy_axe_knight": axe_knight(), "enemy_fleaman": fleaman(), "enemy_hunchback": hunchback(),
        "enemy_werewolf": werewolf(), "enemy_bone_knight": bone_knight(), "enemy_giant_bat": giant_bat(),
        "enemy_gargoyle": gargoyle(), "enemy_merman": merman(), "enemy_armor_lord": armor_lord(),
        "enemy_warg": warg(), "enemy_phantom": phantom(), "enemy_succubus": succubus(), "enemy_reaper": reaper(),
        "prop_candle": candle(), "prop_candelabrum": candelabrum(), "prop_wall_sconce": wall_sconce(),
        "prop_torch": torch(), "prop_brazier": brazier(), "prop_iron_gate": iron_gate(),
        "prop_gargoyle_statue": gargoyle_statue(), "prop_sarcophagus": sarcophagus(),
        "prop_crate": crate(), "prop_barrel": barrel(), "prop_hanging_chain": hanging_chain(),
        "prop_banner": banner(), "prop_bookshelf": bookshelf(), "prop_altar": altar(), "prop_coffin": coffin(),
        "prop_chandelier": chandelier(), "prop_breakable_wall": breakable_wall(), "prop_throne": throne(),
        "sub_dagger": dagger(), "sub_axe": axe(), "sub_holy_water": holy_water(), "sub_cross": cross(),
        "sub_stopwatch": stopwatch(), "sub_bible": bible(),
        "pickup_heart_small": heart(False), "pickup_heart_big": heart(True), "pickup_meat": meat(),
        "pickup_gold": gold_pickup(), "pickup_potion_red": potion("crimson_shadow", "crimson_mid", "crimson_light"),
        "pickup_potion_blue": potion("teal_shadow", "teal_mid", "teal_light"),
        "pickup_whip_upgrade": whip_upgrade(), "pickup_armor": armor_pickup(),
        "pickup_rosary": rosary(), "pickup_mana": mana(),
    }
