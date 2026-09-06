import { GAME_HEIGHT, GAME_WIDTH, allEnemiesDefeated, attackHitbox, isAttackActive, playerAnimation } from "./engine.js";

export const ASSET_NAMES = Object.freeze([
  "bg_moon",
  "bg_cloud",
  "bg_castle_silhouette",
  "tile_brick_wall",
  "tile_brick_wall_moss",
  "tile_stone_floor",
  "tile_stone_floor_cracked",
  "tile_cobble",
  "tile_platform",
  "tile_pillar",
  "tile_column",
  "tile_lancet_window",
  "tile_rose_window",
  "tile_door",
  "tile_trim",
  "tile_balcony",
  "prop_chandelier",
  "prop_banner",
  "prop_torch",
  "prop_brazier",
  "prop_bookshelf",
  "prop_altar",
  "prop_throne",
  "prop_hanging_chain",
  "prop_gargoyle_statue",
  "enemy_skeleton",
  "enemy_bat_0",
  "enemy_bat_1",
  "hero_idle_0",
  "hero_idle_1",
  "hero_idle_2",
  "hero_idle_3",
  "hero_walk_0",
  "hero_walk_1",
  "hero_walk_2",
  "hero_walk_3",
  "hero_walk_4",
  "hero_walk_5",
  "hero_attack_0",
  "hero_attack_1",
  "hero_attack_2",
  "hero_attack_3",
  "hero_attack_4",
  "hero_attack_5",
  "hero_airborne",
  "hero_hurt",
  "pickup_heart_small",
  "pickup_gold",
  "ui_heart_full",
  "ui_heart_empty",
  "ui_hp_bar",
  "ui_mana_bar",
  "ui_subweapon_frame",
]);

const PIXEL_FONT = '"Courier New", monospace';
const STARS = Object.freeze([
  [26, 31], [57, 19], [93, 37], [141, 24], [177, 42], [252, 18], [307, 29], [364, 17], [418, 39], [461, 24],
]);

export function loadAssets(assetBase) {
  return Promise.all(
    ASSET_NAMES.map(
      (name) =>
        new Promise((resolve, reject) => {
          const image = new Image();
          image.decoding = "async";
          image.onload = () => resolve([name, image]);
          image.onerror = () => reject(new Error(`Unable to load generated asset: ${name}.png`));
          image.src = new URL(`${name}.png`, assetBase).href;
        }),
    ),
  ).then((entries) => Object.fromEntries(entries));
}

function image(assets, name) {
  return assets[name];
}

