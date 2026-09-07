const DEFAULT_SEED = 0x6e6f6374;

export function normalizeSeed(seed = DEFAULT_SEED) {
  const value = Number.isFinite(seed) ? Number(seed) >>> 0 : DEFAULT_SEED;
  return value === 0 ? DEFAULT_SEED : value;
}

export function nextRandom(state) {
  let value = (state.seed + Math.imul(state.rngCalls + 1, 0x9e3779b9)) >>> 0;
  value ^= value >>> 16;
  value = Math.imul(value, 0x21f0aaad) >>> 0;
  value ^= value >>> 15;
  value = Math.imul(value, 0x735a2d97) >>> 0;
  value ^= value >>> 15;
  return {
    value: (value >>> 0) / 0x100000000,
    state: { ...state, rngCalls: state.rngCalls + 1 },
  };
}

export function randomInt(state, min, max) {
  const low = Math.ceil(min);
  const high = Math.floor(max);
  if (high < low) throw new RangeError(`Invalid random range ${min}..${max}`);
  const result = nextRandom(state);
  return {
    value: low + Math.floor(result.value * (high - low + 1)),
    state: result.state,
  };
}

export function weightedPick(state, entries) {
  const valid = entries.filter((entry) => Number(entry.weight) > 0);
  if (valid.length === 0) return { value: null, state };
  const total = valid.reduce((sum, entry) => sum + Number(entry.weight), 0);
  const roll = nextRandom(state);
  let cursor = roll.value * total;
  for (const entry of valid) {
    cursor -= Number(entry.weight);
    if (cursor < 0) return { value: entry.value ?? entry, state: roll.state };
  }
  return { value: valid.at(-1).value ?? valid.at(-1), state: roll.state };
}

export { DEFAULT_SEED };
