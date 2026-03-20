# RAPHAEL'S REALM - Player Survival Game

## Overview
You are a chosen mortal in a vast, dangerous world created by **Raphael the Archangel**. Raphael names you, creates your world, and serves as your divine mentor throughout your journey. You control your character directly with keyboard input.

---

## HOW TO RUN
```powershell
cd c:\Users\Hiro\Documents\VSCode\BitaCarnes
python main.py
```

**Make sure Ollama is running first:**
```powershell
ollama serve
```

---

## GAME CONTROLS

### Movement (WASD)
- **W** — Move UP
- **S** — Move DOWN
- **A** — Move LEFT
- **D** — Move RIGHT

### Actions
- **G** — GATHER (collect food or wood from current tile)
- **E** — EXCAVATE (dig for buried treasures/gold)
- **B** — BUILD (construct a house at current location)
- **SPACE** — ATTACK (fight adjacent enemy)
- **Z** — REST (recover HP slowly)

### Divine & Info
- **R** — CALL RAPHAEL (opens input to speak to Raphael)
- **M** — MAP (view world map)
- **S** — STATS (view character stats)
- **A** — TOGGLE AI MODE (enable/disable auto-play)

---

## GAME MECHANICS

### Resources
- **Food** — Prevents starvation (depletes each tick at ~0.15/tick)
- **Wood** — Used to build houses
- **Gold** — Found in treasure chests; valuable trade currency
- **Blessed Water** — Found at shrines; provides regeneration

### Terrain Types
- **🌲 Trees** — Harvest for wood
- **🍎 Food** — Harvest for food
- **⛰️ Mountains** — Impassable terrain
- **💧 Water** — Hazard, don't cross
- **⛪ Shrines** — Visit for full HP restoration
- **🏠 Houses** — Shelter you've built
- **👾 Enemies** — Fight them for score
- **💎 Treasures** — Excavate for gold
- **🪤 Traps** — Environmental hazards (deal damage)

### Survival Rules
- **HP** — Your health; reach 0 and die
- **Starvation** — Food depletes each tick; reaches 0 = HP damage
- **Traps** — Stepping on traps deals 2 HP damage
- **Enemies** — Adjacent enemies can be attacked

---

## RAPHAEL SYSTEM

### Who is Raphael?
Raphael is an Archangel with full omniscience about your world. At game start, Raphael:
1. **Designs your world** (grid size, terrain, difficulty)
2. **Names you** (your character name)
3. **Creates your origin lore**

### Speaking to Raphael
Press **R** to open a text input prompt. Ask Raphael:
- Strategic advice
- Information about the world
- Prayers or appeals
- Lore questions

Raphael maintains full **session memory** — all your conversations are remembered and inform future responses.

### Raphael's Responses
Raphael may offer:
- **Wisdom** — Poetic insight and guidance
- **Suggestions** — Tactical advice
- **Blessings** — Rare supernatural aid (if the situation warrants)

---

## SCORING

- **Gathering**: +2 points per resource
- **Building House**: +15 points
- **Defeating Enemy**: +20 points
- **Visiting Shrine**: +25 points
- **Finding Treasure**: +value of gold found

---

## OPTIONAL: SURVIVOR AI MODE

Press **A** to toggle **Survivor AI auto-mode**. When enabled:
- The AI controls your character each tick
- Makes intelligent resource gathering, building, and combat decisions
- You can still speak to Raphael for guidance

Return to manual control by pressing **A** again.

---

## TIPS FOR SURVIVAL

1. **Gather Early** — Build up food stores before exploring
2. **Seek Shrines** — Map shows shrine locations; visit for full healing
3. **Build Houses** — Create safe zones across the map
4. **Call Raphael** — When stuck, ask for guidance
5. **Avoid Traps** — Watch the minimap to identify hazards
6. **Balance Resources** — Keep food and wood balanced

---

## ENDING THE GAME

The game ends when:
- Your **HP reaches 0** (death)
- You press **Q** or close the window

Final score and stats display after ending.

---

## EXAMPLE GAMEPLAY

```
[Game starts]
Raphael: "I name you KESSANDRA, born of the northern peaks..."
[16x16 world is created]

[You press W to move north]
[You gather food]

[HP drops to 12/20]
[You press R and ask Raphael for direction]
You: "Where should I go?"
Raphael: "Seek the shrine to the east; its waters will restore you."

[You move east and find ⛪]
[You visit shrine, HP restored to 20/20]
[Score increases]
```

---

Enjoy your journey in Raphael's Realm!
