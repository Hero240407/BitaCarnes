"""World house generation integration - creates Stardew Valley-like houses in the world."""

from __future__ import annotations
from typing import Optional, List, Dict, Tuple
import random
from dataclasses import dataclass
from .house_generation import HouseGenerator, HouseStructure, HouseStyle


@dataclass
class WorldHouseData:
    """Data about a house placed in the world."""
    origin: Tuple[int, int]
    structure: HouseStructure
    npc_residents: List[str]  # NPC IDs living here
    village_id: str
    unique_id: str


class WorldHouseManager:
    """Manages house generation and placement in the world."""

    def __init__(self, world_size: int):
        self.world_size = world_size
        self.houses: Dict[str, WorldHouseData] = {}
        self.house_tiles: set[Tuple[int, int]] = set()  # All tiles occupied by houses
        self.house_doors: Dict[Tuple[int, int], str] = {}  # Door position -> House ID
        self.npc_house_map: Dict[str, str] = {}  # NPC ID -> House ID

    def generate_village_houses(self, vil_x: int, vil_y: int, vila_id: str, 
                              num_houses: int = 3, npCs: Optional[List] = None) -> List[WorldHouseData]:
        """Generate a cluster of houses for a village.
        
        Args:
            vil_x: Village center X
            vil_y: Village center Y
            vila_id: Village identifier
            num_houses: Number of houses to generate
            npCs: Optional list of NPC data to assign homes
        
        Returns:
            List of generated WorldHouseData
        """
        generated_houses = []
        npcs = npCs or []
        npc_index = 0

        # Generate houses in a circle around village center
        styles = list(HouseStyle)
        sizes = ["small", "medium", "small", "cabin", "small"]  # Mix of sizes

        for i in range(num_houses):
            if npc_index >= len(npcs):
                break

            # Calculate position around village (roughly circular)
            angle = (360 / num_houses) * i
            import math
            distance = 3 + random.randint(0, 2)
            hx = int(vil_x + distance * math.cos(math.radians(angle)))
            hy = int(vil_y + distance * math.sin(math.radians(angle)))

            # Clamp to world bounds
            hx = max(0, min(self.world_size - 1, hx))
            hy = max(0, min(self.world_size - 1, hy))

            # Check if position is valid (no overlaps)
            if not self._can_place_house(hx, hy, 8, 6):
                continue

            # Generate house structure
            style = random.choice(styles)
            size = sizes[i % len(sizes)]
            house = HouseGenerator.generate_house(
                hx, hy, 
                style=style, 
                size=size,
                npc_home=f"{npcs[npc_index]['nome']}'s Home" if npc_index < len(npcs) else None
            )

            # Register house
            house_id = f"{vila_id}_house_{i}"
            house_data = WorldHouseData(
                origin=(hx, hy),
                structure=house,
                npc_residents=[npcs[npc_index]['id']] if npc_index < len(npcs) else [],
                village_id=vila_id,
                unique_id=house_id
            )

            self.houses[house_id] = house_data
            self._register_house_tiles(house)

            # Map NPC to house
            if npc_index < len(npcs):
                self.npc_house_map[npcs[npc_index]['id']] = house_id

            generated_houses.append(house_data)
            npc_index += 1

        return generated_houses

    def generate_special_buildings(self, vil_x: int, vil_y: int, 
                                  vila_id: str) -> Dict[str, WorldHouseData]:
        """Generate special buildings like barn and community center.
        
        Returns:
            Dictionary of {building_id: WorldHouseData}
        """
        special_buildings = {}

        # Barn - typically 2-3 tiles away
        barn_x = vil_x + 5
        barn_y = vil_y
        barn_x = max(0, min(self.world_size - 1, barn_x))
        barn_y = max(0, min(self.world_size - 1, barn_y))

        if self._can_place_house(barn_x, barn_y, 8, 5):
            barn = HouseGenerator.generate_barn(barn_x, barn_y)
            barn_id = f"{vila_id}_barn"
            barn_data = WorldHouseData(
                origin=(barn_x, barn_y),
                structure=barn,
                npc_residents=[],
                village_id=vila_id,
                unique_id=barn_id
            )
            self.houses[barn_id] = barn_data
            self._register_house_tiles(barn)
            special_buildings["barn"] = barn_data

        # Community center - large, central building
        if random.random() < 0.6:
            center_x = vil_x
            center_y = vil_y - 5
            center_x = max(0, min(self.world_size - 1, center_x))
            center_y = max(0, min(self.world_size - 1, center_y))

            if self._can_place_house(center_x, center_y, 10, 8):
                center = HouseGenerator.generate_community_center(center_x, center_y)
                center_id = f"{vila_id}_community_center"
                center_data = WorldHouseData(
                    origin=(center_x, center_y),
                    structure=center,
                    npc_residents=[],
                    village_id=vila_id,
                    unique_id=center_id
                )
                self.houses[center_id] = center_data
                self._register_house_tiles(center)
                special_buildings["community_center"] = center_data

        return special_buildings

    def _can_place_house(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if a house can be placed at position."""
        for hx in range(x, min(self.world_size, x + width)):
            for hy in range(y, min(self.world_size, y + height)):
                if (hx, hy) in self.house_tiles:
                    return False
        return True

    def _register_house_tiles(self, house: HouseStructure) -> None:
        """Register all tiles occupied by a house."""
        for tile in house.tiles:
            self.house_tiles.add((tile.x, tile.y))
            if tile.is_entrance:
                self.house_doors[(tile.x, tile.y)] = house.npc_home or "House"

    def get_house_by_npc(self, npc_id: str) -> Optional[WorldHouseData]:
        """Get the house where an NPC lives."""
        house_id = self.npc_house_map.get(npc_id)
        return self.houses.get(house_id) if house_id else None

    def get_house_at_position(self, x: int, y: int) -> Optional[WorldHouseData]:
        """Get house at a specific position."""
        for house_data in self.houses.values():
            if (house_data.structure.x <= x < house_data.structure.x + house_data.structure.width and
                house_data.structure.y <= y < house_data.structure.y + house_data.structure.height):
                return house_data
        return None

    def is_door_position(self, x: int, y: int) -> bool:
        """Check if position is a house door."""
        return (x, y) in self.house_doors

    def get_door_house_name(self, x: int, y: int) -> Optional[str]:
        """Get house name from door position."""
        return self.house_doors.get((x, y))

    def get_all_houses_in_village(self, vila_id: str) -> List[WorldHouseData]:
        """Get all houses in a specific village."""
        return [h for h in self.houses.values() if h.village_id == vila_id]

    def export_for_world_model(self) -> Dict[str, set[Tuple[int, int]]]:
        """Export data in format compatible with Mundo world model.
        
        Returns:
            Dictionary with 'tiles_casa' and 'house_doors' sets
        """
        return {
            "tiles_casa": self.house_tiles.copy(),
            "house_doors": self.house_doors.copy(),
        }
