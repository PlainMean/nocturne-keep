"""The single color source for the Nocturne Cathedral asset set.

Every native asset and the composed scene uses these named RGB colors.  Ramps
move from cool/violet shadows toward warmer highlights instead of changing
value alone.  ASCII maps store palette *names* through ``SYMBOLS``; no drawing
module owns color literals.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import Final

PALETTE_NAME: Final = "Nocturne Cathedral"

_PALETTE = {
    # Global ink and nocturnal depth.
    "void": (5, 6, 14),
    "ink": (10, 10, 22),
    "night_shadow": (10, 13, 31),
    "night_dark": (17, 22, 45),
    "night_mid": (29, 36, 65),
    "night_light": (48, 55, 84),
    # Moonlight warms subtly as it rises in value.
    "moon_shadow": (82, 102, 137),
    "moon_dark": (126, 151, 181),
    "moon_mid": (190, 203, 211),
    "moon_light": (241, 232, 198),
    # Limestone: violet shadow, neutral body, warm worn edge.
    "stone_shadow": (38, 32, 53),
    "stone_dark": (58, 55, 75),
    "stone_mid": (91, 88, 105),
    "stone_light": (136, 130, 140),
    "stone_highlight": (184, 165, 148),
    # Old red masonry.
    "brick_shadow": (50, 27, 43),
    "brick_dark": (76, 39, 50),
    "brick_mid": (112, 57, 58),
    "brick_light": (157, 84, 68),
    "brick_highlight": (195, 121, 85),
    # Oak and leather split into separate ramps for boundary contrast.
    "wood_shadow": (44, 27, 38),
    "wood_dark": (73, 42, 43),
    "wood_mid": (112, 66, 48),
    "wood_light": (162, 101, 58),
    "leather_shadow": (40, 28, 48),
    "leather_dark": (73, 43, 51),
    "leather_mid": (120, 69, 50),
    "leather_light": (184, 113, 62),
    # Cold metal catches pale moonlight.
    "iron_shadow": (27, 29, 45),
    "iron_dark": (50, 56, 77),
    "iron_mid": (83, 91, 111),
    "iron_light": (139, 146, 155),
    "iron_highlight": (201, 201, 191),
    # Flesh turns from plum shadow to peach-gold light.
    "skin_shadow": (105, 57, 72),
    "skin_dark": (163, 89, 75),
    "skin_mid": (220, 145, 99),
    "skin_light": (250, 199, 132),
    # Hunter cloth and cape lining.
    "navy_shadow": (20, 29, 58),
    "navy_dark": (29, 52, 87),
    "navy_mid": (46, 84, 123),
    "navy_light": (82, 133, 163),
    "crimson_shadow": (61, 22, 51),
    "crimson_dark": (103, 25, 48),
    "crimson_mid": (164, 34, 49),
    "crimson_light": (224, 68, 55),
    # Gold shifts from umber to candle yellow.
    "gold_shadow": (99, 59, 38),
    "gold_dark": (153, 96, 44),
    "gold_mid": (218, 156, 59),
    "gold_light": (255, 220, 124),
    # Bone and supernatural ramps.
    "bone_shadow": (100, 94, 103),
    "bone_dark": (151, 143, 132),
    "bone_mid": (209, 197, 166),
    "bone_light": (245, 231, 190),
    "undead_shadow": (37, 58, 59),
    "undead_dark": (59, 92, 70),
    "undead_mid": (101, 139, 82),
    "undead_light": (160, 181, 102),
    "moss_shadow": (35, 52, 46),
    "moss_dark": (55, 78, 54),
    "moss_mid": (91, 116, 66),
    "moss_light": (148, 154, 82),
    "purple_shadow": (45, 28, 66),
    "purple_dark": (72, 42, 94),
    "purple_mid": (116, 65, 132),
    "purple_light": (177, 111, 173),
    "ghost_shadow": (65, 81, 121),
    "ghost_dark": (103, 127, 164),
    "ghost_mid": (164, 182, 202),
    "ghost_light": (222, 225, 222),
    # Stained glass and magic.
    "teal_shadow": (22, 61, 72),
    "teal_dark": (31, 94, 102),
    "teal_mid": (48, 139, 137),
    "teal_light": (101, 190, 167),
    # Fire moves from crimson-violet embers to cream-white cores.
    "flame_shadow": (102, 28, 43),
    "flame_red": (180, 49, 31),
    "flame_orange": (242, 116, 36),
    "flame_yellow": (255, 191, 70),
    "flame_white": (255, 239, 160),
    "blood": (133, 20, 38),
    "eye": (245, 61, 43),
}

PALETTE = MappingProxyType(_PALETTE)

RAMPS = MappingProxyType({
    "night": ("night_shadow", "night_dark", "night_mid", "night_light"),
    "moon": ("moon_shadow", "moon_dark", "moon_mid", "moon_light"),
    "stone": ("stone_shadow", "stone_dark", "stone_mid", "stone_light", "stone_highlight"),
    "brick": ("brick_shadow", "brick_dark", "brick_mid", "brick_light", "brick_highlight"),
    "wood": ("wood_shadow", "wood_dark", "wood_mid", "wood_light"),
    "leather": ("leather_shadow", "leather_dark", "leather_mid", "leather_light"),
    "iron": ("iron_shadow", "iron_dark", "iron_mid", "iron_light", "iron_highlight"),
    "skin": ("skin_shadow", "skin_dark", "skin_mid", "skin_light"),
    "navy": ("navy_shadow", "navy_dark", "navy_mid", "navy_light"),
    "crimson": ("crimson_shadow", "crimson_dark", "crimson_mid", "crimson_light"),
    "gold": ("gold_shadow", "gold_dark", "gold_mid", "gold_light"),
    "bone": ("bone_shadow", "bone_dark", "bone_mid", "bone_light"),
    "undead": ("undead_shadow", "undead_dark", "undead_mid", "undead_light"),
    "moss": ("moss_shadow", "moss_dark", "moss_mid", "moss_light"),
    "purple": ("purple_shadow", "purple_dark", "purple_mid", "purple_light"),
    "ghost": ("ghost_shadow", "ghost_dark", "ghost_mid", "ghost_light"),
    "teal": ("teal_shadow", "teal_dark", "teal_mid", "teal_light"),
    "flame": ("flame_shadow", "flame_red", "flame_orange", "flame_yellow", "flame_white"),
})

# One symbol is one native pixel.  Values are names, never duplicated RGB data.
SYMBOLS = MappingProxyType({
    ".": None,
    "k": "ink", "0": "void",
    "n": "night_shadow", "N": "night_dark", "d": "night_mid", "D": "night_light",
    "s": "stone_shadow", "S": "stone_dark", "t": "stone_mid", "T": "stone_light", "i": "stone_highlight",
    "b": "brick_shadow", "B": "brick_dark", "r": "brick_mid", "R": "brick_light",
    "w": "wood_shadow", "W": "wood_dark", "o": "wood_mid", "O": "wood_light",
    "q": "iron_shadow", "Q": "iron_dark", "j": "iron_mid", "J": "iron_light",
    "u": "skin_shadow", "U": "skin_dark", "e": "skin_mid", "E": "skin_light",
    "l": "leather_shadow", "L": "leather_dark", "c": "leather_mid", "C": "leather_light",
    "a": "navy_shadow", "A": "navy_dark", "h": "navy_mid", "H": "navy_light",
    "x": "crimson_shadow", "X": "crimson_dark", "v": "crimson_mid", "V": "crimson_light",
    "g": "gold_shadow", "G": "gold_dark", "y": "gold_mid", "Y": "gold_light",
    "p": "bone_shadow", "P": "bone_dark", "z": "bone_mid", "Z": "bone_light",
    "m": "undead_shadow", "M": "undead_dark", "f": "undead_mid", "F": "undead_light",
    "1": "moss_shadow", "2": "moss_dark", "3": "moss_mid", "4": "moss_light",
    "5": "purple_shadow", "6": "purple_dark", "7": "purple_mid", "8": "purple_light",
    "9": "ghost_shadow", "-": "ghost_dark", "+": "ghost_mid", "=": "ghost_light",
    "[": "teal_shadow", "]": "teal_dark", "{": "teal_mid", "}": "teal_light",
    "!": "flame_shadow", "@": "flame_red", "$": "flame_orange", "%": "flame_yellow", "&": "flame_white",
    "?": "blood", "*": "eye",
})


def rgb(name: str) -> tuple[int, int, int]:
    """Resolve a palette name, rejecting every undefined color."""
    try:
        return PALETTE[name]
    except KeyError:
        raise KeyError(f"undefined {PALETTE_NAME} color: {name!r}") from None


def rgba(name: str, alpha: int = 255) -> tuple[int, int, int, int]:
    if not 0 <= alpha <= 255:
        raise ValueError(f"alpha must be 0..255, got {alpha}")
    return (*rgb(name), alpha)


def luminance(value: tuple[int, int, int]) -> float:
    return 0.2126 * value[0] + 0.7152 * value[1] + 0.0722 * value[2]


def validate_palette() -> list[str]:
    """Return definition errors; used by tests and the project validator."""
    errors: list[str] = []
    seen: dict[tuple[int, int, int], str] = {}
    for name, value in PALETTE.items():
        if len(value) != 3 or any(type(channel) is not int or not 0 <= channel <= 255 for channel in value):
            errors.append(f"{name}: invalid RGB {value!r}")
        if value in seen:
            errors.append(f"{name}: duplicates RGB used by {seen[value]}")
        seen[value] = name
    for ramp_name, names in RAMPS.items():
        missing = [name for name in names if name not in PALETTE]
        if missing:
            errors.append(f"{ramp_name}: undefined colors {missing}")
            continue
        values = [luminance(PALETTE[name]) for name in names]
        if any(left >= right for left, right in zip(values, values[1:])):
            errors.append(f"{ramp_name}: luminance is not strictly increasing: {values}")
    for symbol, name in SYMBOLS.items():
        if len(symbol) != 1:
            errors.append(f"legend key {symbol!r} is not one character")
        if name is not None and name not in PALETTE:
            errors.append(f"legend symbol {symbol!r} references undefined {name!r}")
    return errors
