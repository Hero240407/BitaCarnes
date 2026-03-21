# 🌾 BitaCarnes - Guia de Novos Recursos

## O Que Foi Adicionado?

Seu jogo agora possui **7 novos módulos Python** que implementam um sistema completo inspirado em **Stardew Valley**, com tudo gerado por IA (Raphael) para garantir um mundo único a cada playthrough.

---

## 📦 Arquivos Criados

| Arquivo | Função | Classes Principais |
|---------|--------|-------------------|
| `farming.py` | Sistema de agricultura | `FarmManager`, `PlantaCultivada`, `CelulaCultivavel` |
| `npc_relations.py` | Relacionamentos e comportamento de NPCs | `GerenciadorRelacoes`, `ComportamentoNPC`, `RotinaDiaria` |
| `calendar.py` | Calendário, estações e festivais | `Calendario`, `Estacao`, `Festival` |
| `quests.py` | Sistema de missões e objetivos | `QuestManager`, `Quest`, `ObjetivoGeral` |
| `fishing.py` | Minigame de pesca | `MiniGamePesca`, `Peixe`, `HistoricoPesca` |
| `weather.py` | Sistema de clima dinâmico | `SistemaClima`, `TipoClima`, `AlertasClimaticos` |
| `ui_enhanced.py` | Interface melhorada com novos painéis | Funções de renderização para os novos sistemas |

---

## 🎮 Como Funciona

### 1️⃣ **Agricultura (farming.py)**

Cultive plantações como em Stardew Valley:

```python
farm.aradir_terreno(x, y)           # Prepara solo
farm.regar_terreno(x, y)            # Rega a célula
farm.plantar_semente(x, y, "trigo", 4, dia, estacao)
sucesso, info = farm.colher(x, y, plantas_dados)
```

**Características:**
- ✅ Múltiplos tipos de culturas
- ✅ Crescimento realista (dias variáveis)
- ✅ Saúde das plantas afetada por rega
- ✅ Sistema de XP e níveis
- ✅ Dinheiro ganho com colheitas

---

### 2️⃣ **Relacionamentos com NPCs (npc_relations.py)**

Desenvolva relacionamentos e até case-se:

```python
rel = relacao.registrar_npc("npc_001", "João")
relacao.dar_presente("npc_001", "presente_raro", afinidade=2)
relacao.conversar_npc("npc_001", "assunto")
relacao.casar("npc_001")  # Requer 8 corações
filhos = relacao.ter_filho()  # Após 60 dias casado
```

**Características:**
- ✅ Sistema de corações (0-10)
- ✅ Rotinas diárias geradas por IA
- ✅ Degradação de relacionamento
- ✅ Casamento e filhos
- ✅ Estados emocionais (feliz, triste, furioso, etc)

---

### 3️⃣ **Calendário e Estações (calendar.py)**

Sistema completo de tempo com festivais:

```python
eventos = calendario.avancar_dia()  # Avança dia
if eventos["festival"]:
    print(f"Festival: {eventos['festival'].nome}")
    
plantas = calendario.obter_plantas_plantaveis()  # Plantas da estação
lua = calendario.get_lua_fase()  # 🌙 Fase da lua
```

**Características:**
- ✅ 4 estações com 28 dias cada
- ✅ 7 festivais únicos ao longo do ano
- ✅ Fases da lua
- ✅ Plantas variam por estação
- ✅ Eventos sazonais aleatórios

---

### 4️⃣ **Sistema de Quests (quests.py)**

Missões com progresso automático:

```python
quest_manager.ativar_quest("quest_id")
quest.avancar_progresso(1)
sucesso, recompensa = quest_manager.completar_quest("quest_id")
```

**Características:**
- ✅ 9 tipos de quests diferentes
- ✅ Progresso automático
- ✅ Quests repetíveis e diárias
- ✅ Recompensas (ouro, XP, itens)
- ✅ Geração aleatória de quests
- ✅ Histórico de completas

---

### 5️⃣ **Pesca (fishing.py)**

Minigame de pesca interativo:

```python
if pesca.iniciar_pesca("rio", hora, "primavera"):
    sucesso, msg = pesca.tentar_pescagem(duracao_minutos=5)
    if sucesso:
        historico.registrar_captura(pesca.peixe_capturado_nome, pesca.ganho_ouro)
```

**Características:**
- ✅ 7 espécies de peixes
- ✅ 4 níveis de raridade
- ✅ Peixes variam por estação/hora
- ✅ Minigame com durabilidade de linha
- ✅ Histórico de capturas
- ✅ Peixes lendários raros

---

### 6️⃣ **Clima Dinâmico (weather.py)**

Clima afeta todo o gameplay:

```python
clima_tipo, msg = clima.avancar_dia("primavera")
info = clima.obter_info_clima()  # Temperatura, umidade, etc

efeitos_agri = clima.afeta_agricultura()  # Chuva rega automaticamente
efeitos_pesca = clima.afeta_pesca()       # Chuva aumenta raros
efeitos_npc = clima.afeta_npcs()          # Tempestade = NPCs em casa
```

**Características:**
- ✅ 7 tipos de clima diferentes
- ✅ Temperatura, umidade, vento dinâmicos
- ✅ Clima afeta agricultura
- ✅ Clima afeta pesca
- ✅ Clima afeta comportamento de NPCs
- ✅ Iluminação afetada por clima

---

### 7️⃣ **Interface Melhorada (ui_enhanced.py)**

Novos painéis visuais:

```python
renderizar_hud_expandida(tela, calendario, clima, farm, relacoes, quest_manager, rect)
```

