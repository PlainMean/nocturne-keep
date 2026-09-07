import { createGame, reduceGame } from "../engine/reducer.js";
import { deserializeState, serializeState } from "../engine/save.js";
import { renderGame } from "./render.js";

const SAVE_KEY = "nocturne-keep:ashen-bell:v1";

const root = document.querySelector("#game-app");
const loadStatus = document.querySelector("#load-status");
const gameShell = document.querySelector(".game-shell");
let state = createGame(0x6e6f6374);

function readSave() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    return raw ? deserializeState(raw) : null;
  } catch {
    return null;
  }
}

function saveState() {
  try {
    if (state.mode === "title") {
      localStorage.removeItem(SAVE_KEY);
      return;
    }
    localStorage.setItem(SAVE_KEY, serializeState(state));
  } catch {
    // Storage is optional; gameplay remains available in private browsing.
  }
}

function restoreSave() {
  const saved = readSave();
  if (!saved) return;
  state = saved;
  render();
}

function render() {
  renderGame(root, state);
  if (state.mode === "title" && readSave()) {
    const title = root.querySelector(".title-screen");
    const continueButton = document.createElement("button");
    continueButton.className = "secondary-button giant-button";
    continueButton.dataset.action = "continue-save";
    continueButton.type = "button";
    continueButton.textContent = "Continue Saved Game";
    title?.append(continueButton);
  }
  loadStatus.hidden = true;
}

function dispatch(action) {
  if (action.type === "CONTINUE_SAVE") {
    restoreSave();
    return;
  }
  const next = reduceGame(state, action);
  if (next !== state) {
    state = next;
    saveState();
    render();
  }
}

function activate(selector) {
  const button = root.querySelector(selector);
  if (button instanceof HTMLButtonElement && !button.disabled) button.click();
}

root.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled) return;
  const action = button.dataset.action;
  if (action === "new-game") dispatch({ type: "NEW_GAME" });
  else if (action === "continue-save") dispatch({ type: "CONTINUE_SAVE" });
  else if (action === "restart") dispatch({ type: "RESTART" });
  else if (action === "explore-story") dispatch({ type: "EXPLORE_STORY" });
  else if (action === "enter-story-encounter") dispatch({ type: "ENTER_STORY_ENCOUNTER" });
  else if (action === "command") dispatch({ type: "COMMAND", command: button.dataset.command });
  else if (action === "select-skill") dispatch({ type: "SELECT_SKILL", skillId: button.dataset.skillId });
  else if (action === "select-item") dispatch({ type: "SELECT_ITEM", itemId: button.dataset.itemId });
  else if (action === "select-target") dispatch({ type: "SELECT_TARGET", targetId: button.dataset.targetId });
  else if (action === "cancel-target") dispatch({ type: "CANCEL_TARGET" });
});

document.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA", "SELECT"].includes(event.target?.tagName)) return;
  const key = event.key;
  if (["Enter", "Escape", " ", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(key) || /^[1-9]$/.test(key)) {
    event.preventDefault();
  }
  if (key === "r" || key === "R") {
    if (state.mode === "victory" || state.mode === "defeat") dispatch({ type: "RESTART" });
    return;
  }
  if (key === "Escape") {
    if (state.mode === "battle" && state.battle.phase === "target") dispatch({ type: "CANCEL_TARGET" });
    else if (state.mode === "battle" && state.battle.menu !== "main") dispatch({ type: "COMMAND", command: "back" });
    return;
  }
  if (key === "Enter" || key === " ") {
    if (state.mode === "title") activate('[data-action="new-game"]');
    else if (state.mode === "story") activate('[data-action="explore-story"], [data-action="enter-story-encounter"]');
    else if (state.mode === "victory" || state.mode === "defeat") activate('[data-action="restart"]');
    return;
  }
  if (state.mode !== "battle" || !/^[1-9]$/.test(key)) return;
  const index = Number(key) - 1;
  let selector;
  if (state.battle.phase === "target") selector = `[data-action="select-target"]:nth-child(${index + 1})`;
  else if (state.battle.menu === "skills") selector = `[data-action="select-skill"]:nth-child(${index + 1})`;
  else if (state.battle.menu === "items") selector = `[data-action="select-item"]:nth-child(${index + 1})`;
  else selector = `[data-action="command"]:nth-child(${index + 1})`;
  activate(selector);
});

for (const eventName of ["contextmenu", "selectstart", "dragstart", "touchmove", "gesturestart", "gesturechange", "gestureend"]) {
  document.addEventListener(eventName, (event) => {
    if (gameShell.contains(event.target)) event.preventDefault();
  }, { passive: false });
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") document.activeElement?.blur?.();
});

render();
