# NPC Behavioral & AI Systems Analysis

## 1. NPC DATA STRUCTURE

### Core NPC Data (created in `modelos.py` lines 795-809)
Each NPC has these attributes:
```python
{
    "id": "npc_v1_1",              # Unique identifier
    "nome": "Generated random",      # Name from BancoPersonagens
    "idade": int(18-78),            # Random age
    "papel": str,                   # Social role (from PAPEIS_NPC)
    "vila_id": "v1",                # Village they belong to
    "casa_id": "v1_c1",             # House location
    "pos": [x, y],                  # Current tile position
    "memoria": [],                  # Interaction history
    "relacao": 0,                   # Relationship level with player
    "perfil": {...}                 # Full character profile from BancoPersonagens
}
```

### Profile Fields (from `personagens.py` lines 125-140)
```python
{
    "nome": str,
    "idade": int,
    "papel_social": str,            # "andarilho", "aprendiz", etc.
    "origem": str,                  # Generated backstory: "{name} {origin_template}"
    "corpo": str,                   # Path to body sprite
    "pes": str,                     # Feet sprite
    "pernas": str,                  # Pants sprite
    "camisa": str,                  # Shirt sprite
    "cabelo": str,                  # Hair sprite
    "cabeca": str,                  # Head sprite
    "cor_roupa": [r, g, b],         # Color palette
    "cor_cabelo": [r, g, b],
    "cor_cabeca": [r, g, b],
}
```

### Personality & Preferences (from grep findings)
**Available personality types** in modelos.py (lines 708-720):
- Basic: "timido", "curioso", "agressivo", "calmo"
- Fantasy: "nobre", "selvagem", "misterioso", "alegre", "melancolico", "obsessivo", "astuto", "leal", "traidor", "sarcástico", "compassivo", "destruidor", "protetor", "solitário"

**Additional NPC info fields** (from npc_dialogue_ai.py):
```python
npc_info = {
    "personalidade": "calmo",       # Used in dialogue context
    "afetos": "Neutro",            # Emotional state
    "profissao": "Habitante",      # Profession
    "relacionamento_historico": "Primeiro encontro"
}
```

---

## 2. GAME TIME SYSTEM

### Time Measurement (from `modelos.py` SistemaTempo class)
```python
class SistemaTempo:
    segundos_por_dia: float = 24 * 60  # 1440 seconds per day
    segundos_totais: float              # Cumulative game seconds
    
    # Computed properties:
    @property
    def dia: int                        # Days elapsed (starts at 1)
    @property
    def hora_decimal: float             # 0-24 hour format
    @property
    def horario_formatado: str          # "HH:MM" format
    @property
    def fase: str                       # "manha", "tarde", "anoitecer", "noite"
```

**Time Phases:**
- "manha" (morning): 6:00-12:00
- "tarde" (afternoon): 12:00-18:00
- "anoitecer" (dusk): 18:00-22:00
- "noite" (night): 22:00-6:00

### Calendar System (from `calendar.py`)
```python
class Calendario:
    ano: int                           # Current year
    estacao: Estacao enum              # PRIMAVERA, VERAO, OUTONO, INVERNO
    dia_mes: int                       # 1-28 (each month is 28 days)
    dia_ano: int                       # 1-112
    dias_totais: int
    
    # Each season corresponds to a month:
    # 1-28: Spring, 29-56: Summer, 57-84: Fall, 85-112: Winter
    # Year advances when Spring starts again
```

**Festival System:**
- 4 major festivals per year (one per season)
- Festival data: `Festival(nome, estacao, dia_mes, descricao, premios, npcs_participando, tipo_festival)`
- Types: "colheita", "danca", "competicao", "casamento", "celebracao"

---

## 3. NPC DAILY ROUTINES & SCHEDULING

### Daily Activity Structure (from `npc_relations.py` lines 1-30)

**DiaRotinaAtividade** dataclass:
```python
@dataclass
class DiaRotinaAtividade:
    hora_inicio: int                # 6-22 (24-hour format)
    hora_fim: int
    tipo_atividade: str             # "trabalho", "comer", "dormir", "social", "descanso"
    locacao: tuple[int, int]        # (x, y) tile position
    descricao: str                  # Activity description
```

**RotinaDiaria** dataclass:
```python
@dataclass
class RotinaDiaria:
    npc_nome: str
    atividades: list[DiaRotinaAtividade]
    
    def obter_atividade_atual(hora_decimal: float) -> Optional[DiaRotinaAtividade]:
        """Checks what NPC should be doing at current time"""
```

### Generated Routine Pattern (from `npc_relations.py` lines 170-210)

