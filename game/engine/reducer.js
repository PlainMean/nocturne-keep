import {
  ENCOUNTER_BY_ID,
  ENEMY_BY_ID,
  HERO_BY_ID,
  ITEM_BY_ID,
  SKILL_BY_ID,
  STORY_BY_ID,
} from "./catalog.js";
import { nextRandom, weightedPick } from "./rng.js";
import {
  assertStateInvariant,
  clampStats,
  createGame,
  createNewGame,
  livingParty,
  partyMember,
  restartToTitle,
} from "./state.js";

const PARTY_KIND = "party";
const ENEMY_KIND = "enemy";
const MAX_LOG_LINES = 14;
const STATUS_DAMAGE = new Set(["burn", "bleed", "poison"]);

function cloneState(state) {
  return JSON.parse(JSON.stringify(state));
}

function addLog(state, message) {
  const battle = state.battle;
  if (!battle) return;
  battle.log = [...battle.log, message].slice(-MAX_LOG_LINES);
}

function setNotice(state, message) {
  state.notice = message;
}

function roll(state) {
  const result = nextRandom(state);
  state.rngCalls = result.state.rngCalls;
  return result.value;
}

function rollInt(state, maxExclusive) {
  if (maxExclusive <= 1) return 0;
  return Math.min(maxExclusive - 1, Math.floor(roll(state) * maxExclusive));
}

function actorKind(id) {
  return id.startsWith("enemy:") ? ENEMY_KIND : PARTY_KIND;
}

function enemyId(enemy) {
  return enemy.uid ?? `enemy:${enemy.id}:0`;
}

function findEnemy(state, id) {
  return state.battle?.enemies.find((enemy) => enemy.uid === id) ?? null;
}

function findActor(state, id) {
  return actorKind(id) === PARTY_KIND ? partyMember(state, id) : findEnemy(state, id);
}

function livingEnemies(state) {
  return state.battle?.enemies.filter((enemy) => enemy.hp > 0) ?? [];
}

function hasStatus(actor, id) {
  return actor.statuses.some((status) => status.id === id && status.turns > 0);
}

function getStatus(actor, id) {
  return actor.statuses.find((status) => status.id === id && status.turns > 0) ?? null;
}

function addOrRefreshStatus(actor, status) {
  if (!status?.id) return;
  const existing = actor.statuses.find((entry) => entry.id === status.id);
  if (existing) {
    existing.turns = Math.max(existing.turns, status.turns ?? 1);
    existing.power = status.power ?? existing.power;
    return;
  }
  actor.statuses.push({
    id: status.id,
    turns: Math.max(1, Math.floor(status.turns ?? 1)),
    power: Number(status.power ?? 1),
  });
}

function removeStatuses(actor, ids) {
  const remove = new Set(ids);
  actor.statuses = actor.statuses.filter((status) => !remove.has(status.id));
}

function applyRawDamage(state, target, amount, sourceLabel = "The curse") {
  const damage = Math.max(0, Math.floor(amount));
  target.hp = Math.max(0, target.hp - damage);
  if (target.hp === 0) target.defending = false;
  if (damage > 0 && sourceLabel && state.battle) addLog(state, `${sourceLabel} deals ${damage} damage to ${target.name}.`);
  return damage;
}

function tickStatuses(state, actor) {
  let skipTurn = false;
  const remaining = [];
  for (const status of actor.statuses) {
    if (STATUS_DAMAGE.has(status.id)) {
      applyRawDamage(state, actor, status.power, `${status.id[0].toUpperCase()}${status.id.slice(1)}`);
    }
    if (status.id === "petrify") skipTurn = true;
    if (status.turns > 1 && actor.hp > 0) {
      remaining.push({ ...status, turns: status.turns - 1 });
    }
  }
  actor.statuses = remaining;
  if (actor.hp <= 0) addLog(state, `${actor.name} falls in the dark.`);
  if (skipTurn && actor.hp > 0) addLog(state, `${actor.name} is petrified and loses the turn.`);
  return skipTurn;
}