function drawImage(ctx, assets, name, x, y, width, height, flip = false) {
  const sprite = image(assets, name);
  if (!sprite) return;
  const drawWidth = width ?? sprite.naturalWidth;
  const drawHeight = height ?? sprite.naturalHeight;
  const drawX = Math.round(x);
  const drawY = Math.round(y);
  if (!flip) {
    ctx.drawImage(sprite, drawX, drawY, drawWidth, drawHeight);
    return;
  }
  ctx.save();
  ctx.translate(drawX + drawWidth, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(sprite, 0, drawY, drawWidth, drawHeight);
  ctx.restore();
}

function drawBackground(ctx, assets, state) {
  ctx.fillStyle = "#090c1b";
  ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

  ctx.fillStyle = "#11162a";
  ctx.fillRect(0, 42, GAME_WIDTH, 182);
  for (const [x, y] of STARS) {
    ctx.fillStyle = (x + y) % 3 === 0 ? "#f6c453" : "#a8b2d2";
    ctx.fillRect(x, y, 1, 1);
  }
  drawImage(ctx, assets, "bg_moon", 224, 16, 48, 48);
  drawImage(ctx, assets, "bg_cloud", 48, 50, 72, 30);
  drawImage(ctx, assets, "bg_cloud", 350, 62, 72, 30, true);
  drawImage(ctx, assets, "bg_castle_silhouette", 8, 38, 192, 96);
  drawImage(ctx, assets, "bg_castle_silhouette", 286, 38, 192, 96, true);

  for (let y = 46; y < 222; y += 16) {
    for (let x = 0; x < GAME_WIDTH; x += 16) {
      const moss = (x / 16 + y / 16) % 11 === 0;
      drawImage(ctx, assets, moss ? "tile_brick_wall_moss" : "tile_brick_wall", x, y);
    }
  }

  drawImage(ctx, assets, "tile_lancet_window", 108, 61, 32, 64);
  drawImage(ctx, assets, "tile_lancet_window", 340, 61, 32, 64);
  drawImage(ctx, assets, "tile_rose_window", 224, 55, 48, 48);
  drawImage(ctx, assets, "tile_column", 74, 58, 32, 64);
  drawImage(ctx, assets, "tile_column", 374, 58, 32, 64, true);
  drawImage(ctx, assets, "prop_hanging_chain", 206, 44);
  drawImage(ctx, assets, "prop_hanging_chain", 280, 44, 12, 32, true);
  drawImage(ctx, assets, "prop_chandelier", 214, 8, 40, 24);
  drawImage(ctx, assets, "prop_banner", 160, 96);
  drawImage(ctx, assets, "prop_banner", 292, 96, 32, 40, true);
  drawImage(ctx, assets, "prop_torch", 20, 155);
  drawImage(ctx, assets, "prop_torch", 440, 155, 20, 24, true);
  drawImage(ctx, assets, "prop_gargoyle_statue", 68, 154);
  drawImage(ctx, assets, "prop_gargoyle_statue", 388, 154, 24, 32, true);

  ctx.fillStyle = "#292b43";
  ctx.fillRect(0, 214, GAME_WIDTH, 14);
  for (let x = 0; x < GAME_WIDTH; x += 16) {
    drawImage(ctx, assets, x % 48 === 0 ? "tile_stone_floor_cracked" : "tile_stone_floor", x, 220);
    drawImage(ctx, assets, "tile_cobble", x, 236);
    drawImage(ctx, assets, "tile_stone_floor", x, 252);
  }
  ctx.fillStyle = "#16192e";
  ctx.fillRect(0, 228, GAME_WIDTH, 2);
  for (let x = 30; x < GAME_WIDTH; x += 48) {
    ctx.fillStyle = "#47465f";
    ctx.fillRect(x, 245 + ((x / 48) % 2) * 3, 18, 1);
  }

  for (const platform of state.platforms) {
    if (platform.kind === "floor") continue;
    ctx.fillStyle = "#1c1d33";
    ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
    for (let x = platform.x; x < platform.x + platform.w; x += 16) {
      drawImage(ctx, assets, "tile_platform", x, platform.y - 8);
    }
    for (let x = platform.x; x < platform.x + platform.w; x += 16) {
      drawImage(ctx, assets, "tile_trim", x, platform.y - 1);
    }
  }

  drawImage(ctx, assets, "prop_bookshelf", 10, 184, 40, 40);
  drawImage(ctx, assets, "prop_altar", 202, 190, 32, 32);
  drawImage(ctx, assets, "prop_throne", 426, 184, 40, 40);
  drawImage(ctx, assets, "prop_brazier", 246, 202, 20, 20);

  if (allEnemiesDefeated(state)) {
    ctx.fillStyle = `rgba(246, 196, 83, ${0.16 + Math.sin(state.tick * 0.08) * 0.06})`;
    ctx.fillRect(449, 180, 25, 48);
  }
  drawImage(ctx, assets, "tile_door", 454, 196, 16, 32);
}

function drawCollectibles(ctx, assets, state) {
  for (const item of state.collectibles) {
    if (item.collected) continue;
    const bob = Math.round(Math.sin((state.tick + item.bob) * 0.12) * 2);
    drawImage(ctx, assets, item.type === "heart" ? "pickup_heart_small" : "pickup_gold", item.x, item.y + bob);
    ctx.fillStyle = item.type === "heart" ? "rgba(239, 82, 101, 0.16)" : "rgba(246, 196, 83, 0.16)";
    ctx.fillRect(item.x - 2, item.y + bob - 2, 20, 20);
  }
}

function drawEnemies(ctx, assets, state) {
  for (const enemy of state.enemies) {
    if (!enemy.alive) continue;
    const flash = enemy.hitTimer > 0 && enemy.hitTimer % 2 === 0;
    if (flash) ctx.globalAlpha = 0.55;
    if (enemy.type === "skeleton") {
      drawImage(ctx, assets, "enemy_skeleton", enemy.x - 2, enemy.y);
    } else {
      drawImage(ctx, assets, `enemy_bat_${Math.floor(state.tick / 8) % 2}`, enemy.x - 1, enemy.y - 1);
    }
    ctx.globalAlpha = 1;
    if (enemy.health < enemy.maxHealth) {
      ctx.fillStyle = "#151528";
      ctx.fillRect(enemy.x, enemy.y - 5, enemy.w, 2);
      ctx.fillStyle = "#ef6f7a";
      ctx.fillRect(enemy.x, enemy.y - 5, Math.ceil((enemy.w * enemy.health) / enemy.maxHealth), 2);
    }
  }
}

function drawPlayer(ctx, assets, state) {
  const player = state.player;
  const animation = playerAnimation(player);
  const spriteName = animation.kind === "idle"
    ? `hero_idle_${animation.frame}`
    : animation.kind === "walk"
      ? `hero_walk_${animation.frame}`
      : animation.kind === "attack"
        ? `hero_attack_${animation.frame}`
        : `hero_${animation.kind}`;
  const flash = player.invulnerable > 0 && Math.floor(player.invulnerable / 4) % 2 === 0;
  if (flash) ctx.globalAlpha = 0.5;
  drawImage(ctx, assets, spriteName, player.x - 12, player.y - 6, 48, 48, player.facing < 0);
  ctx.globalAlpha = 1;

  if (isAttackActive(player)) {
    const hitbox = attackHitbox(player);
    ctx.fillStyle = "rgba(246, 196, 83, 0.16)";
    ctx.fillRect(hitbox.x, hitbox.y, hitbox.w, hitbox.h);
    ctx.fillStyle = "#f6c453";
    ctx.fillRect(player.facing > 0 ? hitbox.x + hitbox.w - 3 : hitbox.x, hitbox.y + 11, 3, 3);
  }
}

function drawParticles(ctx, state) {
  for (const particle of state.particles) {
    ctx.globalAlpha = Math.min(1, particle.life / 12);
    ctx.fillStyle = particle.color;
    ctx.fillRect(Math.round(particle.x), Math.round(particle.y), particle.size, particle.size);
  }
  ctx.globalAlpha = 1;
}

function drawHud(ctx, assets, state) {
  ctx.fillStyle = "rgba(10, 12, 29, 0.94)";
  ctx.fillRect(8, 7, 464, 30);
  ctx.strokeStyle = "#55546e";
  ctx.lineWidth = 1;
  ctx.strokeRect(8.5, 7.5, 463, 29);
  ctx.fillStyle = "#f6c453";
  ctx.font = `bold 8px ${PIXEL_FONT}`;
  ctx.textAlign = "left";
  ctx.fillText("NOCTURNE KEEP", 16, 17);
  ctx.fillStyle = "#a8b2d2";
  ctx.font = `7px ${PIXEL_FONT}`;
  ctx.fillText("HP", 16, 29);
  drawImage(ctx, assets, "ui_hp_bar", 31, 22, 96, 10);
  if (state.player.health < state.player.maxHealth) {
    ctx.fillStyle = "#17192e";
    ctx.fillRect(37 + state.player.health * 16, 25, (state.player.maxHealth - state.player.health) * 16 - 2, 4);
  }
  for (let index = 0; index < state.player.maxHealth; index += 1) {
    drawImage(ctx, assets, index < state.player.health ? "ui_heart_full" : "ui_heart_empty", 138 + index * 11, 20, 8, 8);
  }
  drawImage(ctx, assets, "pickup_gold", 206, 17, 16, 16);
  ctx.fillStyle = "#f6c453";
  ctx.font = `bold 8px ${PIXEL_FONT}`;
  ctx.fillText(String(state.score).padStart(4, "0"), 225, 27);
  drawImage(ctx, assets, "ui_subweapon_frame", 278, 12, 32, 16);
  ctx.fillStyle = "#ef6f7a";
  ctx.fillRect(286, 17, 4, 6);
  ctx.fillStyle = "#a8b2d2";
  ctx.font = `7px ${PIXEL_FONT}`;
  ctx.fillText("WHIP", 320, 23);
  ctx.fillText(`${state.collectedGold} RELICS`, 392, 23);

  if (state.status === "playing" && state.message && state.tick > 20 && state.tick % 240 < 130) {
    ctx.fillStyle = "rgba(10, 12, 29, 0.78)";
    ctx.fillRect(134, 244, 212, 15);
    ctx.fillStyle = "#c9d1e5";
    ctx.textAlign = "center";
    ctx.font = `7px ${PIXEL_FONT}`;
    ctx.fillText(state.message.toUpperCase(), 240, 254);
    ctx.textAlign = "left";
  }
}

function drawOverlay(ctx, state) {
  if (state.status === "playing") return;
  ctx.fillStyle = "rgba(7, 9, 21, 0.74)";
  ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
  ctx.textAlign = "center";

  if (state.status === "title") {
    ctx.fillStyle = "#f6c453";
    ctx.font = `bold 23px ${PIXEL_FONT}`;
    ctx.fillText("NOCTURNE KEEP", GAME_WIDTH / 2, 82);
    ctx.fillStyle = "#ef6f7a";
    ctx.font = `bold 9px ${PIXEL_FONT}`;
    ctx.fillText("A HALL OF ASH AND MOONLIGHT", GAME_WIDTH / 2, 99);
    ctx.fillStyle = "#c9d1e5";
    ctx.font = `8px ${PIXEL_FONT}`;
    ctx.fillText("A / D OR ARROWS  •  SPACE JUMP  •  X / J WHIP", GAME_WIDTH / 2, 137);
    ctx.fillText("DEFEAT THE GUARDIANS, CLAIM THE GOLD, REACH THE DOOR", GAME_WIDTH / 2, 150);
    ctx.fillStyle = "#f6c453";
    ctx.font = `bold 10px ${PIXEL_FONT}`;
    ctx.fillText("PRESS ENTER OR TAP A CONTROL TO ENTER", GAME_WIDTH / 2, 184);
  } else {
    ctx.fillStyle = state.status === "won" ? "#f6c453" : "#ef6f7a";
    ctx.font = `bold 20px ${PIXEL_FONT}`;
    ctx.fillText(state.status === "won" ? "THE HALL IS YOURS" : "THE KEEP CLAIMS YOU", GAME_WIDTH / 2, 105);
    ctx.fillStyle = "#c9d1e5";
    ctx.font = `9px ${PIXEL_FONT}`;
    ctx.fillText(state.status === "won" ? "The eastern door opens onto the night." : "The dead rise when courage falters.", GAME_WIDTH / 2, 125);
    ctx.fillStyle = "#f6c453";
    ctx.font = `bold 10px ${PIXEL_FONT}`;
    ctx.fillText("PRESS R / ENTER OR TAP TO RESTART", GAME_WIDTH / 2, 164);
    ctx.fillStyle = "#a8b2d2";
    ctx.font = `8px ${PIXEL_FONT}`;
    ctx.fillText(`SCORE ${String(state.score).padStart(4, "0")}  •  RELICS ${state.collectedGold}`, GAME_WIDTH / 2, 183);
  }
  ctx.textAlign = "left";
}

export function createRenderer(ctx, assets) {
  ctx.imageSmoothingEnabled = false;
  return {
    render(state) {
      ctx.imageSmoothingEnabled = false;
      drawBackground(ctx, assets, state);
      drawCollectibles(ctx, assets, state);
      drawEnemies(ctx, assets, state);
      drawPlayer(ctx, assets, state);
      drawParticles(ctx, state);
      drawHud(ctx, assets, state);
      drawOverlay(ctx, state);
      if (state.player.hurtTimer > 0) {
        ctx.fillStyle = `rgba(239, 111, 122, ${Math.min(0.12, state.player.hurtTimer / 100)})`;
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
      }
    },
  };
}

export function drawLoading(ctx, message) {
  ctx.fillStyle = "#090c1b";
  ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
  ctx.fillStyle = "#f6c453";
  ctx.font = `bold 13px ${PIXEL_FONT}`;
  ctx.textAlign = "center";
  ctx.fillText(message, GAME_WIDTH / 2, GAME_HEIGHT / 2);
  ctx.textAlign = "left";
}
