const WORLD_WIDTH = 480;
const WORLD_HEIGHT = 270;
const FLOOR_Y = 228;
const PLAYER_WIDTH = 24;
const PLAYER_HEIGHT = 42;
const FIXED_STEP = 1;
const MAX_HEALTH = 5;
const MOVE_ACCELERATION = 0.34;
const MOVE_FRICTION = 0.72;
const MAX_MOVE_SPEED = 2.25;
const GRAVITY = 0.34;
const JUMP_VELOCITY = -7.1;
const MAX_FALL_SPEED = 7.5;
const ATTACK_DURATION = 18;
const ATTACK_COOLDOWN = 22;
const INVULNERABILITY_FRAMES = 52;

export const GAME_WIDTH = WORLD_WIDTH;
export const GAME_HEIGHT = WORLD_HEIGHT;
export const PLAYER_MAX_HEALTH = MAX_HEALTH;

export const PLATFORMS = Object.freeze([
  Object.freeze({ x: 0, y: FLOOR_Y, w: WORLD_WIDTH, h: WORLD_HEIGHT - FLOOR_Y, kind: "floor" }),
  Object.freeze({ x: 48, y: 184, w: 126, h: 8, kind: "platform" }),
  Object.freeze({ x: 302, y: 174, w: 124, h: 8, kind: "platform" }),
  Object.freeze({ x: 190, y: 136, w: 102, h: 8, kind: "platform" }),
]);

const EXIT = Object.freeze({ x: 450, y: 180, w: 24, h: 48 });

function makePlayer() {
  return {
    x: 34,
    y: FLOOR_Y - PLAYER_HEIGHT,
    w: PLAYER_WIDTH,
    h: PLAYER_HEIGHT,
    vx: 0,
    vy: 0,
    facing: 1,
    onGround: true,
    health: 4,
    maxHealth: MAX_HEALTH,
    invulnerable: 0,
    hurtTimer: 0,
    attackTimer: 0,
    attackCooldown: 0,
    attackHit: false,
    walkFrame: 0,
    idleFrame: 0,
  };
}

function makeEnemies() {
  return [
    {
      id: "skeleton-guard",
      type: "skeleton",
      x: 350,
      y: FLOOR_Y - 40,
      w: 27,
      h: 40,
      vx: 0,
      vy: 0,
      direction: -1,
      patrolMin: 316,
      patrolMax: 438,
      health: 2,
      maxHealth: 2,
      alive: true,
      hitTimer: 0,
    },
    {
      id: "castle-bat",
      type: "bat",
      x: 112,
      y: 84,
      w: 30,
      h: 22,
      vx: 0,
      vy: 0,
      direction: 1,
      patrolMin: 90,
      patrolMax: 382,
      baseY: 84,
      phase: 11,
      health: 1,
      maxHealth: 1,
      alive: true,
      hitTimer: 0,
    },
  ];
}

function makeCollectibles() {
  return [
    { id: "heart-landing", type: "heart", x: 102, y: 164, w: 16, h: 16, collected: false, bob: 0 },
    { id: "gold-window", type: "gold", x: 246, y: 110, w: 16, h: 16, collected: false, bob: 7 },
    { id: "gold-ledge", type: "gold", x: 392, y: 150, w: 16, h: 16, collected: false, bob: 13 },
  ];
}

function makeState(seed = 1337) {
  return {
    seed: seed >>> 0,
    tick: 0,
    status: "title",
    score: 0,
    collectedGold: 0,
    message: "",
    player: makePlayer(),
    enemies: makeEnemies(),
    collectibles: makeCollectibles(),
    particles: [],
    platforms: PLATFORMS.map((platform) => ({ ...platform })),
    exit: { ...EXIT },
  };
}

export function createGame(seed = 1337) {
  return makeState(seed);
}

export function restartGame(previousState) {
  const next = makeState(previousState?.seed ?? 1337);
  next.status = "playing";
  next.message = "The keep stirs...";
  return next;
}

export function startGame(state) {
  if (state.status === "title") {
    state.status = "playing";
    state.message = "Defeat the keep's guardians.";
  }
  return state;
}

export function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

export function attackHitbox(player) {
  const reach = 42;
  const y = player.y + 6;
  return player.facing > 0
    ? { x: player.x + player.w - 4, y, w: reach, h: 25 }
    : { x: player.x - reach + 4, y, w: reach, h: 25 };
}

export function isAttackActive(player) {
  if (player.attackTimer <= 0) return false;
  const elapsed = ATTACK_DURATION - player.attackTimer;
  return elapsed >= 3 && elapsed <= 13;
}

export function allEnemiesDefeated(state) {
  return state.enemies.every((enemy) => !enemy.alive);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function inputPressed(input, name) {
  return input?.[`${name}Pressed`] === true;
}

function inputHeld(input, name) {
  return input?.[name] === true;
}

function horizontalOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x;
}

