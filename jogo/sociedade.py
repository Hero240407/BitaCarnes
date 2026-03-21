import random

# Sistema de Culturas e Plantacoes - fantasy e isekai themed
PLANTAS_DISPONIVEIS = {
    # Culturas comuns
    "trigo": {
        "dias_crescimento": 4,
        "food_yield": 3.0,
        "nome": "Trigo",
        "descricao": "Cultura rapida, rendimento moderado",
    },
    "batata": {
        "dias_crescimento": 5,
        "food_yield": 4.5,
        "nome": "Batata",
        "descricao": "Nutritiva e de crescimento medio",
    },
    "milho": {
        "dias_crescimento": 6,
        "food_yield": 5.0,
        "nome": "Milho",
        "descricao": "Rende muito, mas requer mais tempo",
    },
    "melancia": {
        "dias_crescimento": 7,
        "food_yield": 6.0,
        "nome": "Melancia",
        "descricao": "Lenta ao crescer, mas muito nutritiva",
    },
    "feijao": {
        "dias_crescimento": 3,
        "food_yield": 2.0,
        "nome": "Feijao",
        "descricao": "Muito rapida, rendimento baixo",
    },
    # Culturas magicas e isekai
    "mandrake_arcana": {
        "dias_crescimento": 8,
        "food_yield": 7.5,
        "nome": "Mandrake Arcana",
        "descricao": "Raiz magica que grita ao ser colhida e repousa mana",
    },
    "trigo_celestial": {
        "dias_crescimento": 5,
        "food_yield": 5.5,
        "nome": "Trigo Celestial",
        "descricao": "Cereal brilhante que fortalece a resistencia magica",
    },
    "buncumber_isekai": {
        "dias_crescimento": 4,
        "food_yield": 4.0,
        "nome": "Buncumber Isekai",
        "descricao": "Fruto translucido do outro mundo, muito saciante",
    },
    "taro_demonaco": {
        "dias_crescimento": 7,
        "food_yield": 6.5,
        "nome": "Taro Demonaco",
        "descricao": "Tuberculo negro que fornece energia profunda",
    },
    "silvervine_lunar": {
        "dias_crescimento": 6,
        "food_yield": 5.0,
        "nome": "Silvervine Lunar",
        "descricao": "Planta prateada que brilha a noite",
    },
    "glowmushroom": {
        "dias_crescimento": 3,
        "food_yield": 2.5,
        "nome": "Glowmushroom",
        "descricao": "Cogumelo luminescente que cresce em cavernas arcanas",
    },
    "dragonbloom": {
        "dias_crescimento": 10,
        "food_yield": 8.0,
        "nome": "Dragonbloom",
        "descricao": "Flor ancestral com petalas flamejantes, muito rara",
    },
    "moonwheat": {
        "dias_crescimento": 5,
        "food_yield": 4.5,
        "nome": "Moonwheat",
        "descricao": "Grains that absorb lunar energy overnight",
    },
    "spiritrice": {
        "dias_crescimento": 9,
        "food_yield": 7.0,
        "nome": "Spirit Rice",
        "descricao": "Arroz espiritual que conecta com o plano dos ancestrais",
    },
    "verdant_lotus": {
        "dias_crescimento": 8,
        "food_yield": 6.0,
        "nome": "Verdant Lotus",
        "descricao": "Lotus sagrada que purifica mana corrompida",
    },
}

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
    # Prefixos de fantasia/isekai
    "Seraph",
    "Dragon",
    "Mystic",
    "Eternal",
    "Shadow",
    "Crystal",
    "Moonlit",
    "Arcane",
    "Divine",
    "Celestial",
    "Void",
    "Ember",
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
    # Sufixos de fantasia/isekai
    "holm",
    "realm",
    "spire",
    "nexus",
    "sanctuary",
    "citadel",
    "abyss",
    "summit",
    "refuge",
    "sanctum",
    "keep",
    "bower",
]

