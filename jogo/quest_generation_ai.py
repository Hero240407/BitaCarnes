"""
AI-powered quest generation system integrated with world and player lore.
Generates dynamic, contextual quests tied to world narrative, player background, and Raphael's observations.
"""

import json
from typing import Optional, Dict, Any

from .quests import Quest, QuestTipo, QuestStatus
from .servicos import chamar_ollama_pesado


def extrair_contexto_mundo(mundo) -> str:
    """
    Extrai contexto do mundo para prompt de geração de quests.
    
    Args:
        mundo: Objeto Mundo
        
    Returns:
        String formatada com contexto do mundo
    """
    lore = mundo.world_lore or {}
    
    return f"""
CONTEXTO DO MUNDO:
- Era: {lore.get('era_inicial', 'Desconhecida')}
- Profecia: {lore.get('profecia', 'Nenhuma registrada')}
- Conflito Principal: {lore.get('conflito_principal', 'Desconhecido')}
- Legenda Local: {lore.get('legenda', 'Perdida no tempo')}
- Eixo Histórico: {lore.get('eixo_historico', 'Desconhecido')}
- Condição de Raphael: {lore.get('condicao_raphael', 'Desconhecida')}
- Lugar Místico: {lore.get('lugar_mstico', {}).get('nome', 'Desconhecido')}
"""


def extrair_contexto_jogador(mundo) -> str:
    """
    Extrai contexto do jogador para prompt de geração de quests.
    
    Args:
        mundo: Objeto Mundo
        
    Returns:
        String formatada com contexto do jogador
    """
    perfil = mundo.perfil_jogador or {}
    
    return f"""
CONTEXTO DO JOGADOR:
- Nome: {mundo.nome_humano}
- Idade: {mundo.idade_humano}
- Origem: {perfil.get('origem', mundo.origem_humano)}
- Legado: {perfil.get('legado', 'Desconhecido')}
- Motivação: {perfil.get('motivacao', 'Sobreviver')}
- Segredo: {perfil.get('segredo', 'Nenhum revelado')}
- Moralidade: {mundo.moralidade_jogador}
"""


def extrair_contexto_raphael(memoria) -> str:
    """
    Extrai contexto de Raphael para prompt de geração de quests.
    
    Args:
        memoria: Objeto MemoriaRaphael
        
    Returns:
        String formatada com contexto de Raphael
    """
    return f"""
OBSERVAÇÕES DE RAPHAEL:
- Moralidade de Raphael: {memoria.moralidade_raphael}
- Intervencoes Realizadas: {memoria.intervencoes}
- Eventos Recentes: {len(memoria.eventos)}
- Conversas: {len(memoria.historico_conversas)}
"""


def extrair_contexto_estado_jogo(mundo) -> str:
    """
    Extrai estado atual do jogo para tornar quests apropriadas.
    
    Args:
        mundo: Objeto Mundo
        
    Returns:
        String formatada com estado do jogo
    """
    return f"""
ESTADO ATUAL DO JOGO:
- Inventário: {mundo.inventario}
- HP: {mundo.hp:.1f}/{mundo.hp_maximo}
- Quests Ativas: {len(mundo.quests_ativas)}
- Tempo de Jogo: Ano {mundo.ano_atual}
- NPCs Conhecidos: {len(mundo.npcs)}
"""


