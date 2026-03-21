#!/usr/bin/env python3
"""Test script to validate improved world generation without pygame."""

import sys
import json

# Add jogo module to path
sys.path.insert(0, r'c:\Users\Hiro\Documents\VSCode\BitaCarnes')

from jogo.modelos import Mundo

def test_world_generation():
    """Test that world generation works with all improvements."""
    print("=" * 60)
    print("Testing Improved World Generation System")
    print("=" * 60)
    
    # Create a test world
    config = {
        "tamanho_grid": 20,
        "nome_humano": "TestHero",
        "origem_humano": "Test Origin",
        "hp_inicial": 20,
        "comida_inicial": 8,
        "madeira_inicial": 2,
        "ouro_inicial": 0,
        "spawn_inicial": {"x": 10, "y": 10, "tema": "vila"},
        "perfil_jogador": None,
    }
    
    try:
        print("\n1. Creating world with size 20x20...")
        mundo = Mundo(config["tamanho_grid"], config)
        print("   ✓ World created successfully")
        
        # Analyze generation
        print("\n2. Analyzing Terrain Generation:")
        print(f"   - Mountains: {len(mundo.tiles_montanha)} tiles")
        print(f"   - Water lakes: {len(mundo.tiles_agua)} tiles")
        print(f"   - Sea tiles: {len(mundo.tiles_mar)} tiles")
        print(f"   - Stone paths: {len(mundo.tiles_caminho_pedra)} tiles")
        print(f"   - Asphalt roads: {len(mundo.tiles_estrada_asfalto)} tiles")
        print(f"   - Trees: {len(mundo.tiles_arvore)} tiles")
        print(f"   - Villages: {len(mundo.vilas)}")
        
        # Check village protection (no mountains in villages)
        print("\n3. Checking Village Protection Zones:")
        for vila_id, vila in mundo.vilas.items():
            vx, vy = vila["pos"]
            mountains_near = 0
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if (vx + dx, vy + dy) in mundo.tiles_montanha:
                        mountains_near += 1
            
            print(f"   - {vila['nome']} at ({vx}, {vy}): {mountains_near} mountains nearby")
            if mountains_near > 2:
                print(f"     ⚠ Warning: More mountains than expected near village")
        
        # Check water lakes (7+ tiles minimum)
        print("\n4. Analyzing Water Bodies:")
        if mundo.tiles_agua:
            # Find connected components of water
            water_groups = []
            visited = set()
            
            def flood_fill(start_pos, visited_set):
                group = set()
                stack = [start_pos]
                while stack:
                    pos = stack.pop()
                    if pos in visited_set or pos not in mundo.tiles_agua:
                        continue
                    visited_set.add(pos)
                    group.add(pos)
                    x, y = pos
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (x + dx, y + dy)
                        if neighbor not in visited_set:
                            stack.append(neighbor)
                return group
            
            for water_tile in mundo.tiles_agua:
                if water_tile not in visited:
                    group = flood_fill(water_tile, visited)
                    water_groups.append(len(group))
            
            water_groups.sort(reverse=True)
            print(f"   - Found {len(water_groups)} water groups")
            print(f"   - Largest lake: {water_groups[0]} tiles" + 
                  (" ✓" if water_groups[0] >= 7 else " ⚠ (below 7-tile minimum)"))
            if len(water_groups) > 1:
                print(f"   - Second largest: {water_groups[1]} tiles")
        
        # Check mountain coherence
        print("\n5. Analyzing Mountain Groups:")
        if mundo.tiles_montanha:
            mountain_groups = []
            visited = set()
            
            def flood_fill(start_pos, visited_set):
                group = set()
                stack = [start_pos]
                while stack:
                    pos = stack.pop()
                    if pos in visited_set or pos not in mundo.tiles_montanha:
                        continue
                    visited_set.add(pos)
                    group.add(pos)
                    x, y = pos
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (x + dx, y + dy)
                        if neighbor not in visited_set:
                            stack.append(neighbor)
                return group
            
            for mountain_tile in mundo.tiles_montanha:
                if mountain_tile not in visited:
                    group = flood_fill(mountain_tile, visited)
                    mountain_groups.append(len(group))
            
            mountain_groups.sort(reverse=True)
            print(f"   - Found {len(mountain_groups)} mountain groups")
            print(f"   - Largest mountain range: {mountain_groups[0]} tiles" +
                  (" ✓" if mountain_groups[0] >= 3 else " ⚠ (below 3-tile minimum)"))
            
            # Count groups with < 3 tiles
            small_groups = sum(1 for g in mountain_groups if g < 3)
            if small_groups > 0:
                print(f"   - Groups with <3 tiles: {small_groups} ⚠")
        
        # Check player spawn
        print("\n6. Player Spawn Position:")
        px, py = mundo.humano
        print(f"   - Player at ({px}, {py})")
        walkable = mundo.eh_caminavel(px, py)
        print(f"   - Tile is walkable: {'✓' if walkable else '✗'}")
        
        # Check paths
        print("\n7. Path Generation:")
        print(f"   - Stone paths generated: {len(mundo.tiles_caminho_pedra)} tiles")
        print(f"   - Asphalt roads generated: {len(mundo.tiles_estrada_asfalto)} tiles")
        
        print("\n" + "=" * 60)
        print("✓ World Generation Test Completed Successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during world generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_world_generation()
    sys.exit(0 if success else 1)
