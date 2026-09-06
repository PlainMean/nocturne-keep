"""Palette-locked cathedral hall scene with deterministic gothic depth."""
from __future__ import annotations

import random
from collections.abc import Mapping, Sequence

from PIL import Image, ImageDraw

from .palette import rgba
from .tools import blit, dither_disc, ellipse, line, nearest, new_canvas, pixel, polygon, rect, texture_line

WIDTH, HEIGHT = 480, 270
FLOOR_Y = 188
GROUND_Y = 258
SCENE_SCALE = 3
SCENE_SIZE = (WIDTH * SCENE_SCALE, HEIGHT * SCENE_SCALE)


def _dither_polygon(
    image: Image.Image,
    points: Sequence[tuple[int, int]],
    color: str,
    period: int,
    phase: int = 0,
) -> None:
    mask = Image.new("1", image.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=1)
    value = rgba(color)
    for y in range(image.height):
        for x in range(image.width):
            if mask.getpixel((x, y)) and (x + y * 3 + phase) % period == 0:
                image.putpixel((x, y), value)


def _sky(image: Image.Image) -> None:
    # Only the strip above the masonry is open sky; window depth is composed
    # explicitly later so no hidden background work is overwritten.
    rect(image, 0, 0, WIDTH, 20, "night_shadow")
    rng = random.Random(1603)
    for _ in range(34):
        x, y = rng.randrange(3, WIDTH - 3), rng.randrange(2, 19)
        color = "moon_light" if (x * 5 + y) % 7 == 0 else "moon_mid"
        pixel(image, x, y, color)


def _brick_wall(image: Image.Image) -> None:
    rect(image, 0, 20, WIDTH, FLOOR_Y - 20, "brick_shadow")
    rng = random.Random(1147)
    brick_width, brick_height = 24, 10
    for row, y in enumerate(range(22, FLOOR_Y - 2, brick_height)):
        offset = 0 if row % 2 == 0 else brick_width // 2
        for x in range(offset, WIDTH, brick_width):
            width = min(brick_width - 2, WIDTH - x)
            if width <= 0:
                continue
            choice = rng.randrange(6)
            color = "brick_mid" if choice < 3 else "brick_dark" if choice < 5 else "stone_shadow"
            rect(image, x, y, width, brick_height - 2, color)
            rect(image, x, y, width, 1, "brick_light")
        rect(image, 0, y + brick_height - 2, WIDTH, 2, "brick_shadow")
    # Sparse weathering stays subordinate to large architectural forms.
    for x, y in ((42, 53), (91, 112), (171, 68), (304, 121), (398, 54), (441, 151)):
        texture_line(image, ((x, y), (x - 3, y + 7), (x + 2, y + 13), (x - 4, y + 20)), "stone_shadow")
    for x, y in ((23, 119), (26, 121), (453, 93), (456, 95), (315, 51), (318, 51)):
        rect(image, x, y, 3, 2, "moss_dark")


def _lancet(
    image: Image.Image,
    x: int,
    apex_y: int,
    width: int,
    bottom: int,
    moonlit: bool = False,
) -> None:
    center = x + width // 2
    spring = apex_y + width // 2
    outer = ((x, bottom), (x, spring), (center, apex_y), (x + width, spring), (x + width, bottom))
    polygon(image, outer, "stone_shadow")
    inset = 6
    inner = ((x + inset, bottom - 4), (x + inset, spring + 2), (center, apex_y + 9),
             (x + width - inset, spring + 2), (x + width - inset, bottom - 4))
    polygon(image, inner, "night_shadow")
    if moonlit:
        _dither_polygon(image, inner, "moon_shadow", 5, 1)
    line(image, ((x + 2, bottom - 2), (x + 2, spring), (center, apex_y + 2),
                 (x + width - 2, spring), (x + width - 2, bottom - 2)), "stone_mid", 4)
    line(image, ((x + 5, bottom - 4), (x + 5, spring + 2), (center, apex_y + 8),
                 (x + width - 5, spring + 2), (x + width - 5, bottom - 4)), "stone_highlight", 2)
    _lancet_tracery(image, x, apex_y, width, bottom)
    rect(image, x - 3, bottom - 5, width + 6, 5, "stone_dark")
    rect(image, x, bottom - 5, width, 2, "stone_light")


def _lancet_tracery(image: Image.Image, x: int, apex_y: int, width: int, bottom: int) -> None:
    center = x + width // 2
    spring = apex_y + width // 2
    rect(image, center - 1, apex_y + 10, 3, bottom - apex_y - 15, "stone_dark")
    cross_y = spring + (bottom - spring) // 2
    rect(image, x + 5, cross_y, width - 10, 3, "stone_dark")


