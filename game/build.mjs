import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { ASSET_NAMES } from "./src/render.js";

const gameRoot = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(gameRoot, "..");
const distRoot = join(projectRoot, "dist");
const distGame = join(distRoot, "game");
const distAssets = join(distRoot, "assets");

await rm(distRoot, { recursive: true, force: true });
await mkdir(distGame, { recursive: true });
await mkdir(distAssets, { recursive: true });

await cp(join(gameRoot, "index.html"), join(distRoot, "index.html"));
await cp(join(gameRoot, "styles.css"), join(distRoot, "styles.css"));
for (const file of ["engine.js", "input.js", "main.js", "render.js"]) {
  await cp(join(gameRoot, "src", file), join(distGame, file));
}

for (const name of ASSET_NAMES) {
  const source = join(projectRoot, "out", `${name}.png`);
  if (!existsSync(source)) {
    throw new Error(`Missing generated source asset: out/${name}.png`);
  }
  await cp(source, join(distAssets, `${name}.png`));
}

await writeFile(
  join(distRoot, "BUILD_INFO.json"),
  `${JSON.stringify({ assetCount: ASSET_NAMES.length, source: "out/manifest.json", generatedBy: "game/build.mjs" }, null, 2)}\n`,
);

console.log(`Built dist/ with ${ASSET_NAMES.length} generated PNG assets.`);
