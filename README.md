# Nocturne Cathedral Pixel Asset Pipeline

A deterministic, pixel-native Pillow pipeline for a Castlevania-inspired 2D action game. It generates a complete native asset inventory, hash manifest, contact sheets, animation proofs, and a composed 1440x810 cathedral scene without external art or runtime dependencies beyond Pillow.

## Clean build and verification

Run from the project root:

```bash
python3 -m src.generate
python3 -m src.validate
python3 -m src.digest
python3 -m unittest discover -s tests -v
```

Render only the final scene without rewriting native assets:

```bash
python3 render_scene.py
```

`src.generate` always deletes and recreates both `out/` and `sheets/` before writing the complete inventory, so stale native or review files cannot survive a successful build.

## Source-of-truth structure

- `src/palette.py` — the single **Nocturne Cathedral** palette: 80 named colors organized into 18 warm-highlight/cool-shadow ramps. ASCII symbols resolve to palette names, never duplicated RGB literals.
- `src/spec.py` — exact ordered `AssetSpec` inventory, native dimensions, descriptions, categories, alpha policies, animation frame deltas, timings, regional-difference thresholds, and volume tolerances.
- `src/tools.py` — clipping-safe palette primitives, mandatory 2px structural lines, strict rectangular ASCII maps, palette-safe dithered light, nearest-neighbor scaling, and pixel iteration helpers.
- `src/hero.py` — independent hand-authored ASCII reference plus four idle, six walk, six whip-attack, crouch, airborne, and hurt poses.
- `src/sprites.py` — enemies, gothic props, ASCII-authored sub-weapons, and pickups.
- `src/tiles.py` — seamless terrain, modular pointed arches, lancets, rose window, columns, weathering overlays, hazards, and trim.
- `src/ui.py` — moon/castle background pieces and a coherent nine-slice-style gothic HUD set.
- `src/scene.py` — native 480x270 cathedral composition, scaled 3x with no resampling blur.
- `src/generate.py` — exact build orchestration, PNG serialization, hash manifest, contact sheets, strips, GIFs, and scene output.
- `src/validate.py` — disk/build/manifest/palette/alpha/animation/review contract validator.
- `src/digest.py` — independent disk-only aggregate digest command.
- `tests/test_pipeline.py` — focused malformed-map, deterministic-build, stale-output, palette, dimension, alpha, and animation regressions.

Old split implementations were removed; every asset has exactly one builder and one manifest record.

## Inventory

The manifest contains exactly **110 native RGBA PNGs**:

| Category | Count | Contents |
|---|---:|---|
| Hero | 20 | ASCII reference, 4 idle, 6 walk, 6 whip attack, crouch, airborne, hurt |
| Enemies | 20 | Zombie through reaper, including a two-frame validated bat cycle |
| Props | 18 | Candles, braziers, gate, statues, tomb furniture, chains, banners, books, throne |
| Items | 16 | 6 sub-weapons and 10 pickups/upgrades |
| Tiles | 24 | Floors, walls, variants, modular arches, lancet, rose window, door, trim, hazards, overlays |
| Background/UI | 12 | Moon, cloud, castle silhouette, frame pieces, hearts, bars, sub-weapon frame |

`out/manifest.json` records every logical name, filename, exact dimensions, category, alpha policy, description, per-file SHA-256, and the aggregate deterministic digest.

## Enforced art contracts

### Palette and alpha

All opaque native pixels must belong to `PALETTE` in `src/palette.py`. Native alpha is binary: sprite assets require both transparent padding and opaque art; declared full-bleed tiles/bars require every pixel opaque. Transparent pixels are normalized to `(0, 0, 0, 0)` so hidden RGB data cannot destabilize hashes.

### Pixel construction

Structural `line()` calls reject widths below 2px. Limbs, weapon shafts, chains, architectural ribs, and primary facial marks use 2px-or-larger native clusters. One-pixel operations are confined to non-structural cracks, mortar, glints, stars, and ordered dithering. Every primitive rejects out-of-bounds geometry instead of silently clipping.

`validate_map()` rejects empty, ragged, non-string, multi-character-legend, and undefined-symbol maps. Rows are never silently padded or normalized.

### Animation

Frame intent is explicit in `ANIMATIONS` rather than inferred from translated copies:

- Idle: four breathing/weight-shift poses; maximum pixel-volume drift 4%.
- Walk: six contact/recoil/passing poses with opposed arms, lifted feet, and cape follow-through; maximum drift 10%.
- Whip attack: six ready/wind-up/cast/extension/crack/recovery poses with continuous equal-scale weapon arcs; maximum drift 9%.
- Bat: distinct upstroke/downstroke silhouettes; maximum drift 3%.

Validation compares every adjacent pair (including loop closure for cycles), checks full-frame pixel deltas, checks silhouette-only deltas in named body regions, enforces volume tolerances, and rejects detached structural hero components.

### Scene

The scene uses clustered piers, multiple pointed lancets, intersecting vault ribs, a rose window, distant spires, masonry courses, cracks, moss, perspective floor slabs, moon rays, ordered-dither torch pools, and contact shadows. Moonlight and torchlight use named palette colors rather than alpha-blended arbitrary RGBs. Actors share a documented ground line; floating enemies are deliberately unshadowed.

## Review artifacts

A full build creates exactly 16 files in `sheets/`:

- Category sheets: `hero.png`, `enemies.png`, `props.png`, `items.png`, `tiles.png`, `ui.png`, and `all.png`.
- Animation strips/GIFs: `hero_idle_*`, `hero_walk_*`, `hero_attack_*`, and `enemy_bat_*`.
- Best scene screenshot: `scene.png`.

To add an asset: add one `AssetSpec`, implement it in the matching builder module, use palette names only, and run the complete verification block above. Builder/spec mismatches, stale files, wrong dimensions, wrong modes, palette leaks, alpha leaks, nondeterministic bytes, and missing review artifacts all fail validation.

## Playable game vertical slice

The repository also contains a complete, dependency-free browser game: **Nocturne Keep**. It uses only the generated PNGs in `out/` at runtime and keeps the asset generator/documentation above unchanged.

### Local run

From the project root:

```bash
npm test
npm run build
npm run serve
```

Open `http://localhost:4173/`. `npm run build` recreates a self-contained `dist/` directory with relative asset paths; it copies only the generated PNGs required by the game. The server is intentionally plain Python, so no package install or runtime network access is required.

### Controls

- **A / D** or **Left / Right** — move
- **Space** or **Up** — jump
- **X / J** — whip attack
- **R / Enter** — restart after a win or loss
- Large touch buttons are available below the canvas on desktop and portrait mobile.

Defeat the skeleton and bat, collect hearts and gold, then reach the eastern door. The simulation runs at a fixed 60 Hz step and has deterministic enemy patrols, collisions, damage, collectibles, and win/loss transitions.

### Game source layout

- `game/src/engine.js` — deterministic state, physics, collisions, combat, collectibles, and state transitions
- `game/src/render.js` — crisp nearest-neighbor Canvas renderer and generated-asset loader
- `game/src/input.js` — keyboard/pointer input normalization
- `game/src/main.js` — fixed-step browser loop
- `game/test/engine.test.js` — browser-free core simulation tests
- `game/build.mjs` — zero-dependency static build into `dist/`
- `.github/workflows/pages.yml` — GitHub Pages deployment of `dist/` on pushes to `main` or manual dispatch
