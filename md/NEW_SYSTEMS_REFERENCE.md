# 🎯 New Systems - Quick Reference Card

## 🏰 Dungeon System

```python
from jogo.dungeon import Gerador_Masmorra, TipoBiomaMasmorra

# Generate dungeon
gen = Gerador_Masmorra(seed=12345)
dungeon = gen.gerar(depth=2, biomo=TipoBiomaMasmorra.CAVERNA_PEDRA)

# Explore
room = dungeon.sala_atual
enemies = room.obter_inimigos_vivos()
treasures = room.bauzins

# Move between rooms
dungeon.avancar_para_sala(next_room_id)
dungeon.foi_completada = True

# Check progress
print(dungeon.obter_progresso())  # "3/10 salas exploradas"
```

**Available biomes**: CAVERNA_PEDRA, CRIPTA_ANTIGA, TORRE_MALDITA, TEMPLO_ESQUECIDO, MINA_PROFUNDA, FLORESTAS_SOMBRIAS, VULCAO

---

## 🐉 Mob System

```python
from jogo.mobs import GerenciadorMobs, BiomaMob, MOBS_DATABASE

mgr = GerenciadorMobs()

# Spawn random mob for biome
mob = mgr.spawan_mob_random(BiomaMob.FLORESTA, x=10, y=15)

# Combat
dano_real = mob.receber_dano(15)
print(f"Health: {mob.percentual_vida}%")

# Loot
if not mob.esta_vivo:
    print(f"Gold: {mob.ouro_drop}")
    print(f"EXP: {mob.exp_drop}")

# Get all mobs in area
nearby = mgr.obter_mobs_em_area(x, y, raio=3)

# Get mob database info
info = mgr.debugar_stats_mob("lobo")
```

**Mob types**: goblin, lobo, urso, aranha_gigante, morcego, esqueleto, zumbi, espectro, elemental_fogo, dragao_jovem

**Biomes**: FLORESTA, PRADARIA, MONTANHA, SUBTERRANEO, ALAGADO, CEMITERIO, VULCAO

---

## ⚔️ Equipment System

```python
from jogo.equipment import Equipamento, BancoDados_Items, TipoItem

# Create player equipment
eq = Equipamento()

# Equip items
eq.equipar_arma(BancoDados_Items.ESPADA_BRONZE)
eq.equipar_armadura(BancoDados_Items.ARMADURA_FERRO)
eq.adicionar_acessorio(BancoDados_Items.ANEL_VITALIDADE)  # 3 max

# Get bonuses
ataque = eq.bônus_ataque
defesa = eq.bônus_defesa
peso = eq.obter_peso_total()

# Item management
item = BancoDados_Items.POCAO_VIDA.copy()
item.danificar(5)
print(f"Durability: {item.percentual_durabilidade}%")
item.reparar()  # Full repair

# Get all items
todos = BancoDados_Items.obter_todos_items()
```

**Item rarities**: COMUM, INCOMUM, RARO, EPICO, LENDARIO

**Item types**: ARMA, ARMADURA, ACESSORIO, CONSUMIVEL, MATERIAL

---

## 📚 Progression System

```python
from jogo.progression import SistemaProgression, BancoDados_Habilidades

prog = SistemaProgression()

# Gain EXP
prog.ganhar_experiencia(150)
print(f"Level: {prog.nivel}")
print(f"EXP: {prog.experiencia}/{prog.exp_para_proximonivel}")

# Learn skill
prog.aprender_habilidade(101)  # Golpe Crítico

# Use skill
dano = prog.calcular_dano_habilidade(101)

# Level up skill
prog.aumentar_habilidade(101)

# Get available skills
disponiveis = prog.obter_habilidades_disponiveis()

# Stats
print(f"Attack: {prog.ataque_total}")
print(f"Defense: {prog.defesa_total}")
print(f"Max HP: {prog.vida_max}")
```

**Combat skills**: GOLPE_CRITICO (101), ATAQUE_TORNADO (102), DEFESA_FERREA (103), LÂMINA_MÁGICA (104)

**Magic skills**: BOLA_FOGO (201), ESCUDO_MAGICO (202), RAIO (203), TELEPORTE (204)

**Nature skills**: REGENERACAO (301), ACELERAÇÃO_VEGETAL (302), INVOCACAO_ANIMAL (303)

**Survival skills**: RASTREAMENTO (401), COLETA_EFICIENTE (402), CAMUFLAGEM (403)

---

## 🌍 Biome System