function resetBattleMenu(battle) {
  battle.phase = "command";
  battle.menu = "main";
  battle.pending = null;
}

function actorEntries(state) {
  const party = state.party.map((member, index) => ({
    id: member.id,
    kind: PARTY_KIND,
    speed: member.speed,
    tie: index,
  }));
  const enemies = state.battle.enemies.map((enemy, index) => ({
    id: enemy.uid,
    kind: ENEMY_KIND,
    speed: enemy.speed,
    tie: state.party.length + index,
  }));
  return [...party, ...enemies]
    .sort((left, right) => right.speed - left.speed || left.tie - right.tie)
    .map(({ id }) => id);
}

function makeBattle(state, encounter) {
  const enemies = encounter.enemies.map((id, index) => {
    const template = ENEMY_BY_ID[id];
    if (!template) throw new Error(`Encounter references unknown enemy: ${id}`);
    return {
      ...template,
      uid: `enemy:${template.id}:${index}`,
      hp: template.maxHp,
      maxMp: 0,
      mp: 0,
      statuses: [],
      defending: false,
    };
  });
  const battle = {
    encounterId: encounter.id,
    name: encounter.name,
    room: encounter.room,
    boss: Boolean(encounter.boss),
    enemies,
    round: 1,
    phase: "command",
    menu: "main",
    pending: null,
    activeId: null,
    turnIndex: 0,
    turnOrder: [],
    log: [encounter.intro],
  };
  state.battle = battle;
  battle.turnOrder = actorEntries(state);
  battle.activeId = battle.turnOrder[0] ?? state.party[0].id;
  setNotice(state, encounter.intro);
}

function allEnemiesDefeated(state) {
  return livingEnemies(state).length === 0;
}

function allPartyDefeated(state) {
  return livingParty(state).length === 0;
}

function gainExperience(member, amount) {
  const next = { ...member, xp: member.xp + amount };
  const levelUps = [];
  while (next.level < 99 && next.xp >= next.level * 100) {
    next.level += 1;
    next.maxHp += 14 + next.level * 2;
    next.maxMp += next.level % 2 === 0 ? 7 : 4;
    next.attack += 3;
    next.magic += 2;
    next.defense += 2;
    next.speed += next.level % 3 === 0 ? 1 : 0;
    next.hp = next.maxHp;
    next.mp = next.maxMp;
    levelUps.push(next.level);
  }
  return { member: clampStats(next), levelUps };
}

function finishVictory(state) {
  const battle = state.battle;
  const encounter = ENCOUNTER_BY_ID[battle.encounterId];
  const defeated = battle.enemies;
  const xp = defeated.reduce((sum, enemy) => sum + enemy.xp, 0);
  const gold = defeated.reduce((sum, enemy) => sum + enemy.gold, 0);
  const rewards = encounter.rewardItems ?? {};
  const levelUps = [];

  state.party = state.party.map((member) => {
    const result = gainExperience(member, xp);
    if (result.levelUps.length) levelUps.push(`${member.name} reached level ${result.member.level}.`);
    return result.member;
  });
  for (const [itemId, count] of Object.entries(rewards)) {
    state.inventory[itemId] = (state.inventory[itemId] ?? 0) + count;
  }
  state.gold += gold;
  state.storyProgress[battle.encounterId === "gate_guardians" ? "keep_gate" : battle.encounterId === "chapel_shadows" ? "chapel_crypt" : "ashen_bell"].cleared = true;
  state.lastBattle = {
    encounterId: battle.encounterId,
    victory: true,
    escaped: false,
    xp,
    gold,
    rewards: { ...rewards },
    rounds: battle.round,
    log: [...battle.log],
    levelUps,
  };
  const chapter = STORY_BY_ID[state.storyId];
  state.battle = null;
  if (battle.boss) {
    state.mode = "victory";
    state.notice = "The Ashen Bell falls silent. Dawn enters Nocturne Keep.";
    return state;
  }
  state.mode = "story";
  state.storyId = chapter.next;
  state.notice = levelUps.length
    ? `${levelUps.join(" ")} The next stair waits below.`
    : `Victory. ${chapter.next ? STORY_BY_ID[chapter.next].title : "The keep is quiet."}`;
  return state;
}

