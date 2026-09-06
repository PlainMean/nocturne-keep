"""Reference hunter and explicit, volume-conscious animation frames."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from .tools import Anchor, ellipse, line, map_sprite, new_canvas, polygon, rect

FRAME_SIZE = (48, 48)

# This deliberately literal one-character-per-pixel map is the style anchor:
# plum/cool outlines, warm skin, navy wool, crimson lining, and gold hardware.
# It is not generated from the animation renderer, so the pipeline retains an
# independently hand-authored reference rather than recursively copying a pose.
REFERENCE_HUNTER = (
    "....................",
    ".......cccc.........",
    ".....cccCCccc.......",
    "....ccCCCCCCcc......",
    "....cCeeeeeeCc......",
    "...cCCeEeeEecCc.....",
    "...cCeeeeeeecCc.....",
    "...cCeeekkeecCc.....",
    "...cCeeeeeeecCc.....",
    "....cUeeeeUcc.......",
    ".....UUUUUU.........",
    "....xxkUUUkxx.......",
    "...xxAAkkAAxx.......",
    "..xxAAAhhAAAxx......",
    "..xAAAhHHhAAAxx.....",
    ".xxAAhhhhhhAAAx.....",
    ".xAAhhyyyyhhAAx.....",
    ".xAAhhhyYyhhAAx.....",
    "..AAhhhhhhhhAA......",
    "..AAAhhhhhhhAAA.....",
    "..xAAAhhhhhAAAxx....",
    "..xxAAhhhhAAxxx.....",
    "...xAAhhhhAAxx......",
    "...xAAhhhhAAx.......",
    "....AAhAAhAA........",
    "....AAhAAhAA........",
    "....AAhAAhAA........",
    "...LLLh..hLLL.......",
    "...LLLh..hLLL.......",
    "..LLLL....LLLL......",
    "..LLLL....LLLL......",
    "....................",
)


@dataclass(frozen=True)
class HeroPose:
    near_leg: tuple[tuple[int, int], ...]
    far_leg: tuple[tuple[int, int], ...]
    near_arm: tuple[tuple[int, int], ...]
    far_arm: tuple[tuple[int, int], ...]
    cape_tip: tuple[int, int]
    body_y: int = 0
    head_x: int = 0
    coat_tail: int = 0
    chain: tuple[tuple[int, int], ...] = ()
    body_x: int = 0


IDLE_POSES = (
    HeroPose(((28, 31), (29, 38), (30, 44)), ((21, 31), (20, 38), (19, 44)),
             ((31, 20), (34, 27), (32, 32)), ((18, 21), (15, 27), (16, 32)), (11, 35)),
    HeroPose(((28, 31), (29, 38), (30, 44)), ((21, 31), (20, 38), (19, 44)),
             ((31, 19), (35, 25), (33, 31)), ((18, 20), (14, 26), (16, 32)), (9, 33), coat_tail=-1),
    HeroPose(((28, 31), (29, 38), (30, 44)), ((21, 31), (20, 38), (19, 44)),
             ((31, 20), (34, 27), (32, 32)), ((18, 21), (15, 27), (16, 32)), (12, 36), head_x=1),
    HeroPose(((28, 31), (29, 38), (30, 44)), ((21, 31), (20, 38), (19, 44)),
             ((31, 21), (33, 28), (31, 33)), ((18, 20), (13, 25), (14, 31)), (8, 36), coat_tail=1),
)

WALK_POSES = (
    HeroPose(((28, 31), (32, 37), (37, 44)), ((21, 31), (18, 38), (13, 44)),
             ((31, 20), (28, 27), (25, 32)), ((18, 20), (14, 25), (11, 29)), (8, 35), coat_tail=-2),
    HeroPose(((28, 32), (31, 38), (34, 44)), ((21, 32), (18, 38), (16, 44)),
             ((31, 21), (29, 27), (27, 32)), ((18, 21), (14, 27), (12, 31)), (9, 36), body_y=1, coat_tail=-1),
    HeroPose(((28, 31), (27, 37), (26, 44)), ((21, 31), (19, 35), (16, 40)),
             ((31, 20), (32, 26), (30, 31)), ((18, 20), (16, 27), (18, 32)), (11, 36), coat_tail=1),
    HeroPose(((28, 31), (31, 38), (36, 44)), ((21, 31), (17, 37), (12, 44)),
             ((31, 20), (35, 25), (38, 29)), ((18, 20), (21, 27), (24, 32)), (12, 34), coat_tail=2),
    HeroPose(((28, 32), (32, 38), (34, 44)), ((21, 32), (18, 38), (15, 44)),
             ((31, 21), (35, 27), (37, 31)), ((18, 21), (21, 27), (23, 32)), (11, 36), body_y=1, coat_tail=1),
    HeroPose(((28, 31), (30, 35), (33, 40)), ((21, 31), (22, 37), (23, 44)),
             ((31, 20), (33, 27), (31, 32)), ((18, 20), (17, 26), (19, 31)), (9, 36), coat_tail=-1),
)

# Attack poses all shift the body left inside the 48px action box, reserving a
# real weapon arc.  Each chain polyline is approximately equal length.
ATTACK_POSES = (
    HeroPose(((20, 31), (21, 38), (23, 44)), ((13, 31), (12, 38), (11, 44)),
             ((23, 20), (29, 26), (30, 31)), ((11, 20), (9, 27), (10, 32)), (3, 35),
             chain=((22, 31), (15, 34), (9, 32), (4, 27), (2, 21), (5, 16), (10, 14)), body_x=-8),
    HeroPose(((20, 31), (21, 38), (23, 44)), ((13, 31), (12, 38), (11, 44)),
             ((23, 20), (30, 15), (29, 9)), ((11, 20), (9, 25), (10, 31)), (2, 34),
             chain=((21, 9), (24, 5), (19, 2), (13, 2), (7, 5), (3, 10), (2, 15)), body_x=-8),
    HeroPose(((20, 31), (22, 38), (24, 44)), ((13, 31), (11, 38), (11, 44)),
             ((23, 20), (27, 16), (30, 12)), ((11, 20), (9, 27), (10, 32)), (3, 36),
             chain=((22, 12), (28, 8), (35, 6), (42, 8), (46, 13), (43, 18)), body_x=-8, coat_tail=-1),
    HeroPose(((20, 31), (23, 38), (26, 44)), ((13, 31), (11, 38), (10, 44)),
             ((23, 20), (27, 19), (31, 19)), ((11, 20), (9, 27), (10, 32)), (2, 36),
             chain=((23, 19), (29, 18), (35, 17), (41, 18), (46, 20)), body_x=-8, coat_tail=-2),
    HeroPose(((20, 32), (23, 38), (25, 44)), ((13, 32), (10, 38), (10, 44)),
             ((23, 21), (27, 22), (31, 25)), ((11, 21), (9, 27), (10, 32)), (2, 37),
             chain=((23, 26), (29, 24), (35, 27), (41, 32), (45, 38), (46, 42)), body_x=-8, body_y=1, coat_tail=-1),
    HeroPose(((20, 31), (21, 38), (23, 44)), ((13, 31), (12, 38), (11, 44)),
             ((23, 20), (26, 27), (24, 32)), ((11, 20), (9, 27), (10, 32)), (3, 35),
             chain=((16, 32), (22, 35), (29, 38), (36, 38), (42, 35), (46, 29)), body_x=-8, coat_tail=1),
)


def reference_hunter() -> Image.Image:
    return map_sprite(REFERENCE_HUNTER, (32, 48), Anchor("center", "bottom"))


def _offset(points: tuple[tuple[int, int], ...], dx: int, dy: int) -> tuple[tuple[int, int], ...]:
    return tuple((x + dx, y + dy) for x, y in points)


def _limb(image: Image.Image, points: tuple[tuple[int, int], ...], inner: str) -> None:
    line(image, points, "ink", 6)
    line(image, points, inner, 3)


def _boot(image: Image.Image, foot: tuple[int, int], facing: int = 1) -> None:
    x, y = foot
    x -= 3 if facing > 0 else 2
    rect(image, x, y - 2, 7, 4, "leather_shadow")
    rect(image, x + (2 if facing > 0 else 0), y - 2, 5, 2, "leather_mid")


def _draw_chain(image: Image.Image, points: tuple[tuple[int, int], ...]) -> None:
    line(image, points, "leather_shadow", 3)
    line(image, points, "leather_light", 2)
    tip_x, tip_y = points[-1]
    rect(image, max(0, min(image.width - 3, tip_x - 1)), max(0, min(image.height - 3, tip_y - 1)), 3, 3, "gold_light")


def draw_hero(pose: HeroPose) -> Image.Image:
    image = new_canvas(*FRAME_SIZE)
    dx, dy = pose.body_x, pose.body_y

    # Weapon behind the body in wind-up/ready poses, then redrawn at the front
    # after the hand so its attachment remains legible.
    if pose.chain:
        _draw_chain(image, pose.chain)

    # Crimson-lined coat/cape gives the silhouette a unique trailing wedge.
    cape_tip_x, cape_tip_y = pose.cape_tip
    polygon(image, _offset(((18, 19), (15, 26), (cape_tip_x - dx, cape_tip_y - dy), (20, 36 + pose.coat_tail)), dx, dy), "ink")
    polygon(image, _offset(((18, 21), (16, 27), (cape_tip_x - dx + 2, cape_tip_y - dy - 1), (20, 34 + pose.coat_tail)), dx, dy), "crimson_dark")
    polygon(image, _offset(((18, 22), (17, 27), (cape_tip_x - dx + 4, cape_tip_y - dy - 2), (20, 32 + pose.coat_tail)), dx, dy), "crimson_mid")

    # Far limbs first; each structural stroke has a 6px outline and 3px fill.
    far_leg = _offset(pose.far_leg, dx, dy)
    near_leg = _offset(pose.near_leg, dx, dy)
    far_arm = _offset(pose.far_arm, dx, dy)
    near_arm = _offset(pose.near_arm, dx, dy)
    _limb(image, far_leg, "navy_dark")
    _boot(image, far_leg[-1], -1)
    _limb(image, far_arm, "navy_dark")
    ellipse(image, far_arm[-1][0] - 2, far_arm[-1][1] - 2, 5, 5, "leather_mid")

    # Tailored long coat and bright lining split.
    polygon(image, _offset(((17, 18), (29, 17), (33, 23), (31, 32), (28, 36), (19, 36), (15, 31), (14, 23)), dx, dy), "ink")
    polygon(image, _offset(((18, 19), (28, 19), (30, 23), (29, 32), (26, 34), (20, 34), (17, 30), (16, 23)), dx, dy), "navy_mid")
    polygon(image, _offset(((18, 20), (21, 19), (21, 33), (19, 33), (17, 29), (17, 23)), dx, dy), "navy_light")
    polygon(image, _offset(((24, 20), (28, 20), (29, 24), (28, 33), (25, 35)), dx, dy), "navy_dark")
    rect(image, 17 + dx, 28 + dy, 13, 3, "leather_dark")
    rect(image, 22 + dx, 28 + dy, 3, 3, "gold_light")
    rect(image, 25 + dx, 22 + dy, 2, 2, "gold_mid")
    rect(image, 25 + dx, 25 + dy, 2, 2, "gold_mid")

    _limb(image, near_leg, "navy_mid")
    _boot(image, near_leg[-1], 1)
    _limb(image, near_arm, "navy_mid")
    ellipse(image, near_arm[-1][0] - 2, near_arm[-1][1] - 2, 5, 5, "leather_light")

    # Neck, head, hair mass, headband, and a 2px eye cluster.
    head_dx = dx + pose.head_x
    rect(image, 21 + head_dx, 15 + dy, 6, 5, "skin_dark")
    polygon(image, _offset(((17, 7), (20, 4), (28, 4), (32, 8), (31, 17), (28, 20), (18, 18), (16, 13)), head_dx, dy), "leather_shadow")
    ellipse(image, 19 + head_dx, 7 + dy, 11, 12, "skin_mid")
    rect(image, 20 + head_dx, 8 + dy, 9, 3, "crimson_dark")
    rect(image, 21 + head_dx, 8 + dy, 7, 2, "crimson_light")
    polygon(image, _offset(((17, 7), (20, 4), (28, 4), (31, 7), (28, 8), (23, 7), (20, 11), (17, 10)), head_dx, dy), "leather_dark")
    rect(image, 18 + head_dx, 11 + dy, 3, 8, "leather_mid")
    rect(image, 28 + head_dx, 10 + dy, 3, 7, "leather_dark")
    rect(image, 27 + head_dx, 12 + dy, 2, 2, "ink")
    rect(image, 27 + head_dx, 15 + dy, 3, 2, "skin_light")
    rect(image, 21 + head_dx, 5 + dy, 5, 2, "leather_light")

    # Whip handle remains a 3px feature and anchors the chain to the glove.
    hand_x, hand_y = near_arm[-1]
    rect(image, max(0, min(45, hand_x - 1)), max(0, min(45, hand_y - 1)), 3, 3, "gold_dark")
    return image


def crouch() -> Image.Image:
    return draw_hero(HeroPose(
        ((28, 34), (34, 39), (38, 43)), ((21, 34), (17, 39), (13, 43)),
        ((31, 22), (35, 28), (32, 33)), ((18, 22), (14, 27), (12, 31)),
        (8, 39), body_y=3, coat_tail=1,
    ))


def airborne() -> Image.Image:
    return draw_hero(HeroPose(
        ((28, 29), (34, 33), (31, 38)), ((21, 29), (16, 33), (19, 38)),
        ((31, 19), (36, 22), (38, 27)), ((18, 19), (13, 22), (11, 27)),
        (8, 31), body_y=-3, coat_tail=-2,
    ))


def hurt() -> Image.Image:
    return draw_hero(HeroPose(
        ((28, 31), (33, 38), (36, 44)), ((21, 31), (17, 38), (13, 44)),
        ((31, 19), (36, 17), (39, 20)), ((18, 20), (13, 18), (10, 21)),
        (7, 31), head_x=-1, coat_tail=-3,
    ))


def build_hero_assets() -> dict[str, Image.Image]:
    assets: dict[str, Image.Image] = {"hero_reference": reference_hunter()}
    assets.update({f"hero_idle_{index}": draw_hero(pose) for index, pose in enumerate(IDLE_POSES)})
    assets.update({f"hero_walk_{index}": draw_hero(pose) for index, pose in enumerate(WALK_POSES)})
    assets.update({f"hero_attack_{index}": draw_hero(pose) for index, pose in enumerate(ATTACK_POSES)})
    assets.update({"hero_crouch": crouch(), "hero_airborne": airborne(), "hero_hurt": hurt()})
    return assets
