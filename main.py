import json
import random
import time
import urllib.error
import urllib.request
from pathlib import Path
from collections import deque

import pygame
import pygame.freetype

OBJECTIVE_PATH = Path(__file__).with_name("objectives.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

# Colors
COLOR_BG = (22, 26, 30)
COLOR_GRID_DARK = (31, 41, 46)
COLOR_GRID_LIGHT = (37, 49, 56)
COLOR_OUTLINE = (66, 89, 102)
COLOR_HUD = (18, 22, 25)
COLOR_CHAT_BG = (25, 25, 35)
COLOR_TEXT = (227, 232, 238)
COLOR_WARN = (220, 91, 73)
COLOR_FOOD = (226, 198, 89)
COLOR_TREE = (87, 148, 98)
COLOR_HOUSE = (177, 121, 84)
COLOR_ENEMY = (181, 77, 89)
COLOR_HUMAN = (109, 177, 236)
COLOR_MOUNTAIN = (120, 120, 130)
COLOR_WATER = (100, 150, 200)
COLOR_SHRINE = (200, 180, 100)
COLOR_TREASURE = (255, 215, 0)
COLOR_TRAP = (200, 100, 100)

CELL_SIZE = 40
HUD_HEIGHT = 100
CHAT_HEIGHT = 150


class RaphaelMemory:
    """Persistent memory system for Raphael."""
    def __init__(self):
        self.conversation_history = deque(maxlen=20)
        self.events = deque(maxlen=50)
        self.world_knowledge = {}

    def add_conversation(self, role: str, message: str) -> None:
        self.conversation_history.append({"role": role, "message": message, "timestamp": time.time()})

    def add_event(self, event: str) -> None:
        self.events.append({"event": event, "timestamp": time.time()})

    def get_context(self) -> str:
        """Build context string from memory for Raphael prompts."""
        context = "=== SESSION MEMORY ===\n"
        if self.conversation_history:
            context += "RECENT CONVERSATIONS:\n"
            for entry in list(self.conversation_history)[-10:]:
                context += f"  {entry['role']}: {entry['message']}\n"
        if self.events:
            context += "\nRECENT EVENTS:\n"
            for entry in list(self.events)[-10:]:
                context += f"  - {entry['event']}\n"
        return context


class World:
    def __init__(self, size: int, config: dict) -> None:
        self.size = size
        self.human = [size // 2, size // 2]
        self.human_name = config.get("human_name", "Chosen One")
        self.human_origin = config.get("human_origin", "A mysterious survivor.")

        self.food_tiles: set[tuple[int, int]] = set()
        self.tree_tiles: set[tuple[int, int]] = set()
        self.house_tiles: set[tuple[int, int]] = set()
        self.enemy_tiles: set[tuple[int, int]] = set()
        self.mountain_tiles: set[tuple[int, int]] = set()
        self.water_tiles: set[tuple[int, int]] = set()
        self.shrine_tiles: set[tuple[int, int]] = set()
        self.treasure_tiles: dict[tuple[int, int], int] = {}
        self.trap_tiles: set[tuple[int, int]] = set()

        self.max_hp = float(config.get("start_hp", 20))
        self.hp = self.max_hp
        self.inventory = {
            "food": float(config.get("start_food", 8)),
            "wood": float(config.get("start_wood", 2)),
            "gold": float(config.get("start_gold", 0)),
            "blessed_water": 0,
        }
        self.stats = {
            "score": 0,
            "houses_built": 0,
            "enemies_defeated": 0,
            "food_gathered": 0,
            "wood_gathered": 0,
            "treasures_found": 0,
            "shrines_visited": 0,
        }
        self.last_event = "world initialized"

        # Spawn complex terrain
        self.spawn_terrain()

    def spawn_terrain(self) -> None:
        """Spawn mountains and water to create landscape."""
        for _ in range(int(self.size * 0.08)):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if [x, y] != self.human:
                self.mountain_tiles.add((x, y))

        for _ in range(int(self.size * 0.06)):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if [x, y] != self.human and (x, y) not in self.mountain_tiles:
                self.water_tiles.add((x, y))

        self.spawn_tiles(self.food_tiles, int(self.size * 0.6))
        self.spawn_tiles(self.tree_tiles, int(self.size * 0.5))
        self.spawn_tiles(self.enemy_tiles, int(self.size * 0.15))
        self.spawn_tiles(self.shrine_tiles, max(1, int(self.size * 0.05)))

        for _ in range(int(self.size * 0.1)):
            x, y = self.random_free_position()
            if (x, y) not in self.treasure_tiles:
                self.treasure_tiles[(x, y)] = random.randint(10, 50)

        self.spawn_tiles(self.trap_tiles, int(self.size * 0.08))

    def random_free_position(self) -> tuple[int, int]:
        for _ in range(300):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.is_walkable(x, y) and [x, y] != self.human:
                return (x, y)
        return (self.size // 2, self.size // 2)

    def is_walkable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        return (x, y) not in self.mountain_tiles and (x, y) not in self.water_tiles

    def spawn_tiles(self, tile_set: set[tuple[int, int]], target_count: int) -> None:
        while len(tile_set) < target_count:
            pos = self.random_free_position()
            if pos not in tile_set and pos not in self.mountain_tiles and pos not in self.water_tiles:
                tile_set.add(pos)

    def move_human(self, direction: str) -> bool:
        dx, dy = DIRECTIONS.get(direction, (0, 0))
        nx, ny = self.human[0] + dx, self.human[1] + dy
        if not self.is_walkable(nx, ny):
            self.last_event = "blocked by terrain"
            return False
        self.human = [nx, ny]
        self.last_event = f"moved {direction}"

        # Check trap
        if (nx, ny) in self.trap_tiles:
            self.hp -= 2
            self.last_event = "triggered a trap!"
            self.trap_tiles.discard((nx, ny))

        return True

    def gather(self) -> bool:
        pos = tuple(self.human)
        if pos in self.food_tiles:
            self.food_tiles.discard(pos)
            self.inventory["food"] += 1
            self.stats["food_gathered"] += 1
            self.stats["score"] += 2
            self.last_event = "gathered food"
            self.spawn_tiles(self.food_tiles, int(self.size * 0.6))
            return True
        if pos in self.tree_tiles:
            self.tree_tiles.discard(pos)
            self.inventory["wood"] += 1
            self.stats["wood_gathered"] += 2
            self.stats["score"] += 2
            self.last_event = "gathered wood"
            self.spawn_tiles(self.tree_tiles, int(self.size * 0.5))
            return True
        self.last_event = "nothing to gather"
        return False

    def excavate(self) -> bool:
        pos = tuple(self.human)
        if pos in self.treasure_tiles:
            gold = self.treasure_tiles.pop(pos)
            self.inventory["gold"] += gold
            self.stats["treasures_found"] += 1
            self.stats["score"] += gold
            self.last_event = f"found {gold}g!"
            return True
        self.last_event = "no treasure here"
        return False

    def build_house(self, wood_cost: int, food_cost: int) -> bool:
        pos = tuple(self.human)
        if pos in self.house_tiles or pos in self.enemy_tiles or pos in self.mountain_tiles or pos in self.water_tiles:
            self.last_event = "cannot build here"
            return False
        if self.inventory["wood"] < wood_cost or self.inventory["food"] < food_cost:
            self.last_event = "insufficient resources"
            return False
        self.inventory["wood"] -= wood_cost
        self.inventory["food"] -= food_cost
        self.house_tiles.add(pos)
        self.stats["houses_built"] += 1
        self.stats["score"] += 15
        self.last_event = "house built"
        return True

    def attack(self) -> bool:
        hx, hy = self.human
        candidates = [(abs(ex - hx) + abs(ey - hy), ex, ey) for ex, ey in self.enemy_tiles if abs(ex - hx) + abs(ey - hy) <= 1]
        if not candidates:
            self.last_event = "no enemy nearby"
            return False
        _, ex, ey = min(candidates)
        self.enemy_tiles.discard((ex, ey))
        self.stats["enemies_defeated"] += 1
        self.stats["score"] += 20
        self.last_event = "enemy defeated"
        self.spawn_tiles(self.enemy_tiles, int(self.size * 0.15))
        return True

    def rest(self) -> bool:
        self.hp = min(self.max_hp, self.hp + 3)
        self.last_event = "rested and recovered"
        return True

    def visit_shrine(self) -> bool:
        pos = tuple(self.human)
        if pos in self.shrine_tiles:
            self.hp = self.max_hp
            self.inventory["blessed_water"] += 2
            self.stats["shrines_visited"] += 1
            self.stats["score"] += 25
            self.last_event = "shrine blessed you"
            return True
        self.last_event = "no shrine here"
        return False

    def nearest(self, tiles: set[tuple[int, int]]) -> dict:
        hx, hy = self.human
        best = None
        best_dist = 10**9
        for tx, ty in tiles:
            dist = abs(tx - hx) + abs(ty - hy)
            if dist < best_dist:
                best_dist = dist
                best = {"x": tx, "y": ty, "distance": dist}
        return best if best else {"x": hx, "y": hy, "distance": 0}

    def state(self, tick: int) -> dict:
        return {
            "tick": tick,
            "human": {"x": self.human[0], "y": self.human[1], "name": self.human_name},
            "hp": int(self.hp),
            "max_hp": int(self.max_hp),
            "inventory": {k: int(v) for k, v in self.inventory.items()},
            "stats": self.stats,
            "nearby": {
                "food": self.nearest(self.food_tiles)["distance"],
                "tree": self.nearest(self.tree_tiles)["distance"],
                "enemy": self.nearest(self.enemy_tiles)["distance"],
                "shrine": self.nearest(self.shrine_tiles)["distance"],
            },
            "last_event": self.last_event,
        }


def load_objectives(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def call_ollama(prompt: str, model: str) -> str | None:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4},
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            envelope = json.loads(raw)
            return envelope.get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def create_world_with_raphael(objectives: dict) -> tuple[World, str, RaphaelMemory]:
    """Have Raphael design the world and name the player's character."""
    raphael_cfg = objectives["raphael"]
    world_cfg = objectives["world_creator"]
    memory = RaphaelMemory()

    prompt = (
        f"{raphael_cfg['identity_prompt']}\n\n"
        f"TASK: Design a survival world.\n"
        f"{world_cfg['narrative']}\n\n"
        f"CONSTRAINTS:\n" + "\n".join(f"- {c}" for c in world_cfg["world_constraints"]) +
        f"\n\nRespond ONLY with valid JSON:\n"
        """{"grid_size": integer, "human_name": string, "origin_lore": string, "health": integer, "food": integer, "wood": integer, "description": string}"""
    )

    response = call_ollama(prompt, MODEL_NAME)
    if not response:
        # Fallback
        world_config = {
            "grid_size": 20,
            "human_name": "Chosen One",
            "origin_lore": "Born under starlight.",
            "start_hp": 20,
            "start_food": 8,
            "start_wood": 2,
            "start_gold": 0,
        }
    else:
        try:
            parsed = json.loads(response)
            world_config = {
                "grid_size": min(32, max(16, int(parsed.get("grid_size", 20)))),
                "human_name": parsed.get("human_name", "Chosen One"),
                "origin_lore": parsed.get("origin_lore", "A mysterious survivor."),
                "start_hp": max(15, int(parsed.get("health", 20))),
                "start_food": max(5, int(parsed.get("food", 8))),
                "start_wood": max(1, int(parsed.get("wood", 2))),
                "start_gold": 0,
            }
        except:
            world_config = {
                "grid_size": 20,
                "human_name": "Chosen One",
                "origin_lore": "Born under starlight.",
                "start_hp": 20,
                "start_food": 8,
                "start_wood": 2,
                "start_gold": 0,
            }

    world = World(world_config["grid_size"], world_config)
    memory.add_event(f"World created: {world_config['grid_size']}x{world_config['grid_size']} grid")
    memory.add_event(f"Character created: {world_config['human_name']}")

    return world, world_config["grid_size"], memory


def raphael_response(objectives: dict, message: str, world: World, memory: RaphaelMemory) -> str:
    """Get Raphael's response to player's question/appeal."""
    memory.add_conversation("Player", message)
    context = memory.get_context()
    state_str = json.dumps(world.state(0), indent=2)

    prompt = (
        f"{objectives['raphael']['identity_prompt']}\n\n"
        f"{context}\n\n"
        f"CURRENT WORLD STATE:\n{state_str}\n\n"
        f"The mortal {world.human_name} speaks to you:\n\"{message}\"\n\n"
        f"Respond with divine wisdom, insight, and guidance. Be poetic yet practical. "
        f"Keep response brief (2-3 sentences)."
    )

    response = call_ollama(prompt, MODEL_NAME)
    if not response:
        response = f"The divine silence wraps around you, {world.human_name}. Trust your instincts."

    memory.add_conversation("Raphael", response)
    return response


def draw_tile(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=5)


def draw_emoji(surface: pygame.Surface, font: pygame.font.Font, text: str, center: tuple[int, int]) -> None:
    glyph = font.render(text, True, (12, 14, 18))
    glyph_rect = glyph.get_rect(center=center)
    surface.blit(glyph, glyph_rect)


def render_world(screen: pygame.Surface, world: World, hud_font: pygame.font.Font, emoji_font: pygame.font.Font, mode: str) -> None:
    """Render the game world."""
    screen.fill(COLOR_BG)

    for y in range(world.size):
        for x in range(world.size):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
            checker = (x + y) % 2
            base = COLOR_GRID_DARK if checker == 0 else COLOR_GRID_LIGHT
            pygame.draw.rect(screen, base, rect)
            pygame.draw.rect(screen, COLOR_OUTLINE, rect, 1)

            pos = (x, y)
            if pos in world.mountain_tiles:
                inner = rect.inflate(-8, -8)
                draw_tile(screen, inner, COLOR_MOUNTAIN)
                draw_emoji(screen, emoji_font, "⛰️", rect.center)
            elif pos in world.water_tiles:
                inner = rect.inflate(-8, -8)
                draw_tile(screen, inner, COLOR_WATER)
                draw_emoji(screen, emoji_font, "💧", rect.center)
            elif pos in world.shrine_tiles:
                inner = rect.inflate(-10, -10)
                draw_tile(screen, inner, COLOR_SHRINE)
                draw_emoji(screen, emoji_font, "⛪", rect.center)
            elif pos in world.house_tiles:
                inner = rect.inflate(-10, -10)
                draw_tile(screen, inner, COLOR_HOUSE)
                draw_emoji(screen, emoji_font, "🏠", rect.center)
            elif pos in world.enemy_tiles:
                inner = rect.inflate(-12, -12)
                draw_tile(screen, inner, COLOR_ENEMY)
                draw_emoji(screen, emoji_font, "👾", rect.center)
            elif pos in world.food_tiles:
                inner = rect.inflate(-14, -14)
                draw_tile(screen, inner, COLOR_FOOD)
                draw_emoji(screen, emoji_font, "🍎", rect.center)
            elif pos in world.tree_tiles:
                inner = rect.inflate(-12, -12)
                draw_tile(screen, inner, COLOR_TREE)
                draw_emoji(screen, emoji_font, "🌲", rect.center)
            elif pos in world.trap_tiles:
                inner = rect.inflate(-14, -14)
                draw_tile(screen, inner, COLOR_TRAP)
                draw_emoji(screen, emoji_font, "🪤", rect.center)
            elif pos in world.treasure_tiles:
                inner = rect.inflate(-14, -14)
                draw_tile(screen, inner, COLOR_TREASURE)
                draw_emoji(screen, emoji_font, "💎", rect.center)

    hx, hy = world.human
    human_rect = pygame.Rect(hx * CELL_SIZE, hy * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
    avatar = human_rect.inflate(-6, -6)
    draw_tile(screen, avatar, COLOR_HUMAN)
    draw_emoji(screen, emoji_font, "🧑", human_rect.center)

    # HUD
    hud_y = world.size * CELL_SIZE
    hud_rect = pygame.Rect(0, hud_y, world.size * CELL_SIZE, HUD_HEIGHT)
    pygame.draw.rect(screen, COLOR_HUD, hud_rect)

    line1 = f"{world.human_name} | HP {int(world.hp)}/{int(world.max_hp)} | Food {int(world.inventory['food'])} Wood {int(world.inventory['wood'])} Gold {int(world.inventory['gold'])}"
    line2 = f"Houses {world.stats['houses_built']} | Defeated {world.stats['enemies_defeated']} | Score {world.stats['score']} | Mode: {mode}"
    line3 = f"Event: {world.last_event}"

    for idx, line in enumerate([line1, line2, line3]):
        txt = hud_font.render(line, True, COLOR_TEXT)
        screen.blit(txt, (8, hud_y + 8 + idx * 28))


def render_chat_ui(screen: pygame.Surface, chat_history: list[str], hud_font: pygame.font.Font, grid_size: int) -> None:
    """Render the chat interface."""
    chat_y = grid_size * CELL_SIZE + HUD_HEIGHT
    chat_rect = pygame.Rect(0, chat_y, grid_size * CELL_SIZE, CHAT_HEIGHT)
    pygame.draw.rect(screen, COLOR_CHAT_BG, chat_rect)
    pygame.draw.line(screen, COLOR_OUTLINE, (0, chat_y), (grid_size * CELL_SIZE, chat_y), 2)

    txt_title = hud_font.render("RAPHAEL'S WORDS (Press R to speak):", True, COLOR_WARN)
    screen.blit(txt_title, (8, chat_y + 5))

    for idx, line in enumerate(chat_history[-3:]):
        if idx < 3:
            txt = hud_font.render(line[:60], True, COLOR_TEXT)
            screen.blit(txt, (8, chat_y + 30 + idx * 25))


def run() -> None:
    print("\n=== RAPHAEL'S REALM ===\n")

    objectives = load_objectives(OBJECTIVE_PATH)
    print("[Raphael is awakening...]")
    world, grid_actual, memory = create_world_with_raphael(objectives)
    print(f"[Raphael has spoken.]")
    print(f"[World: {grid_actual}x{grid_actual} | Your name: {world.human_name}]")
    print(f"[Lore: {world.human_origin}]\n")

    pygame.init()
    pygame.display.set_caption("Raphael's Realm - Player Controlled")
    window_width = grid_actual * CELL_SIZE
    window_height = grid_actual * CELL_SIZE + HUD_HEIGHT + CHAT_HEIGHT
    screen = pygame.display.set_mode((window_width, window_height))
    hud_font = pygame.font.SysFont("consolas", 16)
    emoji_font = pygame.font.SysFont("segoe ui emoji", 20)

    clock = pygame.time.Clock()
    running = True
    tick = 0
    last_action_time = 0.0
    action_delay = 0.2
    chat_history: list[str] = ["Raphael: Welcome, mortal."]
    player_mode = True
    ai_mode = False

    while running and world.hp > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                now = time.time()
                if now - last_action_time < action_delay:
                    continue

                # Movement
                if event.key == pygame.K_w:
                    world.move_human("up")
                    last_action_time = now
                elif event.key == pygame.K_s:
                    world.move_human("down")
                    last_action_time = now
                elif event.key == pygame.K_a:
                    world.move_human("left")
                    last_action_time = now
                elif event.key == pygame.K_d:
                    world.move_human("right")
                    last_action_time = now
                # Actions
                elif event.key == pygame.K_g:
                    world.gather()
                    last_action_time = now
                elif event.key == pygame.K_e:
                    world.excavate()
                    last_action_time = now
                elif event.key == pygame.K_b:
                    world.build_house(4, 2)
                    last_action_time = now
                elif event.key == pygame.K_SPACE:
                    world.attack()
                    last_action_time = now
                elif event.key == pygame.K_z:
                    world.rest()
                    last_action_time = now
                # Special
                elif event.key == pygame.K_r:
                    print("\n[Call to Raphael]")
                    user_input = input("Speak to Raphael: ")
                    if user_input.strip():
                        response = raphael_response(objectives, user_input, world, memory)
                        chat_history.append(f"You: {user_input[:40]}")
                        chat_history.append(f"Raphael: {response[:60]}")
                        print(f"Raphael: {response}\n")
                elif event.key == pygame.K_m:
                    # Map view (display all tile positions)
                    print("[World Map Generated]")

        # Starvation upkeep
        world.inventory["food"] -= objectives["world"]["economy"]["food_upkeep_per_tick"]
        if world.inventory["food"] <= 0:
            world.hp -= objectives["world"]["economy"]["starvation_damage_per_tick"]
            world.last_event = "starving"

        tick += 1
        mode_str = "PLAYER" if player_mode else "AI_AUTO"
        render_world(screen, world, hud_font, emoji_font, mode_str)
        render_chat_ui(screen, chat_history, hud_font, grid_actual)
        pygame.display.flip()
        clock.tick(60)

    print(f"\n[Simulation Ended]")
    print(json.dumps(world.stats, indent=2))
    pygame.quit()


if __name__ == "__main__":
    run()
