# AI-Powered Quest Generation System

## Overview

Your quest system is now **AI-integrated and fully contextual** to world lore, player backstory, and Raphael's observations. Every quest is dynamically generated based on:

- **World Lore**: Prophecies, conflicts, legends, eras, mystical places
- **Player Background**: Origin, legacy, motivation, secret  
- **Game State**: Player morale, current inventory, progress
- **Raphael's Wisdom**: Observations of player actions and world state

## Features

### 1. **Dynamic AI Quest Generation**

When you request a quest or Raphael offers one, the system:

1. **Extracts Context** from:
   - World lore (prophecy, conflict, legend)
   - Player profile (origin, legacy, motivation)
   - Raphael's memory (events, conversations)
   - Current game state (HP, food, progress)

2. **Sends to Ollama** with full context about world and player

3. **Generates Unique Quests** that:
   - Reference specific prophecies and conflicts
   - Consider player's background/motivation
   - Feel narratively connected to the world
   - Have appropriate difficulty and rewards

4. **Fallback System** - If Ollama unavailable:
   - Still uses world lore templates
   - Still considers player origin
   - Graceful degradation (not generic)

### 2. **Special Quest Types**

#### **Dynamic Contextual Quest** (!quest / !missao)
```
Requests: "!quest" or "!missao"
Generates: General contextual quest based on all world/player lore
Example outcome:
  "Os guardiões da profecia antiga observam você. 
   Como descendente de cartógrafos, você pode mapear 
   as localizações onde os dragões rivais se alimentam de mana."
```

#### **Prophecy-Driven Quest** (!profecia / !prophecy)
```
Requests: "!profecia" or "!prophecy"  
Focuses: Specifically on world prophecy
Generates: Quest that moves you toward fulfilling prophecy
Example:
  "A profecia diz que você quebrará a sétima selagem.
   Primeiro, você deve encontrar 3 cristais antigos."
```

#### **Conflict Quest** (!conflito / !conflict)
```
Requests: "!conflito" or "!conflict"
Focuses: On main world conflict  
Generates: Quest that involves you in the conflict
Example:
  "Os Dragões Rivais reclamam apoio. Escolha uma facção
   e recolha amostras de mana de suas terras."
```

### 3. **Quest Data Generated**

Each AI-generated quest includes:

```python
{
    "nome": "Unique quest title",
    "descricao": "Narrative description tied to lore",
    "tipo": "coleta|entrega|derrota|descoberta|...",
    "dificuldade": 1-5,
    "recompensa_ouro": 50-500,
    "recompensa_exp": 100-2000,
    "npc_giver": "NPC or Raphael",
    "ai_generated": true,
    "lore_connection": "How it connects to world/player lore"
}
```

## In-Game Usage

### Chat Commands (Press R to activate)

```
!quest, !missao, !questao
→ Generates contextual AI quest from Raphael
→ Uses world prophecies, conflicts, and player background

!profecia, !prophecy  
→ Generates quest specifically about the world prophecy
→ Moves you toward prophecy fulfillment

!conflito, !conflict
→ Generates quest about the main world conflict  
→ Involves you in factional/world disputes

!history, !historico, !stats, !estatisticas
→ View action history (from previous system)

!recent, !recentes
→ View last 15 actions (from previous system)
```

## How World Lore is Used

### Prophecy Integration
```
World Generated:
  "profecia": "Bentoira quebrará a sétima selagem e libertará o caos"

Quest Generated:
  "A profecia que Raphael murmurou sobre você volta à memória:
   talvez você deva investigar as sete selagens antigas."
```

### Conflict Integration
```
World Generated:
  "conflito_principal": "Batalha entre Dragões Rivais pelo domínio"

Quest Generated:
  "Um dragão azul e um dourado disputam terras. Ambos precisam
   de coletas de mana especial. Sua escolha terá consequências."
```

### Raphael's Condition Integration
```
World Generated:
  "condicao_raphael": "Raphael está dividido entre misericórdia e justiça"

Quest Generated:
  "Raphael, dividido internamente, oferece uma quest de escolha moral.
   Salvar inocentes OU punir agressores — qual caminho?"
```

## How Player Lore is Used

### Origin Impact
```
Player Profile:
  "origem": "cresceu entre ruinas antigas e plantações"

Quest Generated:
  "Como alguém que entende ruinas antigas, você reconhece os símbolos.
   Investigar esta estrutura antiga pode revelar segredos..."
```

### Legacy Impact
```
Player Profile:
  "legado": "descendente de cartógrafos do norte"

Quest Generated:
  "Seus antepassados cartógrafos mapearam essas terras. Talvez você
   possa completar seus mapas antigos explorando regiões perdidas."
```

### Motivation Impact
```
Player Profile:
  "motivacao": "reunir as 7 chaves sagradas"

Quest Generated:
  "Rumores falam de uma chave sagrada escondida nas ruinas ao norte.
   Sua motivação de reunir as 7 chaves pode finalmente ter prosseguimento."
```

### Secret Impact
```
Player Profile:
  "segredo": "carrega um símbolo antigo que reage a mana"

Quest Generated:
  "Seu símbolo antigo brilha perto da biblioteca. Algo ali
   reage especificamente ao seu artefato..."
```