function addParticles(state, x, y, color, count = 5) {
  for (let index = 0; index < count; index += 1) {
    const direction = index % 2 === 0 ? 1 : -1;
    state.particles.push({
      x,
      y,
      vx: direction * (0.35 + (index % 3) * 0.25),
      vy: -1.1 - (index % 4) * 0.28,
      life: 18 + index * 3,
      color,
      size: index % 2 === 0 ? 2 : 1,
    });
  }
}

function updateParticles(state) {
  for (const particle of state.particles) {
    particle.x += particle.vx;
    particle.y += particle.vy;
    particle.vy += 0.08;
    particle.life -= 1;
  }
  state.particles = state.particles.filter((particle) => particle.life > 0);
}

function movePlayer(state, input, dt) {
  const player = state.player;
  const direction = (inputHeld(input, "right") ? 1 : 0) - (inputHeld(input, "left") ? 1 : 0);

  if (direction !== 0) {
    player.vx = clamp(player.vx + direction * MOVE_ACCELERATION * dt, -MAX_MOVE_SPEED, MAX_MOVE_SPEED);
    player.facing = direction;
    player.walkFrame = (player.walkFrame + 1) % 36;
  } else {
    player.vx *= Math.pow(MOVE_FRICTION, dt);
    if (Math.abs(player.vx) < 0.04) player.vx = 0;
    player.idleFrame = (player.idleFrame + 1) % 48;
  }

  if (inputPressed(input, "jump") && player.onGround && player.attackTimer <= 0) {
    player.vy = JUMP_VELOCITY;
    player.onGround = false;
    addParticles(state, player.x + player.w / 2, player.y + player.h, "#a8a9bb", 4);
  }

  player.x = clamp(player.x + player.vx * dt, 4, WORLD_WIDTH - player.w - 4);

  const previousBottom = player.y + player.h;
  player.vy = clamp(player.vy + GRAVITY * dt, -20, MAX_FALL_SPEED);
  player.y += player.vy * dt;
  player.onGround = false;

  if (player.vy >= 0) {
    for (const platform of state.platforms) {
      const currentBottom = player.y + player.h;
      if (
        previousBottom <= platform.y + 0.5 &&
        currentBottom >= platform.y &&
        horizontalOverlap(player, platform)
      ) {
        player.y = platform.y - player.h;
        player.vy = 0;
        player.onGround = true;
        break;
      }
    }
  } else {
    const previousTop = previousBottom - player.h;
    for (const platform of state.platforms) {
      const platformBottom = platform.y + platform.h;
      if (
        previousTop >= platformBottom - 0.5 &&
        player.y <= platformBottom &&
        horizontalOverlap(player, platform)
      ) {
        player.y = platformBottom;
        player.vy = 0;
        break;
      }
    }
  }
}

function beginAttack(player) {
  if (player.attackCooldown <= 0 && player.attackTimer <= 0) {
    player.attackTimer = ATTACK_DURATION;
    player.attackCooldown = ATTACK_COOLDOWN;
    player.attackHit = false;
  }
}

function updateEnemies(state) {
  for (const enemy of state.enemies) {
    if (!enemy.alive) continue;
    enemy.hitTimer = Math.max(0, enemy.hitTimer - 1);

    if (enemy.type === "skeleton") {
      enemy.x += enemy.direction * 0.46;
      if (enemy.x <= enemy.patrolMin) {
        enemy.x = enemy.patrolMin;
        enemy.direction = 1;
      } else if (enemy.x + enemy.w >= enemy.patrolMax) {
        enemy.x = enemy.patrolMax - enemy.w;
        enemy.direction = -1;
      }
    } else {
      enemy.x += enemy.direction * 0.78;
      if (enemy.x <= enemy.patrolMin) {
        enemy.x = enemy.patrolMin;
        enemy.direction = 1;
      } else if (enemy.x + enemy.w >= enemy.patrolMax) {
        enemy.x = enemy.patrolMax - enemy.w;
        enemy.direction = -1;
      }
      enemy.y = enemy.baseY + Math.sin((state.tick + enemy.phase) * 0.08) * 11;
    }
  }
}

function damageEnemy(state, enemy) {
  enemy.health -= 1;
  enemy.hitTimer = 9;
  addParticles(state, enemy.x + enemy.w / 2, enemy.y + enemy.h / 2, "#f6c453", 6);
  if (enemy.health <= 0) {
    enemy.alive = false;
    state.score += enemy.type === "skeleton" ? 150 : 100;
    state.collectibles.push({
      id: `drop-${enemy.id}-${state.tick}`,
      type: "gold",
      x: enemy.x + enemy.w / 2 - 8,
      y: enemy.y + enemy.h - 12,
      w: 16,
      h: 16,
      collected: false,
      bob: state.tick % 17,
    });
    addParticles(state, enemy.x + enemy.w / 2, enemy.y + enemy.h / 2, "#c9d1e5", 10);
  }
}