function finishDefeat(state) {
  const battle = state.battle;
  state.lastBattle = {
    encounterId: battle?.encounterId ?? null,
    victory: false,
    escaped: false,
    xp: 0,
    gold: 0,
    rewards: {},
    rounds: battle?.round ?? 0,
    log: battle ? [...battle.log] : [],
    levelUps: [],
  };
  state.mode = "defeat";
  state.battle = null;
  state.notice = "The crypt closes over the party. The bell keeps ringing.";
  return state;
}

function finishEscape(state) {
  const battle = state.battle;
  state.lastBattle = {
    encounterId: battle.encounterId,
    victory: false,
    escaped: true,
    xp: 0,
    gold: 0,
    rewards: {},
    rounds: battle.round,
    log: [...battle.log],
    levelUps: [],
  };
  state.mode = "story";
  state.battle = null;
  state.notice = "The party retreats to the rain outside the keep.";
  return state;
}

function prepareActorTurn(state, actor) {
  actor.defending = false;
  return tickStatuses(state, actor);
}

function advanceUntilParty(state) {
  const battle = state.battle;
  if (!battle) return state;
  let guard = 0;
  while (state.mode === "battle" && guard < 100) {
    guard += 1;
    if (allPartyDefeated(state)) return finishDefeat(state);
    if (allEnemiesDefeated(state)) return finishVictory(state);
    if (battle.turnIndex >= battle.turnOrder.length) {
      battle.round += 1;
      battle.turnIndex = 0;
      battle.turnOrder = actorEntries(state);
      addLog(state, `Round ${battle.round}. The bell marks another measure.`);
    }
    const id = battle.turnOrder[battle.turnIndex];
    battle.activeId = id;
    const actor = findActor(state, id);
    if (!actor || actor.hp <= 0) {
      battle.turnIndex += 1;
      continue;
    }
    const skip = prepareActorTurn(state, actor);
    if (actor.hp <= 0 || skip) {
      battle.turnIndex += 1;
      continue;
    }
    if (actorKind(id) === ENEMY_KIND) {
      resolveEnemyTurn(state, actor);
      battle.turnIndex += 1;
      continue;
    }
    resetBattleMenu(battle);
    return state;
  }
  if (guard >= 100) throw new Error("Turn advancement exceeded safety limit");
  return state;
}

function advanceAfterPlayerAction(state) {
  state.totalTurns += 1;
  state.battle.turnIndex += 1;
  return advanceUntilParty(state);
}

function targetPool(state, source, definition) {
  const sourceIsParty = actorKind(source.id) === PARTY_KIND;
  if (definition.target === "ally") {
    return sourceIsParty ? livingParty(state) : livingEnemies(state);
  }
  if (definition.target === "deadAlly") {
    return sourceIsParty ? state.party.filter((member) => member.hp <= 0) : [];
  }
  return sourceIsParty ? livingEnemies(state) : livingParty(state);
}

export function getTargetOptions(state) {
  if (state.mode !== "battle" || state.battle?.phase !== "target") return [];
  const pending = state.battle.pending;
  if (!pending) return [];
  const source = partyMember(state, pending.sourceId);
  if (!source) return [];
  let definition;
  if (pending.kind === "skill") definition = SKILL_BY_ID[pending.id];
  else if (pending.kind === "item") definition = ITEM_BY_ID[pending.id];
  else definition = { target: "enemy" };
  if (pending.kind === "item") definition = { target: definition.target };
  return targetPool(state, source, definition).map((target) => ({
    id: target.uid ?? target.id,
    name: target.name,
    hp: target.hp,
    maxHp: target.maxHp,
    kind: target.uid ? ENEMY_KIND : PARTY_KIND,
  }));
}

