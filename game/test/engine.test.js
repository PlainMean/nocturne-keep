import assert from "node:assert/strict";
import test from "node:test";

import {
  allEnemiesDefeated,
  attackHitbox,
  createGame,
  getConstants,
  rectsOverlap,
  restartGame,
  startGame,
  stepGame,
} from "../src/engine.js";
import { inputForTests } from "../src/input.js";

function playingGame() {
  const state = createGame(7);
  startGame(state);
  return state;
}

function advance(state, overrides = {}, frames = 1) {
  for (let frame = 0; frame < frames; frame += 1) {
    stepGame(state, inputForTests(overrides), 1);
  }
  return state;
}

test("horizontal movement accelerates, changes facing, and stays inside the hall", () => {
  const state = playingGame();
  const initialX = state.player.x;
  advance(state, { right: true }, 12);
  assert.ok(state.player.x > initialX + 10);
  assert.equal(state.player.facing, 1);

  advance(state, { left: true }, 30);
  assert.equal(state.player.facing, -1);
  assert.ok(state.player.x >= 4);

  state.player.x = 900;
  advance(state);
  assert.equal(state.player.x, 452);
});

test("jump applies gravity and lands on the floor and raised platforms", () => {
  const state = playingGame();
  const constants = getConstants();
  state.player.x = 10;
  advance(state, { jumpPressed: true });
  assert.equal(state.player.onGround, false);
  assert.equal(state.player.vy < 0, true);
  advance(state, {}, 60);
  assert.equal(state.player.onGround, true);
  assert.equal(state.player.y, constants.floorY - constants.playerHeight);

  state.player.x = 70;
  state.player.y = 130;
  state.player.vy = 5;
  state.player.onGround = false;
  advance(state, {}, 4);
  assert.equal(state.player.onGround, true);
  assert.equal(state.player.y, 184 - constants.playerHeight);
});

test("attack hitbox damages and defeats a nearby skeleton", () => {
  const state = playingGame();
  const player = state.player;
  player.x = 100;
  player.y = 140;
  player.onGround = false;
  player.invulnerable = 100;
  const skeleton = state.enemies.find((enemy) => enemy.type === "skeleton");
  skeleton.x = 132;
  skeleton.y = 142;
  skeleton.patrolMin = 132;
  skeleton.patrolMax = 180;
  skeleton.health = 1;
  skeleton.maxHealth = 1;

  assert.equal(rectsOverlap(attackHitbox(player), skeleton), true);
  advance(state, { attackPressed: true }, 6);
  assert.equal(skeleton.alive, false);
  assert.equal(state.score, 150);
  assert.ok(state.collectibles.some((item) => item.id.startsWith("drop-skeleton")));
});
test("enemy contact removes health and grants temporary invulnerability", () => {
  const state = playingGame();
  const player = state.player;
  const skeleton = state.enemies.find((enemy) => enemy.type === "skeleton");
  skeleton.x = player.x;
  skeleton.y = player.y;
  skeleton.patrolMin = player.x;
  skeleton.patrolMax = player.x + skeleton.w + 2;
  player.health = 3;
  advance(state);
  assert.equal(player.health, 2);
  assert.ok(player.invulnerable > 0);

  advance(state, {}, 4);
  assert.equal(player.health, 2);
});

test("heart and gold collectibles update health, score, and relic count", () => {
  const state = playingGame();
  const player = state.player;
  player.health = 2;
  const heart = state.collectibles.find((item) => item.type === "heart");
  player.x = heart.x;
  player.y = heart.y;
  advance(state);
  assert.equal(heart.collected, true);
  assert.equal(player.health, 3);

  const gold = state.collectibles.find((item) => item.type === "gold");
  player.x = gold.x;
  player.y = gold.y;
  const scoreBefore = state.score;
  advance(state);
  assert.equal(gold.collected, true);
  assert.equal(state.collectedGold, 1);
  assert.equal(state.score, scoreBefore + 25);
});

test("defeating every guardian and reaching the exit wins; zero health loses and restart is clean", () => {
  const state = playingGame();
  for (const enemy of state.enemies) enemy.alive = false;
  state.player.x = 440;
  state.player.y = 186;
  state.player.onGround = true;
  advance(state);
  assert.equal(allEnemiesDefeated(state), true);
  assert.equal(state.status, "won");

  const lost = playingGame();
  const skeleton = lost.enemies.find((enemy) => enemy.type === "skeleton");
  lost.player.health = 1;
  skeleton.x = lost.player.x;
  skeleton.y = lost.player.y;
  skeleton.patrolMin = lost.player.x;
  skeleton.patrolMax = lost.player.x + skeleton.w + 2;
  advance(lost);
  assert.equal(lost.status, "lost");
  const restarted = stepGame(lost, inputForTests({ restartPressed: true }));
  assert.equal(restarted.status, "playing");
  assert.equal(restarted.player.health, 4);
  assert.equal(restarted.enemies.every((enemy) => enemy.alive), true);

  const title = createGame();
  assert.equal(title.status, "title");
  stepGame(title, inputForTests({ startPressed: true }));
  assert.equal(title.status, "playing");
  assert.equal(restarted.seed, 7);
  assert.equal(rectsOverlap({ x: 0, y: 0, w: 1, h: 1 }, { x: 1, y: 1, w: 2, h: 2 }), false);
  assert.equal(typeof restartGame, "function");
});
