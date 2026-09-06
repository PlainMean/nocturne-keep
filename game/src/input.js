const KEY_CONTROLS = new Map([
  ["ArrowLeft", "left"],
  ["a", "left"],
  ["A", "left"],
  ["ArrowRight", "right"],
  ["d", "right"],
  ["D", "right"],
  [" ", "jump"],
  ["Spacebar", "jump"],
  ["ArrowUp", "jump"],
  ["x", "attack"],
  ["X", "attack"],
  ["j", "attack"],
  ["J", "attack"],
  ["Enter", "start"],
  ["r", "restart"],
  ["R", "restart"],
]);

const GAME_CONTROLS = ["left", "right", "jump", "attack"];

export class InputManager {
  constructor(root = document, eventTarget = root.defaultView ?? globalThis.window ?? root) {
    this.root = root;
    this.eventTarget = eventTarget ?? root;
    this.held = new Set();
    this.edges = new Set();
    this.keyboardControls = new Set();
    this.manualControls = new Set();
    this.pointerControls = new Map();
    this.pointerTargets = new Map();
    this.controlPointers = new Map();
    this.boundButtons = [];

    this.onKeyDown = (event) => {
      const control = KEY_CONTROLS.get(event.key);
      if (!control) return;
      event.preventDefault();
      this.keyboardControls.add(control);
      this.syncHeld(control);
    };
    this.onKeyUp = (event) => {
      const control = KEY_CONTROLS.get(event.key);
      if (!control) return;
      event.preventDefault();
      this.keyboardControls.delete(control);
      this.syncHeld(control);
    };
    this.onBlur = () => {
      this.releaseAll();
    };
    this.onVisibilityChange = () => {
      if (this.root.visibilityState === "hidden" || this.eventTarget.document?.visibilityState === "hidden") {
        this.releaseAll();
      }
    };
    this.onPointerEnd = (event) => {
      event.preventDefault();
      this.releasePointer(event.pointerId);
    };

    root.addEventListener("keydown", this.onKeyDown, { passive: false });
    root.addEventListener("keyup", this.onKeyUp, { passive: false });
    root.addEventListener("pointerup", this.onPointerEnd, { passive: false });
    root.addEventListener("pointercancel", this.onPointerEnd, { passive: false });
    root.addEventListener("visibilitychange", this.onVisibilityChange);
    this.eventTarget.addEventListener("blur", this.onBlur);
    this.eventTarget.addEventListener("pagehide", this.onBlur);

    for (const button of root.querySelectorAll("[data-control]")) {
      this.bindButton(button, button.dataset.control);
    }
  }

  syncHeld(control) {
    const pointerIds = this.controlPointers.get(control);
    const shouldHold = this.keyboardControls.has(control)
      || this.manualControls.has(control)
      || Boolean(pointerIds?.size);
    if (shouldHold) {
      if (!this.held.has(control)) this.edges.add(control);
      this.held.add(control);
    } else {
      this.held.delete(control);
    }
  }

  bindButton(button, control) {
    if (!control) return;
    const down = (event) => {
      event.preventDefault();
      if (!Number.isFinite(event.pointerId)) return;
      this.releasePointer(event.pointerId);
      this.pointerControls.set(event.pointerId, control);
      this.pointerTargets.set(event.pointerId, button);
      let pointerIds = this.controlPointers.get(control);
      if (!pointerIds) {
        pointerIds = new Set();
        this.controlPointers.set(control, pointerIds);
      }
      pointerIds.add(event.pointerId);
      this.syncHeld(control);
      try {
        button.setPointerCapture?.(event.pointerId);
      } catch {
        // The document-level pointer end listener still releases the input.
      }
    };
    const up = (event) => {
      event.preventDefault();
      this.releasePointer(event.pointerId);
    };
    button.addEventListener("pointerdown", down, { passive: false });
    button.addEventListener("pointerup", up, { passive: false });
    button.addEventListener("pointercancel", up, { passive: false });
    button.addEventListener("lostpointercapture", up, { passive: false });
    this.boundButtons.push({ button, down, up });
  }

  releasePointer(pointerId) {
    if (!Number.isFinite(pointerId)) return;
    const control = this.pointerControls.get(pointerId);
    if (!control) return;
    const button = this.pointerTargets.get(pointerId);
    this.pointerControls.delete(pointerId);
    this.pointerTargets.delete(pointerId);
    const pointerIds = this.controlPointers.get(control);
    pointerIds?.delete(pointerId);
    if (!pointerIds?.size) this.controlPointers.delete(control);
    this.syncHeld(control);
    if (button?.hasPointerCapture?.(pointerId)) {
      try {
        button.releasePointerCapture(pointerId);
      } catch {
        // Capture may already have been released by the browser.
      }
    }
  }

  releaseAll() {
    const activePointers = [...this.pointerTargets.entries()];
    this.keyboardControls.clear();
    this.manualControls.clear();
    this.pointerControls.clear();
    this.pointerTargets.clear();
    this.controlPointers.clear();
    this.held.clear();
    this.edges.clear();
    for (const [pointerId, button] of activePointers) {
      if (!button?.hasPointerCapture?.(pointerId)) continue;
      try {
        button.releasePointerCapture(pointerId);
      } catch {
        // Capture may already have been released by the browser.
      }
    }
  }

  press(control) {
    if (!control) return;
    this.manualControls.add(control);
    this.syncHeld(control);
  }

  release(control) {
    if (!control) return;
    this.manualControls.delete(control);
    this.syncHeld(control);
  }

  poll() {
    const input = {
      left: this.held.has("left"),
      right: this.held.has("right"),
      jump: this.held.has("jump"),
      attack: this.held.has("attack"),
      jumpPressed: this.edges.has("jump"),
      attackPressed: this.edges.has("attack"),
      startPressed: this.edges.has("start"),
      restartPressed: this.edges.has("restart"),
    };
    this.edges.clear();
    return input;
  }

  destroy() {
    this.root.removeEventListener("keydown", this.onKeyDown);
    this.root.removeEventListener("keyup", this.onKeyUp);
    this.root.removeEventListener("pointerup", this.onPointerEnd);
    this.root.removeEventListener("pointercancel", this.onPointerEnd);
    this.root.removeEventListener("visibilitychange", this.onVisibilityChange);
    this.eventTarget.removeEventListener("blur", this.onBlur);
    this.eventTarget.removeEventListener("pagehide", this.onBlur);
    for (const { button, down, up } of this.boundButtons) {
      button.removeEventListener("pointerdown", down);
      button.removeEventListener("pointerup", up);
      button.removeEventListener("pointercancel", up);
      button.removeEventListener("lostpointercapture", up);
    }
    this.releaseAll();
  }
}

export function inputForTests(overrides = {}) {
  return {
    left: false,
    right: false,
    jump: false,
    attack: false,
    jumpPressed: false,
    attackPressed: false,
    startPressed: false,
    restartPressed: false,
    ...overrides,
  };
}

export { GAME_CONTROLS };
