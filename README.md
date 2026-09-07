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

## Playable game: Nocturne Keep — The Ashen Bell

The repository contains a framework-free, mobile-first, menu-driven turn-based RPG. It keeps the generated Nocturne Cathedral pixel art, but replaces the action-platformer loop with an original three-hero gothic quest through the keep, chapel crypt, and Ashen Bell tower.

### Local run

From the project root:

```bash
npm test
npm run build
npm run serve
```

Open `http://127.0.0.1:4173/`. The server is plain Python. `npm run build` creates a self-contained `dist/` tree with relative HTML, ES module, JSON, and generated PNG paths. Runtime code has no CDN, remote font, API, or network dependency.

### Game loop and controls

- **New Game** starts Rowan Vey (Ash Warden), Selene Mourne (Moon Oracle), and Garrick Rook (Grave Knight).
- Three authored nodes progress through the **Outer Keep**, **Chapel / Crypt**, and **Bell Tower**.
- Battles use **Attack**, **Skills / Magic**, **Items**, **Defend**, and **Run**, followed by target selection where required.
- The data catalog contains five regular enemy types plus the Ashen Bellkeeper boss, seven usable items, and eight player/enemy skills.
- Battles include seeded damage variance, critical hits, enemy AI, MP costs, status effects, guard/defend mitigation, rewards, XP/levels, escape chance, victory, defeat, and a dedicated ending screen.
- `Continue Saved Game` restores the latest localStorage autosave. Meaningful reducer actions autosave; **Return to Title** clears the active save. Keyboard users can use `1`–`5` for the main battle commands and `Escape` to back out.

### Source layout

- `game/engine/` — deterministic reducer, state/invariants, seeded RNG, save serialization, combat turn resolution.
- `game/data/*.json` — heroes, enemies, skills, items, encounters, and story dialogue. Content additions do not require engine edits.
- `game/ui/` — DOM menus, battle log, responsive presentation, local save bridge, and generated-art asset mapping.
- `game/styles.css` — portrait-first layout, `100dvh`, safe-area insets, pixel presentation, 44px controls, and landscape guidance.
- `game/build.mjs` — copies the source modules/data and only required files from `out/` into `dist/`.
- `game/test/engine.test.js` — save round-trip, replay determinism, battle/status/inventory, victory/defeat, and progression checks.
- `game/test/mobile-contract.test.js` — viewport, accessibility, safe-area, local-path, and data/build contracts.

### iPhone 15 / GitHub Pages target

The primary target is **393x852 CSS pixels** in portrait, with 390x844 remaining within the same responsive rules. The document uses `viewport-fit=cover`, safe-area `env()` insets, `100dvh` with a fallback, `overscroll-behavior: none`, `touch-action` gesture suppression, nearest-neighbor generated art, and real keyboard-accessible buttons. Landscape phone viewports hide the game surface and show a portrait guidance state.

The built entrypoint and all runtime references are relative, so `dist/` is safe beneath a GitHub Pages repository path. The intended project URL is `https://plainmean.github.io/nocturne-keep/`. No GitHub branch or remote deployment is initialized by this task.

Review screenshot: `game/review/nocturne-keep-rpg-iphone15.webp`.

### Verification

The exact verification block used for this build:

```bash
python3 -m unittest discover -s tests -v
python3 -m src.validate
python3 -m src.digest
npm test
npm run build
```

Observed results:

- Python regression suite: **16 tests passed**; native validator checked **110 assets and 16 review artifacts**; digest remained `a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4`.
- Node/browser-free suite: **13 tests passed**, zero failures.
- Build: `dist/` with **32 generated RPG assets**, JSON content, engine modules, UI modules, and `runtimeNetworkDependencies: 0` in `dist/BUILD_INFO.json`.
- Browser smoke at **393x852**: title, New Game, story exploration, encounter launch, command menu, attack target selection, first-battle victory, reload/Continue Saved Game, and restart were exercised. Document scroll dimensions stayed `393x852`.
- Landscape smoke at **852x393**: portrait guidance displayed and document dimensions stayed `852x393`.
- A static scan of `dist/` found no `http://`, `https://`, root-relative `src`/`href`, or root-relative module URLs.

Full command output and limitations are recorded in `TURN_BASED_BUILD_REPORT.md`.
