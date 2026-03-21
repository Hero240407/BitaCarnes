# Quick Code Examples - New Game Systems

## 🎮 Dungeon System Usage

### Generate a Dungeon
```python
from jogo.dungeon import Gerador_Masmorra, TipoBiomaMasmorra, DificuldadeMasmorra

# Create dungeon generator
gerador = Gerador_Masmorra(seed=12345)

# Generate a dungeon
dungeon = gerador.gerar(
    profundidade=2,  # Depth level (2 = Normal difficulty)
    bioma=TipoBiomaMasmorra.CAVERNA_PEDRA
)

print(f"Dungeon: {dungeon.bioma.value}")
print(f"Rooms: {dungeon.obter_progresso()}")
print(f"Boss: {dungeon.sala_atual.nome}")
```

### Explore Dungeon Rooms
```python
# Get current room
sala_atual = dungeon.sala_atual
print(f"Enemies in room: {len(sala_atual.obter_inimigos_vivos())}")
print(f"Treasures: {len(sala_atual.bauzins)}")

# Move to connected room
if dungeon.avancar_para_sala(1):  # Room ID
    print("Moved to next room!")
    dungeon.sala_atual.foi_explorada = True
```

---

## 🐉 Mob System Usage

### Spawn a Random Mob
```python
from jogo.mobs import GerenciadorMobs, BiomaMob

gerenciador = GerenciadorMobs()

# Spawn random mob for biome
mob = gerenciador.spawan_mob_random(BiomaMob.FLORESTA, x=10, y=15)

print(f"Mob: {mob.nome} (HP: {mob.vida_atual}/{mob.vida_max})")
print(f"Attack: {mob.ataque}, Defense: {mob.defesa}")
```

### Combat with Mobs
```python
# Deal damage
dano_real = mob.receber_dano(15)
print(f"Real damage dealt: {dano_real}")
print(f"Mob life: {mob.percentual_vida}%")

# Check if alive
if mob.esta_vivo:
    print("Mob is still fighting!")
else:
    print(f"You gain {mob.ouro_drop} gold and {mob.exp_drop} EXP!")
```

### Get Mobs in Area
```python
# Get all mobs within radius
mobs_proximos = gerenciador.obter_mobs_em_area(x=10, y=10, raio=3)
for mob in mobs_proximos:
    print(f"- {mob.nome} at ({mob.x}, {mob.y})")
```

---

## ⚔️ Equipment System Usage

### Create and Equip Items
```python
from jogo.equipment import BancoDados_Items, Equipamento

# Get an item from database
espada = BancoDados_Items.ESPADA_BRONZE
pocao = BancoDados_Items.POCAO_VIDA

# Create equipment set
equipamento = Equipamento()
equipamento.equipar_arma(espada)
equipamento.adicionar_acessorio(BancoDados_Items.ANEL_VITALIDADE)

# Check bonuses
print(f"Attack bonus: +{equipamento.bônus_ataque}")
print(f"Defense bonus: +{equipamento.bônus_defesa}")
print(f"Total weight: {equipamento.obter_peso_total()}kg")
```

### Consumable Items
```python
# Use a potion
pocao = BancoDados_Items.POCAO_VIDA
if pocao.efeito_consumivel:
    efeito = pocao.efeito_consumivel
    print(f"Use {pocao.nome}: Heal {efeito['valor']} HP")
    # hero.vida_atual += efeito['valor']
```

### Item Durability
```python
espada = BancoDados_Items.ESPADA_BRONZE.copy()

# Use the weapon in combat
espada.danificar(5)
print(f"Durability: {espada.percentual_durabilidade}%")

# Check if broken
if espada.esta_quebrado:
    print("Weapon is broken! Need to repair.")
else:
    espada.reparar()  # Full repair
    print("Weapon repaired!")
```

---

## 📚 Skill System Usage

### Initialize Progression
```python
from jogo.progression import SistemaProgression, BancoDados_Habilidades

progression = SistemaProgression()

# Gain experience
progression.ganhar_experiencia(150)
print(f"Level: {progression.nivel}")
print(f"EXP: {progression.experiencia}/{progression.exp_para_proximonivel}")
```

### Learn Skills
```python
# Learn a skill
progression.aprender_habilidade(101)  # Golpe Crítico

# Check learned skills
print(f"Learned {len(progression.habilidades_aprendidas)} skills")

# Get available skills to learn
disponiveis = progression.obter_habilidades_disponiveis()
for skill in disponiveis:
    print(f"- {skill.nome} (required level: {skill.nivel_requerido})")
```

### Use Skills
```python
# Calculate damage with skill
dano_skill = progression.calcular_dano_habilidade(101)
print(f"Golpe Crítico deals: {dano_skill} damage")

# Level up a learned skill
progression.aumentar_habilidade(101)
habilidade = progression.habilidades_aprendidas[101]
print(f"Golpe Crítico now level: {habilidade.nivel}")
```

### Check Stats
```python
stats = progression.debugar_stats()
print(f"""
Level: {stats['nivel']}
Attack: {stats['ataque']}
Defense: {stats['defesa']}
Intelligence: {stats['inteligencia']}
Max HP: {stats['vida_max']}
Skills: {stats['habilidades']}
Available skill points: {stats['pontos_skill']}
""")
```