def _window_depth(
    image: Image.Image,
    assets: Mapping[str, Image.Image],
    x: int,
    bottom: int,
) -> None:
    cloud_slice = assets["bg_cloud"].crop((7, 0, 41, 20))
    castle_slice = assets["bg_castle_silhouette"].crop((29, 0, 67, 48))
    blit(image, cloud_slice, x + 8, bottom - 80)
    blit(image, castle_slice, x + 6, bottom - 52)


def _column(image: Image.Image, x: int, top: int, bottom: int, width: int) -> None:
    if bottom <= top + 14:
        raise ValueError("column is too short")
    rect(image, x, top + 7, width, bottom - top - 14, "stone_shadow")
    rect(image, x + 3, top + 7, width - 6, bottom - top - 14, "stone_dark")
    rect(image, x + 5, top + 7, 3, bottom - top - 14, "stone_light")
    rect(image, x + width - 8, top + 7, 3, bottom - top - 14, "stone_mid")
    rect(image, x - 4, top, width + 8, 7, "stone_mid")
    rect(image, x - 1, top, width + 2, 2, "stone_highlight")
    polygon(image, ((x - 5, top + 7), (x + width + 4, top + 7), (x + width, top + 13), (x, top + 13)), "stone_dark")
    rect(image, x - 5, bottom - 8, width + 10, 8, "stone_shadow")
    rect(image, x - 2, bottom - 8, width + 4, 3, "stone_light")


def _vaults(image: Image.Image) -> None:
    # Four clustered piers and intersecting ribs create a nave, not a truss.
    for x in (18, 118, 342, 442):
        _column(image, x, 35 if x in (18, 442) else 68, FLOOR_Y, 20)
    left_rib = ((28, 44), (55, 24), (82, 12), (128, 4), (176, 15), (215, 45))
    right_rib = tuple((WIDTH - 1 - x, y) for x, y in left_rib)
    line(image, left_rib, "stone_dark", 6); line(image, left_rib, "stone_light", 2)
    line(image, right_rib, "stone_dark", 6); line(image, right_rib, "stone_light", 2)
    central_rib = ((128, 74), (153, 48), (190, 22), (240, 3), (290, 22), (327, 48), (362, 74))
    line(image, central_rib, "stone_shadow", 7); line(image, central_rib, "stone_mid", 3)
    # Small stone bosses where ribs cross.
    for x, y in ((128, 5), (240, 3), (352, 5)):
        polygon(image, ((x, y), (x + 4, y + 4), (x, y + 8), (x - 4, y + 4)), "gold_dark")
        rect(image, x - 1, y + 2, 3, 4, "gold_light")


def _floor(image: Image.Image) -> None:
    rect(image, 0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y, "stone_dark")
    # Moonlight reaches the floor before slab seams are drawn over it.
    _dither_polygon(image, ((222, 126), (258, 126), (354, 269), (116, 269)), "moon_shadow", 6, 2)
    _dither_polygon(image, ((230, 126), (250, 126), (304, 269), (172, 269)), "night_light", 5, 1)
    row_edges = (FLOOR_Y, 197, 209, 224, 244, 269)
    for y in row_edges:
        rect(image, 0, y, WIDTH, 2 if y < HEIGHT - 1 else 1, "stone_shadow")
    for bottom_x in range(-40, WIDTH + 80, 40):
        line(image, ((240, FLOOR_Y), (max(0, min(WIDTH - 1, bottom_x)), HEIGHT - 1)), "stone_shadow", 2)
    # Worn upper edges and deterministic chips add scale without visual noise.
    for x, y in ((31, 213), (76, 250), (143, 233), (218, 201), (279, 247), (366, 220), (432, 258)):
        rect(image, x, y, 6, 2, "stone_light")
        pixel(image, x + 2, y + 2, "stone_shadow")


