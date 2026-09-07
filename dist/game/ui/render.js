import { ENEMY_BY_ID, ITEM_BY_ID, SKILL_BY_ID, STORY_BY_ID } from "../engine/catalog.js";
import { getTargetOptions } from "../engine/reducer.js";
import { ASSET_MANIFEST, assetUrl } from "./assets.js";

const ESCAPES = Object.freeze({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#039;",
});

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ESCAPES[character]);
}

function image(id, className, alt = "") {
  return `<img class="${className}" src="${assetUrl(id)}" alt="${escapeHtml(alt)}" draggable="false" />`;
}

function meter(label, value, max, kind) {
  return `<div class="meter-row"><span>${label}</span><div class="meter meter-${kind}" aria-label="${label} ${value} of ${max}"><i style="width:${Math.max(0, Math.min(100, (value / max) * 100))}%"></i></div><b>${value}/${max}</b></div>`;
}

function statusPills(actor) {
  if (!actor.statuses?.length) return "";
  return `<div class="status-pills">${actor.statuses.map((status) => `<span class="status-pill status-${escapeHtml(status.id)}">${escapeHtml(status.id)}</span>`).join("")}</div>`;
}

function partyCard(member, active = false) {
  return `<article class="party-card${active ? " is-active" : ""}${member.hp <= 0 ? " is-fallen" : ""}">
    ${image(member.portrait, "portrait", `${member.name} portrait`)}
    <div class="party-card-copy"><strong>${escapeHtml(member.name)}</strong><span>${escapeHtml(member.title)} · Lv ${member.level}</span>${meter("HP", member.hp, member.maxHp, "hp")}${meter("MP", member.mp, member.maxMp, "mp")}${statusPills(member)}</div>
  </article>`;
}

function partyRoster(state, activeId = "") {
  return `<section class="party-roster" aria-label="Party members">${state.party.map((member) => partyCard(member, member.id === activeId)).join("")}</section>`;
}

function shellHeader(state, kicker, title) {
  return `<header class="screen-header"><div><p class="kicker">${escapeHtml(kicker)}</p><h1>${escapeHtml(title)}</h1></div><span class="seed-label">SEED ${state.seed}</span></header>`;
}

function storyArt(chapter) {
  const art = chapter.id === "keep_gate" ? "castle" : chapter.id === "chapel_crypt" ? "altar" : "throne";
  return `<div class="story-art">${image(art, "story-backdrop", chapter.room)}${image(chapter.id === "keep_gate" ? "rowan" : chapter.id === "chapel_crypt" ? "selene" : "garrick", "story-hero", "Party member")}</div>`;
}

function renderTitle() {
  return `<section class="title-screen" aria-labelledby="title-heading">
    <div class="title-art">${image("moon", "title-moon", "Moon")}${image("castle", "title-castle", "Nocturne Keep")}</div>
    <div class="title-copy"><p class="kicker">ORIGINAL GOTHIC RETRO RPG · TURN-BASED VERTICAL SLICE</p><h1 id="title-heading">Nocturne Keep</h1><p class="title-subtitle">The Ashen Bell</p><p class="tagline">Three vows. One bell. No dawn until the dead remember your names.</p><p class="title-meta">A short castle-and-crypt quest for touch and keyboard.</p></div>
    <button class="primary-button giant-button" data-action="new-game" type="button">New Game</button>
    <p class="control-note">Tap a command · keyboard: Enter, 1–5, Escape</p>
  </section>`;
}

function renderStory(state) {
  const chapter = STORY_BY_ID[state.storyId];
  const progress = state.storyProgress[state.storyId];
  const action = progress.explored ? "enter-story-encounter" : "explore-story";
  const actionLabel = progress.explored ? chapter.button : "Explore the Keep";
  return `<section class="story-screen" aria-labelledby="story-heading">
    ${shellHeader(state, `CHAPTER ${chapter.number} · ${chapter.room}`, "The Keep Remembers")}
    <div class="story-grid">${storyArt(chapter)}<article class="story-card"><p class="chapter-label">${escapeHtml(chapter.title)}</p><h2 id="story-heading">${escapeHtml(chapter.room)}</h2><p class="story-text">${escapeHtml(chapter.text)}</p><p class="story-notice" role="status" aria-live="polite">${escapeHtml(state.notice)}</p><button class="primary-button" data-action="${action}" type="button">${escapeHtml(actionLabel)}</button></article></div>
    ${partyRoster(state)}
    <aside class="objective"><strong>Objective</strong><span>${progress.explored ? `Face the guardians of ${escapeHtml(chapter.room)}.` : "Search the room for a way forward."}</span></aside>
  </section>`;
}