def gerar_quest_dinamica_ai(
    mundo,
    memoria,
    dificuldade_preferida: Optional[int] = None,
    tipo_preferido: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Gera uma quest dinamicamente usando IA, contextualizada ao mundo e jogador.
    
    Args:
        mundo: Objeto Mundo
        memoria: Objeto MemoriaRaphael
        dificuldade_preferida: Dificuldade desejada (1-5), se None escolhe aleatoriamente
        tipo_preferido: Tipo de quest desejado, se None deixa IA decidir
        
    Returns:
        Dicionário com dados de quest
    """
    import random
    
    if dificuldade_preferida is None:
        dificuldade_preferida = random.randint(1, 5)
    
    # Construir prompt contextualizado
    contexto_mundo = extrair_contexto_mundo(mundo)
    contexto_jogador = extrair_contexto_jogador(mundo)
    contexto_raphael = extrair_contexto_raphael(memoria)
    estado_jogo = extrair_contexto_estado_jogo(mundo)
    
    tipos_quest = "coleta, entrega, derrota, descoberta, melhoria, criacao, relacionamento, evento"
    tipo_hint = f"Preferencialmente do tipo: {tipo_preferido}" if tipo_preferido else f"Tipos disponíveis: {tipos_quest}"
    
    prompt = f"""Você é Raphael, um ser arcano observando a jornada do jogador.

{contexto_mundo}

{contexto_jogador}

{contexto_raphael}

{estado_jogo}

TAREFA:
Gere UMA quest dinâmica e contextualizada que:
1. Usa elementos da profecia ou conflito principal do mundo
2. Conecta à origem, legado ou motivação do jogador
3. Reflita a sabedoria e perspectiva de Raphael
4. Seja apropriada e significativa ao estado atual do jogo
5. Tenha dificuldade {dificuldade_preferida}/5
{tipo_hint}

REGRAS:
- A quest deve ser ÚNICA e NARRATIVA, não genérica
- Descrição deve ter 1-2 frases bem escritas em português
- Deve conectar mundo e personagem de forma orgânica
- Está localizada nas vilas ou regiões do mundo
- Envolve NPCs, combate, coleta, exploração ou aprendizado

Responda APENAS com JSON válido (sem ```json, sem explicação):
{{
    "nome": "Nome da Quest Único",
    "descricao": "Descrição coesa com 1-2 frases",
    "tipo": "coleta|entrega|derrota|descoberta|melhoria|criacao|relacionamento|evento",
    "objetivo_quantidade": número se aplicável,
    "dificuldade": {dificuldade_preferida},
    "recompensa_ouro": número 50-500,
    "recompensa_exp": número 100-1000,
    "npc_giver": "Nome de um NPC ou Raphael",
    "npc_target": "Nome do NPC alvo se aplicável",
    "recompensa_item": "Nome do item especial se houver",
    "repetiavel": false,
    "ai_generated": true,
    "lore_connection": "Breve explicação de como a quest conecta ao lore"
}}
"""
    
    # Chamar Ollama com contexto pesado
    resposta = chamar_ollama_pesado(prompt, timeout=30, temperature=0.7)
    
    if not resposta:
        # Fallback se IA falhar
        return gerar_quest_fallback(mundo, dificuldade_preferida, tipo_preferido)
    
    try:
        # Limpar resposta de marcadores de código
        resposta = resposta.strip()
        if resposta.startswith("```json"):
            resposta = resposta[7:]
        if resposta.startswith("```"):
            resposta = resposta[3:]
        if resposta.endswith("```"):
            resposta = resposta[:-3]
        
        dados = json.loads(resposta.strip())
        
        # Validação básica
        campos_obrigatorios = ["nome", "descricao", "tipo", "dificuldade", "recompensa_ouro", "npc_giver"]
        if not all(c in dados for c in campos_obrigatorios):
            return gerar_quest_fallback(mundo, dificuldade_preferida, tipo_preferido)
        
        return dados
        
    except json.JSONDecodeError:
        # Se não conseguir fazer parse, useça fallback
        return gerar_quest_fallback(mundo, dificuldade_preferida, tipo_preferido)


def gerar_quest_fallback(
    mundo,
    dificuldade: int = 3,
    tipo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fallback para quando IA não consegue gerar quest.
    Usa templates que ainda consideram contexto do mundo.
    
    Args:
        mundo: Objeto Mundo
        dificuldade: Nível de dificuldade
        tipo: Tipo de quest desejado
        
    Returns:
        Dicionário com dados de quest
    """
    import random
    
    # Templates que ainda usam contexto
    templates_mundo = {
        "Profecia": [
            f"Investigar rumores sobre a profecia: '{mundo.world_lore.get('profecia', 'desconhecida')}'",
            f"Preparar-se para a profecia mencionada: {mundo.world_lore.get('profecia', 'desconhecida')}",
        ],
        "Conflito": [
            f"Aprender mais sobre: {mundo.world_lore.get('conflito_principal', 'conflito desconhecido')}",
            f"Intermediar no conflito: {mundo.world_lore.get('conflito_principal', 'conflito desconhecido')}",
        ],
        "Legenda": [
            f"Desvendar a verdade sobre: {mundo.world_lore.get('legenda', 'legenda perdida')}",
            f"Investigar os eventos descritos em: {mundo.world_lore.get('legenda', 'legenda antiga')}",
        ],
    }
    
    templates_jogador = [
        f"Uma quest voltada para alguém da origem de um {mundo.origem_humano}",
        f"Usar suas habilidades de {mundo.origem_humano}",
        f"Explorar um lugar relacionado a {mundo.origem_humano}",
    ]
    
    # Escolher template aleatório
    categoria = random.choice(list(templates_mundo.keys()))
    descricao_base = random.choice(templates_mundo[categoria])
    descricao_jogador = random.choice(templates_jogador)
    
    npc_names = list(mundo.npcs.keys())[:5] if mundo.npcs else ["Raphael", "Aldeão Sábio"]
    npc_giver = random.choice(npc_names)
    
    return {
        "nome": f"Quest de {categoria}: {npc_giver}",
        "descricao": f"{descricao_base}. {descricao_jogador}",
        "tipo": tipo or random.choice(["coleta", "entrega", "descoberta"]),
        "objetivo_quantidade": random.randint(3, 10),
        "dificuldade": dificuldade,
        "recompensa_ouro": int(dificuldade * 100 + random.randint(0, 100)),
        "recompensa_exp": int(dificuldade * 200 + random.randint(100, 300)),
        "npc_giver": npc_giver,
        "repetiavel": False,
        "ai_generated": False,
        "lore_connection": f"Conectada a: {categoria}",
    }


def atualizar_quests_dinamicamente(mundo, memoria) -> list[dict]:
    """
    Gera novas quests dinamicamente baseado no estado do mundo.
    Pode ser chamado periodicamente durante o jogo.
    
    Args:
        mundo: Objeto Mundo
        memoria: Objeto MemoriaRaphael
        
    Returns:
        Lista de novas quests geradas
    """
    quests_novas = []
    
    # Gerar 2-3 quests novas com contextos variados
    quantidade = 2 if len(mundo.quests_ativas) > 3 else 3
    
    for _ in range(quantidade):
        try:
            quest_data = gerar_quest_dinamica_ai(mundo, memoria)
            
            # Converter para objeto Quest se necessário
            if isinstance(quest_data, dict):
                quest = criar_quest_de_dados(quest_data)
                quests_novas.append(quest_data)
                
        except Exception as e:
            print(f"[Erro] Falha ao gerar quest dinamicamente: {e}")
            continue
    
    return quests_novas


def criar_quest_de_dados(dados: Dict[str, Any]) -> Optional[Quest]:
    """
    Cria um objeto Quest a partir de dicionário de dados.
    
    Args:
        dados: Dicionário com dados de quest
        
    Returns:
        Objeto Quest ou None se falhar
    """
    try:
        tipo_str = dados.get("tipo", "coleta").upper()
        tipo_map = {
            "COLETA": QuestTipo.COLETA,
            "ENTREGA": QuestTipo.ENTREGA,
            "DERROTA": QuestTipo.DERROTA,
            "DESCOBERTA": QuestTipo.DESCOBERTA,
            "MELHORIA": QuestTipo.MELHORIA,
            "CRIACAO": QuestTipo.CRIACAO,
            "RELACIONAMENTO": QuestTipo.RELACIONAMENTO,
            "EVENTO": QuestTipo.EVENTO,
        }
        
        quest = Quest(
            nome=dados.get("nome", "Quest sem nome"),
            descricao=dados.get("descricao", ""),
            tipo=tipo_map.get(tipo_str, QuestTipo.COLETA),
            status=QuestStatus.DISPONIVEL,
            npc_giver=dados.get("npc_giver", "Raphael"),
            npc_target=dados.get("npc_target"),
            objetivo_quantidade=dados.get("objetivo_quantidade", 1),
            dificuldade=dados.get("dificuldade", 3),
            recompensa={
                "ouro": int(dados.get("recompensa_ouro", 100)),
                "exp": int(dados.get("recompensa_exp", 500)),
                "item": dados.get("recompensa_item"),
            },
            repetiavel=dados.get("repetiavel", False),
        )
        
        return quest
        
    except Exception as e:
        print(f"[Erro] Falha ao criar quest: {e}")
        return None


def gerar_quest_prophecy(mundo, memoria) -> Optional[Dict[str, Any]]:
    """
    Gera uma quest especificamente ligada à profecia do mundo.
    Incentiva o jogador a cumprir a profecia.
    
    Args:
        mundo: Objeto Mundo
        memoria: Objeto MemoriaRaphael
        
    Returns:
        Dicionário com dados de quest ou None
    """
    profecia = mundo.world_lore.get("profecia", "")
    if not profecia:
        return None
    
    prompt = f"""Você é Raphael observando como a profecia se desenrola.

PROFECIA: {profecia}

JOGADOR: {mundo.nome_humano}

Gere UMA quest que posiciona o jogador em direção ao cumprimento dessa profecia.
A quest deve ser significativa, desafiadora e narrativamente rica.

Responda APENAS com JSON válido:
{{
    "nome": "Nome relacionado à profecia",
    "descricao": "Descrição que conecta a próxima profecia",
    "tipo": "descoberta|entrega|derrota",
    "objetivo_quantidade": 1,
    "dificuldade": 4,
    "recompensa_ouro": 500,
    "recompensa_exp": 2000,
    "npc_giver": "Raphael",
    "repetiavel": false,
    "profecia_step": true,
    "lore_connection": "Passo em direção à profecia"
}}
"""
    
    resposta = chamar_ollama_pesado(prompt, timeout=30, temperature=0.8)
    
    if not resposta:
        return None
    
    try:
        resposta = resposta.strip()
        if resposta.startswith("```"):
            resposta = resposta.split("```")[1]
        if resposta.startswith("json"):
            resposta = resposta[4:]
        
        return json.loads(resposta.strip())
        
    except json.JSONDecodeError:
        return None


def gerar_quest_conflito_principal(mundo, memoria) -> Optional[Dict[str, Any]]:
    """
    Gera uma quest ligada ao conflito principal do mundo.
    
    Args:
        mundo: Objeto Mundo
        memoria: Objeto MemoriaRaphael
        
    Returns:
        Dicionário com dados de quest ou None
    """
    conflito = mundo.world_lore.get("conflito_principal", "")
    if not conflito:
        return None
    
    prompt = f"""Você é Raphael observando o conflito no mundo.

CONFLITO PRINCIPAL: {conflito}

JOGADOR: {mundo.nome_humano} ({mundo.origem_humano})

Gere UMA quest que envolve o jogador no conflito principal.
A quest deve oferecer escolhas morais e consequências significativas.

Responda APENAS com JSON válido:
{{
    "nome": "Nome relacionado ao conflito",
    "descricao": "Você é envolvido no conflito...",
    "tipo": "entrega|derrota|relacionamento|descoberta",
    "objetivo_quantidade": 1,
    "dificuldade": 4,
    "recompensa_ouro": 400,
    "recompensa_exp": 1500,
    "npc_giver": "Líder de Facção",
    "repetiavel": false,
    "conflito_quest": true,
    "lore_connection": "Envolvimento no conflito principal"
}}
"""
    
    resposta = chamar_ollama_pesado(prompt, timeout=30, temperature=0.7)
    
    if not resposta:
        return None
    
    try:
        resposta = resposta.strip()
        if resposta.startswith("```"):
            resposta = resposta.split("```")[1]
        if resposta.startswith("json"):
            resposta = resposta[4:]
        
        return json.loads(resposta.strip())
        
    except json.JSONDecodeError:
        return None
