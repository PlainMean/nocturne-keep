"""Exact asset inventory and animation contracts.

This module is deliberately data-only.  Adding a builder without a matching
spec, or a spec without a builder, is a validation error.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

AlphaPolicy = Literal["sprite", "opaque"]
Category = Literal["hero", "enemies", "props", "items", "tiles", "ui"]


@dataclass(frozen=True)
class AssetSpec:
    name: str
    size: tuple[int, int]
    category: Category
    description: str
    alpha: AlphaPolicy = "sprite"


@dataclass(frozen=True)
class AnimationRegion:
    name: str
    box: tuple[int, int, int, int]
    minimum_alpha_diff: int


@dataclass(frozen=True)
class AnimationSpec:
    name: str
    frames: tuple[str, ...]
    durations_ms: tuple[int, ...]
    frame_deltas: tuple[str, ...]
    regions: tuple[AnimationRegion, ...]
    minimum_total_diff: int
    maximum_volume_drift: float
    loop: bool = True


def _asset(
    name: str,
    width: int,
    height: int,
    category: Category,
    description: str,
    alpha: AlphaPolicy = "sprite",
) -> AssetSpec:
    return AssetSpec(name, (width, height), category, description, alpha)


ASSET_SPECS = (
    # Hero reference and complete player state set.
    _asset("hero_reference", 32, 48, "hero", "Hand-authored ASCII vampire-hunter style reference"),
    _asset("hero_idle_0", 48, 48, "hero", "Idle neutral, coat and whip hand settled"),
    _asset("hero_idle_1", 48, 48, "hero", "Idle inhale, shoulders open and coat tail lifts"),
    _asset("hero_idle_2", 48, 48, "hero", "Idle exhale, hair and coat tail settle"),
    _asset("hero_idle_3", 48, 48, "hero", "Idle weight shift, rear hand and cape move"),
    _asset("hero_walk_0", 48, 48, "hero", "Walk contact A: forward heel and opposed arms"),
    _asset("hero_walk_1", 48, 48, "hero", "Walk recoil A: body down, knees absorb impact"),
    _asset("hero_walk_2", 48, 48, "hero", "Walk passing A: rear foot lifts under hips"),
    _asset("hero_walk_3", 48, 48, "hero", "Walk contact B: legs and arms reverse"),
    _asset("hero_walk_4", 48, 48, "hero", "Walk recoil B: opposite knee compresses"),
    _asset("hero_walk_5", 48, 48, "hero", "Walk passing B: opposite rear foot lifts"),
    _asset("hero_attack_0", 48, 48, "hero", "Whip ready: low guard with chain behind"),
    _asset("hero_attack_1", 48, 48, "hero", "Whip wind-up: torso twists and arm rises"),
    _asset("hero_attack_2", 48, 48, "hero", "Whip cast: shoulder drives forward"),
    _asset("hero_attack_3", 48, 48, "hero", "Whip extension: chain reaches full horizontal arc"),
    _asset("hero_attack_4", 48, 48, "hero", "Whip crack: tip descends and knees brace"),
    _asset("hero_attack_5", 48, 48, "hero", "Whip recovery: arm and chain sweep low"),
    _asset("hero_crouch", 48, 48, "hero", "Low defensive crouch with compressed silhouette"),
    _asset("hero_airborne", 48, 48, "hero", "Airborne tuck with readable bent legs"),
    _asset("hero_hurt", 48, 48, "hero", "Backward hit reaction with flared coat"),

    # Enemy roster.  Two bat poses are a validated secondary animation.
    _asset("enemy_zombie", 32, 40, "enemies", "Stooped castle servant reaching with torn sleeves"),
    _asset("enemy_skeleton", 32, 40, "enemies", "Tall skeleton with separated rib cage and limbs"),
    _asset("enemy_bat_0", 32, 24, "enemies", "Bat flight upstroke"),
    _asset("enemy_bat_1", 32, 24, "enemies", "Bat flight downstroke"),
    _asset("enemy_medusa_head", 28, 24, "enemies", "Floating gorgon head with snake halo"),
    _asset("enemy_ghost", 32, 32, "enemies", "Moonlit specter with tapering vapor tail"),
    _asset("enemy_raven", 28, 24, "enemies", "Raven in a broad angular wing pose"),
    _asset("enemy_axe_knight", 40, 40, "enemies", "Crimson plate knight carrying a broad axe"),
    _asset("enemy_fleaman", 24, 24, "enemies", "Compact crouched leaper with long hands"),
    _asset("enemy_hunchback", 32, 32, "enemies", "Hooded hunched servant with forward weight"),
    _asset("enemy_werewolf", 36, 36, "enemies", "Long-limbed wolf creature with claw silhouette"),
    _asset("enemy_bone_knight", 40, 40, "enemies", "Shielded skeleton with a two-pixel spear"),
    _asset("enemy_giant_bat", 48, 32, "enemies", "Large layered-wing bat miniboss"),
    _asset("enemy_gargoyle", 36, 36, "enemies", "Horned stone gargoyle with folded wings"),
    _asset("enemy_merman", 32, 36, "enemies", "Scaled aquatic soldier holding a trident"),
    _asset("enemy_armor_lord", 40, 44, "enemies", "Heavy gold-trimmed castle armor"),
    _asset("enemy_warg", 40, 28, "enemies", "Low quadruped war beast in a running silhouette"),
    _asset("enemy_phantom", 32, 40, "enemies", "Empty hood and ragged supernatural cloak"),
    _asset("enemy_succubus", 40, 40, "enemies", "Winged demon with a readable airborne pose"),
    _asset("enemy_reaper", 48, 48, "enemies", "Cloaked reaper with a broad crescent scythe"),

    # Environment props.
    _asset("prop_candle", 16, 24, "props", "Floor candle with wax drips and warm flame"),
    _asset("prop_candelabrum", 24, 32, "props", "Three-flame gothic standing candelabrum"),
    _asset("prop_wall_sconce", 16, 20, "props", "Wrought-iron wall candle bracket"),
    _asset("prop_torch", 16, 24, "props", "Wall torch with layered flame and iron cradle"),
    _asset("prop_brazier", 24, 24, "props", "Stone fire bowl on a short pedestal"),
    _asset("prop_iron_gate", 32, 40, "props", "Pointed portcullis gate section"),
    _asset("prop_gargoyle_statue", 24, 32, "props", "Weathered crouching gargoyle statue"),
    _asset("prop_sarcophagus", 24, 40, "props", "Carved upright knight sarcophagus"),
    _asset("prop_crate", 20, 20, "props", "Iron-bound breakable oak crate"),
    _asset("prop_barrel", 20, 24, "props", "Hooped old oak barrel"),
    _asset("prop_hanging_chain", 12, 32, "props", "Heavy linked hanging chain"),
    _asset("prop_banner", 20, 36, "props", "Torn crimson heraldic banner"),
    _asset("prop_bookshelf", 32, 40, "props", "Gothic bookcase filled with uneven tomes"),
    _asset("prop_altar", 32, 24, "props", "Stone altar with gold reliquary"),
    _asset("prop_coffin", 24, 40, "props", "Closed tapered wooden coffin"),
    _asset("prop_chandelier", 40, 24, "props", "Hanging iron chandelier with four candles"),
    _asset("prop_breakable_wall", 32, 32, "props", "Cracked masonry secret-wall block"),
    _asset("prop_throne", 28, 40, "props", "High-backed worn gothic throne"),

    # Sub-weapons and pickups.
    _asset("sub_dagger", 16, 16, "items", "Silver throwing dagger"),
    _asset("sub_axe", 16, 16, "items", "Broad crescent throwing axe"),
    _asset("sub_holy_water", 16, 18, "items", "Blue holy-water vial"),
    _asset("sub_cross", 16, 16, "items", "Gold returning cross"),
    _asset("sub_stopwatch", 16, 18, "items", "Moon-silver stopwatch"),
    _asset("sub_bible", 20, 18, "items", "Gold-clasped crimson scripture"),
    _asset("pickup_heart_small", 16, 16, "items", "Small crimson heart"),
    _asset("pickup_heart_big", 16, 16, "items", "Large highlighted heart"),
    _asset("pickup_meat", 18, 16, "items", "Wall meat with bone"),
    _asset("pickup_gold", 16, 16, "items", "Stacked gold coin bag"),
    _asset("pickup_potion_red", 16, 20, "items", "Crimson health potion"),
    _asset("pickup_potion_blue", 16, 20, "items", "Teal magic potion"),
    _asset("pickup_whip_upgrade", 20, 18, "items", "Coiled chain-whip upgrade"),
    _asset("pickup_armor", 18, 20, "items", "Silver breastplate pickup"),
    _asset("pickup_rosary", 18, 18, "items", "Protective gold rosary"),
    _asset("pickup_mana", 16, 18, "items", "Luminous teal mana crystal"),

    # Seamless tiles and modular gothic architecture.
    _asset("tile_stone_floor", 16, 16, "tiles", "Seamless worn limestone floor", "opaque"),
    _asset("tile_stone_floor_cracked", 16, 16, "tiles", "Seamless cracked floor variant", "opaque"),
    _asset("tile_brick_wall", 16, 16, "tiles", "Seamless old red castle brick", "opaque"),
    _asset("tile_brick_wall_moss", 16, 16, "tiles", "Moss-weathered brick variant", "opaque"),
    _asset("tile_cobble", 16, 16, "tiles", "Deep-shadow cobblestone", "opaque"),
    _asset("tile_platform", 16, 16, "tiles", "Carved stone platform edge", "opaque"),
    _asset("tile_stairs", 16, 16, "tiles", "Side-view stone stair repeat", "opaque"),
    _asset("tile_pillar", 16, 32, "tiles", "Heavy square pier module", "opaque"),
    _asset("tile_column", 16, 32, "tiles", "Fluted gothic column module", "opaque"),
    _asset("tile_arch_left", 16, 16, "tiles", "Left half of pointed arch module", "opaque"),
    _asset("tile_arch_right", 16, 16, "tiles", "Right half of pointed arch module", "opaque"),
    _asset("tile_arch_keystone", 16, 16, "tiles", "Pointed arch apex and tracery module", "opaque"),
    _asset("tile_lancet_window", 16, 32, "tiles", "Narrow pointed moonlit lancet", "opaque"),
    _asset("tile_rose_window", 32, 32, "tiles", "Radial stained-glass rose window", "opaque"),
    _asset("tile_door", 16, 32, "tiles", "Pointed oak castle door", "opaque"),
    _asset("tile_trim", 16, 16, "tiles", "Carved quatrefoil wall trim", "opaque"),
    _asset("tile_balcony", 16, 16, "tiles", "Open gothic balcony railing"),
    _asset("tile_spikes", 16, 16, "tiles", "Stone-set iron floor spikes"),
    _asset("tile_chain", 8, 16, "tiles", "Repeatable two-pixel chain"),
    _asset("tile_roof", 16, 16, "tiles", "Slate castle roof repeat", "opaque"),
    _asset("tile_portcullis", 16, 32, "tiles", "Open iron portcullis repeat"),
    _asset("tile_vine", 16, 16, "tiles", "Mossy creeping vine overlay"),
    _asset("tile_rubble", 16, 16, "tiles", "Loose masonry floor rubble"),
    _asset("tile_ceiling", 16, 16, "tiles", "Shadowed ribbed ceiling edge", "opaque"),

    # Background pieces and UI nine-slice components.
    _asset("bg_moon", 32, 32, "ui", "Crescent moon with crater clusters"),
    _asset("bg_cloud", 48, 20, "ui", "Layered moonlit cloud bank"),
    _asset("bg_castle_silhouette", 96, 48, "ui", "Distant spired castle silhouette"),
    _asset("ui_corner", 8, 8, "ui", "Ornate gold-and-stone frame corner"),
    _asset("ui_edge_horizontal", 8, 8, "ui", "Repeatable horizontal UI frame edge"),
    _asset("ui_edge_vertical", 8, 8, "ui", "Repeatable vertical UI frame edge"),
    _asset("ui_heart_full", 8, 8, "ui", "Filled health heart"),
    _asset("ui_heart_empty", 8, 8, "ui", "Empty health heart outline"),
    _asset("ui_hp_bar", 96, 10, "ui", "Segmented crimson player-health bar", "opaque"),
    _asset("ui_mana_bar", 96, 10, "ui", "Segmented teal magic bar", "opaque"),
    _asset("ui_subweapon_frame", 24, 24, "ui", "Gothic sub-weapon HUD frame"),
    _asset("ui_boss_bar", 128, 12, "ui", "Ornate segmented boss-health bar", "opaque"),
)

ASSET_SPECS_BY_NAME = MappingProxyType({spec.name: spec for spec in ASSET_SPECS})

ANIMATIONS = (
    AnimationSpec(
        "hero_idle",
        tuple(f"hero_idle_{index}" for index in range(4)),
        (260, 260, 260, 260),
        (
            "neutral: shoulders level, coat tails resting, whip hand low",
            "inhale: chest opens 1px, near shoulder rises, coat tail lifts left",
            "exhale: chest settles, head tilts, hair lock moves right",
            "weight shift: rear shoulder drops, off hand and cape move outward",
        ),
        (AnimationRegion("upper body", (10, 5, 39, 34), 30),),
        70,
        0.04,
    ),
    AnimationSpec(
        "hero_walk",
        tuple(f"hero_walk_{index}" for index in range(6)),
        (105, 90, 105, 105, 90, 105),
        (
            "contact A: near heel reaches +7px, far foot trails -6px, arms oppose",
            "recoil A: body drops 1px, both knees bend, forward foot plants",
            "passing A: rear foot lifts 4px beneath hips, torso rotates forward",
            "contact B: feet and arm swing reverse, cape trails opposite",
            "recoil B: body drops 1px onto opposite leg, elbows compress",
            "passing B: opposite rear foot lifts 4px, coat tail crosses center",
        ),
        (AnimationRegion("legs", (7, 27, 42, 48), 120), AnimationRegion("arms and cape", (7, 17, 42, 37), 55)),
        300,
        0.10,
    ),
    AnimationSpec(
        "hero_attack",
        tuple(f"hero_attack_{index}" for index in range(6)),
        (110, 95, 70, 75, 95, 125),
        (
            "ready: knees open, weapon hand low, equal-length chain trails behind",
            "wind-up: torso twists back, elbow and chain arc above shoulder",
            "cast: lead shoulder advances, hand crosses face, chain forms high S-curve",
            "extension: arm locks forward and chain reaches horizontal maximum",
            "crack: knees brace, wrist turns, tip cuts down through target line",
            "recovery: arm sweeps below waist and chain curls without losing length",
        ),
        (
            AnimationRegion("weapon arc", (0, 0, 48, 46), 110),
            AnimationRegion("attack body", (7, 5, 34, 47), 24),
        ),
        200,
        0.09,
    ),
    AnimationSpec(
        "enemy_bat",
        ("enemy_bat_0", "enemy_bat_1"),
        (130, 130),
        ("upstroke: wing tips rise and membrane narrows", "downstroke: wings spread broad and low"),
        (AnimationRegion("wings", (0, 1, 32, 21), 150),),
        180,
        0.03,
    ),
)

REVIEW_FILES = frozenset({
    "hero.png", "enemies.png", "props.png", "items.png", "tiles.png", "ui.png", "all.png",
    "hero_idle_strip.png", "hero_idle.gif", "hero_walk_strip.png", "hero_walk.gif",
    "hero_attack_strip.png", "hero_attack.gif", "enemy_bat_strip.png", "enemy_bat.gif", "scene.png",
})


def validate_spec() -> list[str]:
    errors: list[str] = []
    names = [spec.name for spec in ASSET_SPECS]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        errors.append(f"duplicate asset names: {duplicates}")
    for spec in ASSET_SPECS:
        if not spec.name or spec.name.endswith(".png"):
            errors.append(f"invalid logical asset name: {spec.name!r}")
        if spec.size[0] <= 0 or spec.size[1] <= 0:
            errors.append(f"{spec.name}: invalid dimensions {spec.size}")
        if not spec.description.strip():
            errors.append(f"{spec.name}: missing description")
    for animation in ANIMATIONS:
        if not (len(animation.frames) == len(animation.durations_ms) == len(animation.frame_deltas)):
            errors.append(f"{animation.name}: frame metadata lengths differ")
        missing = sorted(set(animation.frames).difference(names))
        if missing:
            errors.append(f"{animation.name}: unknown frames {missing}")
        sizes = {ASSET_SPECS_BY_NAME[frame].size for frame in animation.frames if frame in ASSET_SPECS_BY_NAME}
        if len(sizes) > 1:
            errors.append(f"{animation.name}: frame dimensions differ: {sorted(sizes)}")
        for region in animation.regions:
            if region.box[0] < 0 or region.box[1] < 0 or region.box[2] <= region.box[0] or region.box[3] <= region.box[1]:
                errors.append(f"{animation.name}/{region.name}: invalid region {region.box}")
            elif sizes:
                width, height = next(iter(sizes))
                if region.box[2] > width or region.box[3] > height:
                    errors.append(f"{animation.name}/{region.name}: region {region.box} exceeds {width}x{height}")
    return errors