**ComportamentoNPC.gerar_rotina_randomica()** creates:
```python
# Base pattern (customizable per NPC):
(6, 8, "acordar", "casa", "Acordando e se arrumando")           # 6-8 AM
(8, 12, "trabalho", "local_trabalho", "Trabalhando")           # 8 AM-12 PM
(12, 14, "comer", "taverna", "Comendo e descansando")          # 12-2 PM
(14, 18, "trabalho", "local_trabalho", "Continuando o trabalho") # 2-6 PM
(18, 20, "social", "praca", "Socializando com amigos")         # 6-8 PM
(20, 22, "descanso", "casa", "Descansando")                    # 8-10 PM
(22, 6, "dormir", "casa", "Dormindo")                          # 10 PM-6 AM
```

### NPC Movement System (from `modelos.py`)

**Patrol Route Structure:**
- NPCs follow predefined routes created in `_gerar_roteiros_npcs()`
- Route pattern: Home → Village Center → Nearby Patrol Points → Home
- Movement tracked with: `npc_rotas[npc_id]`, `npc_rota_indice[npc_id]`, `npc_em_casa[npc_id]`

**Movement Update Logic:**
- Calls `atualizar_npcs_movimento(delta_tempo)` each frame
- 1 step per 0.5 seconds movement toward next waypoint
- Can navigate around obstacles
- Waits at target before moving to next

---

## 4. NPC AI & BEHAVIORAL SYSTEMS

### AI-Powered Dialogue System (from `npc_dialogue_ai.py`)

**DialogoIA Class:**
- Generates contextual dialogue per NPC
- Uses Ollama AI with prompt engineering
- **Context provided to AI:**
  ```python
  contexto = f"""
  Personagem NPC: {npc_nome}
  Personalidade: {npc_info.get('personalidade', 'Amigável')}
  Afetos: {npc_info.get('afetos', 'Neutro')}
  Profissão: {npc_info.get('profissao', 'Habitante')}
  Hora do dia: {hora}:00 ({momento_dia})
  
  Jogador:
  Nome: {jogador_info.get('nome', 'Viajante')}
  Profissão: {jogador_info.get('profissao', 'Desconhecida')}
  Relacionamento anterior: {npc_info.get('relacionamento_historico', 'Primeiro encontro')}
  
  Contexto Mundial:
  Estação: {mundo_contexto.get('estacao', 'Primavera')}
  Clima: {mundo_contexto.get('clima', 'Ensolarado')}
  Eventos recentes: {mundo_contexto.get('eventos', 'Nenhum')}
  """
  ```

**Dialogue Caching:**
- One dialogue per hour per NPC (cache_dialogos by `{npc_nome}_{hora_atual}`)
- Fallback templates if Ollama unavailable
- Repeated dialogue shows variation with markers like "(novamente)" or "*repete enquanto sorri*"

**GerenciadorDialogos:**
- Manages all NPC dialogue instances
- Uses `chamar_ollama_pesado(prompt, timeout=15, temperatura=0.8)`
- Extracts dialogue from quoted responses

### Relationship System (from `npc_relations.py`)

**RelacaoNPC dataclass:**
```python
@dataclass
class RelacaoNPC:
    npc_id: str
    npc_nome: str
    coracao: int                    # -10 to 10 (heart value)
    presenteado_hoje: bool          # Gift flag (resets daily)
    ultima_conversa: float          # Timestamp
    conversas_semana: int           # Conversation counter
    
    @property
    def sentimento(self) -> SentimentoNPC:
        # Calculated from coracao:
        # >= 8: APAIXONADO (in love)
        # >= 4: FELIZ (happy)
        # >= 0: NEUTRO (neutral)
        # >= -6: TRISTE (sad)
        # < -6: FURIOSO (furious)
    
    @property
    def pode_casar(self) -> bool:
        # Returns: coracao >= 8
```

**GerenciadorRelacoes:**
- Tracks all NPC relationships
- Manages gift giving (afinidade: -1, 0, 1, 2)
- Conversation cooldown: 1 per hour
- Marriage/divorce/children system
- Daily advancement: `avancar_dia()` degrades relationship if no conversation

### NPC Behavioral Logic (from `npc_relations.py`)

