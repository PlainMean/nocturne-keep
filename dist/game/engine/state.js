import { HEROES, ITEMS, STORY } from "./catalog.js";
import { DEFAULT_SEED, normalizeSeed } from "./rng.js";

export const SAVE_VERSION = 2;
export const MODES = Object.freeze(["title", "story", "battle", "victory", "defeat"]);

function makePartyMember(hero) {
  return {
    id: hero.id,
    name: hero.name,
    title: hero.title,
    role: hero.role,
    portrait: hero.portrait,
    level: 1,
    xp: 0,
    hp: hero.maxHp,
    maxHp: hero.maxHp,
    mp: hero.maxMp,
    maxMp: hero.maxMp,
    attack: hero.attack,
    magic: hero.magic,
    defense: hero.defense,
    speed: hero.speed,
    skills: [...hero.skills],
    statuses: [],
    defending: false,
  };
}

function makeStartingInventory() {
  return Object.fromEntries(
    ITEMS.map((item) => [
      item.id,
      item.id === "bell_resin" ? 1 : item.id === "dusk_bread" ? 1 : 2,
    ]),
  );
}

function makeStoryProgress() {
  return Object.fromEntries(STORY.map((chapter) => [chapter.id, { explored: false, cleared: false, rested: false }]));
}

export function createGame(seed = DEFAULT_SEED) {
  return {
    version: SAVE_VERSION,
    seed: normalizeSeed(seed),
    rngCalls: 0,
    mode: "title",
    storyId: STORY[0].id,
    storyProgress: makeStoryProgress(),
    party: HEROES.map(makePartyMember),
    inventory: makeStartingInventory(),
    gold: 0,
    totalTurns: 0,
    battle: null,
    pendingBonus: null,
    notice: "The bell waits beyond the rain.",
  };
}

export function createNewGame(seed = DEFAULT_SEED) {
  const state = createGame(seed);
  state.mode = "story";
  state.notice = "Three souls cross the threshold of Nocturne Keep.";
  return state;
}

export function restartToTitle(state) {
  return createGame(state?.seed ?? DEFAULT_SEED);
}

export function livingParty(state) {
  return state.party.filter((member) => member.hp > 0);
}

export function partyMember(state, id) {
  return state.party.find((member) => member.id === id) ?? null;
}

export function replacePartyMember(state, id, update) {
  return {
    ...state,
    party: state.party.map((member) => (member.id === id ? update(member) : member)),
  };
}

export function clampStats(member) {
  return {
    ...member,
    hp: Math.max(0, Math.min(member.maxHp, member.hp)),
    mp: Math.max(0, Math.min(member.maxMp, member.mp)),
    statuses: Array.isArray(member.statuses) ? member.statuses : [],
    defending: Boolean(member.defending),
  };
}

export function assertStateInvariant(state) {
  if (!state || typeof state !== "object") throw new TypeError("State must be an object");
  if (state.version !== SAVE_VERSION) throw new Error(`Unsupported state version: ${state.version}`);
  if (!Number.isInteger(state.seed) || !Number.isInteger(state.rngCalls) || state.rngCalls < 0) {
    throw new Error("State has invalid RNG fields");
  }
  if (!MODES.includes(state.mode)) throw new Error(`Invalid game mode: ${state.mode}`);
  if (!Array.isArray(state.party) || state.party.length !== HEROES.length) throw new Error("State must have three heroes");
  const ids = new Set();
  for (const member of state.party) {
    if (!member.id || ids.has(member.id)) throw new Error("Party member IDs must be unique");
    ids.add(member.id);
    if (!Number.isInteger(member.hp) || member.hp < 0 || member.hp > member.maxHp) throw new Error(`Invalid HP for ${member.id}`);
    if (!Number.isInteger(member.mp) || member.mp < 0 || member.mp > member.maxMp) throw new Error(`Invalid MP for ${member.id}`);
    if (!Number.isInteger(member.level) || member.level < 1) throw new Error(`Invalid level for ${member.id}`);
    if (!Array.isArray(member.statuses)) throw new Error(`Invalid statuses for ${member.id}`);
  }
  if (!state.inventory || typeof state.inventory !== "object") throw new Error("Inventory is missing");
  for (const count of Object.values(state.inventory)) {
    if (!Number.isInteger(count) || count < 0) throw new Error("Inventory counts must be non-negative integers");
  }
  if (!state.storyProgress || typeof state.storyProgress !== "object") throw new Error("Story progress is missing");
  if (state.mode === "battle" && (!state.battle || !Array.isArray(state.battle.turnOrder))) {
    throw new Error("Battle mode requires a turn order");
  }
  return true;
}
