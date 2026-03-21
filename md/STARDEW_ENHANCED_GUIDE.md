# BitaCarnes - Stardew Valley Enhanced Edition

## Overview

BitaCarnes has been significantly enhanced with Stardew Valley-like features, AI integration, and visual/UI improvements. This document outlines all new systems and how to use them.

---

## New Systems Added

### 1. **Enhanced UI System** (`ui_enhancements.py`)

Modern, Stardew Valley-inspired UI components with smooth animations and polish.

#### Components:

**MenuAnimado** - Animated menu with smooth transitions
```python
from jogo.ui_enhancements import MenuAnimado

menu = MenuAnimado("Menu Principal", ["Começar", "Configurações", "Sair"])
menu.desenhar(tela, fonte)
```

**BarraProgresso** - Animated progress bars for HP, food, morale
```python
barra = BarraProgresso(largura=200, cor_cheia=(0, 200, 100))
barra.atualizar(0.75)
barra.desenhar(tela, x=10, y=10, rotulo="HP")
```

**TooltipSistema** - Hover tooltips for UI elements
```python
tooltip = TooltipSistema()
tooltip.atualizar_tooltip("Informação útil")
tooltip.desenhar_tooltip(tela, x=100, y=50, fonte=fonte)
```

**PainelInventarioVisual** - Enhanced inventory display
```python
inventario = PainelInventarioVisual(width=300)
inventario.adicionar_item("Madeira", 50, "Material local")
inventario.desenhar(tela, x=10, y=50, fonte_pequeno=fonte_p, fonte_normal=fonte_n)
```

**IndicadorSocial** - NPC relationship and emotion display
```python
indicador = IndicadorSocial("Elias", coracao=7, emocao="Feliz")
indicador.desenhar(tela, x=300, y=10, fonte=fonte)
```

---

### 2. **AI-Powered NPC Dialogue System** (`npc_dialogue_ai.py`)

Contextual, AI-generated dialogue for NPCs using Ollama integration.

#### Features:
- **Contextual Conversations**: Dialogue changes based on time of day, season, weather, and NPC state
- **Emotion-Based Responses**: NPCs react differently based on their sentiment
- **Conversation Memory**: System tracks conversation history with each NPC
- **Fallback System**: Template dialogues when AI unavailable
- **One Dialogue Per Hour**: Caching prevents spam, ensures variety

#### Usage:

```python
from jogo.npc_dialogue_ai import SistemaConversas

sistema_conversas = SistemaConversas()

# Register NPC
npc_info = {
    'personalidade': 'Amigável',
    'profissao': 'Ferreiro',
    'relacionamento_historico': 'Novo amigo'
}

# Start conversation
dialogo = sistema_conversas.iniciar_conversa(
    npc_nome="Elias",
    jogador_info={'nome': 'Você', 'profissao': 'Aventureiro'},
    npc_info=npc_info,
    mundo_contexto={'estacao': 'Primavera', 'clima': 'Ensolarado'},
    hora=14
)

print(dialogo)  # AI-generated unique dialogue
```

#### NPC Dialogue States:
- **Contexto do NPC**: Personalidade, profissão, relacionamento anterior
- **Contexto do Jogador**: Nome, nível, origem, legado
- **Contexto do Mundo**: Estação, clima, hora, eventos recentes

---

### 3. **Location-Based Ambiance System** (`location_ambiance.py`)

Stardew Valley-style biome system with atmospheric effects.

#### Biomes:
- **CAMPO** (Field) - Peaceful, warm, windy
- **FLORESTA** (Forest) - Cool, damp, mystical
- **MONTANHA** (Mountain) - Cold, rarefied, scenic
- **AGUA** (Water) - Wet, abundant, peaceful
- **DESERTO** (Desert) - Hot, sparse, mysterious
- **CAVERNA** (Cave) - Dark, echo-ing, mineral-rich
- **CIDADE** (City) - Social, busy, warm
- **SANTUARIO** (Sanctuary) - Sacred, magical, peaceful

#### Features:
- **Automatic Biome Detection**: Procedural determination based on world position
- **Atmospheric Colors**: Unique light colors per biome
- **Fog Effects**: Biome-specific fog/haze
- **Ambient Particles**: Falling leaves, dust, snow, etc.
- **Environmental Description**: Rich location descriptions

