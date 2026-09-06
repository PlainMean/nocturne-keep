import { createGame, stepGame } from "./engine.js";
import { InputManager } from "./input.js";
import { createRenderer, drawLoading, loadAssets } from "./render.js";

const canvas = document.querySelector("#game-canvas");
const loadStatus = document.querySelector("#load-status");
const context = canvas.getContext("2d", { alpha: false });
const input = new InputManager(document);
let state = createGame();
let renderer = null;
let accumulator = 0;
let previousTime = performance.now();
const FRAME_MS = 1000 / 60;

function requestCanvasAction(event) {
  if (event.type === "pointerdown") {
    canvas.focus({ preventScroll: true });
    input.press("start");
  } else {
    input.release("start");
  }
}

canvas.addEventListener("pointerdown", requestCanvasAction, { passive: true });
canvas.addEventListener("pointerup", requestCanvasAction, { passive: true });
canvas.addEventListener("pointercancel", requestCanvasAction, { passive: true });

drawLoading(context, "CALLING THE NIGHT...");

async function boot() {
  try {
    const assetBase = new URL("./assets/", document.baseURI);
    const assets = await loadAssets(assetBase.href);
    renderer = createRenderer(context, assets);
    loadStatus.hidden = true;
    requestAnimationFrame(frame);
  } catch (error) {
    console.error(error);
    loadStatus.textContent = "Generated assets could not be loaded.";
    drawLoading(context, "ASSET LOAD FAILED");
  }
}

function frame(now) {
  const elapsed = Math.min(100, now - previousTime);
  previousTime = now;
  accumulator += elapsed / FRAME_MS;

  while (accumulator >= 1) {
    state = stepGame(state, input.poll(), 1);
    accumulator -= 1;
  }

  renderer.render(state);
  requestAnimationFrame(frame);
}

boot();
