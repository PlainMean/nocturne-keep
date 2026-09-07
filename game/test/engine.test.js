import assert from "node:assert/strict";
import test from "node:test";

import {
  createBattleTestState,
  assertStateInvariant,
  createGame,
  createNewGame,
  deserializeState,
  getTargetOptions,
  reduceGame,
  serializeState,
} from "../engine/index.js";
import { ITEMS, STORY } from "../engine/catalog.js";

function enterFirstBattle(seed = 1) {
  let state = createNewGame(seed);
  state = reduceGame(state, { type: "EXPLORE_STORY" });
  return reduceGame(state, { type: "ENTER_STORY_ENCOUNTER" });
}

function attackOnce(state) {
  if (state.mode !== "battle") return state;
  if (state.battle.phase === "target") {
    const target = getTargetOptions(state).find((entry) => entry.hp > 0);
    return target ? reduceGame(state, { type: "SELECT_TARGET", targetId: target.id }) : state;
  }
  if (state.battle.menu === "main") return reduceGame(state, { type: "COMMAND", command: "attack" });
  return reduceGame(state, { type: "COMMAND", command: "back" });
}

function attackUntilDone(state, limit = 80) {
  for (let index = 0; index < limit && state.mode === "battle"; index += 1) state = attackOnce(state);
  return state;
}

function fullRoute(seed = 1) {
  let state = createNewGame(seed);
  for (let chapter = 0; chapter < STORY.length && state.mode === "story"; chapter += 1) {
    state = reduceGame(state, { type: "EXPLORE_STORY" });
    state = reduceGame(state, { type: "ENTER_STORY_ENCOUNTER" });
    state = attackUntilDone(state, 160);
  }
  return state;
}

test("save serialization round-trips a live battle without losing RNG or inventory", () => {
  const before = enterFirstBattle(17);
  const after = attackOnce(before);
  const restored = deserializeState(serializeState(after));
  assert.deepEqual(restored, after);
  assert.equal(restored.seed, 17);
  assert.equal(restored.rngCalls, after.rngCalls);
  assert.equal(typeof restored.inventory.ember_tonic, "number");
});

test("the reducer is a deterministic replay from the same seed and actions", () => {
  const first = attackUntilDone(enterFirstBattle(43), 12);
  const second = attackUntilDone(enterFirstBattle(43), 12);
  assert.deepEqual(second, first);
  assert.ok(first.rngCalls > 0);
  assert.notEqual(first.rngCalls, 0);
});

test("battle resolution consumes a command, rolls damage, and advances the round log", () => {
  const before = enterFirstBattle(1);
  const enemyHp = before.battle.enemies[0].hp;
  const after = attackUntilDone(before, 2);
  assert.equal(after.mode, "battle");
  assert.ok(after.battle.enemies[0].hp < enemyHp, "the selected attack must resolve against the target");
  assert.ok(after.battle.log.some((line) => /hits|misses|damage/i.test(line)));
  assert.ok(after.rngCalls > before.rngCalls);

  const roundBoundary = attackUntilDone(before, 8);
  assert.ok(roundBoundary.battle?.round > 1 || roundBoundary.mode !== "battle");
});

test("status effects tick, expire, and can be removed by a data-driven item", () => {
  let state = createBattleTestState(5);
  const actor = state.party.find((member) => member.id === state.battle.activeId);
  actor.statuses = [{ id: "burn", turns: 2, power: 9 }];
  const startingHp = actor.hp;
  for (let turn = 0; turn < 8 && state.mode === "battle"; turn += 1) {
    if (state.battle.phase === "target") state = reduceGame(state, { type: "CANCEL_TARGET" });
    else if (state.battle.menu !== "main") state = reduceGame(state, { type: "COMMAND", command: "back" });
    else state = reduceGame(state, { type: "COMMAND", command: "defend" });
  }
  assert.ok(state.party.find((member) => member.id === actor.id).hp < startingHp || state.mode !== "battle", "burn must damage during a turn tick");

  if (state.mode === "battle") {
    const cureTarget = state.party.find((member) => member.hp > 0);
    cureTarget.statuses = [{ id: "poison", turns: 2, power: 4 }];
    state = reduceGame(state, { type: "COMMAND", command: "items" });
    state = reduceGame(state, { type: "SELECT_ITEM", itemId: "grave_salt" });
    const target = getTargetOptions(state).find((entry) => entry.id === cureTarget.id);
    state = reduceGame(state, { type: "SELECT_TARGET", targetId: target.id });
    assert.equal(state.party.find((member) => member.id === cureTarget.id).statuses.some((entry) => entry.id === "poison"), false);
  }
});

test("inventory choices consume stock and restore the selected ally", () => {
  let state = enterFirstBattle(9);
  const actor = state.party.find((member) => member.id === state.battle.activeId);
  actor.hp = 10;
  const stockBefore = state.inventory.ember_tonic;
  state = reduceGame(state, { type: "COMMAND", command: "items" });
  state = reduceGame(state, { type: "SELECT_ITEM", itemId: "ember_tonic" });
  const target = getTargetOptions(state).find((entry) => entry.id === actor.id);
  assert.ok(target);
  state = reduceGame(state, { type: "SELECT_TARGET", targetId: target.id });
  const healed = state.party.find((member) => member.id === actor.id);
  assert.equal(state.inventory.ember_tonic, stockBefore - 1);
  assert.ok(healed.hp > 10);
});

test("victory grants rewards and the final boss reaches the win mode", () => {
  const firstVictory = attackUntilDone(enterFirstBattle(1), 40);
  assert.equal(firstVictory.mode, "story");
  assert.equal(firstVictory.lastBattle.victory, true);
  assert.equal(firstVictory.storyId, "chapel_crypt");
  assert.ok(firstVictory.gold > 0);

  const ending = fullRoute(1);
  assert.equal(ending.mode, "victory");
  assert.equal(ending.lastBattle.victory, true);
  assert.equal(ending.lastBattle.encounterId, "ashen_bell");
  assert.ok(ending.party.every((member) => member.level > 1));
});

test("defeat is reachable when the last living hero falls", () => {
  let state = enterFirstBattle(2);
  const active = state.party.find((member) => member.id === state.battle.activeId);
  for (const member of state.party) member.hp = member.id === active.id ? 1 : 0;
  state = reduceGame(state, { type: "COMMAND", command: "defend" });
  assert.equal(state.mode, "defeat");
  assert.equal(state.battle, null);
  assert.equal(state.lastBattle.victory, false);
});

test("all item definitions are present and the new game starts with usable stock", () => {
  const state = createGame(3);
  assert.ok(ITEMS.length >= 6);
  for (const item of ITEMS) {
    assert.ok(state.inventory[item.id] > 0, `${item.id} should be usable at the start`);
  }
});

test("invariant and soak replay coverage survives repeated story and battle transitions", () => {
  for (const seed of [3, 17, 91, 0xdecafbad]) {
    let state = createGame(seed);
    for (let step = 0; step < 240; step += 1) {
      assertStateInvariant(state);
      if (state.mode === "title") state = createNewGame(seed);
      else if (state.mode === "story") {
        state = reduceGame(state, { type: "EXPLORE_STORY" });
        state = reduceGame(state, { type: "ENTER_STORY_ENCOUNTER" });
      } else if (state.mode === "battle") state = attackOnce(state);
      else state = reduceGame(state, { type: "RESTART" });
      assert.deepEqual(deserializeState(serializeState(state)), state);
    }
    assert.ok(state.rngCalls >= 0);
  }
});
