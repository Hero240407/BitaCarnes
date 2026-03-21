# 🎮 BitaCarnes - Extensões Stardew Valley

## 📁 Novos Módulos Criados

### 1. **farming.py** - Sistema de Agricultura
- `PlantaCultivada`: Representa uma planta em crescimento
- `CelulaCultivavel`: Células de terra arada para plantio
- `FarmManager`: Gerencia toda a fazenda do jogador
- `SistemaIrrigacao`: Sprinklers automáticos para regar

**Recursos:**
- Arar terreno, regar, plantar sementes
- Colheita com rendimento baseado em saúde da planta
- Múltiplos tipos de solo e fertilizante
- Sistema de experiência agrícola com níveis

---

### 2. **npc_relations.py** - Relacionamento e Comportamento de NPCs
- `SentimentoNPC`: Estados emocionais dos NPCs
- `RotinaDiaria`: Rotinas geradas por IA para cada NPC
- `RelacaoNPC`: Tracking de relacionamentos (corações)
- `GerenciadorRelacoes`: Sistema de casamento e filhos
- `ComportamentoNPC`: IA e comportamento dos NPCs

**Recursos:**
- Sistema de corações (até 10 para romance)
- Presentes para aumentar relacionamento
- Casamento com NPCs
- Ter filhos após 60 dias de casamento
- Rotinas dinâmicas para cada NPC
- Degradação de relacionamento se não conversar

---

### 3. **calendar.py** - Calendário e Estações
- `Estacao`: 4 estações do ano (Primavera, Verão, Outono, Inverno)
- `Calendario`: Sistema completo de datas e festivais
- `Festival`: Eventos especiais (Dança da Primavera, Festa de Colheita, etc)
- `EventoSazonal`: Eventos climáticos especiais por estação

**Recursos:**
- 28 dias por mês, 4 meses por ano
- 7 festivais ao longo do ano
- Fases da lua
- Plantas plantáveis variam por estação
- Efeitos de estação na agricultura e NPCs

---

### 4. **quests.py** - Sistema de Quests e Objetivos
- `TipoQuest`: 9 tipos de quests diferentes
- `StatusQuest`: Estados de quests
- `Quest`: Definição completa de uma missão
- `QuestManager`: Gerência todas as quests
- `ObjetivoGeral`: Objetivos principais do jogo

**Recursos:**
- 9 tipos de quests: coleta, entrega, derrota, descoberta, etc
- Quests repetíveis e diárias
- Progresso rastreado automaticamente
- Recompensas em ouro, EXP e itens
- Quests geradas aleatoriamente
- Histórico de quests completas

---

### 5. **fishing.py** - Minigame de Pesca
- `TipoPeixe`: Raridade de peixes
- `Peixe`: Definição de cada espécie
- `EstadoPesca`: Estado do minigame
- `MiniGamePesca`: Minigame interativo
- `HistoricoPesca`: Rastreia peixes capturados

**Recursos:**
- 7 espécies de peixes com características únicas
- 4 níveis de raridade (comum, incomum, raro, lendário)
- Peixes disponíveis variam por estação e hora
- Durabilidade de linha durante pesca
- Histórico de capturas (peixes não capturados, melhores capturas)
- Valor em ouro variano por tipo

---

### 6. **weather.py** - Sistema de Clima
- `TipoClima`: 7 tipos de clima diferentes
- `CondClima`: Condições detalhadas do clima
- `SistemaClima`: Gerencia clima e afeta gameplay
- `AlertasClimaticos`: Sistema de alertas para eventos perigosos

**Recursos:**
- 7 tipos de clima: ensolarado, nublado, chuva, tempestade, neve, neblina, arco-íris
- Temperatura, umidade, velocidade do vento, visibilidade
- Clima afeta agricultura (chuva rega automaticamente)
- Clima afeta pesca (chuva aumenta chance de raros)
- Clima afeta NPCs (profundos em tempestades ficam em casa)
- Iluminação dinâmica baseada em hora e clima

---

### 7. **ui_enhanced.py** - Interface Aprimorada
Novos componentes de UI:
- `renderizar_calendario_expandido()`: Mostra calendário interativo
- `renderizar_clima_detalhado()`: Informações detalhadas do clima
- `renderizar_painel_fazenda()`: Status da fazenda
- `renderizar_relacoes_npcs()`: Painel de relacionamentos
- `renderizar_quests_painel()`: Lista de quests ativas
- `renderizar_hud_expandida()`: HUD completo com todos os painéis
- `renderizar_tela_pesca()`: Interface do minigame de pesca

---

## 🔗 Integração em app.py

Os novos sistemas são inicializados automaticamente:

```python
# Sistemas Stardew Valley
farm_manager = FarmManager(tamanho_farm=20)
relacao_gerenciador = GerenciadorRelacoes()
calendario = Calendario(ano_inicial=1)
quest_manager = QuestManager()
objetivo_geral = ObjetivoGeral()
pesca_manager = MiniGamePesca()
historico_pesca = HistoricoPesca()
clima_sistema = SistemaClima()
```

E são atualizados diariamente:

