import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const gameRoot = fileURLToPath(new URL("..", import.meta.url));
const readGameFile = (name) => readFileSync(join(gameRoot, name), "utf8");

test("mobile shell declares portrait-safe viewport, touch sizing, and landscape guidance", () => {
  const html = readGameFile("index.html");
  const styles = readGameFile("styles.css");
  const main = readGameFile("ui/main.js");
  const render = readGameFile("ui/render.js");

  assert.match(html, /viewport-fit=cover/);
  assert.match(html, /maximum-scale=1/);
  assert.match(html, /user-scalable=no/);
  assert.match(html, /class="orientation-message"/);
  assert.match(html, /href="\.\/styles\.css"/);
  assert.match(html, /src="\.\/game\/ui\/main\.js"/);
  assert.match(html, /href="\.\/assets\/bg_moon\.png"/);
  assert.doesNotMatch(html, /(?:src|href)=["']\//);
  assert.match(styles, /height: 100dvh/);
  assert.match(styles, /min-height: 100dvh/);
  assert.match(styles, /overflow:\s*hidden/);
  assert.match(styles, /touch-action:\s*none/);
  assert.match(styles, /min-height:\s*44px/);
  assert.match(styles, /orientation:\s*landscape/);
  for (const inset of ["top", "right", "bottom", "left"]) assert.match(styles, new RegExp(`safe-area-inset-${inset}`));
  assert.match(main, /data-action/);
  assert.doesNotMatch(main, /https?:\/\//);
  assert.doesNotMatch(render, /https?:\/\//);
  assert.doesNotMatch(render, /<canvas|canvas\./);
});

test("RPG menus expose commands and generated art uses manifest indirection", () => {
  const render = readGameFile("ui/render.js");
  const build = readGameFile("build.mjs");
  const assets = readGameFile("ui/assets.js");

  for (const label of ["Attack", "Skills / Magic", "Items", "Defend", "Run", "Turn Order", "Round Log"]) {
    assert.match(render, new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(render, /select-target/);
  assert.match(render, /getTargetOptions/);
  assert.match(assets, /ASSET_MANIFEST/);
  assert.match(build, /out\/manifest\.json/);
  assert.match(build, /selectedAssets/);
  assert.match(build, /gameRoot, "ui"/);
  assert.doesNotMatch(build, /src.*engine\.js/);
});
