# ⚡ QUICK REFERENCE - Cheat Sheet dos Novos Sistemas

## 🌾 Agricultura - FarmManager

```python
# Criação
farm = FarmManager(tamanho_farm=20)

# Ações básicas
farm.aradir_terreno(x, y)                    # Prepara solo
farm.regar_terreno(x, y)                     # Rega
farm.plantar_semente(x, y, tipo, dias, dia, estacao)  # Planta
sucesso, info = farm.colher(x, y, plantas_dados)      # Colhe

# Inventário
farm.adicionar_sementes("trigo", 5)
farm.obter_sementes_disponiveis()            # Dict de sementes

# Status
farm.dinheiro
farm.nivel_agricultura
farm.exp_agricultura
farm.celulas_cultivo[(x, y)]                 # Acessa célula
```

---

## 💝 Relacionamentos - GerenciadorRelacoes

```python
# Criar/acessar
rel_mgr = GerenciadorRelacoes()
npc = rel_mgr.registrar_npc("npc_001", "João")
relacao = rel_mgr.obter_relacao("npc_001")

# Interações
sucesso, msg = rel_mgr.dar_presente("npc_001", "presente_tipo", 2)
sucesso, msg = rel_mgr.conversar_npc("npc_001", "assunto")

# Status
relacao.coracao                              # 0-10 corações
relacao.sentimento                           # SentimentoNPC enum
relacao.pode_casar                           # bool

# Casamento
rel_mgr.casar("npc_001")                    # Requer 8 corações
rel_mgr.divorciar()
rel_mgr.ter_filho()                         # Após 60 dias

# Atualizar
rel_mgr.avancar_dia()                       # Diário
```

---

## 📅 Calendário - Calendario

```python
# Criação
cal = Calendario(ano_inicial=1)

# Avançar
eventos = cal.avancar_dia()
if eventos['novo_dia']: ...
if eventos['novo_mes']: ...
if eventos['nova_estacao']: ...
if eventos['novo_ano']: ...
if eventos['festival']: print(eventos['festival'].nome)

# Status
cal.ano, cal.estacao, cal.dia_mes            # Valores
cal.estacao_nome                             # "Primavera" etc
cal.data_formatada                           # String formatada
cal.get_lua_fase()                           # "🌙 Lua Cheia"

# Informações
cal.obter_plantas_plantaveis()               # Lista de tipos
cal.obter_proximos_festivais(5)              # Próximos 5
festival = cal.obter_festival_de_hoje()
dias_colheita = cal.obter_dias_para_proxima_colheita()
```

---

## 🎯 Quests - QuestManager

```python
# Criação
quest_mgr = QuestManager()

# Operações
quest_mgr.ativar_quest("quest_id")
quest = quest_mgr.obter_quest("quest_id")
quest.avancar_progresso(1)
sucesso, recompensa = quest_mgr.completar_quest("quest_id")
quest_mgr.falhar_quest("quest_id")

# Status
quest.status                                 # StatusQuest enum
quest.quantidade_completa / quest.objetivo_quantidade
quest_mgr.quests_ativas                      # Lista IDs
quest_mgr.obter_quests_ativas()             # Lista Quest objects
quest_mgr.obter_quests_disponiveis()
quest_mgr.obter_quests_completas()

# Gerar novo
nova_quest = quest_mgr.gerar_quest_randomica()
quest_mgr.registrar_quest(nova_quest)

# Atualizar
quest_mgr.avancar_dia()
```

---

## 🎣 Pesca - MiniGamePesca

```python
# Inicializar
pesca = MiniGamePesca()

# Jogar
if pesca.iniciar_pesca("rio", hora_decimal, "primavera"):
    sucesso, mensagem = pesca.tentar_pescagem(duracao_minutos=5)
    
# Resultado
pesca.peixe_capturado_nome                   # String
pesca.ganho_ouro                             # Int
pesca.ganho_exp                              # Int

# Informações
info = pesca.obter_info_peixe_atual()
info['nome'], info['raridade'], info['valor']
info['durabilidade_linha']
info['posicao_peixe'], info['posicao_anzol']

# Histórico
historico = HistoricoPesca()
historico.registrar_captura("Truta", 75)
stats = historico.obter_estatisticas()
peixes_nao_capturados = historico.obter_peixes_nao_capturados()
```