function turnOrder(state) {
  const battle = state.battle;
  return `<section class="turn-order" aria-label="Turn order"><div class="panel-heading"><span>Turn Order</span><small>ROUND ${battle.round}</small></div><div class="turn-chips">${battle.turnOrder.map((id) => {
    const actor = id.startsWith("enemy:") ? battle.enemies.find((enemy) => enemy.uid === id) : state.party.find((member) => member.id === id);
    if (!actor) return "";
    const active = id === battle.activeId;
    return `<span class="turn-chip${active ? " is-active" : ""}${actor.hp <= 0 ? " is-fallen" : ""}">${escapeHtml(actor.name.split(" ")[0])}</span>`;
  }).join("")}</div></section>`;
}

function enemyCard(enemy) {
  return `<article class="enemy-card${enemy.hp <= 0 ? " is-fallen" : ""}">
    ${image(enemy.art, "enemy-art", enemy.name)}
    <div class="enemy-copy"><strong>${escapeHtml(enemy.name)}</strong><span>${enemy.boss ? "BOSS" : "FOE"}</span>${meter("HP", enemy.hp, enemy.maxHp, "enemy")}${statusPills(enemy)}</div>
  </article>`;
}

function renderLog(state) {
  const log = state.battle?.log ?? [];
  return `<section class="round-log" aria-live="polite" aria-label="Round log"><div class="panel-heading"><span>Round Log</span><small>${log.length} entries</small></div><ol>${log.slice(-7).map((entry) => `<li>${escapeHtml(entry)}</li>`).join("")}</ol></section>`;
}

function commandButton(label, command, hint = "", disabled = false, tone = "") {
  return `<button class="command-button ${tone}" data-action="command" data-command="${command}" type="button"${disabled ? " disabled" : ""}><b>${escapeHtml(label)}</b>${hint ? `<small>${escapeHtml(hint)}</small>` : ""}</button>`;
}

function renderTargetMenu(state) {
  const pending = state.battle.pending;
  const label = pending.kind === "attack" ? "Attack" : pending.kind === "skill" ? SKILL_BY_ID[pending.id]?.name : ITEM_BY_ID[pending.id]?.name;
  const options = getTargetOptions(state);
  return `<div class="target-menu"><div class="menu-title">Choose a target for <strong>${escapeHtml(label)}</strong></div><div class="target-grid">${options.map((target, index) => `<button class="target-button" data-action="select-target" data-target-id="${escapeHtml(target.id)}" type="button"><span>${index + 1}</span><strong>${escapeHtml(target.name)}</strong><small>${target.hp}/${target.maxHp} HP</small></button>`).join("")}</div><button class="secondary-button" data-action="cancel-target" type="button">Back to commands</button></div>`;
}

function renderSkillMenu(state, actor) {
  const skills = actor.skills.map((id) => SKILL_BY_ID[id]).filter(Boolean);
  return `<div class="selection-menu"><div class="menu-title">Skills / Magic <small>${actor.mp}/${actor.maxMp} MP</small></div><div class="selection-list">${skills.map((skill, index) => `<button class="selection-button" data-action="select-skill" data-skill-id="${skill.id}" type="button"${actor.mp < skill.cost ? " disabled" : ""}><span>${index + 1}</span><strong>${escapeHtml(skill.name)}</strong><b>${skill.cost} MP</b><small>${escapeHtml(skill.description)}</small></button>`).join("")}</div>${commandButton("Back", "back")}</div>`;
}

function renderItemMenu(state) {
  const entries = Object.keys(state.inventory).map((id) => ({ item: ITEM_BY_ID[id], count: state.inventory[id] })).filter(({ item, count }) => item && count > 0);
  return `<div class="selection-menu"><div class="menu-title">Items <small>${entries.length} carried types</small></div><div class="selection-list">${entries.map(({ item, count }, index) => `<button class="selection-button" data-action="select-item" data-item-id="${item.id}" type="button"><span>${index + 1}</span><strong>${escapeHtml(item.shortName ?? item.name)}</strong><b>x${count}</b><small>${escapeHtml(item.description)}</small></button>`).join("")}</div>${entries.length ? "" : "<p class=empty-menu>The satchel is empty.</p>"}${commandButton("Back", "back")}</div>`;
}