**Painéis:**
- 📅 Calendário interativo (próximos festivais)
- 🌤️ Informações detalhadas do clima
- 🌾 Status da fazenda (dinheiro, nível, sementes)
- 💝 Painel de relacionamentos (corações por NPC)
- 📋 Quests ativas com progresso

---

## 🤖 Geração de Conteúdo por IA

Cada aspecto pode ser enriquecido com Raphael:

```python
# Exemplos de como Raphael gera conteúdo único
raphael.gerar_lore_npc(perfil_npc)          # Lore único do NPC
raphael.gerar_dialogo_npc(contexto)         # Diálogo contextual
raphael.gerar_nome_local()                  # Nome de localidade
raphael.gerar_descricao_item(tipo_item)     # Descrição de item
```

### Conteúdo Gerado:
- 🎭 Personalidades e backstories de NPCs
- 💬 Diálogos contextuais personalizados
- 📍 Nomes de locais únicos
- 📜 Descrições de itens e culturas
- 🎯 Quests geradas dinamicamente
- 🎪 Festivais com descrições criativas

---

## ⚙️ Integração com Seu Jogo Atual

Todos os sistemas estão **automaticamente integrados**:

1. **Inicialização automática** em `app.py`
2. **Atualizações diárias** sincronizadas com o game loop
3. **Histórico persistente** no chat de Raphael
4. **Documentação completa** em `STARDEW_FEATURES.md`

---

## 🎯 Exemplos Práticos

### Exemplo 1: Playthroughs Únicos

```python
# Cada jogo tem um mundo completamente diferente:
calendario_1_ano_1 = Calendario(ano_inicial=1)  # Worlds totalmente diferentes
climatologia = SistemaClima()                    # Padrão climático aleatório
farm = FarmManager(tamanho_farm=20)             # Layout único de plantações
npcs_mundo = [...]  # Comportamentos aleatórios via IA
```

### Exemplo 2: Gameplay Emergente

```python
# Clima afeta tudo:
if clima.clima_atual == TipoClima.CHUVOSO:
    # Plantas são regadas automaticamente
    farm_manager.avancar_dia()  # Bonus +0.2 crescimento
    
    # Pesca melhora
    efeitos = clima.afeta_pesca()  # taxa_acelerada = 1.5x
    
    # NPCs podem mudar comportamento
    for npc in npcs:
        rotina_npc.atualizar_por_clima(TipoClima.CHUVOSO)
```

### Exemplo 3: Progressão de Relacionamento

```python
# Dia 1: Conhecer NPC
relacao = relacao_gerenciador.registrar_npc("adrien", "Adrien")
relacao_gerenciador.conversar_npc("adrien", "oi")  # +1 coração

# Dia 5: Presentear
sucesso, msg = relacao_gerenciador.dar_presente("adrien", "flor_luar", 2)  # +2 corações

# Dia 30: Visitar frequentemente
# Corações aumentam para 8+

# Dia 50: Proposta
relacao_gerenciador.casar("adrien")

# Dia 120: Ter filho
relacao_gerenciador.ter_filho()  # filho nomeado aleatoriamente
```

---

## 📖 Documentação Detalhada

Para mais informações completas, veja:
- **[STARDEW_FEATURES.md](STARDEW_FEATURES.md)** - Guia técnico detalhado

---

## 🎨 Próximos Passos (Sugestões)

Para expandir ainda mais:

1. **Adicionar Mineração** (`mining.py`)
   - Minas em profundidade
   - Minérios com raridades
   - Combate em minas

2. **Sistema de Receitas** (`recipes.py`)
   - Culinária e comida
   - Boosts temporários

3. **Casa Expansível** (`housing.py`)
   - Decoração
   - Quartos dos filhos

4. **Profissões** (`professions.py`)
   - Minerador, Pescador, Fazendeiro, etc
   - Bonuses especializados

5. **Multiplayer** (`multiplayer.py`)
   - Jogar com amigos
   - Fazer negócios juntos

---

## ✅ Checklist de Recursos

- ✅ Agricultura com múltiplas culturas
- ✅ NPCs com relacionamentos e casamento
- ✅ Calendário com 4 estações
- ✅ Festivais e eventos
- ✅ Sistema de quests
- ✅ Minigame de pesca
- ✅ Clima dinâmico
- ✅ Interface melhorada com painéis
- ✅ Tudo gerado por IA (Raphael)
- ✅ Mundos únicos por playthrough

---

## 🚀 Como Começar

Basta executar o jogo normalmente:

```powershell
cd c:\Users\Hiro\Documents\VSCode\BitaCarnes
ollama serve
python main.py
```

Todos os novos sistemas funcionam automaticamente no background!

---

## 📝 Notas Técnicas

- **Modularidade**: Cada sistema é independente e pode ser usado isoladamente
- **IA-Ready**: Todos os sistemas são designed para trabalhar com Raphael
- **Performance**: Atualizações otimizadas (não travando o jogo)
- **Extensível**: Fácil adicionar novo conteúdo

---

## 💡 Dicas para Aproveitar

1. **Para NPCs Únicos**: Rode o jogo várias vezes - cada mundo terá NPCs diferentes
2. **Para Descobrir Tudo**: Cheque o calendário para não perder festivais
3. **Para Relações**: Cultive amizades regularmente
4. **Para Ouro**: Colha boas plantações e pesque raros
5. **Para Quests**: Ative sempre que possível para ganho rápido de XP

---

**Divirta-se no Reino de Raphael! 🎮✨**