```python
# Avança calendário
eventos_calendario = calendario.avancar_dia()

# Avança clima
clima_tipo, msg_clima = clima_sistema.avancar_dia(calendario.estacao.value)

# Atualiza farm
farm_manager.avancar_dia()

# Atualiza relacionamentos
relacao_gerenciador.avancar_dia()

# Atualiza quests
quest_manager.avancar_dia()
```

---

## 📊 Geração de Conteúdo por IA

Todos os sistemas são projetados para trabalhar com **Raphael** (Ollama):

1. **NPCs**: Rotinas, comportamentos e falas geradas por IA
2. **Eventos**: Festivais e eventos dinâmicos personalizados
3. **Quests**: Missões aleatórias baseadas em IA
4. **Lore Mundial**: Descrições de locais e itens geradas por IA
5. **Diálogos**: Conversas com NPCs personalizadas

---

## 🎯 Como Usar os Novos Sistemas

### Agricultura
```python
farm_manager.aradir_terreno(10, 10)  # Ara terreno
farm_manager.regar_terreno(10, 10)   # Rega
farm_manager.plantar_semente(10, 10, "trigo", 4, 1, "primavera")
sucesso, info = farm_manager.colher(10, 10, PLANTAS_DISPONIVEIS)
```

### Relacionamentos
```python
npc = relacao_gerenciador.registrar_npc("npc_001", "João")
sucesso, msg = relacao_gerenciador.dar_presente("npc_001", "presente_raro", 2)
relacao_gerenciador.casar("npc_001")
relacao_gerenciador.ter_filho()
```

### Quests
```python
quest_manager.ativar_quest("quest_colheita_inicial")
quest = quest_manager.obter_quest("quest_colheita_inicial")
quest.avancar_progresso(1)
sucesso, recompensa = quest_manager.completar_quest("quest_colheita_inicial")
```

### Pesca
```python
if pesca_manager.iniciar_pesca("rio", hora_decimal, "primavera"):
    sucesso, mensagem = pesca_manager.tentar_pescagem(5)
    if sucesso:
        historico_pesca.registrar_captura(pesca_manager.peixe_capturado_nome, pesca_manager.ganho_ouro)
```

### Clima
```python
info_clima = clima_sistema.obter_info_clima()
efeitos_agri = clima_sistema.afeta_agricultura()
efeitos_pesca = clima_sistema.afeta_pesca()
efeitos_npcs = clima_sistema.afeta_npcs()
```

---

## 🌍 Mundo Único

Cada aspecto do jogo incorpora IA para máxima variação:

1. **Cada playthrough tem**:
   - Diferentes NPCs com personalidades únicas
   - Rotinas de NPCs geradas por IA
   - Quests aleatórias personalizadas
   - Clima dinâmico afetando gameplay
   - Festivais com eventos especiais
   - Distribuição variável de peixes
   - Descrições de lore do mundo

2. **Sem conteúdo repetitivo**: Graças à IA, mensagens, diálogos e eventos são contextuais

3. **Gameplay emergente**: Os sistemas interagem uns com os outros (clima afeta NPC, que afeta relacionamentos, etc)

---

## 📝 Exemplos de Uso

### Criar uma fazenda próspera
```python
# Dia 1: Começar com sementes de trigo
farm_manager.adicionar_sementes("trigo", 5)
farm_manager.aradir_terreno(0, 0)
farm_manager.regar_terreno(0, 0)
farm_manager.plantar_semente(0, 0, "trigo", 4, 1, "primavera")

# Dia 4: Colher e ganhar ouro
sucesso, info = farm_manager.colher(0, 0, PLANTAS_DISPONIVEIS)
print(f"Colheu {info['quantidade']} unidades por {info['valor']} ouro!")
```

### Desenvolver relacionamento
```python
# Conversar com NPC
relacao_gerenciador.conversar_npc("npc_001", "assunto_casual")

# Dar presente
sucesso, msg = relacao_gerenciador.dar_presente("npc_001", "flor_luar", 2)

# Após 8 corações, pode casar
if relacao_gerenciador.obter_relacao("npc_001").pode_casar:
    relacao_gerenciador.casar("npc_001")
```

### Sistemas conectados
```python
# Chuva (clima) rega automaticamente plantações (farm)
efeitos = clima_sistema.afeta_agricultura()
if efeitos["regadura_automatica"]:
    for celula in farm_manager.celulas_cultivo.values():
        celula.regar()

# Tempestade (clima) deixa NPCs em casa (NPC behavior)
efeitos_npc = clima_sistema.afeta_npcs()
if efeitos_npc["npcs_dentro_casa"]:
    # Atualizar rotinas dos NPCs
```

---

## 🎨 Esperado no Futuro

Melhorias planejadas:
- Sistema de minério e mineração 🪨
- Casa expansível e decoração 🏠
- Animais domésticos 🐔🐑
- Comunidade Center equivalente 🏛️
- Receitas e culinária 🍳
- Profissões especializadas ⚔️🧙
- Music e som dinâmicos 🎵
- Multiplayer/cooperativo 👥