**ComportamentoNPC Class:**
```python
class ComportamentoNPC:
    energia: int (0-100)            # Energy level (decreases with activity)
    felicidade: int (0-100)         # Happiness level
    objetivo_atual: Optional[str]   # Current goal/task
    contador_atividade: int         # Activity counter
    
    def atualizar_estado(horas_passadas: float):
        # Decreases energia by 0.5-2.0 per hour
        # Recovers energia during "descanso" activities (+5 per hour)
    
    def obter_proximidade_reacao(distancia_celulas: float) -> str:
        # "muito_perto" (< 2 tiles)
        # "perto" (2-5 tiles)
        # "visivel" (5-10 tiles)
        # "distante" (> 10 tiles)
    
    def interagir_jogador(tipo_interacao: str) -> str:
        # Types: "conversa", "presente", "trabalho", "saudacao"
        # Modifies response based on felicidade
```

---

## 5. PERSONALITY & TRAIT SYSTEMS

### Basic Backstory System (from `npc_backstories.py`)

**HistoriaBackstory dataclass:**
```python
@dataclass
class HistoriaBackstory:
    nome_npc: str
    arquetipo: ArchetipoNPC          # GUERREIRO, MAGO, LADRÃO, CLÉRIGO, etc.
    idade_natal: int
    origem_lugar: str
    quem_e: str                      # "You are a..."
    por_que_aqui: str                # Why they're in this location
    objetivo_vida: str               # Life goal
    evento_marcante: str             # Life-changing event
    trauma: TraumaMemoria            # PERDA_FAMILIAR, GUERRA, etc.
    sonho_segredo: str               # Secret wish
    npc_relacionado: Optional[str]   # Connection to another NPC
    tipo_relacao: str                # "amigo", "rival", "inimigo", "amor"
    segredo_escondido: str           # Hidden secret
    perigo_segredo: bool             # If revealed, causes problems
    virtudes: List[str]              # "honesto", "corajoso", "compassivo"
    vícios: List[str]                # "ambicioso", "covarde", "guloso"
```

### Lazy-Loading System (from `npc_backstory_lazy.py`)

**HistoriaBackstoryBasica** (always loaded):
```python
nome_npc: str
papel_social: str
idade: int
origem: str
descricao_rapida: str              # Quick summary
tem_familia: bool
detalhada_gerada: bool             # Generated on first interaction?
```

**HistoriaBackstoryDetalhada** (loaded on first interaction):
- Full narrative backstory
- Family tree with TipoFamiliar relationships
- Secret traumas and dreams
- Friend/rival/enemy/love relationships

### Family System

**TipoFamiliar enum:**
```python
PAI, MAE, IRMAO, IRMA, AVOO, AVOA, TIO, TIA,
SOBRINHO, SOBRINHA, PRIMO, PRIMA, MARIDO, ESPOSA,
FILHO, FILHA, ENTEADO, ENTEADA
```

**Family Member Info:**
```python
@dataclass
class FamiliarInfo:
    nome: str
    tipo_relacao: TipoFamiliar
    idade: int
    status: str                     # "vivo", "falecido", "desaparecido"
    local: str                      # "desconhecido" or location
    descricao_rapida: str
    vivo: bool
```

---

## 6. EXISTING AI PATTERNS & FILES

### File Locations & Patterns

| File | Purpose | AI Pattern |
|------|---------|-----------|
| [npc_dialogue_ai.py](jogo/npc_dialogue_ai.py) | NPC dialogue generation | Ollama + prompt context + fallback templates |
| [npc_relations.py](jogo/npc_relations.py) | Relationship & behavior | Rule-based (coracao, sentimiento, daily decay) |
| [quest_generation_ai.py](jogo/quest_generation_ai.py) | Quest generation | Ollama with full world + player lore context |
| [npc_backstories.py](jogo/npc_backstories.py) | Character templates | Fixed template filling + randomly chosen values |
| [npc_backstory_lazy.py](jogo/npc_backstory_lazy.py) | Lazy backstory loading | Template-based, detailed on first interaction |
| [calendar.py](jogo/calendar.py) | Time + festivals | Rule-based seasonal events |

### AI Decision-Making Pattern

**Ollama Integration (Pattern used in all AI files):**
```python
from .servicos import chamar_ollama_pesado

# 1. Extract context
contexto = f"""
Detailed contextual information:
- NPC personality and stats
- World state (time, season, events)
- Player info and relationship
"""

# 2. Create prompt
prompt = f"""
{contexto}

INSTRUCTIONS (detailed, specific)
Respond in Portuguese (Brasil)

Respond ONLY with [JSON/quoted text/etc]
"""

# 3. Call Ollama
resposta = chamar_ollama_pesado(
    prompt=prompt,
    timeout=15,          # seconds
    temperatura=0.7      # 0.5-0.8 typical range
)

# 4. Extract & validate
try:
    result = extrair_e_validar(resposta)
except:
    return fallback_templateado()
```