function resolveAttack(state) {
  const player = state.player;
  if (!isAttackActive(player) || player.attackHit) return;
  const hitbox = attackHitbox(player);
  for (const enemy of state.enemies) {
    if (enemy.alive && rectsOverlap(hitbox, enemy)) {
      damageEnemy(state, enemy);
      player.attackHit = true;
      break;
    }
  }
}

function damagePlayer(state, enemy) {
  const player = state.player;
  if (player.invulnerable > 0) return;
  player.health = Math.max(0, player.health - 1);
  player.invulnerable = INVULNERABILITY_FRAMES;
  player.hurtTimer = 16;
  player.vx = enemy.x + enemy.w / 2 < player.x + player.w / 2 ? 1.7 : -1.7;
  player.vy = -3.1;
  addParticles(state, player.x + player.w / 2, player.y + player.h / 2, "#ef6f7a", 7);
  state.message = "The darkness bites back.";
  if (player.health <= 0) {
    state.status = "lost";
    state.message = "The keep claims another hunter.";
  }
}

function resolveEnemyContacts(state) {
  const player = state.player;
  for (const enemy of state.enemies) {
    if (enemy.alive && rectsOverlap(player, enemy)) {
      damagePlayer(state, enemy);
      if (state.status === "lost") return;
    }
  }
}

function resolveCollectibles(state) {
  const player = state.player;
  for (const item of state.collectibles) {
    if (item.collected || !rectsOverlap(player, item)) continue;
    if (item.type === "heart") {
      if (player.health < player.maxHealth) {
        player.health += 1;
        item.collected = true;
        state.message = "A heart rekindles your courage.";
        addParticles(state, item.x + 8, item.y + 8, "#ef5265", 7);
      }
    } else {
      item.collected = true;
      state.collectedGold += 1;
      state.score += 25;
      state.message = "Gold for the road ahead.";
      addParticles(state, item.x + 8, item.y + 8, "#f6c453", 7);
    }
  }
}

function resolveExit(state) {
  if (allEnemiesDefeated(state)) {
    state.message = "The eastern door is unsealed.";
    if (rectsOverlap(state.player, state.exit)) {
      state.status = "won";
      state.message = "The castle hall falls silent.";
      addParticles(state, state.exit.x + 10, state.exit.y + 20, "#f6c453", 14);
    }
  }
}

function updateTimers(state, dt) {
  const player = state.player;
  player.invulnerable = Math.max(0, player.invulnerable - dt);
  player.hurtTimer = Math.max(0, player.hurtTimer - dt);
  player.attackCooldown = Math.max(0, player.attackCooldown - dt);
  if (player.attackTimer > 0) player.attackTimer = Math.max(0, player.attackTimer - dt);
}

export function stepGame(state, input = {}, dt = FIXED_STEP) {
  if (state.status === "title") {
    if (
      inputHeld(input, "left") ||
      inputHeld(input, "right") ||
      inputPressed(input, "jump") ||
      inputPressed(input, "attack") ||
      inputPressed(input, "start")
    ) {
      startGame(state);
    }
    return state;
  }

  if (state.status === "won" || state.status === "lost") {
    if (
      inputPressed(input, "restart") ||
      inputPressed(input, "start") ||
      inputPressed(input, "jump") ||
      inputPressed(input, "attack")
    ) {
      return restartGame(state);
    }
    return state;
  }

  state.tick += dt;
  const player = state.player;
  updateTimers(state, dt);
  if (inputPressed(input, "attack")) beginAttack(player);
  movePlayer(state, input, dt);
  updateEnemies(state);
  resolveAttack(state);
  resolveEnemyContacts(state);
  resolveCollectibles(state);
  resolveExit(state);
  updateParticles(state);

  if (state.status === "playing" && player.y > WORLD_HEIGHT + 30) {
    player.health = 0;
    state.status = "lost";
    state.message = "You vanish beneath the ruined floor.";
  }

  return state;
}

export function playerAnimation(player) {
  if (player.hurtTimer > 0) return { kind: "hurt", frame: 0 };
  if (!player.onGround) return { kind: "airborne", frame: 0 };
  if (player.attackTimer > 0) {
    const elapsed = ATTACK_DURATION - player.attackTimer;
    return { kind: "attack", frame: Math.min(5, Math.floor(elapsed / 3)) };
  }
  if (Math.abs(player.vx) > 0.12) {
    return { kind: "walk", frame: Math.floor(player.walkFrame / 6) % 6 };
  }
  return { kind: "idle", frame: Math.floor(player.idleFrame / 12) % 4 };
}

export function getConstants() {
  return Object.freeze({
    attackDuration: ATTACK_DURATION,
    attackCooldown: ATTACK_COOLDOWN,
    fixedStep: FIXED_STEP,
    floorY: FLOOR_Y,
    gravity: GRAVITY,
    jumpVelocity: JUMP_VELOCITY,
    playerHeight: PLAYER_HEIGHT,
    playerWidth: PLAYER_WIDTH,
  });
}
