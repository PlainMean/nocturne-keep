import assert from "node:assert/strict";
import test from "node:test";

import { ENEMIES, HEROES, ITEMS, SKILLS } from "../engine/catalog.js";
import { ASSET_MANIFEST } from "../ui/assets.js";

test("catalog contains the requested vertical-slice breadth", () => {
  assert.equal(HEROES.length, 3);
  assert.ok(ENEMIES.filter((enemy) => !enemy.boss).length >= 5);
  assert.ok(ENEMIES.some((enemy) => enemy.boss));
  assert.ok(SKILLS.length >= 4);
  assert.ok(SKILLS.some((skill) => skill.cost > 0));
  assert.ok(ITEMS.length >= 6);
  assert.ok(SKILLS.some((skill) => skill.kind === "heal"));
  assert.ok(SKILLS.some((skill) => skill.status?.id));
});

test("every party and enemy art reference resolves through the generated manifest", () => {
  for (const hero of HEROES) assert.ok(ASSET_MANIFEST[hero.portrait], `missing portrait ${hero.portrait}`);
  for (const enemy of ENEMIES) assert.ok(ASSET_MANIFEST[enemy.art], `missing enemy art ${enemy.art}`);
});
