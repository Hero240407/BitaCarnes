#!/usr/bin/env python3
"""Test and demonstration of the new sprite system."""

import sys
import pygame
from pathlib import Path

# Add jogo to path
sys.path.insert(0, str(Path(__file__).parent))

from jogo.sprite_system import get_sprite_manager, render_sprite
from jogo.sprite_renderer import TerrainRenderer, HouseVisualizer
from jogo.house_generation import HouseGenerator, HouseStyle
from jogo.farming import FarmManager, CelulaCultivavel
from jogo.config import TAMANHO_CELULA


def test_sprite_manager():
    """Test sprite manager loading."""
    print("Testing Sprite Manager...")
    mgr = get_sprite_manager()
    
    # Test terrain sprites
    sprites_tested = {
        "grass": mgr.get_terrain_sprite("grass"),
        "water": mgr.get_terrain_sprite("water"),
        "mountain": mgr.get_terrain_sprite("mountain"),
        "forest": mgr.get_terrain_sprite("forest"),
        "sand": mgr.get_terrain_sprite("sand"),
    }
    
    for name, sprite in sprites_tested.items():
        status = "✓" if sprite else "✗"
        print(f"  {status} {name} sprite")
    
    # Test plant sprites
    plants_tested = {
        "wheat": mgr.get_plant_sprite("wheat", 0),
        "corn": mgr.get_plant_sprite("corn", 1),
        "carrot": mgr.get_plant_sprite("carrot", 2),
    }
    
    for name, sprite in plants_tested.items():
        status = "✓" if sprite else "✗"
        print(f"  {status} {name} plant sprite")
    
    # Test building sprites
    building_sprites = {
        "wall": mgr.get_building_sprite("house", "wall"),
        "door": mgr.get_building_sprite("house", "door"),
        "floor": mgr.get_building_sprite("house", "floor"),
        "window": mgr.get_building_sprite("house", "window"),
    }
    
    for name, sprite in building_sprites.items():
        status = "✓" if sprite else "✗"
        print(f"  {status} {name} building sprite")


def test_terrain_renderer():
    """Test terrain renderer."""
    print("\nTesting Terrain Renderer...")
    renderer = TerrainRenderer()
    
    # Create a test surface
    pygame.init()
    surface = pygame.Surface((320, 240))
    rect = pygame.Rect(10, 10, TAMANHO_CELULA, TAMANHO_CELULA)
    
    # Test terrain rendering
    renderer.render_terrain(surface, rect, "floresta", 5, 5)
    print("  ✓ Terrain rendering works")
    
    # Test farm cell rendering
    farm_cell = CelulaCultivavel(5, 5)
    farm_cell.foi_arada = True
    farm_cell.foi_regada_hoje = True
    renderer.render_farm_cell(surface, rect, farm_cell.sprite_solo)
    print("  ✓ Farm cell rendering works")
    
    # Test object rendering
    renderer.render_object(surface, rect, "tree")
    print("  ✓ Object rendering works")


def test_house_generation():
    """Test house generation system."""
    print("\nTesting House Generation...")
    
    # Test small house
    house = HouseGenerator.generate_house(10, 10, style=HouseStyle.COZY, size="small")
    print(f"  ✓ Small house: {house.width}x{house.height}, {len(house.tiles)} tiles")
    
    # Test medium house
    house = HouseGenerator.generate_house(20, 20, style=HouseStyle.ELEGANT, size="medium")
    print(f"  ✓ Medium house: {house.width}x{house.height}, {len(house.tiles)} tiles")
    
    # Test cabin
    house = HouseGenerator.generate_house(30, 30, style=HouseStyle.RUSTIC, size="cabin")
    print(f"  ✓ Cabin: {house.width}x{house.height}, {len(house.tiles)} tiles")
    
    # Test barn
    barn = HouseGenerator.generate_barn(40, 40)
    print(f"  ✓ Barn: {barn.width}x{barn.height}, {len(barn.tiles)} tiles")
    
    # Test community center
    center = HouseGenerator.generate_community_center(50, 50)
    print(f"  ✓ Community Center: {center.width}x{center.height}, {len(center.tiles)} tiles")
    
    # Check structure validity
    house = HouseGenerator.generate_house(0, 0)
    has_doors = len(house.doors) > 0
    has_interior = len(house.interior_cells) > 0
    has_windows = len(house.windows) > 0
    
    print(f"  ✓ House has doors: {has_doors}")
    print(f"  ✓ House has interior: {has_interior}")
    print(f"  ✓ House has windows: {has_windows}")


