"""Sprite-based terrain and world renderer integrating with the main UI system."""

from __future__ import annotations
import pygame
import random
from typing import Optional, Tuple
from .sprite_system import get_sprite_manager, render_sprite
from .house_generation import HouseStructure, HouseGenerator, HouseStyle
from .config import TAMANHO_CELULA


class TerrainRenderer:
    """Renders terrain using sprite sheets."""

    BIOMA_SPRITES = {
        # Grass and plains
        "grass": "grass",
        "grass_dark": "grass_dark",
        "grassland": "grass",
        # Forest
        "floresta": "forest",
        "floresta_sombra": "forest",
        "floresta_sagrada": "forest",
        "floresta_elfo": "forest",
        # Mountains
        "montanha": "mountain",
        "picos_nevados": "mountain",
        # Water
        "agua": "water",
        "oceano": "water",
        "rio": "water",
        # Desert
        "deserto": "sand",
        # Snow
        "neve": "snow",
        "tundra": "snow",
        "inverno": "snow",
        # Cave
        "caverna": "cave",
        "caverna_cristal": "cave",
        "mina_anao": "cave",
        # Default
        None: "grass",
    }

    BUILDING_TILES = {
        "wall": "wall_wood",
        "wall_brick": "wall_brick",
        "door": "door_wood",
        "door_metal": "door_metal",
        "window": "window",
        "roof": "roof_wood",
        "floor": "floor_wood",
        "floor_stone": "floor_stone",
    }

    def __init__(self):
        self._sprite_manager = get_sprite_manager()
        self._terrain_cache: dict[Tuple[str, int], pygame.Surface] = {}
        self._seed_variations: dict[Tuple[int, int], int] = {}

    def _get_variation(self, x: int, y: int) -> int:
        """Get consistent variation for a coordinate."""
        if (x, y) not in self._seed_variations:
            self._seed_variations[(x, y)] = ((x * 73856093) ^ (y * 19349663)) % 4
        return self._seed_variations[(x, y)]

    def render_terrain(self, surface: pygame.Surface, rect: pygame.Rect, 
                      bioma: str, x: int, y: int) -> None:
        """Render a terrain tile with sprite or fallback color."""
        sprite_key = self.BIOMA_SPRITES.get(bioma, "grass")
        variation = self._get_variation(x, y)

        # Try to get sprite
        sprite = self._sprite_manager.get_terrain_sprite(sprite_key, variation)
        if sprite:
            render_sprite(surface, sprite, rect, scale=TAMANHO_CELULA / 16)
        else:
            # Fallback rendering
            self._render_terrain_fallback(surface, rect, sprite_key)

    def _render_terrain_fallback(self, surface: pygame.Surface, rect: pygame.Rect, 
                                 terrain_type: str) -> None:
        """Fallback rendering when sprites aren't available."""
        fallback_colors = {
            "grass": ((108, 166, 112), (116, 174, 118)),
            "grass_dark": ((60, 84, 68), (52, 76, 60)),
            "forest": ((34, 139, 34), (40, 122, 72)),
            "mountain": ((96, 88, 96), (148, 144, 154)),
            "water": ((54, 112, 168), (134, 214, 236)),
            "sand": ((184, 168, 112), (212, 196, 150)),
            "cave": ((40, 40, 60), (80, 80, 100)),
            "snow": ((200, 220, 240), (240, 240, 248)),
        }

        if terrain_type in fallback_colors:
            dark, light = fallback_colors[terrain_type]
            if (rect.x + rect.y) % 2 == 0:
                pygame.draw.rect(surface, dark, rect)
            else:
                pygame.draw.rect(surface, light, rect)
        else:
            pygame.draw.rect(surface, (108, 166, 112), rect)

    def render_object(self, surface: pygame.Surface, rect: pygame.Rect, 
                     obj_type: str, variation: int = 0) -> None:
        """Render world objects (trees, rocks, etc)."""
        sprite = self._sprite_manager.get_object_sprite(obj_type, variation)
        if sprite:
            render_sprite(surface, sprite, rect, scale=TAMANHO_CELULA / 16)
        else:
            self._render_object_fallback(surface, rect, obj_type)

    def _render_object_fallback(self, surface: pygame.Surface, rect: pygame.Rect, 
                               obj_type: str) -> None:
        """Fallback rendering for objects."""
        if obj_type == "tree":
            pygame.draw.rect(surface, (128, 90, 52), 
                           pygame.Rect(rect.centerx - 3, rect.centery + 2, 6, 12))
            pygame.draw.circle(surface, (40, 122, 72), (rect.centerx, rect.centery - 1), 11)
        elif obj_type == "rock_large":
            pygame.draw.rect(surface, (96, 88, 96), rect.inflate(-8, -8))
            pygame.draw.rect(surface, (148, 144, 154), rect.inflate(-8, -8), 1)
        elif obj_type == "rock_small":
            pygame.draw.ellipse(surface, (96, 88, 96), rect.inflate(-12, -12))
        elif obj_type == "bush":
            pygame.draw.circle(surface, (40, 122, 72), rect.center, rect.width // 3)

    def render_farm_cell(self, surface: pygame.Surface, rect: pygame.Rect,
                        soil_state: str, plant_type: Optional[str] = None, 
                        growth_stage: int = 0) -> None:
        """Render a farm cell with soil and optional plant."""
        # Render soil
        soil_sprite = self._sprite_manager.get_soil_sprite(soil_state)
        if soil_sprite:
            render_sprite(surface, soil_sprite, rect, scale=TAMANHO_CELULA / 16)
        else:
            self._render_soil_fallback(surface, rect, soil_state)

        # Render plant if present
        if plant_type and plant_type != "none":
            plant_sprite = self._sprite_manager.get_plant_sprite(plant_type, growth_stage)
            if plant_sprite:
                render_sprite(surface, plant_sprite, rect, scale=TAMANHO_CELULA / 16)
            else:
                self._render_plant_fallback(surface, rect, plant_type, growth_stage)

    def _render_soil_fallback(self, surface: pygame.Surface, rect: pygame.Rect, 
                             state: str) -> None:
        """Fallback rendering for soil states."""
        colors = {
            "untilled": (139, 101, 53),
            "tilled": (160, 120, 70),
            "watered": (100, 80, 50),
            "planted": (120, 100, 60),
        }
        color = colors.get(state, (139, 101, 53))
        pygame.draw.rect(surface, color, rect)

        # Add visual indicators
        if state == "watered":
            pygame.draw.circle(surface, (54, 112, 168), rect.center, 3)
        elif state == "planted":
            pygame.draw.circle(surface, (34, 139, 34), rect.center, 2)

    def _render_plant_fallback(self, surface: pygame.Surface, rect: pygame.Rect,
                              plant_type: str, growth_stage: int) -> None:
        """Fallback rendering for plants."""
        plant_colors = {
            "wheat": (184, 168, 112),
            "corn": (200, 180, 80),
            "carrot": (255, 140, 0),
            "tomato": (200, 50, 50),
            "potato": (160, 100, 60),
        }

        color = plant_colors.get(plant_type, (100, 180, 100))
        
        # Size grows with stage
        size = 2 + (growth_stage * 2)
        pygame.draw.circle(surface, color, rect.center, size)

    def render_house(self, surface: pygame.Surface, house: HouseStructure,
                    camera_x: int, camera_y: int, show_interior: bool = False) -> None:
        """Render a house structure using sprites."""
        for tile in house.tiles:
            # Calculate screen position
            sx = (tile.x - camera_x) * TAMANHO_CELULA
            sy = (tile.y - camera_y) * TAMANHO_CELULA
            rect = pygame.Rect(sx, sy, TAMANHO_CELULA, TAMANHO_CELULA)

            # Skip if off-screen
            if rect.right < 0 or rect.left >= surface.get_width():
                continue
            if rect.bottom < 0 or rect.top >= surface.get_height():
                continue

            # Get appropriate sprite
            sprite_key = self.BUILDING_TILES.get(tile.tile_type, "floor")
            if tile.material == "brick":
                sprite_key = sprite_key.replace("wood", "brick")

            sprite = self._sprite_manager.get_building_sprite(house.npc_home or "house", tile.tile_type)
            if sprite:
                render_sprite(surface, sprite, rect, scale=TAMANHO_CELULA / 16)
            else:
                self._render_house_tile_fallback(surface, rect, tile.tile_type, tile.material)

    def _render_house_tile_fallback(self, surface: pygame.Surface, rect: pygame.Rect,
                                   tile_type: str, material: str) -> None:
        """Fallback rendering for house tiles."""
        # Color based on type and material
        color_map = {
            ("wall", "wood"): (139, 101, 53),
            ("wall", "brick"): (180, 100, 70),
            ("wall", "stone"): (160, 160, 160),
            ("door", "wood"): (92, 58, 38),
            ("door", "metal"): (120, 120, 120),
            ("floor", "wood"): (160, 140, 100),
            ("floor", "stone"): (150, 150, 150),
            ("roof", "wood"): (120, 80, 50),
            ("roof", "tile"): (180, 120, 80),
            ("window", None): (124, 180, 210),
        }

        color = color_map.get((tile_type, material), (150, 150, 150))
        pygame.draw.rect(surface, color, rect)

        # Draw borders for walls/structure
        if tile_type in ("wall", "door", "roof"):
            pygame.draw.rect(surface, tuple(min(255, c - 40) for c in color), rect, 1)
        
        # Draw window panes
        if tile_type == "window":
            pygame.draw.line(surface, (100, 100, 150), rect.midtop, rect.midbottom, 1)
            pygame.draw.line(surface, (100, 100, 150), rect.midleft, rect.midright, 1)


class HouseVisualizer:
    """Manages visual representation of houses in the world."""

    def __init__(self):
        self._terrain_renderer = TerrainRenderer()
        self._houses: dict[Tuple[int, int], HouseStructure] = {}

    def add_house(self, origin: Tuple[int, int], house: HouseStructure) -> None:
        """Register a house in the world."""
        self._houses[origin] = house

    def get_house_at(self, x: int, y: int) -> Optional[HouseStructure]:
        """Get house at coordinates."""
        for house in self._houses.values():
            if (house.x <= x < house.x + house.width and
                house.y <= y < house.y + house.height):
                return house
        return None

    def render_all_houses(self, surface: pygame.Surface, 
                         camera_x: int, camera_y: int) -> None:
        """Render all houses in view."""
        for house in self._houses.values():
            self._terrain_renderer.render_house(surface, house, camera_x, camera_y)

    def get_house_interior_description(self, house: HouseStructure) -> str:
        """Get text description of house interior."""
        return f"{house.npc_home or 'House'} Interior - {house.width}x{house.height} with {len(house.interior_cells)} rooms"