**Fallback Strategy:**
- Every AI call has a fallback
- Fallback uses templates but still considers context
- No game crashes if Ollama unavailable
- Example: Dialogue defaults to random templates if AI fails

### Temperature Settings (creativity levels)
- **Quest generation (0.7)**: Balanced creativity + coherence
- **Dialogue (0.8)**: More personality variation
- **Standard (0.5)**: Consistent, less random

---

## 7. HOW GAME TIME INTEGRATES WITH NPCs

### Time-Based NPC Activity
1. **Hora Decimal** (0-24) determines current activity stage
2. **RotinaDiaria.obter_atividade_atual(hora_decimal)** checks which activity is active
3. **Movement update** occurs in `atualizar_npcs_movimento()` at configurable intervals
4. **Dialogue context** includes `hora_atual` and `momento_dia` (morning/afternoon/dusk/night)

### Daily Reset
- `GerenciadorRelacoes.avancar_dia()` called when day changes:
  - Resets gift flags
  - Degrades relationship if no conversation (-0.5 if conversas_semana == 0)
  - Resets conversation counter

### Seasonal Events
- Festivals trigger on specific dates
- Certain activities only available in specific seasons
- NPC behavior could be modified per season (not yet implemented)

---

## 8. AVAILABLE PERSONALITY/TRAIT DATA

### Personality Types (14 basic + fantasy)
```python
BASIC: "timido", "curioso", "agressivo", "calmo"
FANTASY: "nobre", "selvagem", "misterioso", "alegre", 
         "melancolico", "obsessivo", "astuto", "leal", 
         "traidor", "sarcástico", "compassivo", "destruidor", 
         "protetor", "solitário"
```

### Social Roles (from PAPEIS_NPC)
```python
"andarilho", "aprendiz", "guardiao", "curandeiro", 
"ferreiro", "caçador", "mercadora", "cronista"
```

### Virtues & Vices (from templates)
```python
VIRTUES: "honesto", "corajoso", "compassivo", "sábio", "leal",
         "justo", "diligente", "humilde", "esperançoso"
VICES: "ambicioso", "guloso", "covarde", "preguiçoso", 
       "invejoso", "irado", "luxurioso", "ganancioso"
```

### Trauma Types
```python
PERDA_FAMILIAR, GUERRA, ESCRAVIDÃO, MALDIÇÃO, 
AMOR_PERDIDO, EXÍLIO, INJUSTIÇA, NENHUM
```

### Activity Types
```python
"acordar", "trabalho", "comer", "dormir", 
"social", "descanso"
```

---

## 9. KEY INTEGRATION POINTS FOR NEW SYSTEMS

### Where to Hook NPC Behavior:
1. **Daily cycle update**: `atualizar_npcs_movimento(delta_tempo)` in `modelos.py`
2. **Dialogue generation**: `DialogoIA.gerar_dialogo_contextual()` in `npc_dialogue_ai.py`
3. **Activity selection**: `RotinaDiaria.obter_atividade_atual()` in `npc_relations.py`
4. **Relationship changes**: `RelacaoNPC` methods in `npc_relations.py`
5. **Personality-based responses**: `interagir_jogador()` in `npc_relations.py`

### Data Flow for Time-Based Changes:
```
game loop (app.py)
  → mundo.tempo.atualizar(delta)
  → get sistema_tempo.hora_decimal
  → for each NPC:
    → check RotinaDiaria.obter_atividade_atual(hora)
    → call atualizar_npcs_movimento()
    → update ComportamentoNPC.energia based on activity type
```

### NPC Decision Making Chain:
```
Player approaches NPC
  → check obter_proximidade_reacao(distancia)
  → trigger interagir_jogador(tipo)
  → call DialogoIA.gerar_dialogo_contextual() with:
     - NPCpersonalidade
     - GameState (time, season, events)
     - Relationship history
  → return dialogue (AI or template fallback)
```

---

## 10. SUMMARY: READY FOR EXPANSION

**What's Implemented:**
✅ Complete time system (down to minute precision)  
✅ Daily routine framework (activities by hour)  
✅ Personality types and traits  
✅ Relationship system with heart values  
✅ AI dialogue generation (Ollama-based)  
✅ Activity-based NPC movement  
✅ Lazy-loaded detailed backstories  
✅ Festival system  

**What's Ready for Enhancement:**
- 🔧 Dynamic personality expression based on sentimento
- 🔧 Goal-oriented behavior (long-term plans)
- 🔧 Inter-NPC relationships and drama
- 🔧 Seasonal behavior variations
- 🔧 Memory-based dialogue callbacks
- 🔧 Emergent scheduling (NPCs react to world events)

