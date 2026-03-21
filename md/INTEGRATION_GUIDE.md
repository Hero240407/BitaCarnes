# Integration Guide - Adding New Systems to Game

## Step 1: Update Imports in `app.py`

Add these imports at the top of your `jogo/app.py`:

```python
# New systems
from .dungeon import Masmorra, Gerador_Masmorra, TipoBiomaMasmorra, DificuldadeMasmorra
from .mobs import GerenciadorMobs, BiomaMob, TipoMob, Mob
from .equipment import Equipamento, BancoDados_Items, Item
from .progression import SistemaProgression, BancoDados_Habilidades
from .biomas import ConfiguradorBiomas, TipoBioma
from .npc_backstories import SistemaBackstories, ArchetipoNPC
from .animations import GerenciadorAnimações, AnimadorEntidade, TipoAnimacao, Direcao
```

## Step 2: Initialize in Game Class

In your `Mundo` class initialization (in `modelos.py`), add:

```python
class Mundo:
    def __init__(self, tamanho: int, config: dict) -> None:
        # ... existing code ...
        
        # New systems
        self.gerenciador_mobs = GerenciadorMobs()
        self.sistemas_progression = SistemaProgression()
        self.sistema_backstories = SistemaBackstories()
        self.gerenciador_animacoes = GerenciadorAnimações()
        self.dungeons_disponiveis = {}
        self.biomas_config = ConfiguradorBiomas.obter_todos_biomas()
```

## Step 3: Mob Spawning in Game World

In your main game loop, add periodic mob spawning:

```python
def atualizar_mobs(self, tempo_delta: float):
    """Atualiza e spawna mobs no mundo"""
    # Atualiza existentes
    self.gerenciador_mobs.atualizar_mobs(tempo_delta)
    
    # Spawna novos mobs ocasionalmente
    if random.random() < 0.01:  # 1% chance per frame
        # Determina bioma na posição aleatória próxima
        bioma = self._obter_bioma_em_posicao(self.humano[0] + random.randint(-10, 10), 
                                             self.humano[1] + random.randint(-10, 10))
        
        mob = self.gerenciador_mobs.spawan_mob_random(
            BiomaMob[bioma.upper()],  # Converter string para enum
            self.humano[0] + random.randint(-5, 5),
            self.humano[1] + random.randint(-5, 5)
        )
```

## Step 4: Combat with New Equipment

Update combat to use equipment stats:

```python
def atacar_inimigo(self, alvo_mob: Mob):
    """Ataca um inimigo com equipment"""
    # Damage integrado com equipment
    ataque_total = self.sistemas_progression.ataque_total
    
    # Adiciona bonus de arma
    if self.equipamento.arma:
        ataque_total += self.equipamento.arma.ataque
    
    # Calcula dano
    dano = random.randint(int(ataque_total * 0.8), ataque_total)
    dano_real = alvo_mob.receber_dano(dano)
    
    # Trigg'er animação de ataque
    self.animador.animar(TipoAnimacao.ATAQUE)
    
    # Se mob morre, ganhar loot
    if not alvo_mob.esta_vivo:
        self._processar_loot_mob(alvo_mob)
```

## Step 5: Render Biome-specific Features

In `ui.py`, update terrain rendering:

```python
def renderizar_mundo_com_biomas(self, tela, mundo, camera):
    """Renderiza mundo com características de bioma"""
    bioma_atual = mundo._obter_bioma_em_posicao(mundo.humano[0], mundo.humano[1])
    bioma_config = mundo.biomas_config.get(bioma_atual)
    
    if bioma_config:
        # Aplica cor do bioma
        tela.fill(bioma_config.cor_base)
        
        # Renderiza objetos do bioma
        # ... código de renderização ...
```

## Step 6: Skill Usage in Combat

Allow player to use learned skills:

```python
def usar_habilidade(self, habilidade_id: int, alvo=None):
    """Executa uma habilidade aprendida"""
    if habilidade_id not in self.sistemas_progression.habilidades_aprendidas:
        return False
    
    habilidade_obj = self.sistemas_progression.habilidades_aprendidas[habilidade_id]
    todas_skills = BancoDados_Habilidades.obter_todasabilidades()
    
    if habilidade_id not in todas_skills:
        return False
    
    skill_def = todas_skills[habilidade_id]
    
    # Calcula dano
    dano = self.sistemas_progression.calcular_dano_habilidade(habilidade_id)
    
    # Aplica efeito
    if alvo and hasattr(alvo, 'receber_dano'):
        alvo.receber_dano(dano)
        # Trigger animação e efeitos
        self.animador.animar(TipoAnimacao.EFEITO_MAGICO)
    
    return True
```