```python
from jogo.biomas import ConfiguradorBiomas, TipoBioma

biomas = ConfiguradorBiomas.obter_todos_biomas()

# Get biome config
floresta = biomas[TipoBioma.FLORESTA]

# Basic info
print(floresta.nome)          # "Floresta Densa"
print(floresta.descricao)
print(floresta.temperaturaBase)  # 18°C
print(floresta.umidade)          # 0.8
print(floresta.periculosidade)   # 1-5

# Resources
for recurso in floresta.recursos:
    print(f"{recurso.nome}: {recurso.raridade}")

# Mobs
print(f"Native mobs: {floresta.mobs_nativos}")

# Characteristics
for char in floresta.caracteristicas:
    print(f"{char.nome}: {char.descricao}")
```

**Biome types**: FLORESTA, PRADARIA, MONTANHA, DESERTO, ALAGADO, VULCAO, TUNDRA, CAVERNA, CEMITERIO, FLORESTA_SOMBRA

---

## 🎭 NPC Backstory System

```python
from jogo.npc_backstories import GeradorBackstoryIA, SistemaBackstories, ArchetipoNPC

# Generate single backstory
backstory = GeradorBackstoryIA.gerar_backstory(
    "Marcus",
    ArchetipoNPC.GUERREIRO,
    age=32
)
print(backstory.relato_vida)
print(backstory.sonho_segredo)
print(backstory.virtudes)

# Manage NPC backstories
sistema = SistemaBackstories()
sistema.adicionar_npc("Isabella", ArchetipoNPC.MAGO, 24)

# Get backstory
bs = sistema.obter_backstory("Isabella")

# Get dialogue
diálogo = sistema.obter_diálogo_contextualizado("Isabella", "saudacao")
```

**Archetypes**: GUERREIRO, MAGO, LADRÃO, CLÉRIGO, MERCADOR, BARDO, CAÇADOR, CAMPONÊS, NOBRE, EREMITA

**Traumas**: PERDA_FAMILIAR, GUERRA, ESCRAVIDÃO, MALDIÇÃO, AMOR_PERDIDO, EXÍLIO, INJUSTIÇA, NENHUM

---

## 🎬 Animation System

```python
from jogo.animations import AnimadorEntidade, TipoAnimacao, Direcao

# Create animator for entity
anim = AnimadorEntidade(entidade_id=1)

# Start animations
anim.animar(TipoAnimacao.MOVIMENTO, Direcao.NORTE)
anim.animar(TipoAnimacao.ATAQUE)
anim.animar(TipoAnimacao.CURA)

# Update in game loop
anim.atualizar(delta_time=0.016)

# Get current frame to render
frame = anim.obter_frame_renderizacao()
if frame:
    sprite_id = frame.id_sprite
    offset = (frame.offset_x, frame.offset_y)

# Get all animations
from jogo.animations import DefinidorAnimacoes
todas = DefinidorAnimacoes.obter_todasanimacoes()
```

**Animation types**: MOVIMENTO, ATAQUE, EFEITO_MAGICO, CURA, MORTE, DANO, PARADO, CORRIDA, SALTO

**Directions**: NORTE, NOROESTE, OESTE, SUDOESTE, SUL, SUDESTE, LESTE, NORDESTE

---

## 💾 Complete Integration Example

```python
# In your main game class init:
from jogo.dungeon import Gerador_Masmorra
from jogo.mobs import GerenciadorMobs
from jogo.progression import SistemaProgression
from jogo.animations import AnimadorEntidade
from jogo.biomas import ConfiguradorBiomas

self.gerador_dungeons = Gerador_Masmorra()
self.gerenciador_mobs = GerenciadorMobs()
self.progression = SistemaProgression()
self.animador = AnimadorEntidade(1)
self.biomas = ConfiguradorBiomas.obter_todos_biomas()

# In your game loop:
self.gerenciador_mobs.atualizar_mobs(delta_time)
self.animador.atualizar(delta_time)

# On combat:
mob = self.gerenciador_mobs.spawan_mob_random(bioma_atual, x, y)
ataque = self.progression.ataque_total + bonus_equipment
dano = mob.receber_dano(ataque)
self.animador.animar(TipoAnimacao.ATAQUE)

# On victory:
self.progression.ganhar_experiencia(mob.exp_drop)
```

---

## 🔍 Debugging

```python
# Progression
stats = prog.debugar_stats()

# Mobs
info = mgr.debugar_stats_mob("lobo")

# Get all mobs alive
vivos = mgr.obter_mobs_vivos()

# Dungeon progress
dungeon.obter_progresso()
```

---

**For detailed info**, see:
- Technical: `md/ENHANCEMENT_SYSTEMS_GUIDE.md`
- Integration steps: `md/INTEGRATION_GUIDE.md`
- Full examples: `md/CODE_EXAMPLES.md`
