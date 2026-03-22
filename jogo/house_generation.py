"""Stardew Valley-like house generation system with walls, doors, and interiors."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import pygame
from enum import Enum


class HouseStyle(Enum):
    """Different house styles available."""
    RUSTIC = "rustic"
    COZY = "cozy"
    ELEGANT = "elegant"
    MODEST = "modest"


@dataclass
class HouseTile:
    """Represents a single tile in a house structure."""
    x: int
    y: int
    tile_type: str  # 'wall', 'floor', 'door', 'window', 'roof', 'corner'
    material: str  # 'wood', 'brick', 'stone', 'thatch'
    passable: bool = False
    is_entrance: bool = False


@dataclass
class HouseStructure:
    """Represents a complete house structure."""
    x: int
    y: int
    width: int
    height: int
    style: HouseStyle
    tiles: List[HouseTile]
    doors: List[Tuple[int, int]]  # Door positions for entering/exiting
    windows: List[Tuple[int, int]]  # Window positions
    interior_cells: List[Tuple[int, int]]  # Interior tile positions (for pathfinding)
    npc_home: Optional[str] = None  # NPC that lives here


class HouseGenerator:
    """Generates Stardew Valley-like house structures."""

    # House templates (relative coordinates from origin)
    SMALL_HOUSE = {
        "width": 4,
        "height": 4,
        "template": [
            # Top row (roof)
            ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)),
            # Sides with top wall
            ("wall", (0, 1)), ("wall", (1, 1)), ("wall", (2, 1)), ("wall", (3, 1)),
            # Middle interior
            ("floor", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)),
            # Bottom row with door
            ("wall", (0, 3)), ("door", (1, 3)), ("door", (2, 3)), ("wall", (3, 3)),
        ]
    }

    MEDIUM_HOUSE = {
        "width": 6,
        "height": 5,
        "template": [
            # Roof
            ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)), ("roof", (4, 0)), ("roof", (5, 0)),
            # Top walls
            ("wall", (0, 1)), ("window", (1, 1)), ("window", (2, 1)), ("window", (3, 1)), ("window", (4, 1)), ("wall", (5, 1)),
            # Middle-upper interior
            ("wall", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)), ("floor", (4, 2)), ("wall", (5, 2)),
            # Middle-lower interior
            ("wall", (0, 3)), ("floor", (1, 3)), ("floor", (2, 3)), ("floor", (3, 3)), ("floor", (4, 3)), ("wall", (5, 3)),
            # Bottom with doors
            ("wall", (0, 4)), ("door", (1, 4)), ("door", (2, 4)), ("floor", (3, 4)), ("door", (4, 4)), ("wall", (5, 4)),
        ]
    }

    LARGE_HOUSE = {
        "width": 8,
        "height": 6,
        "template": [
            # Roof row
            ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)),
            ("roof", (4, 0)), ("roof", (5, 0)), ("roof", (6, 0)), ("roof", (7, 0)),
            # Top walls & windows
            ("wall", (0, 1)), ("window", (1, 1)), ("window", (2, 1)), ("wall", (3, 1)),
            ("wall", (4, 1)), ("window", (5, 1)), ("window", (6, 1)), ("wall", (7, 1)),
            # Upper interior
            ("wall", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)),
            ("floor", (4, 2)), ("floor", (5, 2)), ("floor", (6, 2)), ("wall", (7, 2)),
            # Middle interior
            ("wall", (0, 3)), ("floor", (1, 3)), ("floor", (2, 3)), ("floor", (3, 3)),
            ("floor", (4, 3)), ("floor", (5, 3)), ("floor", (6, 3)), ("wall", (7, 3)),
            # Lower interior with furniture space
            ("wall", (0, 4)), ("floor", (1, 4)), ("floor", (2, 4)), ("floor", (3, 4)),
            ("floor", (4, 4)), ("floor", (5, 4)), ("floor", (6, 4)), ("wall", (7, 4)),
            # Bottom doors
            ("wall", (0, 5)), ("door", (1, 5)), ("door", (2, 5)), ("floor", (3, 5)),
            ("floor", (4, 5)), ("door", (5, 5)), ("door", (6, 5)), ("wall", (7, 5)),
        ]
    }

    CABIN = {
        "width": 5,
        "height": 4,
        "template": [
            # Roof
            ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)), ("roof", (4, 0)),
            # Top wall
            ("wall", (0, 1)), ("window", (1, 1)), ("window", (2, 1)), ("window", (3, 1)), ("wall", (4, 1)),
            # Interior
            ("wall", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)), ("wall", (4, 2)),
            # Bottom with door
            ("wall", (0, 3)), ("floor", (1, 3)), ("door", (2, 3)), ("floor", (3, 3)), ("wall", (4, 3)),
        ]
    }

    @staticmethod
    def generate_house(x: int, y: int, style: HouseStyle = HouseStyle.COZY,
                       size: str = "small", npc_home: Optional[str] = None) -> HouseStructure:
        """Generate a house structure.
        
        Args:
            x: World X coordinate for house origin
            y: World Y coordinate for house origin
            style: House style (rustic, cozy, elegant, modest)
            size: House size (small, medium, large, cabin)
            npc_home: Optional NPC name for this house
        
        Returns:
            HouseStructure with all tiles configured
        """
        # Select template based on size
        template_map = {
            "small": HouseGenerator.SMALL_HOUSE,
            "medium": HouseGenerator.MEDIUM_HOUSE,
            "large": HouseGenerator.LARGE_HOUSE,
            "cabin": HouseGenerator.CABIN,
        }

        template = template_map.get(size, HouseGenerator.SMALL_HOUSE)
        width = template["width"]
        height = template["height"]

        # Map style to material
        material_map = {
            HouseStyle.RUSTIC: "wood",
            HouseStyle.COZY: "wood",
            HouseStyle.ELEGANT: "brick",
            HouseStyle.MODEST: "stone",
        }
        material = material_map.get(style, "wood")

        # Generate tiles from template
        tiles = []
        doors: List[Tuple[int, int]] = []
        windows: List[Tuple[int, int]] = []
        interior_cells: List[Tuple[int, int]] = []

        for tile_type, (tx, ty) in template["template"]:
            house_x = x + tx
            house_y = y + ty
            passable = tile_type in {"floor", "door"}

            tile = HouseTile(
                x=house_x,
                y=house_y,
                tile_type=tile_type,
                material=material,
                passable=passable,
                is_entrance=(tile_type == "door")
            )
            tiles.append(tile)

            if tile_type == "door":
                doors.append((house_x, house_y))
            elif tile_type == "window":
                windows.append((house_x, house_y))
            elif tile_type == "floor":
                interior_cells.append((house_x, house_y))

        house = HouseStructure(
            x=x,
            y=y,
            width=width,
            height=height,
            style=style,
            tiles=tiles,
            doors=doors,
            windows=windows,
            interior_cells=interior_cells,
            npc_home=npc_home
        )

        return house

    @staticmethod
    def generate_barn(x: int, y: int) -> HouseStructure:
        """Generate a farm barn structure."""
        barn_template = {
            "width": 7,
            "height": 4,
            "template": [
                ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)), ("roof", (4, 0)), ("roof", (5, 0)), ("roof", (6, 0)),
                ("wall", (0, 1)), ("window", (1, 1)), ("floor", (2, 1)), ("floor", (3, 1)), ("floor", (4, 1)), ("window", (5, 1)), ("wall", (6, 1)),
                ("wall", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)), ("floor", (4, 2)), ("floor", (5, 2)), ("wall", (6, 2)),
                ("wall", (0, 3)), ("door", (1, 3)), ("floor", (2, 3)), ("floor", (3, 3)), ("floor", (4, 3)), ("door", (5, 3)), ("wall", (6, 3)),
            ]
        }

        tiles = []
        doors: List[Tuple[int, int]] = []
        interior_cells: List[Tuple[int, int]] = []

        for tile_type, (tx, ty) in barn_template["template"]:
            house_x = x + tx
            house_y = y + ty
            passable = tile_type in {"floor", "door"}

            tile = HouseTile(
                x=house_x,
                y=house_y,
                tile_type=tile_type,
                material="wood",
                passable=passable,
                is_entrance=(tile_type == "door")
            )
            tiles.append(tile)

            if tile_type == "door":
                doors.append((house_x, house_y))
            elif tile_type == "floor":
                interior_cells.append((house_x, house_y))

        return HouseStructure(
            x=x,
            y=y,
            width=barn_template["width"],
            height=barn_template["height"],
            style=HouseStyle.RUSTIC,
            tiles=tiles,
            doors=doors,
            windows=[],
            interior_cells=interior_cells,
            npc_home="Barn"
        )

    @staticmethod
    def generate_community_center(x: int, y: int) -> HouseStructure:
        """Generate a community center structure."""
        center_template = {
            "width": 10,
            "height": 7,
            "template": [
                # Roof
                ("roof", (0, 0)), ("roof", (1, 0)), ("roof", (2, 0)), ("roof", (3, 0)), ("roof", (4, 0)),
                ("roof", (5, 0)), ("roof", (6, 0)), ("roof", (7, 0)), ("roof", (8, 0)), ("roof", (9, 0)),
                # Top wall with windows
                ("wall", (0, 1)), ("window", (1, 1)), ("window", (2, 1)), ("wall", (3, 1)), ("wall", (4, 1)),
                ("wall", (5, 1)), ("window", (6, 1)), ("window", (7, 1)), ("window", (8, 1)), ("wall", (9, 1)),
                # Upper interior
                ("wall", (0, 2)), ("floor", (1, 2)), ("floor", (2, 2)), ("floor", (3, 2)), ("floor", (4, 2)),
                ("floor", (5, 2)), ("floor", (6, 2)), ("floor", (7, 2)), ("floor", (8, 2)), ("wall", (9, 2)),
                # Middle interior
                ("wall", (0, 3)), ("floor", (1, 3)), ("floor", (2, 3)), ("floor", (3, 3)), ("floor", (4, 3)),
                ("floor", (5, 3)), ("floor", (6, 3)), ("floor", (7, 3)), ("floor", (8, 3)), ("wall", (9, 3)),
                # Lower middle interior
                ("wall", (0, 4)), ("floor", (1, 4)), ("floor", (2, 4)), ("floor", (3, 4)), ("floor", (4, 4)),
                ("floor", (5, 4)), ("floor", (6, 4)), ("floor", (7, 4)), ("floor", (8, 4)), ("wall", (9, 4)),
                # Seating area
                ("wall", (0, 5)), ("floor", (1, 5)), ("floor", (2, 5)), ("floor", (3, 5)), ("floor", (4, 5)),
                ("floor", (5, 5)), ("floor", (6, 5)), ("floor", (7, 5)), ("floor", (8, 5)), ("wall", (9, 5)),
                # Bottom with large doors
                ("wall", (0, 6)), ("door", (1, 6)), ("door", (2, 6)), ("door", (3, 6)), ("door", (4, 6)),
                ("door", (5, 6)), ("door", (6, 6)), ("door", (7, 6)), ("door", (8, 6)), ("wall", (9, 6)),
            ]
        }

        tiles = []
        doors: List[Tuple[int, int]] = []
        interior_cells: List[Tuple[int, int]] = []

        for tile_type, (tx, ty) in center_template["template"]:
            house_x = x + tx
            house_y = y + ty
            passable = tile_type in {"floor", "door"}

            tile = HouseTile(
                x=house_x,
                y=house_y,
                tile_type=tile_type,
                material="brick",
                passable=passable,
                is_entrance=(tile_type == "door")
            )
            tiles.append(tile)

            if tile_type == "door":
                doors.append((house_x, house_y))
            elif tile_type == "floor":
                interior_cells.append((house_x, house_y))

        return HouseStructure(
            x=x,
            y=y,
            width=center_template["width"],
            height=center_template["height"],
            style=HouseStyle.ELEGANT,
            tiles=tiles,
            doors=doors,
            windows=[],
            interior_cells=interior_cells,
            npc_home="Community Center"
        )


def is_point_in_house(x: int, y: int, house: HouseStructure) -> bool:
    """Check if a point is inside a house structure."""
    return (house.x <= x < house.x + house.width and
            house.y <= y < house.y + house.height)


def can_enter_house(x: int, y: int, house: HouseStructure) -> bool:
    """Check if a point is a valid door entrance."""
    return (x, y) in house.doors