---

## 🌍 Biome System Usage

### Get Biome Config
```python
from jogo.biomas import ConfiguradorBiomas, TipoBioma

biomas = ConfiguradorBiomas.obter_todos_biomas()

# Get specific biome
floresta = biomas[TipoBioma.FLORESTA]
print(f"Biome: {floresta.nome}")
print(f"Description: {floresta.descricao}")
print(f"Temperature: {floresta.temperaturaBase}°C")
print(f"Native mobs: {floresta.mobs_nativos}")
print(f"Danger level: {floresta.periculosidade}/5")

# Get resources
for recurso in floresta.recursos:
    print(f"- {recurso.nome} (value: {recurso.valor_ouro}g)")
```

### Get Biome Effects
```python
# Check characteristics
for char in floresta.caracteristicas:
    print(f"{char.nome}: {char.descricao}")
    print(f"  Type: {char.tipo}")
    if char.efeito_jogador:
        print(f"  Player effects: {char.efeito_jogador}")
```

### Loop Through All Biomes
```python
for tipo_bioma, config in biomas.items():
    print(f"{config.nome} ({tipo_bioma.value})")
    print(f"  Danger: {config.periculosidade}/5")
    print(f"  Resources: {len(config.recursos)}")
```

---

## 🎭 NPC Backstory Usage

### Generate NPC Backstory
```python
from jogo.npc_backstories import GeradorBackstoryIA, ArchetipoNPC

# Generate a backstory
backstory = GeradorBackstoryIA.gerar_backstory(
    npc_nome="Marcus",
    arquetipo=ArchetipoNPC.GUERREIRO,
    idade=32
)

print(backstory.relato_vida)
print(f"Trauma: {backstory.evento_marcante}")
print(f"Secret: {backstory.sonho_segredo}")
```

### System Management
```python
from jogo.npc_backstories import SistemaBackstories

sistema = SistemaBackstories()

# Add NPCs with backstories
sistema.adicionar_npc("Isabella", ArchetipoNPC.MAGO, 24)
sistema.adicionar_npc("Thorne", ArchetipoNPC.LADRÃO, 28)

# Get backstory
backstory = sistema.obter_backstory("Isabella")

# Get contextual dialogue
dialogue = sistema.obter_diálogo_contextualizado("Isabella", "saudacao")
print(f"Isabella: {dialogue}")
```

---

## 🎬 Animation System Usage

### Start Animation
```python
from jogo.animations import AnimadorEntidade, TipoAnimacao, Direcao

# Create entity animator
animador = AnimadorEntidade(entidade_id=1)

# Start animations
animador.animar(TipoAnimacao.MOVIMENTO, Direcao.NORTE)
animador.animar(TipoAnimacao.ATAQUE)
animador.animar(TipoAnimacao.CURA)
```

### Update and Render
```python
# In game loop:
delta_time = 0.016  # 60 FPS

# Update animations
animador.atualizar(delta_time)

# Get current frame to render
frame = animador.obter_frame_renderizacao()
if frame:
    # Render sprite at position
    # sprite_id = frame.id_sprite
    # offset = (frame.offset_x, frame.offset_y)
    # scale = frame.escala
    pass
```

### View All Animations
```python
from jogo.animations import DefinidorAnimacoes

todas_anims = DefinidorAnimacoes.obter_todasanimacoes()
for nome, anim_seq in todas_anims.items():
    print(f"{nome}: {anim_seq.num_frames} frames, loop={anim_seq.loop}")
```

---

## 🎯 Example: Complete Combat Scenario

```python
# Setup
from jogo.mobs import GerenciadorMobs, BiomaMob
from jogo.progression import SistemaProgression
from jogo.equipment import Equipamento, BancoDados_Items
from jogo.animations import AnimadorEntidade, TipoAnimacao

# Initialize systems
gerenciador_mobs = GerenciadorMobs()
progression = SistemaProgression()
equipamento = Equipamento()
animador = AnimadorEntidade(1)

# Equip player
equipamento.equipar_arma(BancoDados_Items.ESPADA_BRONZE)

# Spawn enemy
mob = gerenciador_mobs.spawan_mob_random(BiomaMob.FLORESTA, 10, 10)

# Combat loop
while mob.esta_vivo and progression.nivel < 100:
    # Player attacks
    ataque_total = progression.ataque_total + equipamento.bônus_ataque
    dano = random.randint(int(ataque_total * 0.8), ataque_total)
    
    # Animate attack
    animador.animar(TipoAnimacao.ATAQUE)
    
    # Deal damage
    dano_real = mob.receber_dano(dano)
    print(f"Hit for {dano_real} damage!")
    
    if not mob.esta_vivo:
        # Victory
        progression.ganhar_experiencia(mob.exp_drop)
        print(f"Victory! +{mob.exp_drop} EXP, +{mob.ouro_drop}g")
        break
    
    # Enemy attacks back (simplified)
    inimigo_dano = max(1, mob.ataque - progression.defesa_total)
    print(f"Took {inimigo_dano} damage!")
```

---

All these systems are now ready for use and integration into your game!
