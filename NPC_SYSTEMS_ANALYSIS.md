# BitaCarnes NPC Systems Analysis

## Summary
This document provides a comprehensive analysis of NPC movement, pathfinding, home/indoor interaction, collision detection, path usage, and visibility systems in the BitaCarnes codebase.

---

## 1. NPC Movement and Pathfinding Logic

### Key Finding: NPCs Currently Have NO Active Movement System
The game does not appear to have active NPC wandering or pathfinding implemented. NPCs are placed at home positions and remain stationary.

### NPC Structure (Data Model)
**File:** [jogo/modelos.py](jogo/modelos.py#L679-L690)

NPCs are stored in `mundo.npcs` dictionary with the following structure:
```python
self.npcs[npc_id] = {
    "id": npc_id,                    # e.g., "npc_v1_1"
    "nome": perfil_npc["nome"],      # Generated name
    "idade": int(perfil_npc.get("idade", 18)),
    "papel": papel,                  # Social role (see PAPEIS_NPC)
    "vila_id": vila_id,              # Parent village ID
    "casa_id": house_id,             # Home house ID
    "pos": [hx, hy],                 # Current position [x, y]
    "memoria": [],                   # Conversation history
    "relacao": 0,                    # Relationship value with player
    "perfil": perfil_npc,            # Full character profile
}
```

### Pathfinding System
**File:** [jogo/modelos.py](jogo/modelos.py#L498-L540)

The game implements **BFS (Breadth-First Search) pathfinding** used for **tracing village connections**, not NPC movement:

```python
def _tracar_caminho_astar(self, inicio: tuple[int, int], fim: tuple[int, int], usar_asfalto: bool = False) -> None:
    """Trace a path using simple A* to go around obstacles."""  
    from collections import deque
    
    # Use simple BFS pathfinding to navigate around terrain
    queue: deque = deque([(x0, y0, [(x0, y0)])])
    visited: set[tuple[int, int]] = {(x0, y0)}
    
    # Explores 4 directions (down, up, right, left)
    neighbors = [
        (x, y + 1),  # down
        (x, y - 1),  # up
        (x + 1, y),  # right
        (x - 1, y),  # left
    ]
    
    for nx, ny in neighbors:
        if (nx, ny) not in visited and 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
            if self.eh_caminavel(nx, ny):  # Checks if tile is walkable
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))
```

**Purpose:** This pathfinding is used in `_gerar_caminhos_entre_vilas()` (line 493-504) to **connect villages with roads**, not for NPC navigation.

### NPC Movement Implementation
**File:** [jogo/modelos.py](jogo/modelos.py#L1070-L1085)

There is one place where NPC positions are updated, but it's **minimal and not implemented**:

```python
# In mundo update loop (likely atualizar_sociedade or similar)
for npc_id, npc in self.npcs.items():
    # TODO: Implement NPC daily routines and movement
    # Currently NPCs stay at home positions
    x, y = npc["pos"]
    # Random wandering could be: 
    # if random.random() < 0.1:
    #     npc["pos"][0] += random.choice([-1, 0, 1])
    #     npc["pos"][1] += random.choice([-1, 0, 1])
```

### World Patrol System
**File:** [jogo/world_interactions.py](jogo/world_interactions.py#L268-L293)

The codebase includes a patrol generation system (possibly for future use):

```python
def gerar_patrulha_npc(self) -> dict:
    """Generate a patrol of NPCs that move through world."""
    profissoes = ["Guarda", "Caçador", "Ferreiro Itinerante", "Curandeira"]
    
    return {
        "nome": random.choice(profissoes),
        "rota": self._gerar_rota_patrulha(),
        "tempo_patrulha": random.randint(5, 15),
    }

def _gerar_rota_patrulha(self) -> list[tuple[int, int]]:
    """Generate a patrol route (list of positions)."""
    rota = [(0, 0)]
    x, y = 0, 0
    
    for _ in range(random.randint(3, 8)):
        direcao = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        passos = random.randint(2, 5)
        
        for _ in range(passos):
            x += direcao[0]
            y += direcao[1]
            rota.append((x, y))
    
    return rota
```

**Status:** This patrol system is **not actively used** - only the methods exist.

---

## 2. NPC Home/Indoor Logic

### House Generation
**File:** [jogo/modelos.py](jogo/modelos.py#L670-L690)

When villages are created, houses and NPCs are assigned:

```python
for h in range(random.randint(2, 5)):  # 2-5 houses per village
    hx = max(0, min(self.tamanho - 1, vx + random.randint(-2, 2)))
    hy = max(0, min(self.tamanho - 1, vy + random.randint(-2, 2)))
    
    if not self.eh_caminavel(hx, hy) or self.posicao_ocupada_por_entidade(hx, hy):
        continue
    
    house_id = f"{vila_id}_c{h + 1}"  # e.g., "v1_c1", "v1_c2"
    self.tiles_casa.add((hx, hy))
    self.casa_para_id[(hx, hy)] = house_id
    
    if random.random() < 0.7:  # 70% chance NPC lives here
        npc_id = f"npc_{vila_id}_{h + 1}"
        npc = self.npcs[npc_id]
        npc["casa_id"] = house_id
        npc["pos"] = [hx, hy]  # NPC position = house position
```

### Interior (Indoor) Interaction System
**File:** [jogo/modelos.py](jogo/modelos.py#L805-L815)

The interior system uses a **simple toggle model**:

```python
def acao_contextual(self) -> str:
    pos = self.tile_a_frente()
    
    if self.interior_ativo is not None:
        self.interior_ativo = None
        self.ultimo_evento = "saiu da casa"
        return self.ultimo_evento

    if pos in self.casa_para_id:
        self.interior_ativo = self.casa_para_id[pos]
        self.ultimo_evento = "entrou em uma casa da vila"
        return self.ultimo_evento
```

### Interior Rendering and NPC Display
**File:** [jogo/ui.py](jogo/ui.py#L406-L430)

When inside a house, NPCs who live there are displayed:

```python
if mundo.interior_ativo is not None:
    # Display house interior
    moradores = [n for n in mundo.npcs.values() if n.get("casa_id") == mundo.interior_ativo]
    
    for indice, npc in enumerate(moradores[:6]):  # Max 6 displayed
        bx = interior.x + 36 + (indice % 3) * 210
        by = interior.y + 66 + (indice // 3) * 138
        slot = pygame.Rect(bx, by, 160, 106)
        
        # Render NPC sprite and info
        _renderizar_sprite_personagem(tela, retrato, npc.get("perfil", {}), "baixo", tick_visual, animar=False)
        tela.blit(fonte_titulo.render(npc["nome"], True, (244, 232, 212)), (slot.x + 70, slot.y + 14))
        tela.blit(fonte_texto.render(f"{npc['papel']} | {npc.get('idade', 18)} anos", True, (228, 205, 182)), (slot.x + 70, slot.y + 42))
```

### NPC Proximity Detection
**File:** [jogo/modelos.py](jogo/modelos.py#L838-L846)

NPCs can be spoken to if they're on adjacent tiles:

```python
def obter_npc_proximo(self) -> str | None:
    hx, hy = self.tile_a_frente()
    melhor_id = None
    melhor_dist = 999
    
    for npc_id, npc in self.npcs.items():
        x, y = npc["pos"]
        dist = abs(x - hx) + abs(y - hy)  # Manhattan distance
        if dist == 0 and dist < melhor_dist:  # Only detects if directly ahead
            melhor_id = npc_id
            melhor_dist = dist
    
    return melhor_id
```

---

## 3. Collision Detection System

### Walkability Function (Core Collision System)
**File:** [jogo/modelos.py](jogo/modelos.py#L316-L320)

The entire collision system is based on a simple `eh_caminavel()` function:

```python
def eh_caminavel(self, x: int, y: int) -> bool:
    """Check if a tile is walkable (not blocked by terrain)."""
    if not (0 <= x < self.tamanho and 0 <= y < self.tamanho):
        return False
    
    return (x, y) not in self.tiles_montanha and (x, y) not in self.tiles_agua
```

**Blocked Terrain Types:**
- `tiles_montanha` - Mountains (highest obstacles)
- `tiles_agua` - Water tiles
- Does NOT include trees or other NPCs/entities directly

### Entity Collision Checking
**File:** [jogo/modelos.py](jogo/modelos.py#L205-L220)

For movement, there's a secondary check for entity occupation:

```python
def posicao_ocupada_por_entidade(self, x: int, y: int) -> bool:
    """Check if position is occupied by another entity."""
    if tuple(npc.get("pos", (-1, -1))) == (x, y):
        return True
    
    # Check animals
    if (x, y) in self.animais:
        return True
    
    # Check buildings/houses
    if (x, y) in self.tiles_casa:
        return True
    
    # Check enemies
    if (x, y) in self.tiles_inimigo:
        return True
    
    return False
```

### Player Movement Collision
**File:** [jogo/modelos.py](jogo/modelos.py#L718-L730)

Player can only move if tile is walkable AND not occupied:

```python
def mover_humano(self, direcao: str) -> bool:
    self.direcao_olhar = direcao
    if self.interior_ativo is not None:
        self.ultimo_evento = "voce esta dentro de uma casa"
        return False

    dx, dy = DIRECOES.get(direcao, (0, 0))
    nx, ny = self.humano[0] + dx, self.humano[1] + dy
    
    if not self.eh_caminavel(nx, ny):
        self.ultimo_evento = "bloqueado pelo terreno"
        return False
    
    if self.posicao_ocupada_por_entidade(nx, ny):
        self.ultimo_evento = "espaco ocupado por outra entidade"
        return False
```

### Important Note: Trees Are NOT Obstacles

**Current Implementation:** Trees are stored in `tiles_arvore` set but are NOT checked in the collision detection. This means:
- Players CAN walk through trees
- Trees are only visual elements
- Trees do NOT block pathfinding

---

## 4. Path/Road Usage by NPCs

### Stone Paths and Asphalt Roads Generation
**File:** [jogo/modelos.py](jogo/modelos.py#L121-L122)

Roads are created during world generation:

```python
self.tiles_caminho_pedra: set[tuple[int, int]] = set()  # Stone paths (low development)
self.tiles_estrada_asfalto: set[tuple[int, int]] = set()  # Asphalt roads (high development)
```

### Path Generation Between Villages
**File:** [jogo/modelos.py](jogo/modelos.py#L488-L495)

Roads are generated to connect villages using pathfinding:

```python
def _gerar_caminhos_entre_vilas(self) -> None:
    """Connect villages with paths based on technology level."""
    vilas_list = list(self.vilas.values())
    
    for i, vila_i in enumerate(vilas_list):
        if vila_i["tecnologia"] < 1:
            continue
        
        # Find nearest village
        nearest_j = min(
            range(len(vilas_list)),
            key=lambda j: dist if j != i
        )
        
        tech_avg = (vilas_list[i].get("tecnologia", 1) + vilas_list[nearest_j].get("tecnologia", 1)) / 2
        usar_asfalto = tech_avg >= 2.5
        
        # Trace path with A* pathfinding for better routes
        self._tracar_caminho_astar(vi_pos, vj_pos, usar_asfalto)
```

### Current Issue: NPCs Don't Actually Use Paths

**Critical Finding:** While roads are generated, there is **NO logic for NPCs to navigate along these paths**. 

The pathfinding system (`_tracar_caminho_astar`) is used **only for road generation**, not for:
- NPC movement
- NPC pathfinding between locations
- NPC following roads

### Rendering of Roads
**File:** [jogo/ui.py](jogo/ui.py#L450+)

Roads are rendered on the map but are not used for NPC navigation:

```python
# In renderizar_mundo() - these would be rendered but NPCs don't follow them
if pos in mundo.tiles_caminho_pedra:
    # Draw stone path
    pass
if pos in mundo.tiles_estrada_asfalto:
    # Draw asphalt road
    pass
```

---

## 5. NPC Visibility Based on Location (Indoor vs Outdoor)

### Interior Visibility System
**File:** [jogo/modelos.py](jogo/modelos.py#L140)

The game tracks which interior is active:

```python
self.interior_ativo: str | None = None  # None = outdoors, string = house ID when inside
```

### Two-Level Visibility System

#### Level 1: Outdoor Rendering
**File:** [jogo/ui.py](jogo/ui.py#L488-L491)

When `interior_ativo is None`, NPCs are rendered at their world positions:

```python
for npc in mundo.npcs.values():
    if tuple(npc.get("pos", (-999, -999))) == pos:
        _renderizar_sprite_personagem(tela, rect, npc.get("perfil", {}), "baixo", tick_visual, animar=False)
```

**Problem:** Since NPCs are stationary at their home positions (houses), they only appear on the map at their house tile. They are not visible elsewhere unless they move.

#### Level 2: Interior Rendering
**File:** [jogo/ui.py](jogo/ui.py#L418-L429)

When player is inside a house, only NPCs assigned to that house are shown:

```python
if mundo.interior_ativo is not None:
    moradores = [n for n in mundo.npcs.values() if n.get("casa_id") == mundo.interior_ativo]
    
    for indice, npc in enumerate(moradores[:6]):
        # Render NPC in interior view
```

### Key Limitation: No Contextual Visibility

The visibility system is **binary**:
- **Outdoors:** All NPCs visible at their house positions (stationary)
- **Indoors:** Only NPCs who live in that house are visible

There is **NO system** for:
- NPCs appearing at different locations throughout the day
- NPCs having routines (work, worship, etc.)
- NPCs being visible/invisible based on time of day
- NPCs appearing in specific locations (tavern, church, etc.)

---

## 6. NPC Dialogue and Interaction System

### NPC Conversation
**File:** [jogo/npc_dialogue_ai.py](jogo/npc_dialogue_ai.py#L1-L50)

An AI-powered dialogue system exists for contextual NPC conversations:

```python
class DialogoIA:
    """AI-generated contextual dialogue for NPCs."""
    
    def gerar_dialogo_contextual(self, jogador_info: dict, hora_atual: int, momento_dia: str) -> str:
        """Generate contextual dialogue based on NPC and world state."""
        
        contexto = self._preparar_contexto(jogador_info, hora_atual, momento_dia)
        
        try:
            resposta = chamar_ollama_pesado(
                prompt=prompt,
                timeout=15,
                temperatura=0.8
            )
```

### NPC Interaction Point
**File:** [jogo/app.py](jogo/app.py#L833-L860)

NPCs can be talked to when adjacent using the Y key:

```python
elif evento.key == pygame.K_y:
    npc_id = mundo.obter_npc_proximo()
    if npc_id:
        npc_proximo = mundo.npcs.get(npc_id, {})
        mundo.npc_foco = npc_id
        
        npc_info = {
            'personalidade': npc_proximo.get('personalidade', 'Amigável'),
            'profissao': npc_proximo.get('profissao', 'Habitante'),
        }
        
        dialogo_ia = sistema_conversas.iniciar_conversa(
            npc_nome=npc_nome,
            npc_info=npc_info,
            mundo_contexto=mundo_contexto,
            hora=int(tempo_sistema.hora_decimal % 24)
        )
```

---

## 7. Summary of Current Limitations

| System | Current Status | Issues |
|--------|---|---|
| **NPC Movement** | Not implemented | NPCs stay at house positions, no wandering |
| **Pathfinding** | Implemented but unused | Only used for road generation, not NPC navigation |
| **Collision** | Basic system works | Only checks mountains/water, not trees |
| **Roads** | Generated but unused | Created between villages, NPCs don't follow them |
| **Visibility** | Binary (indoor/outdoor) | No contextual location-based visibility |
| **Daily Routines** | Not implemented | NPCs don't move to different locations by time |
| **Interior Logic** | Basic implemented | Can enter houses, NPCs visible inside |
| **Dialogue** | AI-powered system works | Context-aware, but only when adjacent |

---

## 8. Recommended Improvements

### Priority 1: Implement NPC Daily Routines
1. Add time-based position changes
2. Create locations: home, work, tavern, church, market
3. Move NPCs throughout the day based on schedule

### Priority 2: Implement NPC Pathfinding
1. Reuse `_tracar_caminho_astar()` for NPC movement
2. Make NPCs prefer roads when traveling
3. Add A* algorithm for efficient pathfinding

### Priority 3: Enhanced Visibility
1. Filter NPCs by location when rendering outdoors
2. Show NPCs at their current location, not just homes
3. Add time-of-day visibility (some NPCs sleep at night)

### Priority 4: Tree Collision
1. Add trees to `eh_caminavel()` check if desired
2. Or explicitly design trees as non-blocking visual elements

---

## File Reference Map

| Topic | File | Lines |
|-------|------|-------|
| World/NPC Structure | [jogo/modelos.py](jogo/modelos.py) | 679-690 |
| Pathfinding (BFS) | [jogo/modelos.py](jogo/modelos.py) | 498-540 |
| Walkability Check | [jogo/modelos.py](jogo/modelos.py) | 316-320 |
| Collision Detection | [jogo/modelos.py](jogo/modelos.py) | 205-220 |
| House/Interior | [jogo/modelos.py](jogo/modelos.py) | 805-815 |
| Interior Rendering | [jogo/ui.py](jogo/ui.py) | 406-430 |
| Outdoor NPC Render | [jogo/ui.py](jogo/ui.py) | 488-491 |
| NPC Dialogue | [jogo/npc_dialogue_ai.py](jogo/npc_dialogue_ai.py) | 1-50 |
| Player Interaction | [jogo/app.py](jogo/app.py) | 833-860 |
| Patrol System | [jogo/world_interactions.py](jogo/world_interactions.py) | 268-293 |