def _contact_shadow(image: Image.Image, x: int, baseline: int, width: int) -> None:
    ellipse(image, x - width // 2, baseline - 4, width, 7, "ink")
    for offset in range(2, width - 2, 4):
        pixel(image, x - width // 2 + offset, baseline + 3, "stone_shadow")


def _torch_light(image: Image.Image, center_x: int, center_y: int) -> None:
    dither_disc(image, center_x, center_y, 48, (
        (0.30, "flame_orange", 4),
        (0.58, "flame_red", 6),
        (1.00, "flame_shadow", 9),
    ))


def _hud(image: Image.Image, assets: Mapping[str, Image.Image]) -> None:
    rect(image, 6, 6, 154, 38, "night_shadow")
    rect(image, 8, 8, 150, 34, "stone_shadow")
    rect(image, 10, 10, 146, 30, "night_dark")
    # Repeated edges and corners demonstrate the nine-slice pieces in context.
    for x in range(10, 154, 8): blit(image, assets["ui_edge_horizontal"], x, 6)
    blit(image, assets["ui_corner"], 6, 6)
    blit(image, assets["ui_hp_bar"], 19, 14)
    blit(image, assets["ui_mana_bar"], 19, 27)
    blit(image, assets["ui_heart_full"], 10, 15)
    blit(image, assets["ui_subweapon_frame"], 128, 12)
    weapon = assets["sub_cross"]
    blit(image, weapon, 132, 16)


def render(assets: Mapping[str, Image.Image], scale: int = SCENE_SCALE) -> Image.Image:
    image = new_canvas(WIDTH, HEIGHT, "night_shadow")
    _sky(image)
    _brick_wall(image)

    # Three narrow lancets and one dominant central opening establish a
    # cathedral grammar.  The moon is composited *after* the opening, so it can
    # never be hidden by an opaque window panel.
    _lancet(image, 63, 57, 50, 171, True)
    _lancet(image, 367, 57, 50, 171, True)
    _lancet(image, 197, 15, 86, 164, True)
    _window_depth(image, assets, 63, 171)
    _window_depth(image, assets, 367, 171)
    _lancet_tracery(image, 63, 57, 50, 171)
    _lancet_tracery(image, 367, 57, 50, 171)
    blit(image, assets["bg_moon"], 224, 47)
    # Central window tracery is redrawn over the moon.
    rect(image, 238, 25, 4, 134, "stone_dark")
    rect(image, 205, 112, 70, 4, "stone_dark")
    rose = nearest(assets["tile_rose_window"], 2)
    blit(image, rose, 208, 96)

    _vaults(image)
    rect(image, 0, FLOOR_Y - 5, WIDTH, 5, "stone_shadow")
    rect(image, 0, FLOOR_Y - 5, WIDTH, 2, "stone_highlight")
    _floor(image)

    # Palette dither produces believable falloff without inventing blended RGBs.
    for torch_x in (142, 338):
        _torch_light(image, torch_x, 143)
    for pool_x in (142, 338):
        dither_disc(image, pool_x, 235, 30, ((0.4, "brick_highlight", 4), (0.7, "brick_light", 7), (1.0, "brick_mid", 11)))

    # Architectural dressing remains behind actors and shares the floor line.
    blit(image, assets["prop_bookshelf"], 42, FLOOR_Y - 40)
    blit(image, assets["prop_gargoyle_statue"], 92, FLOOR_Y - 32)
    blit(image, assets["prop_coffin"], 414, FLOOR_Y - 40)
    blit(image, assets["prop_banner"], 151, 92)
    blit(image, assets["prop_banner"], 309, 92)
    blit(image, assets["prop_chandelier"], 220, 61)
    for torch_x in (134, 330): blit(image, assets["prop_torch"], torch_x, 134)

    # Grounded gameplay layer: every foot shares GROUND_Y and every body gets a
    # contact shadow.  Floating enemies deliberately omit floor shadows.
    warg = assets["enemy_warg"]
    _contact_shadow(image, 88, GROUND_Y, 42); blit(image, warg, 68, GROUND_Y - warg.height)
    hero = assets["hero_idle_0"]
    _contact_shadow(image, 228, GROUND_Y, 34); blit(image, hero, 204, GROUND_Y - hero.height)
    knight = assets["enemy_axe_knight"]
    _contact_shadow(image, 374, GROUND_Y, 38); blit(image, knight, 354, GROUND_Y - knight.height)
    candelabrum = assets["prop_candelabrum"]
    _contact_shadow(image, 164, GROUND_Y, 24); blit(image, candelabrum, 152, GROUND_Y - candelabrum.height)
    crate = assets["prop_crate"]
    _contact_shadow(image, 431, GROUND_Y, 22); blit(image, crate, 421, GROUND_Y - crate.height)
    blit(image, assets["tile_rubble"], 291, GROUND_Y - 16)

    blit(image, assets["enemy_ghost"], 283, 145)
    blit(image, assets["enemy_bat_0"], 112, 73)
    blit(image, assets["pickup_heart_big"], 264, 196)

    _hud(image, assets)
    return nearest(image, scale)