function targetIsValid(state, pending, targetId) {
  return getTargetOptions({
    ...state,
    battle: { ...state.battle, phase: "target", pending },
  }).some((target) => target.id === targetId);
}

function damageValue(state, source, target, { power = 1, magic = false, accuracy = 1 } = {}) {
  if (roll(state) > accuracy) return { hit: false, damage: 0, critical: false };
  const variance = 0.88 + roll(state) * 0.24;
  const critical = roll(state) < Math.min(0.22, 0.08 + source.speed * 0.002);
  const frenzy = hasStatus(source, "frenzy") ? 1.22 : 1;
  const offense = (magic ? source.magic : source.attack) * frenzy * power;
  const shaken = hasStatus(target, "shaken") ? 0.84 : 1;
  const mitigation = magic ? target.defense * 0.28 : target.defense * 0.58;
  let damage = Math.max(1, Math.floor((offense - mitigation * shaken) * variance * (critical ? 2 : 1)));
  if (target.defending) damage = Math.max(1, Math.floor(damage * 0.5));
  if (hasStatus(target, "warded")) damage = Math.max(1, Math.floor(damage * 0.72));
  return { hit: true, damage, critical };
}

function describeDamage(state, source, target, result) {
  if (!result.hit) {
    addLog(state, `${source.name}'s attack misses ${target.name}.`);
    return false;
  }
  applyRawDamage(state, target, result.damage, "");
  const critical = result.critical ? " Critical!" : "";
  addLog(state, `${source.name} hits ${target.name} for ${result.damage} damage.${critical}`.trim());
  if (target.hp <= 0) addLog(state, `${target.name} is defeated.`);
  return true;
}

function applySkillStatus(state, source, target, skill) {
  const status = skill.status;
  if (!status || roll(state) > (status.chance ?? 1)) return;
  addOrRefreshStatus(target, status);
  addLog(state, `${target.name} is afflicted with ${status.id}.`);
}

function resolveSkill(state, source, target, skill) {
  if (hasStatus(source, "silenced")) {
    addLog(state, `${source.name} is silenced and cannot cast ${skill.name}.`);
    return;
  }
  source.mp = Math.max(0, source.mp - skill.cost);
  if (skill.kind === "heal") {
    const amount = Math.max(1, Math.floor((32 + source.magic * 1.1) * skill.power));
    const before = target.hp;
    target.hp = Math.min(target.maxHp, target.hp + amount);
    addLog(state, `${source.name} casts ${skill.name}; ${target.name} recovers ${target.hp - before} HP.`);
    return;
  }
  if (skill.kind === "buff") {
    addOrRefreshStatus(target, skill.status);
    addLog(state, `${source.name} casts ${skill.name} on ${target.name}.`);
    return;
  }
  const result = damageValue(state, source, target, {
    power: skill.power ?? 1,
    magic: skill.kind === "magic",
    accuracy: skill.accuracy ?? 1,
  });
  describeDamage(state, source, target, result);
  if (skill.removes) {
    if (skill.removes.includes("guard")) target.defending = false;
    removeStatuses(target, skill.removes);
    addLog(state, `${skill.name} strips the foe's guard.`);
  }
  if (result.hit && target.hp > 0) applySkillStatus(state, source, target, skill);
  if (skill.recoil) {
    applyRawDamage(state, source, skill.recoil, `${source.name}'s oath`);
    if (source.hp <= 0) addLog(state, `${source.name} falls from the recoil.`);
  }
}

function resolveBasicAttack(state, source, target) {
  const result = damageValue(state, source, target, { power: 1, accuracy: 0.96 });
  describeDamage(state, source, target, result);
}

