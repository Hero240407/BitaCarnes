import random

PREFIXOS = [
    "Astra",
    "Val",
    "Lum",
    "Fer",
    "Nor",
    "Ishi",
    "Cora",
    "Eld",
    "Sol",
    "Drak",
]

SUFIXOS = [
    "gard",
    "vale",
    "heim",
    "polis",
    "torre",
    "hollow",
    "ford",
    "costa",
    "vila",
    "mont",
]

PAPEIS_NPC = [
    "ferreiro",
    "sacerdote",
    "bibliotecaria",
    "mercador",
    "guarda",
    "mestre_arcano",
    "fazendeiro",
    "alquimista",
]

OBJETIVOS_BASE = [
    "derrotar o atual imperador",
    "salvar o mundo do deus demonio",
    "fundar uma familia respeitada",
    "unificar os reinos em paz",
    "restaurar as bibliotecas antigas",
]

EVENTOS_COLETIVOS = [
    "Todos se reuniram para o primeiro festival do deus Raphael.",
    "A vila celebrou um casamento nobre e novas aliancas.",
    "Um torneio magico definiu o novo conselho local.",
    "Mercadores distantes abriram rotas com terras desconhecidas.",
]


def gerar_nome_local() -> str:
    return f"{random.choice(PREFIXOS)}{random.choice(SUFIXOS)}"


def gerar_lore_mundo(nome_humano: str) -> dict:
    eixo = random.choice([
        "O mundo foi rasgado por uma guerra entre ceu e abismo.",
        "Uma chuva de mana alterou a historia dos reinos.",
        "As coroas humanas nasceram sob oraculos conflitantes.",
        "A magia antiga voltou junto com ruinas impossiveis.",
    ])
    condicao_raphael = random.choice([
        "Raphael esta forte, mas politicamente contido pela Igreja do Verbo.",
        "Raphael esta em silencio forçado por juramentos antigos.",
        "Raphael disputa influencia com cultos rivais e oraculos humanos.",
    ])
    era = random.choice([1500, 1600, 1700, 2200])
    return {
        "eixo_historico": eixo,
        "condicao_raphael": condicao_raphael,
        "era_inicial": era,
        "profecia": f"{nome_humano} pode alterar o destino de imperios.",
    }


def gerar_objetivo_inicial() -> dict:
    alvo = random.choice(OBJETIVOS_BASE)
    return {
        "id": "q_main_1",
        "titulo": "Destino Inesperado",
        "descricao": f"Seu objetivo inicial e {alvo}.",
        "status": "ativa",
        "origem": "destino",
        "ignorada": False,
    }


def resposta_npc(nome: str, papel: str, mensagem: str, memoria: list[dict], ano: int) -> str:
    tom = {
        "ferreiro": "O aco canta quando o mundo muda.",
        "sacerdote": "O oraculo fala em simbolos, nao em certezas.",
        "bibliotecaria": "Ha conhecimento perigoso entre os pergaminhos.",
        "mercador": "Informacao vale mais que ouro em tempos de guerra.",
        "guarda": "Sem ordem, nenhuma cidade sobrevive.",
        "mestre_arcano": "A mana responde a vontade e disciplina.",
        "fazendeiro": "Terra e estacoes decidem quem vive.",
        "alquimista": "Toda cura cobra um preco invisivel.",
    }.get(papel, "O mundo e mais estranho do que parece.")

    ultimo = memoria[-1]["mensagem"] if memoria else ""
    if ultimo and ultimo.lower() in mensagem.lower():
        return f"{nome}: Ja falamos disso. {tom}"
    return f"{nome} ({papel}, ano {ano}): {tom} Sobre isso: {mensagem[:90]}"


def evoluir_tipo_assentamento(populacao: int, tecnologia: int, magia: int) -> str:
    score = populacao + tecnologia * 6 + magia * 4
    if score >= 240:
        return "metropole"
    if score >= 170:
        return "cidade"
    if score >= 110:
        return "castelo"
    if score >= 60:
        return "vila"
    return "aldeia"


def maybe_evento_coletivo() -> str | None:
    if random.random() < 0.08:
        return random.choice(EVENTOS_COLETIVOS)
    return None
