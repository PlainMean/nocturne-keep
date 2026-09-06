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
  constructor(root = document) {
    this.root = root;
    this.held = new Set();
    this.edges = new Set();
    this.pointerControls = new Map();
    this.boundButtons = [];

    this.onKeyDown = (event) => {
      const control = KEY_CONTROLS.get(event.key);
      if (!control) return;
      event.preventDefault();
      this.press(control);
    };
    this.onKeyUp = (event) => {
      const control = KEY_CONTROLS.get(event.key);
      if (!control) return;
      event.preventDefault();
      this.release(control);
    };
    this.onBlur = () => {
      this.held.clear();
      this.pointerControls.clear();
    };

    root.addEventListener("keydown", this.onKeyDown, { passive: false });
    root.addEventListener("keyup", this.onKeyUp, { passive: false });
    window.addEventListener("blur", this.onBlur);

    for (const button of root.querySelectorAll("[data-control]")) {
      this.bindButton(button, button.dataset.control);
    }
  }

  bindButton(button, control) {
    if (!control) return;
    const down = (event) => {
      event.preventDefault();
      button.setPointerCapture?.(event.pointerId);
      this.pointerControls.set(event.pointerId, control);
      this.press(control);
    };
    const up = (event) => {
      event.preventDefault();
      this.pointerControls.delete(event.pointerId);
      this.release(control);
    };
    button.addEventListener("pointerdown", down, { passive: false });
    button.addEventListener("pointerup", up, { passive: false });
    button.addEventListener("pointercancel", up, { passive: false });
    button.addEventListener("lostpointercapture", up, { passive: false });
    this.boundButtons.push({ button, down, up });
  }

  press(control) {
    if (!control) return;
    if (!this.held.has(control)) this.edges.add(control);
    this.held.add(control);
  }

  release(control) {
    this.held.delete(control);
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
    window.removeEventListener("blur", this.onBlur);
    for (const { button, down, up } of this.boundButtons) {
      button.removeEventListener("pointerdown", down);
      button.removeEventListener("pointerup", up);
      button.removeEventListener("pointercancel", up);
      button.removeEventListener("lostpointercapture", up);
    }
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