## Step 7: Dungeon Entry Point

Add dungeon entry interaction:

```python
def criar_entrada_dungeon(self, x: int, y: int, tipo_bioma: TipoBiomaMasmorra, profundidade: int):
    """Cria uma entrada de dungeon no mundo"""
    gerador = Gerador_Masmorra(seed=hash(f"{x}{y}"))
    dungeon = gerador.gerar(profundidade, tipo_bioma)
    
    dungeon_id = f"dungeon_{x}_{y}"
    self.dungeons_disponiveis[dungeon_id] = dungeon
    
    return dungeon_id

def entrar_dungeon(self, dungeon_id: str):
    """Entra em uma dungeon"""
    if dungeon_id in self.dungeons_disponiveis:
        self.dungeon_atual = self.dungeons_disponiveis[dungeon_id]
        self.em_dungeon = True
        self.dungeon_atual.foi_visitada = True
        return True
    return False
```

## Step 8: NPC Backstory Integration

When NPCs are created, generate backstories:

```python
def criar_npc_com_backstory(self, nome: str, arquetipo_str: str, idade: int):
    """Cria um NPC com backstory gerada"""
    try:
        arquetipo = ArchetipoNPC[arquetipo_str.upper()]
    except:
        arquetipo = random.choice(list(ArchetipoNPC))
    
    # Gera backstory
    self.sistema_backstories.adicionar_npc(nome, arquetipo, idade)
    
    # Cria NPC normalmente
    # ... código de criação NPC ...
```

## Step 9: Equipment Management

Add equipping items:

```python
def equipar_item(self, item: Item) -> bool:
    """Equipa um item do inventário"""
    if item.tipo == TipoItem.ARMA:
        return self.equipamento.equipar_arma(item)
    elif item.tipo == TipoItem.ARMADURA:
        return self.equipamento.equipar_armadura(item)
    elif item.tipo == TipoItem.ACESSORIO:
        return self.equipamento.adicionar_acessorio(item)
    return False

def atualizar_stats_com_equipment(self):
    """Atualiza stats do jogador baseado em equipment"""
    # Base stats
    ataque = self.sistemas_progression.ataque_total
    defesa = self.sistemas_progression.defesa_total
    
    # Adiciona bonuses de equipment
    ataque += self.equipamento.bônus_ataque
    defesa += self.equipamento.bônus_defesa
    
    return ataque, defesa
```

## Step 10: UI for New Systems

Update rendering to show:

```python
def renderizar_hud_expandida(self, tela):
    """Renderiza HUD com informações expandidas"""
    # Nível e EXP
    nivel_texto = f"Nível: {self.mundo.sistemas_progression.nivel}"
    # ...
    
    # Equipment display
    if self.mundo.equipamento.arma:
        arma_texto = f"Arma: {self.mundo.equipamento.arma.nome}"
    # ...
    
    # Health /  Mana
    hp = getattr(self.jogador, 'vida_atual', 100)
    hp_max = self.mundo.sistemas_progression.vida_max
    # ...
```

---

## 🎯 Minimal Integration Example

For quick testing, you can integrate just the essentials:

```python
# In your main game tick/update:

# Update mobs
mundo.gerenciador_mobs.atualizar_mobs(delta_time)

# Render mobs
for mob in mundo.gerenciador_mobs.obter_mobs_vivos():
    renderizar_sprite(tela, mob.x, mob.y, mob_sprite_id)
    renderizar_vida_bar(tela, mob.x, mob.y, mob.percentual_vida)

# Check combat
if jogador_ataque_input:
    inimigos_proximos = mundo.gerenciador_mobs.obter_mobs_em_area(
        jogador.x, jogador.y, raio=1
    )
    if inimigos_proximos:
        atacar_inimigo(inimigos_proximos[0])
```

---

## ✅ Testing Checklist

- [ ] Mobs spawn and move correctly
- [ ] Combat calculates damage with equipment
- [ ] Equipment UI shows equipped items
- [ ] Skills can be learned and leveled
- [ ] Biome-specific mobs spawn
- [ ] Dungeons generate and persist
- [ ] Animations play during combat
- [ ] NPC backstories are created
- [ ] Loot drops from defeated mobs
- [ ] Save/load includes new systems

This guide provides the foundation. Each system can be expanded further based on your specific needs!