## Technical Implementation

### File Structure
```
jogo/
├── quest_generation_ai.py          ← New AI quest generation module
├── modelos.py                       ← Updated with AI quest generation
├── app.py                          ← Updated with new chat commands
└── quests.py                       ← Existing quest system
```

### Key Functions

**`gerar_quest_dinamica_ai(mundo, memoria, dificuldade, tipo)`**
- Main AI quest generation function
- Uses Ollama with full world/player context
- Returns quest data dictionary
- Has fallback system if Ollama unavailable

**`gerar_quest_prophecy(mundo, memoria)`**
- Specifically generates prophecy-focused quests
- Helps you move toward world prophecy
- Higher difficulty/rewards

**`gerar_quest_conflito_principal(mundo, memoria)`**
- Generates conflict-focused quests  
- Involves you in main world dispute
- Moral choice opportunities

**`extrair_contexto_mundo(mundo)`**
- Formats all world lore into prompt context
- Includes prophecy, conflict, legend, etc.

**`extrair_contexto_jogador(mundo)`**
- Formats player lore into prompt context
- Includes origin, legacy, motivation, secret

### Prompt Strategy

The system sends Ollama a detailed prompt containing:

1. **World Context**: Full lore (prophecies, conflicts, legends, eras)
2. **Player Context**: Full profile (origin, legacy, motivation, secrets)
3. **Game State**: Current HP, food, progress, NPCs known
4. **Quest Requirements**: Difficulty level, type preference, narrative instructions
5. **Raphael's Wisdom**: His perspective on player actions

Example prompt snippet:
```
"CONTEXTO DO MUNDO:
- Profecia: Bentoira quebrará a sétima selagem e libertará o caos
- Conflito Principal: Batalha entre Dragões Rivais
- Eixo Histórico: Uma chuva de mana alterou a história...

CONTEXTO DO JOGADOR:
- Nome: Bentoira
- Origem: cresceu entre plantações e ruinas antigas
- Legado: descendente de cartógrafos do norte
- Motivação: reunir as 7 chaves sagradas
- Segredo: carrega um símbolo antigo que reage a mana

Gere uma quest que:
1. Use elementos da profecia
2. Conecte ao conflito principal
3. Considere a origem/motivação do jogador
4. Seja significativa e narrativa"
```

## Performance & Safety

### Offline Support
- If Ollama is unavailable, system uses **fallback templated quests**
- Fallback quests still consider world/player context
- No game crashes on AI timeout (30-second timeout with fallback)

### Token Efficiency
- Uses `chamar_ollama_pesado()` (temperature=0.7) - balanced creativity
- Queries limited to 30 seconds max
- Context compressed to essential lore elements

### Safety
- JSON parsing with error handling
- Validation of returned quest data
- Guaranteed quest structure even if parsing fails

## Advantages Over Previous System

| Aspect | Before | After |
|--------|--------|-------|
| Quest Generation | Hardcoded 4 choices | AI-generated unlimited variety |
| World Lore Usage | Only terrain theme | Full prophecy/conflict integration |
| Player Lore Usage | Name only | Full origin/legacy/secret consideration |
| Quest Personalization | Generic | Contextual to player background |
| World Narrative | Disconnected | Integrated quest chains |
| Player Motivation | Unused | Drives quest themes |

## Future Enhancements

Possible additions:
1. **Quest Chains** - Multi-step quest lines toward prophecy fulfillment
2. **NPC-Specific Quests** - Each NPC generates quests based on their role
3. **Dynamic Rewards** - Quest rewards change based on player lore
4. **Reputation System** - Quest impacts on NPC relations
5. **World Events to Quests** - Events automatically spawn related quests
6. **Prophecy Progress Tracking** - Quests track movement toward prophecy
7. **Legacy Quests** - Special quests based on player's family legacy

## Example Playthroughs

### Scenario 1: Maritime Explorer Origin
```
Player Background:
- Name: Nautilus
- Origin: "aprendeu a navegar entre ilhas misteriosas"
- Legacy: "herdeiro de antigos exploradores"
- Motivation: "descobrir o continente perdido"

Generated Quest:
"Como herdeiro de antigos exploradores, você sente o chamado.
 Rumors say the lost continent leaves artifacts on beaches.
 Colete 5 artefatos antigos de explorer."
```

### Scenario 2: Chosen One for Prophecy
```
World Prophecy:
- "Bentoira quebrará a sétima selagem e libertará o caos"

Player Background:
- Name: Bentoira
- Motivation: "estar à altura de seu destino"

Generated Quest:
"A profecia que Raphael sussurra te segue. Para quebrar a sétima
 selagem, você primeiro deve aprender com os Guardiões Antigos.
 Encontre 3 Guardiões e aprenda seus ensinamentos."
```

## Conclusion

Your quest system is now **narrative-first, lore-integrated, and AI-powered**. Every quest feels like it belongs to your unique world and tells your specific story. The system combines:

✓ World-building depth (prophecies, conflicts, legends)
✓ Character development (origin, legacy, motivation)  
✓ AI intelligence (context-aware generation)
✓ Failsafe design (works offline with templates)
✓ Player agency (special commands for quest types)

This transforms quests from generic tasks into **narrative extensions of your game world**.
