"""Advanced sprite system using Kenney assets and mana-seed-farmer sprites."""

from __future__ import annotations
from pathlib import Path
import pygame
from functools import lru_cache
from typing import Optional, Tuple


RAIZ_SPRITES = Path(__file__).resolve().parent.parent / "sprites"


class SpriteManager:
    """Manages sprite loading, caching, and retrieval from Kenney asset packs."""

    def __init__(self):
        self._cache: dict[str, pygame.Surface] = {}
        self._tilesets: dict[str, pygame.Surface] = {}
        self._load_tilesets()

    def _load_tilesets(self) -> None:
        """Load all available tilesets from sprite packs."""
        # 1-bit pack - Simple, retro style
        try:
            path = RAIZ_SPRITES / "kenney_1-bit-pack" / "Tilemap" / "tileset_legacy.png"
            if path.exists():
                self._tilesets["1bit_legacy"] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Warning: Could not load 1-bit legacy tileset: {e}")

        # Pico-8 city pack - Urban environments
        try:
            path = RAIZ_SPRITES / "kenney_pico-8-city" / "Tilemap" / "tilemap.png"
            if path.exists():
                self._tilesets["pico8_city"] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Warning: Could not load pico-8 city tileset: {e}")

        # Roguelike indoors - Building interiors and structures
        try:
            path = RAIZ_SPRITES / "kenney_roguelike-indoors" / "Tilesheets" / "roguelikeIndoor_transparent.png"
            if path.exists():
                self._tilesets["roguelike_indoors"] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Warning: Could not load roguelike indoors tileset: {e}")

    def get_sprite(self, tileset: str, x: int, y: int, tile_width: int = 16, tile_height: int = 16) -> Optional[pygame.Surface]:
        """Get a specific sprite from a tileset by grid coordinates."""
        if tileset not in self._tilesets:
            return None

        tilesheet = self._tilesets[tileset]
        rect = pygame.Rect(x * (tile_width + 1), y * (tile_height + 1), tile_width, tile_height)
        sprite = tilesheet.subsurface(rect).copy()
        return sprite

    def get_terrain_sprite(self, terrain_type: str, variation: int = 0) -> Optional[pygame.Surface]:
        """Get terrain sprite for different biome types.
        
        Args:
            terrain_type: Type of terrain (grass, forest, mountain, water, sand, snow)
            variation: Visual variation 0-3
        
        Returns:
            Pygame surface or None
        """
        terrain_sprites = {
            "grass": (1, 1, "1bit_legacy"),
            "grass_dark": (2, 1, "1bit_legacy"),
            "forest": (3, 1, "1bit_legacy"),
            "mountain": (5, 1, "1bit_legacy"),
            "water": (8, 0, "1bit_legacy"),
            "sand": (13, 1, "1bit_legacy"),
            "cave": (23, 1, "1bit_legacy"),
            "snow": (32, 1, "1bit_legacy"),
        }

        if terrain_type not in terrain_sprites:
            return None

        x, y, tileset = terrain_sprites[terrain_type]
        x += variation % 3  # Use variation to pick adjacent tiles
        return self.get_sprite(tileset, x, y, tile_width=16, tile_height=16)

    def get_building_sprite(self, building_type: str, part: str = "wall") -> Optional[pygame.Surface]:
        """Get building sprites for Stardew Valley-like houses.
        
        Args:
            building_type: Type (house, cabin, barn, coop)
            part: Wall, floor, door, roof, corner, etc
        
        Returns:
            Pygame surface or None
        """
        # Building tiles from roguelike indoor tileset
        building_sprites = {
            "wall_wood": (4, 0, 16, 16),
            "wall_brick": (5, 0, 16, 16),
            "floor_wood": (2, 2, 16, 16),
            "floor_stone": (3, 2, 16, 16),
            "door_wood": (7, 1, 16, 16),
            "door_metal": (8, 1, 16, 16),
            "roof_wood": (10, 10, 16, 16),
            "roof_tile": (11, 10, 16, 16),
            "window": (6, 2, 16, 16),
            "corner": (9, 0, 16, 16),
        }

        key = f"{building_type}_{part}"
        if key in building_sprites:
            x, y, w, h = building_sprites[key]
            sprite = self.get_sprite("roguelike_indoors", x, y, tile_width=w, tile_height=h)
            return sprite

        return None

    def get_plant_sprite(self, plant_type: str, growth_stage: int = 0) -> Optional[pygame.Surface]:
        """Get plant sprites for farming.
        
        Args:
            plant_type: Type (wheat, corn, carrot, tomato, etc)
            growth_stage: 0 (seed), 1 (sprout), 2 (growing), 3 (ready)
        
        Returns:
            Pygame surface or None
        """
        plant_sprites = {
            "wheat": {
                0: (14, 2),  # seed
                1: (15, 2),  # sprout
                2: (16, 2),  # growing
                3: (17, 2),  # ready harvest
            },
            "corn": {
                0: (14, 3),
                1: (15, 3),
                2: (16, 3),
                3: (17, 3),
            },
            "carrot": {
                0: (14, 4),
                1: (15, 4),
                2: (16, 4),
                3: (17, 4),
            },
            "tomato": {
                0: (14, 5),
                1: (15, 5),
                2: (16, 5),
                3: (17, 5),
            },
            "potato": {
                0: (14, 6),
                1: (15, 6),
                2: (16, 6),
                3: (17, 6),
            },
        }

        growth_stage = max(0, min(3, growth_stage))
        if plant_type in plant_sprites and growth_stage in plant_sprites[plant_type]:
            x, y = plant_sprites[plant_type][growth_stage]
            sprite = self.get_sprite("1bit_legacy", x, y, tile_width=16, tile_height=16)
            return sprite

        # Fallback: return a colored rectangle
        return None

    def get_soil_sprite(self, soil_state: str) -> Optional[pygame.Surface]:
        """Get soil/farm tile sprites.
        
        Args:
            soil_state: 'untilled', 'tilled', 'watered', 'planted'
        
        Returns:
            Pygame surface or None
        """
        soil_sprites = {
            "untilled": (12, 1),
            "tilled": (13, 1),
            "watered": (14, 1),
            "planted": (15, 1),
        }

        if soil_state in soil_sprites:
            x, y = soil_sprites[soil_state]
            sprite = self.get_sprite("1bit_legacy", x, y, tile_width=16, tile_height=16)
            return sprite

        return None

    def get_object_sprite(self, obj_type: str, variation: int = 0) -> Optional[pygame.Surface]:
        """Get various world object sprites.
        
        Args:
            obj_type: Type (tree, rock, bush, chest, etc)
            variation: Different appearance variations
        
        Returns:
            Pygame surface or None
        """
        object_sprites = {
            "tree": (20, 1),
            "rock_large": (21, 1),
            "rock_small": (22, 1),
            "bush": (23, 2),
            "chest": (24, 1),
            "torch": (25, 1),
            "bed": (26, 2),
            "table": (27, 2),
        }

        if obj_type in object_sprites:
            x, y = object_sprites[obj_type]
            x += variation % 2  # Some objects have variations
            sprite = self.get_sprite("1bit_legacy", x, y, tile_width=16, tile_height=16)
            return sprite

        return None


# Global sprite manager instance
_sprite_manager: Optional[SpriteManager] = None


def get_sprite_manager() -> SpriteManager:
    """Get or create the global sprite manager."""
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager


def render_sprite(surface: pygame.Surface, sprite: Optional[pygame.Surface], 
                 rect: pygame.Rect, scale: float = 1.0) -> None:
    """Render a sprite to a surface with optional scaling."""
    if sprite is None:
        return

    if scale != 1.0:
        new_size = (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
        sprite = pygame.transform.scale(sprite, new_size)

    target_rect = pygame.Rect(
        rect.x + (rect.width - sprite.get_width()) // 2,
        rect.y + (rect.height - sprite.get_height()) // 2,
        sprite.get_width(),
        sprite.get_height()
    )
    surface.blit(sprite, target_rect)
