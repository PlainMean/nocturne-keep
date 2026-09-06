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
- `game/src/input.js` — keyboard and pointer/touch input normalization.
- `game/src/main.js` — browser boot and fixed-step loop.
- `game/index.html` and `game/styles.css` — responsive desktop/portrait layout and large touch controls.
- `game/test/engine.test.js` — browser-free simulation contract tests.
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
```

Results from the completed run:

- `src.generate`: generated 110 native assets, aggregate digest `a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4`, and 16 review artifacts.
- `src.validate`: validated 110 native assets and 16 review artifacts.
- `src.digest`: reproduced the same aggregate digest.
- Python suite: **16 tests passed**.
- `npm test`: **6 simulation tests passed**.
- `npm run build`: **53 generated PNG assets copied** into a fresh `dist/` artifact.

## Static artifact checks

- `dist/index.html`, `dist/styles.css`, `dist/game/{engine,input,main,render}.js`, `dist/BUILD_INFO.json`, and all 53 PNG assets are present.
- All copied PNGs are non-empty.
- A static scan found no absolute-root asset URLs and no `http://` or `https://` runtime references.
- The build uses relative paths and has no runtime network dependency.

## Browser smoke test

Started the exact production artifact with:

```bash
python3 -m http.server 4173 --directory dist
```

Loaded `http://127.0.0.1:4173/` in a browser at desktop and portrait-mobile viewports.

Observed:

- Canvas loaded at 480x270 with generated pixel art and nearest-neighbor presentation.
- Desktop title screen, active gameplay, loss overlay, and restart flow rendered correctly.
- Keyboard movement, attack input, and restart after a real loss were exercised.
- Portrait layout kept the full canvas inside the viewport with four large touch controls and no horizontal overflow.
- Reload diagnostics recorded 0 page errors, 0 console errors, and 0 failed requests.

Review screenshot captured from the active restarted game scene:

- `game/review/nocturne-keep-smoke.webp`

The game is ready for a parent agent to commit and deploy. No GitHub repository was initialized, pushed, or accessed with credentials.