function renderCommandMenu(state, actor) {
  const battle = state.battle;
  if (battle.phase === "target") return renderTargetMenu(state);
  if (battle.menu === "skills") return renderSkillMenu(state, actor);
  if (battle.menu === "items") return renderItemMenu(state);
  const silenced = actor.statuses.some((status) => status.id === "silenced");
  return `<div class="command-menu"><div class="menu-title"><strong>${escapeHtml(actor.name)}</strong> — choose a command</div><div class="command-grid">${commandButton("Attack", "attack", "Physical strike", false, "attack-tone")}${commandButton("Skills / Magic", "skills", "Spend MP", silenced, "magic-tone")}${commandButton("Items", "items", "Use the satchel")}${commandButton("Defend", "defend", "Halve damage", false, "defend-tone")}${commandButton("Run", "run", battle.boss ? "No escape from a boss" : "Try to flee", battle.boss, "run-tone")}</div></div>`;
}

function renderBattle(state) {
  const battle = state.battle;
  const active = state.party.find((member) => member.id === battle.activeId) ?? state.party.find((member) => member.hp > 0) ?? state.party[0];
  return `<section class="battle-screen" aria-labelledby="battle-heading">
    ${shellHeader(state, `${battle.room} · ROUND ${battle.round}`, battle.name)}
    <div class="battle-arena"><div class="arena-moon">${image("moon", "arena-moon-art", "Moon")}</div><div class="arena-castle">${image("castle", "arena-castle-art", "Castle hall")}</div><div class="enemy-line">${battle.enemies.map((enemy) => enemyCard(enemy)).join("")}</div><div class="arena-floor">${image("coffin", "arena-coffin", "Coffin")}${image("torch", "arena-torch", "Torch")}</div></div>
    <div class="battle-columns"><div class="battle-side battle-side-left">${turnOrder(state)}${renderLog(state)}</div><div class="battle-side battle-side-right"><section class="active-panel" aria-labelledby="battle-heading"><div class="active-heading"><span>Acting now</span><h2 id="battle-heading">${escapeHtml(active.name)}</h2>${statusPills(active)}</div>${meter("HP", active.hp, active.maxHp, "hp")}${meter("MP", active.mp, active.maxMp, "mp")}${renderCommandMenu(state, active)}</section>${partyRoster(state, battle.activeId)}</div></div>
  </section>`;
}

function rewardSummary(lastBattle) {
  if (!lastBattle) return "";
  const rewards = Object.entries(lastBattle.rewards ?? {}).map(([id, count]) => `${ITEM_BY_ID[id]?.shortName ?? id} x${count}`).join(" · ") || "No items";
  return `<div class="result-summary"><span>${lastBattle.victory ? "VICTORY" : lastBattle.escaped ? "ESCAPED" : "DEFEAT"}</span><strong>${lastBattle.xp} XP · ${lastBattle.gold} gold</strong><small>${escapeHtml(rewards)}</small></div>`;
}

function renderEnd(state) {
  const victory = state.mode === "victory";
  return `<section class="end-screen ${victory ? "is-victory" : "is-defeat"}" aria-labelledby="end-heading"><div class="end-art">${image(victory ? "moon" : "reaper", "end-art-main", victory ? "Moonrise" : "Bellkeeper")}</div><p class="kicker">${victory ? "THE NIGHT BREAKS" : "THE KEEP CLAIMS YOU"}</p><h1 id="end-heading">${victory ? "Dawn at Nocturne Keep" : "The Bell Still Rings"}</h1><p class="end-copy">${escapeHtml(state.notice)}</p>${rewardSummary(state.lastBattle)}${partyRoster(state)}<button class="primary-button giant-button" data-action="restart" type="button">Return to Title</button><p class="control-note">Press R or Enter to restart</p></section>`;
}

export function renderGame(root, state) {
  if (!root) throw new Error("Game root is required");
  let content;
  if (state.mode === "title") content = renderTitle(state);
  else if (state.mode === "story") content = renderStory(state);
  else if (state.mode === "battle") content = renderBattle(state);
  else content = renderEnd(state);
  root.innerHTML = content;
  root.dataset.mode = state.mode;
  root.dataset.assetCount = String(Object.keys(ASSET_MANIFEST).length);
}
