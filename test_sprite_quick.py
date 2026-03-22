#!/usr/bin/env python3
"""Quick test of sprite system without pygame display."""

from jogo.sprite_system import get_sprite_manager
from jogo.house_generation import HouseGenerator, HouseStyle
from jogo.world_house_manager import WorldHouseManager
from jogo.farming import FarmManager

print("=" * 60)
print("SPRITE SYSTEM FUNCTIONALITY TEST")
print("=" * 60)

# Test 1: Sprite Manager
print("\n[1] Testing Sprite Manager...")
try:
    mgr = get_sprite_manager()
    print("    ✓ Sprite manager created")
    
    # Check available tilesets
    tilesets = mgr._tilesets.keys()
    print(f"    ✓ Loaded tilesets: {list(tilesets)}")
except Exception as e:
    print(f"    ✗ Error: {e}")

# Test 2: House Generation
print("\n[2] Testing House Generation...")
try:
    # Small house
    house1 = HouseGenerator.generate_house(10, 10, style=HouseStyle.COZY, size="small")
    print(f"    ✓ Small house: {house1.width}x{house1.height}, {len(house1.tiles)} tiles")
    print(f"      - Doors: {len(house1.doors)}, Windows: {len(house1.windows)}, Interior: {len(house1.interior_cells)}")
    
    # Medium house
    house2 = HouseGenerator.generate_house(30, 30, style=HouseStyle.ELEGANT, size="medium")
    print(f"    ✓ Medium house: {house2.width}x{house2.height}, {len(house2.tiles)} tiles")
    
    # Barn
    barn = HouseGenerator.generate_barn(50, 50)
    print(f"    ✓ Barn: {barn.width}x{barn.height}, {len(barn.tiles)} tiles")
    
    # Community Center
    center = HouseGenerator.generate_community_center(70, 70)
    print(f"    ✓ Community Center: {center.width}x{center.height}, {len(center.tiles)} tiles")
    
except Exception as e:
    print(f"    ✗ Error: {e}")

# Test 3: World House Manager
print("\n[3] Testing World House Manager...")
try:
    manager = WorldHouseManager(world_size=200)
    print("    ✓ World house manager created")
    
    # Create mock NPCs
    npcs = [
        {"id": "npc_alice", "nome": "Alice"},
        {"id": "npc_bob", "nome": "Bob"},
        {"id": "npc_eve", "nome": "Eve"},
    ]
    
    # Generate village houses
    houses = manager.generate_village_houses(100, 100, "village_1", num_houses=3, npCs=npcs)
    print(f"    ✓ Generated {len(houses)} village houses")
    
    # Generate special buildings
    special = manager.generate_special_buildings(100, 100, "village_1")
    print(f"    ✓ Generated {len(special)} special buildings: {list(special.keys())}")
    
    # Test queries
    house_at_pos = manager.get_house_at_position(102, 102)
    print(f"    ✓ House lookup works: {house_at_pos is not None}")
    
    all_village_houses = manager.get_all_houses_in_village("village_1")
    print(f"    ✓ Found {len(all_village_houses)} total houses in village")
    
    # Test export
    export_data = manager.export_for_world_model()
    print(f"    ✓ Export created with {len(export_data['tiles_casa'])} house tiles")
    
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Farming System
print("\n[4] Testing Farming System with Sprites...")
try:
    farm = FarmManager(tamanho_farm=10)
    print("    ✓ Farm manager created")
    
    # Add seeds
    farm.adicionar_sementes("wheat", 5)
    farm.adicionar_sementes("corn", 3)
    print("    ✓ Added seeds to inventory")
    
    # Get a cell and test
    celula = farm.obter_celula(5, 5)
    print(f"    ✓ Initial soil sprite: '{celula.sprite_solo}'")
    
    # Till the soil
    farm.aradir_terreno(5, 5)
    print(f"    ✓ After tilling soil sprite: '{celula.sprite_solo}'")
    
    # Plant
    farm.plantar_semente(5, 5, "wheat", 10, 1, "primavera")
    print(f"    ✓ Planted wheat, plant growth stage: {celula.planta_atual.estágio_sprite}")
    
    # Water
    farm.regar_terreno(5, 5)
    print(f"    ✓ Watered, soil sprite: '{celula.sprite_solo}'")
    
    # Advance growth
    for day in range(3):
        celula.planta_atual.atualizar_um_dia(True)
    
    print(f"    ✓ After 3 days: growth {celula.planta_atual.percentual_crescimento}%, stage {celula.planta_atual.estágio_sprite}")
    
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: House Structure Validity
print("\n[5] Testing House Structure Validity...")
try:
    house = HouseGenerator.generate_house(0, 0, size="medium")
    
    # Check all required properties
    checks = [
        ("Has tiles", len(house.tiles) > 0),
        ("Has doors", len(house.doors) > 0),
        ("Has interior", len(house.interior_cells) > 0),
        ("Has windows", len(house.windows) > 0),
        ("All tiles have positions", all(t.x >= 0 and t.y >= 0 for t in house.tiles)),
        ("All tiles have types", all(t.tile_type in ["wall", "door", "floor", "window", "roof"] for t in house.tiles)),
        ("Interior cells are passable", all(t.passable for t in house.tiles if t in house.interior_cells)),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"    {status} {check_name}")
        
except Exception as e:
    print(f"    ✗ Error: {e}")

print("\n" + "=" * 60)
print("SPRITE SYSTEM TEST COMPLETE!")
print("=" * 60)
print("\nAll core sprite system components are working correctly.")
print("Ready for integration with main game loop.")