PAPEIS_NPC = [
    # Profissões comuns
    "ferreiro", "sacerdote", "bibliotecaria", "mercador", "guarda", "mestre_arcano", "fazendeiro", "alquimista",
    # Profissões de fantasia e isekai
    "mago_elemental", "paladino", "bardo", "druida", "caçador_demonio", "monge_espiritual", "ninja_sombra",
    "necromante", "curandeira", "forja_divina", "cavaleiro_dragao", "sacerdotisa_lua", "guerreiro_antigo",
    "ladrao_noble", "escriba_magico", "capelao", "orca_nobre", "feiticeira", "vidente",
]

OBJETIVOS_BASE = [
    "derrotar o atual imperador",
    "salvar o mundo do deus demonio",
    "fundar uma familia respeitada",
    "unificar os reinos em paz",
    "restaurar as bibliotecas antigas",
    # Objetivos de fantasia e isekai
    "selar o portal do outro mundo",
    "despertar o dragao ancestral",
    "recuperar o artefato perdido",
    "quebrar a maldicao que assola o reino",
    "encontrar o caminho de volta para casa",
    "reunir as 7 chaves sagradas",
    "construir um santuario para a deusa lunar",
    "desvendar o misterio das torres magicas",
    "libertar os espiritos presos nas ruinas",
    "tornar-se mestre dos 5 elementos",
    "restaurar a confianca entre humanos e elfos",
    "plantar uma floresta sagrada em cada biomo",
    "derrotar os 12 lordes demoniacos",
    "descobrir a verdade sobre o seu passado",
]

EVENTOS_COLETIVOS = [
    "Todos se reuniram para o primeiro festival do deus Raphael.",
    "A vila celebrou um casamento nobre e novas aliancas.",
    "Um torneio magico definiu o novo conselho local.",
    "Mercadores distantes abriram rotas com terras desconhecidas.",
    # Eventos de fantasia e isekai
    "Uma chuva de meteoros magicos caiu, abencando as colheitas.",
    "Um dragao jovem sobrevoou a vila e deixou um presente misterioso.",
    "O portal isekai brilhou tres noites seguidas, trazendo sinais estranhos.",
    "A floresta sagrada floresceu de repente apos seculos.",
    "Elfos ancestrais visitaram a vila pela primeira vez em gerações.",
    "Uma torre magica apareceu a noite no horizonte.",
    "Os espiritos dos ancestrais se comunicaram atraves de sonhos.",
    "Uma equipe de aventureiros legendarios passou pela vila.",
    "O santuario lunar começou a irradiar poder celestial.",
    "Foi descoberto um mapa para o tesouro do imperio perdido.",
    "Uma criatura divina apareceu nos céus como bencao.",
    "Os reinos rivais assinaram um pacto de paz durante o equinocio.",
]


def gerar_nome_local() -> str:
    return f"{random.choice(PREFIXOS)}{random.choice(SUFIXOS)}"