function resolveItem(state, source, target, item) {
  const effect = item.effect;
  state.inventory[item.id] = Math.max(0, (state.inventory[item.id] ?? 0) - 1);
  if (effect.type === "healHp") {
    const before = target.hp;
    target.hp = Math.min(target.maxHp, target.hp + effect.amount);
    addLog(state, `${source.name} uses ${item.name}; ${target.name} recovers ${target.hp - before} HP.`);
  } else if (effect.type === "healMp") {
    const before = target.mp;
    target.mp = Math.min(target.maxMp, target.mp + effect.amount);
    addLog(state, `${source.name} uses ${item.name}; ${target.name} recovers ${target.mp - before} MP.`);
  } else if (effect.type === "cure") {
    removeStatuses(target, effect.statuses);
    addLog(state, `${source.name} uses ${item.name}; curses leave ${target.name}.`);
  } else if (effect.type === "revive") {
    target.hp = Math.max(1, Math.floor(target.maxHp * effect.ratio));
    target.statuses = [];
    addLog(state, `${source.name} uses ${item.name}; ${target.name} rises with ${target.hp} HP.`);
  } else if (effect.type === "status") {
    addOrRefreshStatus(target, effect.status);
    addLog(state, `${source.name} uses ${item.name} on ${target.name}.`);
  }
}

function resolveEnemyTurn(state, enemy) {
  const living = livingParty(state);
  if (!living.length) return;
  let choice = null;
  if (!hasStatus(enemy, "silenced")) {
    const picked = weightedPick(state, enemy.ai.map((entry) => ({ ...entry, value: entry })));
    state.rngCalls = picked.state.rngCalls;
    choice = picked.value;
  }
  if (!choice || choice.kind === "attack") {
    const target = living[rollInt(state, living.length)];
    addLog(state, `${enemy.name} attacks ${target.name}.`);
    resolveBasicAttack(state, enemy, target);
    return;
  }
  const skill = SKILL_BY_ID[choice.skillId];
  if (!skill) {
    const target = living[rollInt(state, living.length)];
    resolveBasicAttack(state, enemy, target);
    return;
  }
  const candidates = targetPool(state, enemy, skill);
  const target = candidates[rollInt(state, candidates.length)] ?? enemy;
  addLog(state, `${enemy.name} uses ${skill.name}.`);
  resolveSkill(state, enemy, target, skill);
}

function startStoryEncounter(state) {
  const chapter = STORY_BY_ID[state.storyId];
  if (!chapter) return state;
  const progress = state.storyProgress[state.storyId];
  if (!progress?.explored) {
    state.notice = "Search the room first. The keep hides its doors from the hurried.";
    return state;
  }
  const encounter = ENCOUNTER_BY_ID[chapter.encounterId];
  if (!encounter) throw new Error(`Story references unknown encounter: ${chapter.encounterId}`);
  state.mode = "battle";
  makeBattle(state, encounter);
  return advanceUntilParty(state);
}

function chooseCommand(state, action) {
  const battle = state.battle;
  const actor = partyMember(state, battle.activeId);
  if (!actor || actor.hp <= 0 || battle.phase !== "command") return state;
  const command = action.command;
  if (command === "skills") {
    battle.menu = "skills";
    return state;
  }
  if (command === "items") {
    battle.menu = "items";
    return state;
  }
  if (command === "back") {
    battle.menu = "main";
    return state;
  }
  if (command === "attack") {
    battle.pending = { kind: "attack", sourceId: actor.id };
    battle.phase = "target";
    battle.menu = "target";
    return state;
  }
  if (command === "defend") {
    actor.defending = true;
    addLog(state, `${actor.name} defends behind a veil of ash.`);
    return advanceAfterPlayerAction(state);
  }
  if (command === "run") {
    if (battle.boss || roll(state) < 0.42) {
      addLog(state, `${actor.name} cannot find a path through the dark.`);
      return advanceAfterPlayerAction(state);
    }
    addLog(state, `${actor.name} leads the party out of the encounter.`);
    return finishEscape(state);
  }
  return state;
}