---

## 🌤️ Clima - SistemaClima

```python
# Criação
clima = SistemaClima()

# Avançar
tipo_clima, msg = clima.avancar_dia("primavera")

# Status
info = clima.obter_info_clima()
info['tipo']                                 # "chuvoso"
info['temperatura'], info['umidade']
info['vento'], info['visibilidade']
info['emoji'], info['descricao']

# Efeitos por sistema
efeitos_agri = clima.afeta_agricultura()
efeitos_agri['pode_plantar'], ['pode_colher']
efeitos_agri['regadura_automatica']
efeitos_agri['bonus_crescimento']

efeitos_pesca = clima.afeta_pesca()
efeitos_pesca['pode_pescar']
efeitos_pesca['taxa_acelerada']
efeitos_pesca['peixes_raros_aumentado']

efeitos_npc = clima.afeta_npcs()
efeitos_npc['npcs_dentro_casa']
efeitos_npc['mood_ajuste']

# Iluminação
light = clima.calcula_iluminacao_dia(hora_decimal)  # 0.0-1.0
```

---

## 🎨 UI Aprimorada - ui_enhanced

```python
# Simples
renderizar_calendario_expandido(tela, calendario, rect)
renderizar_clima_detalhado(tela, clima, rect)
renderizar_painel_fazenda(tela, farm, rect)
renderizar_relacoes_npcs(tela, relacoes, rect, max_npcs=5)
renderizar_quests_painel(tela, quest_mgr, rect, max_quests=4)

# Completo (recomendado)
rect_hud = pygame.Rect(x, y, width, height)
renderizar_hud_expandida(
    tela, 
    calendario, 
    clima, 
    farm_manager,
    relacao_gerenciador, 
    quest_manager, 
    rect_hud
)

# Especial
renderizar_tela_pesca(tela, pesca_manager, rect_pesca)
renderizar_status_plantacao(tela, planta, rect)
```

---

## 📊 Estrutura Quick Access

```python
# Farm
farm.dinheiro                    # Saldo atual
farm.nivel_agricultura           # Nível XP
farm.exp_agricultura             # Experiência

# Relações
relacao.coracao                  # -10 a 10
relacao.sentimento               # Enum
relacao.possível_casar           # Bool (>=8)

# Calendário
calendario.ano
calendario.estacao               # Enum Estacao
calendario.dia_mes               # 1-28
calendario.estacao_nome          # String

# Quest
quest.status                      # Enum StatusQuest
quest.quantidade_completa
quest.objetivo_quantidade
quest.recompensa.ouro

# Pesca
pesca.peixe_atual.nome
pesca.peixe_atual.raridade       # Enum
pesca.peixe_atual.valor_ouro

# Clima
clima.clima_atual                # Enum TipoClima
clima.condicoes_atuais.temperatura
clima.condicoes_atuais.umidade
```

---

## 🔄 Padrão de Atualização Diária

```python
def atualizar_dia():
    # 1. Calendário
    eventos = calendario.avancar_dia()
    
    # 2. Clima
    tipo, msg = clima_sistema.avancar_dia(calendario.estacao.value)
    
    # 3. Farm
    farm_manager.avancar_dia()
    
    # 4. Relacionamentos
    relacao_gerenciador.avancar_dia()
    
    # 5. Quests
    quest_manager.avancar_dia()
    
    # 6. Feedback
    if eventos['festival']:
        print(f"Festival: {eventos['festival'].nome}")
    print(f"Clima: {msg}")
```

---

## 🎯 Enums Principais

