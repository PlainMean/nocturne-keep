# Nocturne Keep: The Ashen Bell — Turn-Based Build Report

## Deliverable

- Deployable artifact: `dist/`
- Entry point: `dist/index.html`
- Runtime modules: `dist/game/engine/`, `dist/game/data/`, `dist/game/ui/`
- Generated art copied from `out/`: `dist/assets/` (32 PNGs plus the selected manifest)
- Build metadata: `dist/BUILD_INFO.json`
- Save key: `nocturne-keep:ashen-bell:v1`

The runtime is framework-free browser ES modules. The reducer clones state before applying actions; seeded RNG state is represented by `seed` and `rngCalls`. JSON catalogs provide heroes, enemies, skills, items, encounters, and story text.

## Architecture

- `game/data/*.json` is the content source of truth: 3 heroes, 5 regular enemies, 1 boss, 13 skills, 7 items, 3 encounters, and 3 story chapters.
- `game/engine/state.js` defines versioned JSON-safe state and invariant checks. `game/engine/rng.js` is a seeded integer/weighted RNG; browser APIs and `Math.random` are absent from the engine.
- `game/engine/reducer.js` is the deterministic reducer. It resolves story exploration, command/menu transitions, target validation, speed-sorted turns, enemy AI, accuracy/variance/critical math, defense/ward/shaken/frenzy modifiers, status ticks, HP/MP, XP/levels, rewards, escape, victory, defeat, and restart.
- `game/engine/save.js` validates `JSON.stringify`/`JSON.parse` round trips. `game/engine/index.js` is the test/runtime export boundary.
- `game/ui/main.js` is the DOM event-delegation/local-save bridge. `game/ui/render.js` owns responsive DOM screens and real buttons. `game/ui/assets.js` maps logical art IDs to the generated `out/manifest.json` files; gameplay data never scatters generated filenames.
- `game/build.mjs` cleans `dist/`, copies only the UI/engine/data modules, resolves selected asset IDs against the generated manifest, and writes `dist/assets/manifest.json` plus build metadata.

## Controls and path

Portrait route: `New Game` → `Explore the Keep` → chapter encounter button → `Attack`/`Skills / Magic`/`Items`/`Defend`/`Run` → target button → round resolution. `Enter` or Space activates title/story/end actions, number keys 1–5 select visible menu entries, and Escape backs out of target/submenus. Touch users use the same real buttons; all controls are at least 44px high. The title offers `Continue Saved Game` when local storage contains a valid version-2 state.

GitHub Pages path: `https://plainmean.github.io/nocturne-keep/`. All page/module/data/image paths are relative to the repository subpath; runtime has zero external network dependencies.

## Commands and observed output

### Python asset regression

```text
$ python3 -m src.generate
generated 110 native assets with Nocturne Cathedral
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4
review artifacts: 16 in /home/cmuxao/projects/hermes_area/pixel_assets/sheets

$ python3 -m src.validate
validated 110 native assets and 16 review artifacts

$ python3 -m src.digest
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4
disk assets: 110
aggregate digest: a88c2c9f7d933a242f64a6410cb9b6cc26040a066c7e4f0fc2746560822b48c4

$ python3 -m unittest discover -s tests -v
Ran 16 tests in 0.566s
OK
```

### Browser-free RPG tests and build

```text
$ npm test
ℹ tests 13
ℹ pass 13
ℹ fail 0

$ npm run build
Built dist/ with 32 generated RPG assets.
```

The Node tests cover save round-trip, replay determinism, damage/round resolution, burn and poison status behavior, item consumption/healing, first-room victory and rewards, full-route boss victory, defeat, and starting inventory.

## Browser verification

Production server:

```text
python3 -m http.server 4176 --directory dist
```

Browser tooling used a Chromium tab at `393x852` CSS pixels.

Observed portrait checks:

1. Title rendered with **Nocturne Keep** and **The Ashen Bell**; `New Game` was a real button.
2. `New Game` -> `Explore the Keep` -> `Enter the Iron Gate` reached the first battle.
3. Battle view showed large generated skeleton/bat art, three party cards, HP/MP meters, a visible turn order, round log, and five live commands.
4. `Attack` opened target selection; selecting an enemy returned to the command menu and advanced the deterministic battle.
5. Repeated attack actions reached the next story node and victory rewards through the actual DOM command path.
6. Reload exposed `Continue Saved Game`; activating it restored the autosaved story state.
7. A valid versioned defeat save fixture opened the defeat screen and `Return to Title` returned to `New Game`. The real defeat transition is also exercised by the Node reducer test (`defeat is reachable when the last living hero falls`).
8. Portrait document dimensions remained `393x852` with `scrollWidth=393` and `scrollHeight=852`.

Landscape check at `852x393`:

- The game surface was hidden and the portrait guidance message displayed.
- Document dimensions remained `852x393`.

Static artifact check:

```text
$ scan dist for https?://, root-relative src/href, and root-relative module URLs
No matches found
```

## Limitations

- Verification used Chromium automation at the iPhone 15 CSS viewport, not physical iPhone Safari hardware.
- The defeat-screen browser check used a valid saved-state fixture to reach the terminal UI quickly; reducer defeat behavior is covered by the deterministic browser-free test.
- No GitHub repository, branch, or remote push was created.