#### Usage:

```python
from jogo.location_ambiance import GerenciadorAmbiance

gerenciador = GerenciadorAmbiance()

# Get ambiance for location
ambiance = gerenciador.obter_ambiance(x=100, y=150, biomas_mapa={})

print(ambiance.descricao)  # Rich atmosphere description
print(ambiance.cores_ambiente)  # RGB tuple for biome color
print(ambiance.temperatura)  # Temperature: -20 to 50°C

# Get detailed location description
localizacao = gerenciador.obter_descricao_localizacao(100, 150, {})
print(localizacao)
```

#### Time & Weather Effects:
```python
from jogo.location_ambiance import SistemaTempoAmbiane

sistema_tempo = SistemaTempoAmbiane()
sistema_tempo.hora_atual = 18
sistema_tempo.clima_atual = "Chuvoso"

# Get lighting based on time
luz = sistema_tempo.obter_intensidade_luz()  # 0.0 to 1.0

# Get color modification based on time/weather
modificador = sistema_tempo.obter_modificador_cores()  # RGB multipliers
```

---

### 4. **World Interactions System** (`world_interactions.py`)

Expanded world with interactive objects, events, and exploration perks.

#### Interactive Objects:

**Object Types:**
- **RECURSO** - Gatherable resources (food, wood)
- **DECORACAO** - Visual only
- **ESTRUTURA** - Buildings/ruins
- **CRIATURA** - Wildlife encounters
- **ARTEFATO** - Magical artifacts
- **PORTAL** - Hidden passages
- **TUMULO** - Historical sites
- **MONUMENTO** - Landmarks

#### Predefined Objects:
- Pedra Antiga (Ancient Stone) - Wisdom/knowledge rewards
- Túmulo de Aventureiro (Adventurer Tomb) - Treasure, lore
- Cachoeira Sagrada (Sacred Waterfall) - Restoration, morale
- Árvore de Cristal (Crystal Tree) - Mana, gold
- Ruínas Cidade Antiga (Ancient City Ruins) - Knowledge, artifacts
- Santuário Perdido (Lost Sanctuary) - Blessings, knowledge
- Ninho Raro (Rare Nest) - Rare creatures
- Floresta Encantada (Enchanted Forest) - Magic materials
- Poço dos Desejos (Wishing Well) - Luck, gold
- Templo em Ruínas (Ruined Temple) - Relics, knowledge

#### Usage:

```python
from jogo.world_interactions import GerenciadorObjetos

gerenciador = GerenciadorObjetos()

# Generate world objects procedurally
gerenciador.gerar_objetos_procedural(tamanho_mundo=50, densidade=0.02)

# Find nearby objects
proximos = gerenciador.obter_objetos_proximo(x=25, y=25, raio=5)

for obj in proximos:
    print(f"{obj.nome} - {obj.descricao}")
    if obj.pode_interagir():
        resultado = gerenciador.interagir_objeto(obj.id)
        print(resultado)

# Track exploration progress
progresso = gerenciador.obter_progresso_exploracao()
print(f"Explorado: {progresso['percentual_exploracao']:.1f}%")
```

#### Dynamic World Events:

```python
from jogo.world_interactions import SistemaPovoado

sistema = SistemaPovoado()

# Generate random encounters
evento = sistema.gerar_evento(x=30, y=40)
if evento:
    print(f"Encontro: {evento['nome']}")
    print(f"Descrição: {evento['descricao']}")
    print(f"Reação: {evento['reacao']}")

# Possible events:
# - Trader (compra/venda)
# - Lost traveler (quest)
# - Wild creature (combat)
# - Treasure (loot)
# - Festival (gathering)
```

#### World Progression Tracking:

```python
from jogo.world_interactions import SistemaProgresso

progresso = SistemaProgresso()

# Register discoveries
progresso.registrar_descoberta("Floresta Leste")
progresso.registrar_evento("evento_tesouro_001")

# Track world changes (e.g., destroyed building)
progresso.aplicar_mudanca_mundo(
    "50_60",
    {"tipo": "destruido", "antes": "Casa", "descricao": "Ruínas de uma casa"}
)
```