```python
# Estação
from .calendar import Estacao
Estacao.PRIMAVERA
Estacao.VERAO
Estacao.OUTONO
Estacao.INVERNO

# Sentimento NPC
from .npc_relations import SentimentoNPC
SentimentoNPC.FELIZ
SentimentoNPC.NEUTRO
SentimentoNPC.TRISTE
SentimentoNPC.FURIOSO
SentimentoNPC.APAIXONADO

# Status Quest
from .quests import StatusQuest
StatusQuest.DISPONIVEL
StatusQuest.ATIVA
StatusQuest.COMPLETA
StatusQuest.FALHADA

# Tipo Clima
from .weather import TipoClima
TipoClima.ENSOLARADO
TipoClima.NUBLADO
TipoClima.CHUVOSO
TipoClima.TEMPESTADE
TipoClima.NEVE
TipoClima.NEBLINA
TipoClima.ARCO_IRIS

# Tipo Peixe
from .fishing import TipoPeixe
TipoPeixe.COMUM
TipoPeixe.INCOMUM
TipoPeixe.RARO
TipoPeixe.LENDARIO
```

---

## ⚙️ Inicialização Completa

```python
# No início de app.py ou rodar()

from .farming import FarmManager
from .npc_relations import GerenciadorRelacoes
from .calendar import Calendario
from .quests import QuestManager, ObjetivoGeral
from .fishing import MiniGamePesca, HistoricoPesca
from .weather import SistemaClima
from .ui_enhanced import renderizar_hud_expandida

# Instanciar
farm_manager = FarmManager(tamanho_farm=20)
relacao_gerenciador = GerenciadorRelacoes()
calendario = Calendario(ano_inicial=1)
quest_manager = QuestManager()
objetivo_geral = ObjetivoGeral()
pesca_manager = MiniGamePesca()
historico_pesca = HistoricoPesca()
clima_sistema = SistemaClima()

# Usar em main loop
while None:
    # ... game logic ...
    
    if novo_dia:
        calendario.avancar_dia()
        clima_sistema.avancar_dia(calendario.estacao.value)
        farm_manager.avancar_dia()
        relacao_gerenciador.avancar_dia()
        quest_manager.avancar_dia()
    
    # Renderizar
    renderizar_hud_expandida(
        tela, calendario, clima_sistema, 
        farm_manager, relacao_gerenciador, 
        quest_manager, rect_hud
    )
```

---

## 🎮 Atalhos de Expansão

Para **adicionar** novo conteúdo:

```python
# Nova planeta
PLANTAS_DISPONIVEIS['nova_planta'] = {
    "dias_crescimento": 6,
    "food_yield": 5.0,
    "nome": "Nova Planta",
    "descricao": "Descrição aqui"
}

# Novo peixe
PEIXES_DISPONIVEIS['novo_peixe'] = Peixe(
    nome="Novo Peixe",
    raridade=TipoPeixe.RARO,
    locais=["rio"],
    estacoes=["verao"],
    hora_ativa_inicio=10,
    hora_ativa_fim=18,
    velocidade_fuga=2.5,
    valor_ouro=250,
    descricao="Um peixe novo"
)

# Nova quest
nova_quest = Quest(
    id="nova_quest",
    nome="Nueva Missão",
    descricao="...",
    tipo=TipoQuest.COLETA,
    objetivo_quantidade=5,
    recompensa=Recompensa(ouro=100, exp=20)
)
quest_manager.registrar_quest(nova_quest)

# Novo festival
novo_festival = Festival(
    nome="Novo Festival",
    estacao=Estacao.PRIMAVERA,
    dia_mes=15,
    descricao="...",
    premios={"ouro": 100},
    npcs_participando=[],
    tipo_festival="celebracao"
)
```

---

## 📈 Dicas de Balanceamento

```python
# Plantas crescem rápido demais?
# Aumentar dias_crescimento no PLANTAS_DISPONIVEIS

# Muito fácil ganhar dinheiro?
# Reduzir farm.dinheiro += ... ou aumentar custo itens

# NPCs mudam relação rápido?
# Ajustar recompensa de corações em dar_presente()

# Quests muito fáceis?
# Aumentar objetivo_quantidade em Quest

# Clima muda muito?
# Aumentar mudanca_clima_em_dias no __init__
```

---

**Tudo pronto para criar seu mundo único! 🚀**
