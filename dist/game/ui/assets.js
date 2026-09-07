const FILES = {
  moon: "bg_moon",
  cloud: "bg_cloud",
  castle: "bg_castle_silhouette",
  wall: "tile_brick_wall",
  mossWall: "tile_brick_wall_moss",
  floor: "tile_stone_floor",
  crackedFloor: "tile_stone_floor_cracked",
  cobble: "tile_cobble",
  door: "tile_door",
  lancet: "tile_lancet_window",
  roseWindow: "tile_rose_window",
  column: "tile_column",
  platform: "tile_platform",
  torch: "prop_torch",
  brazier: "prop_brazier",
  altar: "prop_altar",
  coffin: "prop_coffin",
  bookshelf: "prop_bookshelf",
  banner: "prop_banner",
  chain: "prop_hanging_chain",
  gargoyle: "prop_gargoyle_statue",
  chandelier: "prop_chandelier",
  throne: "prop_throne",
  rowan: "hero_idle_0",
  selene: "hero_idle_2",
  garrick: "hero_idle_3",
  skeleton: "enemy_skeleton",
  bat: "enemy_bat_0",
  ghost: "enemy_ghost",
  medusa: "enemy_medusa_head",
  werewolf: "enemy_werewolf",
  reaper: "enemy_reaper",
};

export const ASSET_MANIFEST = Object.freeze(
  Object.fromEntries(Object.entries(FILES).map(([id, file]) => [id, Object.freeze({ file, path: `${file}.png` })])),
);

export const ASSET_IDS = Object.freeze(Object.keys(ASSET_MANIFEST));
export const ASSET_FILES = Object.freeze([...new Set(Object.values(FILES))]);

export function assetUrl(id, base = new URL("../../assets/", import.meta.url)) {
  const record = ASSET_MANIFEST[id];
  if (!record) throw new Error(`Unknown generated asset id: ${id}`);
  return new URL(record.path, base).href;
}
