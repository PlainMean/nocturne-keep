import { createGame, stepGame } from "./engine.js";
import { InputManager } from "./input.js";
import { createRenderer, drawLoading, loadAssets } from "./render.js";

const canvas = document.querySelector("#game-canvas");
const gameShell = document.querySelector(".game-shell");
const loadStatus = document.querySelector("#load-status");
const context = canvas.getContext("2d", { alpha: false });
const input = new InputManager(document);
let state = createGame();
let renderer = null;
let accumulator = 0;
let previousTime = performance.now();
const FRAME_MS = 1000 / 60;
const canvasPointers = new Set();

function releaseCanvasPointer(event) {
  event.preventDefault();
  if (!Number.isFinite(event.pointerId)) return;
  canvasPointers.delete(event.pointerId);
  if (canvas.hasPointerCapture?.(event.pointerId)) {
    try {
      canvas.releasePointerCapture(event.pointerId);
    } catch {
      // Capture may already have been released by the browser.
    }
  }
  if (canvasPointers.size === 0) input.release("start");
}

function requestCanvasAction(event) {
  event.preventDefault();
  if (!Number.isFinite(event.pointerId)) return;
  if (event.type === "pointerdown") {
    canvas.focus({ preventScroll: true });
    canvasPointers.add(event.pointerId);
    input.press("start");
    try {
      canvas.setPointerCapture?.(event.pointerId);
    } catch {
      // The input manager still handles the action edge.
    }
    return;
  }
  releaseCanvasPointer(event);
}

canvas.addEventListener("pointerdown", requestCanvasAction, { passive: false });
canvas.addEventListener("pointerup", releaseCanvasPointer, { passive: false });
canvas.addEventListener("pointercancel", releaseCanvasPointer, { passive: false });
canvas.addEventListener("lostpointercapture", releaseCanvasPointer, { passive: false });

function preventBrowserGesture(event) {
  if (gameShell.contains(event.target)) event.preventDefault();
}

for (const eventName of ["contextmenu", "selectstart", "dragstart", "touchmove", "gesturestart", "gesturechange", "gestureend"]) {
  document.addEventListener(eventName, preventBrowserGesture, { passive: false });
}

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
