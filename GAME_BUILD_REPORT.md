# Nocturne Keep Game Build Report

## Scope

Built a focused, single-screen gothic castle hall action-platformer in `game/`. The runtime is framework-free Canvas plus ES modules. It uses generated assets from `out/` only; the Python asset generator, manifest, validation rules, and existing review documentation remain unchanged.

Selected generated assets from `out/manifest.json`:

- Hero animation frames: `hero_idle_0..3.png`, `hero_walk_0..5.png`, and `hero_attack_0..5.png` — all 48x48.
- Enemies: `enemy_skeleton.png` (32x40) and `enemy_bat_0..1.png` (32x24).
- Gameplay art: 16x16 floor/wall/platform tiles, 16x32 architectural pieces, generated background pieces, and native-size prop sprites.
- Pickups/HUD: `pickup_heart_small.png`, `pickup_gold.png`, heart icons, health bar, and subweapon frame.

The manifest contains 110 native RGBA PNGs. The production build copies the 53 assets actually used by the game into `dist/assets/`.

## Runtime implementation

- `game/src/engine.js` — deterministic 60 Hz simulation, fixed platforms, gravity, jump, horizontal movement, attack hitbox, enemy patrols, enemy/player damage, invulnerability, collectibles, particles, exit unlock, win/loss/restart states.
- `game/src/render.js` — nearest-neighbor Canvas renderer, cathedral composition, HUD, overlays, asset loading, and animation selection.
- `game/src/input.js` — keyboard and pointer/touch input normalization with pointer capture, multi-pointer ownership, and blur/pagehide/cancel cleanup.
- `game/src/main.js` — browser boot, fixed-step loop, canvas pointer lifecycle, and browser gesture/selection/context-menu suppression.
- `game/index.html` and `game/styles.css` — relative Pages-safe entry paths, iPhone 15 viewport metadata, safe-area-aware 16:9 layout, large touch controls, compact mobile instructions, and a narrow-landscape portrait message.
- `game/test/engine.test.js` — browser-free simulation contract tests.
- `game/test/mobile-contract.test.js` — browser-free viewport/CSS contract checks and simulated pointer lifecycle tests.
- `game/review/nocturne-keep-iphone15.webp` — verified 393x852 production smoke screenshot.
- `game/build.mjs` — zero-dependency static build into `dist/`.
- `.github/workflows/pages.yml` — Pages deployment on `main` pushes and manual dispatch, with the requested read/write/id-token permissions.

## Exact verification commands

Run from the repository root:

```bash
python3 -m src.generate
python3 -m src.validate
python3 -m src.digest
python3 -m unittest discover -s tests -v
npm test
npm run build
python3 -m http.server 4174 --directory dist
```

Results from the completed hardening run:

- Existing asset-pipeline verification (unchanged): 110 native assets, aggregate digest `a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4`, 16 review artifacts, and **16 Python tests passed**.
- `npm test`: **8 tests passed** — 6 browser-free engine tests plus 2 mobile contract/pointer-input tests.
- `npm run build`: **53 generated PNG assets copied** into a fresh `dist/` artifact.
- `dist/BUILD_INFO.json`: `assetCount` is **53**.

## Static artifact checks

- `dist/index.html`, `dist/styles.css`, `dist/game/{engine,input,main,render}.js`, `dist/BUILD_INFO.json`, `dist/assets/`, and the iPhone favicon are present.
- A static scan of `dist/` found no `http://`, `https://`, or absolute-root (`/asset`) runtime URLs.
- HTML/module/asset paths remain relative and resolve below `/nocturne-keep/`.
- The build has no runtime network dependency; every runtime request is a local Pages artifact.

## Browser smoke test

Started the exact production artifact with:

```bash
python3 -m http.server 4174 --directory dist
```

Loaded `http://127.0.0.1:4174/` in the browser at **393x852 CSS pixels** (iPhone 15 portrait target).

Observed:

- Canvas presentation measured **375x210.9375 CSS px**, preserving 16:9 and pixelated rendering.
- Four visible touch controls each measured **88.25x56 CSS px**; all controls stayed below the canvas and inside the viewport.
- Document `scrollWidth`/`scrollHeight` stayed exactly **393/852**; no horizontal overflow or page scroll occurred.
- A pointer-equivalent touch on Jump changed the title screen to gameplay. Held right/left pointer controls reached a real loss state; a visible Jump touch restarted the game. Canvas hashes changed for both transitions.
- Landscape check at **852x393** displayed the portrait orientation message, hid the clipped gameplay layout, and kept document dimensions at **852/393**.
- Loading completed (`#load-status.hidden === true`); console errors, page errors, and HTTP responses with status >= 400 were all **zero**.

Review screenshot captured from the active restarted game scene:

- `game/review/nocturne-keep-iphone15.webp`
- Existing desktop smoke artifact: `game/review/nocturne-keep-smoke.webp`

The game is ready for a parent agent to commit and deploy. No GitHub repository was initialized, pushed, or accessed with credentials.