function selectSkill(state, skillId) {
  const battle = state.battle;
  const actor = partyMember(state, battle.activeId);
  const skill = SKILL_BY_ID[skillId];
  if (!actor || !skill || !actor.skills.includes(skill.id)) return state;
  if (actor.mp < skill.cost) {
    setNotice(state, `${actor.name} needs ${skill.cost} MP for ${skill.name}.`);
    return state;
  }
  if (hasStatus(actor, "silenced")) {
    addLog(state, `${actor.name} is silenced.`);
    return advanceAfterPlayerAction(state);
  }
  battle.pending = { kind: "skill", id: skill.id, sourceId: actor.id };
  battle.phase = "target";
  battle.menu = "target";
  return state;
}

function selectItem(state, itemId) {
  const battle = state.battle;
  const actor = partyMember(state, battle.activeId);
  const item = ITEM_BY_ID[itemId];
  if (!actor || !item || (state.inventory[item.id] ?? 0) <= 0) return state;
  battle.pending = { kind: "item", id: item.id, sourceId: actor.id };
  battle.phase = "target";
  battle.menu = "target";
  return state;
}

function resolveTargetedCommand(state, targetId) {
  const battle = state.battle;
  const pending = battle.pending;
  if (!pending || !targetIsValid(state, pending, targetId)) return state;
  const source = partyMember(state, pending.sourceId);
  const target = findActor(state, targetId);
  if (!source || !target) return state;
  if (pending.kind === "attack") {
    addLog(state, `${source.name} attacks.`);
    resolveBasicAttack(state, source, target);
  } else if (pending.kind === "skill") {
    resolveSkill(state, source, target, SKILL_BY_ID[pending.id]);
  } else {
    resolveItem(state, source, target, ITEM_BY_ID[pending.id]);
  }
  return advanceAfterPlayerAction(state);
}

export function reduceGame(state, action = {}) {
  assertStateInvariant(state);
  if (!action || typeof action.type !== "string") return state;
  if (action.type === "NEW_GAME") return createNewGame(action.seed ?? state.seed);
  if (action.type === "RESTART") return restartToTitle(state);

  const next = cloneState(state);
  switch (action.type) {
    case "EXPLORE_STORY": {
      if (next.mode !== "story") return state;
      const progress = next.storyProgress[next.storyId];
      if (!progress) return state;
      progress.explored = true;
      next.notice = "A hidden passage opens. The keep's guardians hear your names.";
      return next;
    }
    case "ENTER_STORY_ENCOUNTER": {
      if (next.mode !== "story") return state;
      return startStoryEncounter(next);
    }
    case "COMMAND": {
      if (next.mode !== "battle") return state;
      return chooseCommand(next, action);
    }
    case "SELECT_SKILL": {
      if (next.mode !== "battle" || next.battle.menu !== "skills") return state;
      return selectSkill(next, action.skillId);
    }
    case "SELECT_ITEM": {
      if (next.mode !== "battle" || next.battle.menu !== "items") return state;
      return selectItem(next, action.itemId);
    }
    case "SELECT_TARGET": {
      if (next.mode !== "battle" || next.battle.phase !== "target") return state;
      return resolveTargetedCommand(next, action.targetId);
    }
    case "CANCEL_TARGET": {
      if (next.mode !== "battle" || next.battle.phase !== "target") return state;
      resetBattleMenu(next.battle);
      return next;
    }
    default:
      return state;
  }
}

export function stepGame(state, action) {
  return reduceGame(state, action);
}

export function createBattleTestState(seed = 1, encounterId = "gate_guardians") {
  const state = createNewGame(seed);
  state.storyProgress.keep_gate.explored = true;
  state.mode = "story";
  state.storyId = "keep_gate";
  return reduceGame(state, { type: "ENTER_STORY_ENCOUNTER", encounterId });
}

export { createGame, createNewGame, livingParty, partyMember, restartToTitle };