---

## Integration with Existing Systems

### With Farming System
- **Location-based crops**: Certain crops only grow in specific biomes
- **Seasonal ambiance**: Different colors/atmosphere per season
- **Weather effects on yield**: Affected by real climate simulation

### With NPC System
- **Dynamic routines**: NPCs use location ambiance and interactions
- **Relationship tracking**: Dialogue affects relationship hearts
- **Gift preferences**: NPCs prefer items from certain biomes

### With Quest System
- **Location-based quests**: Quests generated for discovered objects/locations
- **Exploration rewards**: Finding objects generates lore/quests
- **NPC interaction quests**: Dialogue choices create quest branches

### With Combat System
- **Creature encounters**: Dynamic enemy placement in ambiances
- **Biome difficulty**: Stronger creatures in deeper caves/mountains
- **Environmental challenges**: Biome hazards (cold mountain, desert heat)

---

## Configuration & Customization

### Adding New Biomes

```python
# In location_ambiance.py
from location_ambiance import Ambiance, TipoBioma

novo_bioma = Ambiance(
    bioma=TipoBioma.NOVO,
    descricao="Descrição do bioma",
    cores_ambiente=(100, 150, 200),
    cor_neblina=(150, 180, 220),
    intensidade_neblina=0.3,
    efeitos_particulas=["exemplo1", "exemplo2"],
    sons_ambiente=["som1", "som2"],
    temperatura=15,
    umidade=65,
)
```

### Adding New Interactive Objects

```python
# In world_interactions.py
GerenciadorObjetos.OBJETOS_PADRAO["novo_objeto"] = {
    "nome": "Nome do Objeto",
    "tipo": TipoObjeto.ESTRUTURA,
    "descricao": "Descrição detalhada",
    "recompensa": {"ouro": 50, "conhecimento": 5},
    "cooldown": 300,  # Turns until next interaction
}
```

### Adjusting NPC Dialogue Frequency

```python
# In npc_dialogue_ai.py
# Modify SistemaConversas.max_tempo_espera in TooltipSistema
# Lower = more frequent dialogue refresh
# Higher = less chatty
```

---

## Performance Considerations

1. **Dialogue Caching**: One dialogue per NPC per hour prevents excessive AI calls
2. **Biome Procedural Generation**: Uses seeded randomness for consistency without storage
3. **Object Pooling**: Interactive objects are pooled and reused
4. **Ambiance Transitions**: 60-frame smooth transitions prevent visual jarring
5. **Event Frequency**: 5% base encounter chance, adjustable per zone

---

## Future Enhancement Ideas

### Phase 2:
- [ ] NPC marriage/family system integration
- [ ] Seasonal festival cutscenes with AI narration
- [ ] Dynamic weather effects on gameplay
- [ ] Quest reward scaling based on world state
- [ ] Environmental storytelling (decaying structures, growth over time)

### Phase 3:
- [ ] Multi-language dialogue support (AI translation)
- [ ] Player reputation system affecting NPC behavior
- [ ] Procedural dungeon generation with story context
- [ ] Wildlife breeding and evolution system
- [ ] Custom worldbuilding via player actions

---

## Known Limitations

1. **AI Dialogue Timeout**: Falls back to templates if Ollama takes >15 seconds
2. **Memory Usage**: Large worlds (1000+ objects) may impact performance
3. **Biome Boundaries**: Procedural biome generation has hard boundaries, not gradual transitions
4. **NPC AI Calls**: Each dialogue requires API call; cache mitigates but still limited

---

## Testing Checklist

- [ ] Load game and verify UI components render smoothly
- [ ] Talk to NPC and receive unique AI dialogue
- [ ] Walk to different biomes and observe color/ambiance changes
- [ ] Find and interact with world objects
- [ ] Check that encounters generate randomly
- [ ] Verify NPC dialogue caches work (talk twice in one hour)
- [ ] Test fallback systems with Ollama offline
- [ ] Verify no performance degradation with full world

---

## Credits & Attribution

- **Stardew Valley** - Inspiration for game design and UX
- **Ollama** - AI backbone for dynamic content
- **Pygame** - Rendering foundation
- **Community** - Feature suggestions and testing
