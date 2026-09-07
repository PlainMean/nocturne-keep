import heroes from "../data/heroes.json" with { type: "json" };
import enemies from "../data/enemies.json" with { type: "json" };
import skills from "../data/skills.json" with { type: "json" };
import items from "../data/items.json" with { type: "json" };
import encounters from "../data/encounters.json" with { type: "json" };
import story from "../data/story.json" with { type: "json" };

function indexById(records) {
  return Object.freeze(Object.fromEntries(records.map((record) => [record.id, record])));
}

export const HEROES = Object.freeze(heroes);
export const ENEMIES = Object.freeze(enemies);
export const SKILLS = Object.freeze(skills);
export const ITEMS = Object.freeze(items);
export const ENCOUNTERS = Object.freeze(encounters);
export const STORY = Object.freeze(story);

export const HERO_BY_ID = indexById(HEROES);
export const ENEMY_BY_ID = indexById(ENEMIES);
export const SKILL_BY_ID = indexById(SKILLS);
export const ITEM_BY_ID = indexById(ITEMS);
export const ENCOUNTER_BY_ID = indexById(ENCOUNTERS);
export const STORY_BY_ID = indexById(STORY);
