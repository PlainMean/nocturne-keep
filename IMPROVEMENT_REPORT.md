# Improvement Report

## Result

Rebuilt the project into a deterministic, data-driven **Nocturne Cathedral** asset pipeline. The baseline generated 53 assets; final inventory is **110 native RGBA PNGs** plus `out/manifest.json` and **16 review artifacts**.

Baseline generation was run before editing. Its strongest parts—Pillow-native rendering, nearest-neighbor review output, named ramps, strict map intent, seeded variation, and contact shadows—were retained. The replacement removes the baseline's duplicate asset implementations, padded malformed maps, very small repeated enemy silhouettes, three-pose walk/attack sets, hidden moon, oversized truss-like central arch, stale bytecode, and stale-output paths.

## Implemented

- `src/palette.py`: one immutable 80-color named palette with 18 hue-shifted ramps; no asset module contains RGB literals.
- `src/spec.py`: exact ordered asset specs, dimensions, descriptions, categories, alpha policies, four explicit animation plans, frame timing, regional-difference floors, and volume tolerances.
- `src/tools.py`: clipping-rejecting palette primitives, 2px-minimum structural lines, strict rectangular ASCII maps, undefined-symbol rejection, nearest scaling, and palette-safe ordered dithering.
- `src/hero.py`: independent ASCII reference; 4 idle, 6 real contact/recoil/passing walk, 6 ready/wind-up/cast/extension/crack/recovery whip frames; crouch, airborne, and hurt poses.
- `src/sprites.py`: 20 enemies, 18 gothic props, 6 sub-weapons, and 10 pickups/upgrades with stronger native silhouettes.
- `src/tiles.py`: 24 environment pieces including cracked/moss variants, modular pointed arches, lancet and rose windows, door, columns, ceiling ribs, portcullis, hazards, rubble, and vine overlays.
- `src/ui.py`: moon/cloud/castle backgrounds and a coherent 9-piece HUD family.
- `src/scene.py`: 480x270 native cathedral hall rendered to 1440x810. Multiple lancets, intersecting vault ribs, distant window depth, masonry/weathering, perspective slabs, palette-dithered moon/torch falloff, grounded actors, and contact shadows. Strict primitives reject clipping.
- `src/generate.py`: always clears and completely rewrites both generated directories, writes fixed PNG bytes and exact JSON hash manifest, then renders sheets, strips, GIFs, and scene.
- `src/validate.py`: checks exact native/review inventory, exact dimensions, RGBA mode, binary/full-bleed alpha policy, normalized transparent RGB, palette membership, exact PNG bytes, manifest contents, per-file hashes, two independent in-memory builds, aggregate digest, regional animation silhouette deltas, frame volume, GIF frame counts, scene size/opacity/palette, and connected hero silhouettes.
- `tests/test_pipeline.py`: 16 focused regressions covering malformed/undefined maps, multi-character legends, 2px structural lines, exact specs, deterministic generation, stale cleanup, disk validation, palette/dimension/mode/alpha violations, and duplicate/translated animation rejection.
- Removed obsolete `src/enemies_items.py` and `src/scene2.py`; updated `render_scene.py` and `README.md` to the single implementation.

## Exact inventory

| Group | Count |
|---|---:|
| Hero | 20 |
| Enemies | 20 |
| Props | 18 |
| Sub-weapons and pickups | 16 |
| Tiles and architecture | 24 |
| Background and UI | 12 |
| **Total** | **110** |

## Commands actually run

All commands were run from the project root. Final verification started from deleted generated directories and disabled bytecode writes.

```text
rm -rf out sheets src/__pycache__ tests/__pycache__

PYTHONDONTWRITEBYTECODE=1 python3 -m src.generate
generated 110 native assets with Nocturne Cathedral
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4
review artifacts: 16 in /home/cmuxao/projects/hermes_area/pixel_assets/sheets

PYTHONDONTWRITEBYTECODE=1 python3 -m src.digest
disk assets: 110
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4

PYTHONDONTWRITEBYTECODE=1 python3 -m src.validate
validated 110 native assets and 16 review artifacts
palette: Nocturne Cathedral (80 colors, 18 hue-shifted ramps)
hero_idle: volumes=[736, 757, 737, 760] drift=0.032 diffs=[95, 180, 196, 121]
hero_walk: volumes=[748, 719, 683, 754, 748, 714] drift=0.098 diffs=[454, 489, 329, 404, 465, 394]
hero_attack: volumes=[782, 849, 847, 809, 840, 838] drift=0.081 diffs=[223, 294, 245, 483, 549, 217]
enemy_bat: volumes=[288, 292] drift=0.014 diffs=[212]
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
Ran 16 tests in 0.524s
OK

PYTHONDONTWRITEBYTECODE=1 python3 render_scene.py
saved /home/cmuxao/projects/hermes_area/pixel_assets/sheets/scene.png (1440, 810) RGBA
```

Generation and the disk-only digest command were then run a second time. The second build produced the same 110 files and the same aggregate digest:

```text
a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4
```

The comprehensive validator was rerun after that second generation and passed with the metrics above.

## Visual review

Visual tooling was available. I inspected the final `scene.png`, complete sheet, hero/enemy/prop/item/tile/UI sheets, and final walk/attack strips. The final scene reads as a cathedral interior rather than an industrial hall: pointed lancets, rose tracery, clustered piers, vault ribs, distant silhouettes, worn masonry, cold central moonlight, warmer localized torch pools, floor perspective, and grounded foreground silhouettes are all visible. Walk passing feet lift rather than translate; attack arm/torso/whip arcs change clearly across all six frames. No visible scene-edge clipping remained.

## Artifacts

- Native assets and exact hash manifest: `/home/cmuxao/projects/hermes_area/pixel_assets/out/`
- Complete contact sheet: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/all.png`
- Category sheets: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/{hero,enemies,props,items,tiles,ui}.png`
- Walk proof: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_walk_strip.png`, `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_walk.gif`
- Attack proof: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_attack_strip.png`, `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_attack.gif`
- Idle and bat proofs: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_idle_strip.png`, `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/hero_idle.gif`, `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/enemy_bat_strip.png`, `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/enemy_bat.gif`
- Best scene screenshot: `/home/cmuxao/projects/hermes_area/pixel_assets/sheets/scene.png`

## Limitations

This is a source-art pipeline, not a gameplay engine. It supplies one facing direction and no collision/hitbox metadata. Ordered palette dithering deliberately replaces smooth physical light blending. A specialist human Aseprite cleanup pass could still improve individual facial clusters and animation timing, but no validator or output is dependent on external editing.