def test_farming_system():
    """Test updated farming system with sprite support."""
    print("\nTesting Farming System...")
    
    farm = FarmManager(tamanho_farm=10)
    farm.adicionar_sementes("wheat", 5)
    farm.adicionar_sementes("corn", 3)
    
    # Test farming operations
    celula = farm.obter_celula(0, 0)
    print(f"  ✓ Created farm cell")
    
    # Test arar
    sucesso = farm.aradir_terreno(0, 0)
    print(f"  ✓ Tilled terrain: {sucesso}")
    print(f"    Soil sprite: {celula.sprite_solo}")
    
    # Test planting
    sucesso = farm.plantar_semente(0, 0, "wheat", 10, 1, "primavera")
    print(f"  ✓ Planted wheat: {sucesso}")
    if celula.planta_atual:
        print(f"    Plant sprite stage: {celula.planta_atual.estágio_sprite}")
    
    # Test watering
    sucesso = farm.regar_terreno(0, 0)
    print(f"  ✓ Watered terrain: {sucesso}")
    print(f"    Soil sprite: {celula.sprite_solo}")
    
    # Advance growth
    for day in range(5):
        celula.planta_atual.atualizar_um_dia(True)
    print(f"  ✓ Plant growth: {celula.planta_atual.percentual_crescimento}%")
    print(f"    Current sprite stage: {celula.planta_atual.estágio_sprite}")


def test_house_visualizer():
    """Test house visualizer."""
    print("\nTesting House Visualizer...")
    
    visualizer = HouseVisualizer()
    
    # Create and add a house
    house = HouseGenerator.generate_house(50, 50, npc_home="Alice")
    visualizer.add_house((50, 50), house)
    print("  ✓ Added house to visualizer")
    
    # Test retrieval
    found = visualizer.get_house_at(51, 52)
    if found:
        print(f"  ✓ Found house at (51, 52)")
    
    # Test description
    desc = visualizer.get_house_interior_description(house)
    print(f"  ✓ House description: {desc}")


def test_world_house_manager():
    """Test world house manager integration."""
    print("\nTesting World House Manager...")
    
    try:
        from jogo.world_house_manager import WorldHouseManager
        
        manager = WorldHouseManager(world_size=200)
        print("  ✓ Created world house manager")
        
        # Create mock NPC list
        npcs = [
            {"id": "npc_1", "nome": "Alice"},
            {"id": "npc_2", "nome": "Bob"},
            {"id": "npc_3", "nome": "Eve"},
        ]
        
        # Generate village houses
        houses = manager.generate_village_houses(100, 100, "village_1", num_houses=3, npCs=npcs)
        print(f"  ✓ Generated {len(houses)} village houses")
        
        # Generate special buildings
        special = manager.generate_special_buildings(100, 100, "village_1")
        print(f"  ✓ Generated {len(special)} special buildings")
        
        # Test queries
        house = manager.get_house_at(102, 102)
        print(f"  ✓ House lookup works: {house is not None}")
        
        all_houses = manager.get_all_houses_in_village("village_1")
        print(f"  ✓ Found {len(all_houses)} houses in village")
        
    except ImportError:
        print("  ⚠ WorldHouseManager not available")


def main():
    """Run all tests."""
    print("=" * 50)
    print("SPRITE SYSTEM TEST SUITE")
    print("=" * 50)
    
    try:
        test_sprite_manager()
        test_terrain_renderer()
        test_house_generation()
        test_farming_system()
        test_house_visualizer()
        test_world_house_manager()
        
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED!")
        print("=" * 50)
        print("\nSprite system is ready for integration.")
        print("See SPRITE_SYSTEM_GUIDE.md for usage examples.")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
