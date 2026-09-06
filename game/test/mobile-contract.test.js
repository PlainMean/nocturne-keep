import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { InputManager } from "../src/input.js";

const gameRoot = fileURLToPath(new URL("..", import.meta.url));
const readGameFile = (name) => readFileSync(join(gameRoot, name), "utf8");

class EventTargetStub {
  constructor() {
    this.listeners = new Map();
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? new Set();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }

  removeEventListener(type, listener) {
    this.listeners.get(type)?.delete(listener);
  }

  dispatch(type, properties = {}) {
    const event = {
      type,
      cancelable: true,
      defaultPrevented: false,
      ...properties,
      preventDefault() {
        this.defaultPrevented = true;
      },
    };
    for (const listener of this.listeners.get(type) ?? []) listener(event);
    return event;
  }
}

class ButtonStub extends EventTargetStub {
  constructor(control) {
    super();
    this.dataset = { control };
    this.captured = new Set();
  }

  setPointerCapture(pointerId) {
    this.captured.add(pointerId);
  }

  hasPointerCapture(pointerId) {
    return this.captured.has(pointerId);
  }

  releasePointerCapture(pointerId) {
    this.captured.delete(pointerId);
  }
}

class RootStub extends EventTargetStub {
  constructor(buttons) {
    super();
    this.buttons = buttons;
    this.visibilityState = "visible";
  }

  querySelectorAll(selector) {
    assert.equal(selector, "[data-control]");
    return this.buttons;
  }
}

test("mobile document contract declares viewport, safe areas, and orientation behavior", () => {
  const html = readGameFile("index.html");
  const styles = readGameFile("styles.css");
  const main = readGameFile("src/main.js");
  const render = readGameFile("src/render.js");

  assert.match(html, /viewport-fit=cover/);
  assert.match(html, /maximum-scale=1/);
  assert.match(html, /user-scalable=no/);
  assert.match(html, /class="orientation-message"/);
  assert.match(html, /href="\.\/styles\.css"/);
  assert.match(html, /src="\.\/game\/main\.js"/);
  assert.match(html, /href="\.\/assets\/bg_moon\.png"/);
  assert.doesNotMatch(html, /(?:src|href)=["']\//);
  assert.match(styles, /height: 100dvh/);
  assert.match(styles, /min-height: 100dvh/);
  for (const inset of ["top", "right", "bottom", "left"]) {
    assert.match(styles, new RegExp(`safe-area-inset-${inset}`));
  }
  assert.match(styles, /aspect-ratio: 16 \/ 9/);
  assert.match(styles, /image-rendering: pixelated/);
  assert.match(styles, /touch-action: none/);
  assert.match(styles, /overscroll-behavior: none/);
  assert.match(styles, /min-height: 56px/);
  assert.match(styles, /orientation: landscape/);
  assert.doesNotMatch(main, /https?:\/\//);
  assert.doesNotMatch(render, /https?:\/\//);
});

test("pointer controls capture, support simultaneous touches, and always release", () => {
  const left = new ButtonStub("left");
  const jump = new ButtonStub("jump");
  const root = new RootStub([left, jump]);
  const viewport = new EventTargetStub();
  const input = new InputManager(root, viewport);

  const firstDown = left.dispatch("pointerdown", { pointerId: 11 });
  assert.equal(firstDown.defaultPrevented, true);
  assert.equal(left.hasPointerCapture(11), true);
  assert.equal(input.poll().left, true);

  left.dispatch("pointerdown", { pointerId: 12 });
  left.dispatch("pointerup", { pointerId: 11 });
  assert.equal(input.poll().left, true);

  const cancel = root.dispatch("pointercancel", { pointerId: 12 });
  assert.equal(cancel.defaultPrevented, true);
  assert.equal(input.poll().left, false);

  jump.dispatch("pointerdown", { pointerId: 13 });
  jump.dispatch("lostpointercapture", { pointerId: 13 });
  assert.equal(input.poll().jump, false);

  left.dispatch("pointerdown", { pointerId: 14 });
  viewport.dispatch("blur");
  assert.equal(input.poll().left, false);
  assert.equal(input.pointerControls.size, 0);

  input.destroy();
});