def gerar_lore_mundo(nome_humano: str) -> dict:
    eixo = random.choice([
        "O mundo foi rasgado por uma guerra entre ceu e abismo.",
        "Uma chuva de mana alterou a historia dos reinos.",
        "As coroas humanas nasceram sob oraculos conflitantes.",
        "A magia antiga voltou junto com ruinas impossiveis.",
        "Portais antigos se abriram liberando poder esquecido.",
        "Tres familias reais competem pelo Artefato Perdido.",
        # Eixos de fantasia e isekai
        "Um isekai aconteceu, trazendo herois de outro mundo.",
        "A maldição de um deus dorme sob as montanhas sagradas.",
        "Sete torres magicas caíram em uma noite, liberando caos.",
        "Os dragões desapareceram, deixando ruinas e mistério.",
        "Uma civilização avançada do passado acordou de seu sono.",
        "Os elementais romperam seu trato com os humanos.",
        "Um eclipse eterno assombra as terras do norte.",
    ])
    
    condicao_raphael = random.choice([
        "Raphael esta forte, mas politicamente contido pela Igreja do Verbo.",
        "Raphael esta em silencio forçado por juramentos antigos.",
        "Raphael disputa influencia com cultos rivais e oraculos humanos.",
        "Raphael observa de distancia, testando os dignos.",
        "Raphael prefere nao intervir no destino livre dos mortais.",
        "Raphael respeita a autonomia dos reinos e vilas.",
        "Raphael mantem distancia, observando com paciencia infinita.",
        # Condições especiais para Raphael
        "Raphael foi selado em um cristal antigo horas antes de seu retorno.",
        "Raphael compete com outros arcanjos pela influencia divina.",
        "Raphael está dividido entre misericórdia e justiça.",
        "Raphael observa os eventos climáticos para sinais de perigo.",
    ])
    
    era = random.choice([1500, 1600, 1700, 2200, 3000, 5000])
    
    # Legendas e eventos que moldaram o mundo
    legendas = [
        "Os santuarios antigos guardam reliquias de poder imemorial.",
        "Uma criatura primordial adormece nas montanhas.",
        "A bendcao de Raphael protege apenas os puros de coracao.",
        "Artefatos perdidos concedem sabedoria ou ruina.",
        "Nas aguas sagradas, ecos do mundo anterior ecoam.",
        # Legendas de fantasia/isekai
        "Os dragões ancestrais construíram cidades ocultas nas nuvens.",
        "O primeiro isekai trouxe heróis que mudaram tudo para sempre.",
        "Sete apóstolos divinos selaram demônios em dimensões paralelas.",
        "Elfos imortais guardam segredos que mortal algum pode compreender.",
        "Uma árvore cósmica conecta todos os reis sob suas raízes.",
        "Os anões forjaram armas que cortam até a própria destino.",
    ]
    
    # Profecia relacionada ao personagem
    profecia = random.choice([
        f"{nome_humano} pode alterar o destino de imperios.",
        f"{nome_humano} foi predito pelas cronicas esquecidas.",
        f"O sangue de {nome_humano} reacenderá magia adormecida.",
        f"{nome_humano} herdara o que reis nao conseguem reivindicar.",
        # Profecias especiais
        f"{nome_humano} quebrará a sétima selagem e libertará o caos.",
        f"{nome_humano} será o primeiro a dominar os 5 elementos juntos.",
        f"{nome_humano} retornará para casa atravessando dimensões.",
        f"{nome_humano} será a ponte entre o mundo antigo e novo.",
    ])
    
    # Tema geografico do mundo
    tema_terra = random.choice([
        "terra_mutante",  # Magia descontrolada mudou a geografia
        "reino_fragmentado",  # Reinos dispersos em conflito
        "ruinas_mystticas",  # Ruinas de civilizacao anterior
        "santuarios_selvagens",  # Lugares sagrados intactos
        # Temas adicionais de fantasia
        "isekai_convergente",  # Múltiplos mundos se cruzam
        "era_draconica",  # Período em que dragões dominam
        "apocalipse_magico",  # Magia foi usada como arma
    ])
    
    return {
        "eixo_historico": eixo,
        "condicao_raphael": condicao_raphael,
        "era_inicial": era,
        "profecia": profecia,
        "legenda": random.choice(legendas),
        "tema_terra": tema_terra,
        "conflito_principal": random.choice([
            f"Busca pelo Artefato dos {era}",
            "Guerra entre Magia Antiga e Nova",
            "Ressurgimento de uma Ameaca Esquecida",
            "Purificacao das Terras Corrompidas",
            "Restauracao da Monarquia Despedacada",
            # Conflitos adicionais
            "À procura da Terra Prometida do Isekai",
            "Batalha entre Dragões Rivais",
            "Selagem do Portal Demoníaco",
            "Resgate dos Mundos Paralelos",
        ]),
        "lugar_mstico": {
            "nome": gerar_nome_local(),
            "descricao": random.choice([
                "Um templo onde o ceu toca o solo",
                "Uma floresta que recusa o tempo",
                "Aguas que refletem outras realidades",
                "Ruinas que sussurram em linguas mortas",
                "Uma montanha que repousa sonhos",
                # Descrições adicionais
                "A torre onde os magos imortais vivem",
                "A floresta onde elfos e humanos assinaram paz",
                "A caverna onde dragões depositam seus ovos",
                "O portal por onde chegam os isekai",
                "O poço onde se banha a luna eterna",
                "A biblioteca flutuante entre dimensões",
            ]),
        },
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
