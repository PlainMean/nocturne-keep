import { SAVE_VERSION, assertStateInvariant } from "./state.js";

export function serializeState(state) {
  assertStateInvariant(state);
  return JSON.stringify(state);
}

export function deserializeState(raw) {
  const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new TypeError("Save is not an object");
  if (parsed.version !== SAVE_VERSION) throw new Error("Unsupported save version");
  assertStateInvariant(parsed);
  return parsed;
}
