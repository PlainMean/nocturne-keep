import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { ASSET_FILES, ASSET_MANIFEST } from "./ui/assets.js";

const gameRoot = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(gameRoot, "..");
const distRoot = join(projectRoot, "dist");
const distGame = join(distRoot, "game");
const distUi = join(distGame, "ui");
const distEngine = join(distGame, "engine");
const distData = join(distGame, "data");
const distAssets = join(distRoot, "assets");

await rm(distRoot, { recursive: true, force: true });
await mkdir(distUi, { recursive: true });
await mkdir(distEngine, { recursive: true });
await mkdir(distData, { recursive: true });
await mkdir(distAssets, { recursive: true });

await cp(join(gameRoot, "index.html"), join(distRoot, "index.html"));
await cp(join(gameRoot, "styles.css"), join(distRoot, "styles.css"));
for (const file of ["main.js", "render.js", "assets.js"]) {
  await cp(join(gameRoot, "ui", file), join(distUi, file));
}
for (const file of ["catalog.js", "index.js", "reducer.js", "rng.js", "save.js", "state.js"]) {
  await cp(join(gameRoot, "engine", file), join(distEngine, file));
}
for (const file of ["encounters.json", "enemies.json", "heroes.json", "items.json", "skills.json", "story.json"]) {
  await cp(join(gameRoot, "data", file), join(distData, file));
}

const sourceManifest = JSON.parse(await readFile(join(projectRoot, "out", "manifest.json"), "utf8"));
const records = new Map(sourceManifest.assets.map((asset) => [asset.name, asset]));
const selectedAssets = [];
for (const [id, mapping] of Object.entries(ASSET_MANIFEST)) {
  const record = records.get(mapping.file);
  if (!record) throw new Error(`Missing generated manifest record for ${id}: ${mapping.file}`);
  const source = join(projectRoot, "out", record.file);
  if (!existsSync(source)) throw new Error(`Missing generated source asset: out/${record.file}`);
  await cp(source, join(distAssets, record.file));
  selectedAssets.push({ id, ...record });
}
if (selectedAssets.length !== ASSET_FILES.length) throw new Error("Asset manifest contains duplicate or missing file mappings");
await writeFile(join(distAssets, "manifest.json"), `${JSON.stringify({ source: "out/manifest.json", aggregate_sha256: sourceManifest.aggregate_sha256, assets: selectedAssets }, null, 2)}\n`);
await writeFile(
  join(distRoot, "BUILD_INFO.json"),
  `${JSON.stringify({ assetCount: selectedAssets.length, source: "out/manifest.json", generatedBy: "game/build.mjs", runtime: "turn-based-rpg", runtimeNetworkDependencies: 0 }, null, 2)}\n`,
);

console.log(`Built dist/ with ${selectedAssets.length} generated RPG assets.`);
