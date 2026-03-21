"""Sistema de Biomas Expandido - Biomas únicos com ambiance, recursos e mecânicas especiais"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Tuple
import random


class TipoBioma(Enum):
    """Tipos de biomas disponíveis no mundo"""
    FLORESTA = "floresta"
    PRADARIA = "pradaria"
    MONTANHA = "montanha"
    DESERTO = "deserto"
    ALAGADO = "alagado"
    VULCAO = "vulcao"
    TUNDRA = "tundra"
    CAVERNA = "caverna"
    CEMITERIO = "cemiterio"
    FLORESTA_SOMBRA = "floresta_sombra"
    OCEANO = "oceano"


class EstacaoBioma(Enum):
    """Estações que afetam biomas"""
    PRIMAVERA = "primavera"
    VERAO = "verao"
    OUTONO = "outono"
    INVERNO = "inverno"


@dataclass(slots=True)
class RecursoBioma:
    """Define um recurso disponível em um bioma"""
    nome: str
    tipo: str  # "planta", "minério", "animal", "artefato"
    raridade: float  # 0-1, chance de encontrar por célula
    quantidade_min: int
    quantidade_max: int
    estacoes_disponivel: List[EstacaoBioma] = field(default_factory=list)
    valor_ouro: int = 10
    descricao: str = ""
    item_id: Optional[int] = None  # ID no banco de items


@dataclass(slots=True)
class CaracteristicaBioma:
    """Características especiais de um bioma"""
    nome: str
    descricao: str
    tipo: str  # "positiva", "negativa", "neutra"
    efeito_jogador: Dict = field(default_factory=dict)  # Modificadores de stats
    efeito_mundo: Dict = field(default_factory=dict)  # Efeitos no mundo


@dataclass(slots=True)
class DadosBioma:
    """Armazena dados completos de um bioma"""
    tipo: TipoBioma
    nome: str
    descricao: str
    cor_base: Tuple[int, int, int]  # RGB para rendering
    cor_noite: Tuple[int, int, int]
    ambiance: str  # ID de fundo sonoro
    
    # Visuais
    sprite_terreno: str
    sprites_objetos: List[str] = field(default_factory=list)
    
    # Mobs
    mobs_nativos: List[str] = field(default_factory=list)
    densidade_mobs: float = 0.5  # 0-1
    
    # Recursos
    recursos: List[RecursoBioma] = field(default_factory=list)
    recursos_raros: List[RecursoBioma] = field(default_factory=list)
    
    # Características
    caracteristicas: List[CaracteristicaBioma] = field(default_factory=list)
    temperaturaBase: int = 20  # Graus Celsius
    umidade: float = 0.5  # 0-1
    periculosidade: int = 1  # 1-5
    
    # Estruturas/Pontos de interesse
    tipos_estrutura: List[str] = field(default_factory=list)
    chance_estrutura: float = 0.1
    
    # Mecânicas especiais
    mecanicas_especiais: Dict = field(default_factory=dict)


class ConfiguradorBiomas:
    """Define todos os biomas do jogo"""
    
    @staticmethod
    def obter_floresta() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.FLORESTA,
            nome="Floresta Densa",
            descricao="Uma floresta exuberante repleta de vida e mistério.",
            cor_base=(34, 139, 34),
            cor_noite=(20, 60, 20),
            ambiance="forest_ambiance",
            sprite_terreno="grass_forest",
            sprites_objetos=["tree_oak", "tree_pine", "mushroom", "flower"],
            mobs_nativos=["lobo", "urso", "cervo", "coelho"],
            densidade_mobs=0.6,
            recursos=[
                RecursoBioma("Madeira", "planta", 0.7, 1, 3, estacoes_disponivel=[
                    EstacaoBioma.PRIMAVERA, EstacaoBioma.VERAO, EstacaoBioma.OUTONO], valor_ouro=15),
                RecursoBioma("Maçã Selvagem", "planta", 0.4, 1, 2, 
                    estacoes_disponivel=[EstacaoBioma.VERAO, EstacaoBioma.OUTONO], valor_ouro=20),
                RecursoBioma("Cogumelo Raro", "planta", 0.15, 1, 1, valor_ouro=50),
            ],
            recursos_raros=[
                RecursoBioma("Orquídea Ancestral", "planta", 0.02, 1, 1, valor_ouro=200),
            ],
            caracteristicas=[
                CaracteristicaBioma("Vegetação Densa", "Você se encontra em meio a plantas espessas.",
                    "neutra", {"velocidade": -1}),
                CaracteristicaBioma("Aura Natural", "A floresta cura você lentamente.",
                    "positiva", {"regenração": 1}, {"cura_lenta": 0.1}),
            ],
            temperaturaBase=18,
            umidade=0.8,
            periculosidade=2,
            tipos_estrutura=["cabana_madeira", "santuario_antigo"],
            chance_estrutura=0.08,
            mecanicas_especiais={"regrowth": True, "iluminacao_natural": True}
        )
    
    @staticmethod
    def obter_montanha() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.MONTANHA,
            nome="Picos Nevados",
            descricao="Montanhas altas com picos nevados e cavernas profundas.",
            cor_base=(139, 140, 137),
            cor_noite=(80, 80, 75),
            ambiance="mountain_wind",
            sprite_terreno="stone_mountain",
            sprites_objetos=["rock_large", "ice_crystal", "snow_peak"],
            mobs_nativos=["urso", "cabra_montanha", "aguia", "elemental_gelo"],
            densidade_mobs=0.4,
            recursos=[
                RecursoBioma("Minério de Ferro", "minério", 0.5, 2, 5, valor_ouro=30),
                RecursoBioma("Cristal de Gelo", "minério", 0.2, 1, 2, valor_ouro=60),
                RecursoBioma("Cristal Raro", "minério", 0.08, 1, 1, valor_ouro=150),
            ],
            recursos_raros=[
                RecursoBioma("Ouro Puro", "minério", 0.01, 1, 2, valor_ouro=500),
            ],
            caracteristicas=[
                CaracteristicaBioma("Altitude", "O ar é frio e rarefeito.",
                    "negativa", {"vida_max": -20, "velocidade": -1}),
                CaracteristicaBioma("Minas Ricas", "Muito minério disponível para mineração.",
                    "positiva", {}, {"minério_abundante": True}),
            ],
            temperaturaBase=0,
            umidade=0.3,
            periculosidade=3,
            tipos_estrutura=["mina", "templo_montanha", "torre_vigia"],
            chance_estrutura=0.12,
            mecanicas_especiais={"frio_danoso": True, "queda_possivel": True}
        )
    
    @staticmethod
    def obter_deserto() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.DESERTO,
            nome="Deserto Ardente",
            descricao="Areias infindáveis sob um sol implacável.",
            cor_base=(210, 180, 100),
            cor_noite=(80, 70, 50),
            ambiance="desert_wind",
            sprite_terreno="sand_desert",
            sprites_objetos=["cactus", "duna", "ossada", "miragem"],
            mobs_nativos=["escorpiao", "hiena", "cobra_areia"],
            densidade_mobs=0.3,
            recursos=[
                RecursoBioma("Areia Dourada", "material", 0.8, 5, 10, valor_ouro=5),
                RecursoBioma("Cristal de Areia", "material", 0.15, 1, 2, valor_ouro=40),
                RecursoBioma("Óleo do Deserto", "material", 0.1, 1, 1, valor_ouro=80),
            ],
            recursos_raros=[
                RecursoBioma("Rubi do Deserto", "material", 0.02, 1, 1, valor_ouro=300),
            ],
            caracteristicas=[
                CaracteristicaBioma("Calor Extremo", "O calor é devastador.",
                    "negativa", {"defesa": -1, "inteligencia": -1}, {"consumo_agua": True}),
                CaracteristicaBioma("Oásis Secreto", "Ocasionalmente você encontra água.",
                    "positiva", {}, {"descanso_refresh": True}),
            ],
            temperaturaBase=45,
            umidade=0.05,
            periculosidade=3,
            tipos_estrutura=["ruinas_cidade_antiga", "templo_deserto", "tumulo"],
            chance_estrutura=0.1,
            mecanicas_especiais={"desodracao": True, "tempestades_areia": True}
        )
    
    @staticmethod
    def obter_vulcao() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.VULCAO,
            nome="Vulcão Ativo",
            descricao="Terra queimada com lava fluindo, impossível ignorar o perigo.",
            cor_base=(139, 35, 35),
            cor_noite=(205, 92, 92),
            ambiance="volcano_rumble",
            sprite_terreno="lava_flow",
            sprites_objetos=["lava_lake", "obsidian", "steam"],
            mobs_nativos=["elemental_fogo", "dragao_jovem", "salamandra"],
            densidade_mobs=0.5,
            recursos=[
                RecursoBioma("Obsidiana", "minério", 0.4, 2, 4, valor_ouro=50),
                RecursoBioma("Enxofre", "material", 0.3, 2, 3, valor_ouro=35),
                RecursoBioma("Cristal Flamejante", "raro", 0.05, 1, 1, valor_ouro=200),
            ],
            recursos_raros=[
                RecursoBioma("Coração de Dragão", "lendario", 0.01, 1, 1, valor_ouro=1000),
            ],
            caracteristicas=[
                CaracteristicaBioma("Lava Escaldante", "Você sofre dano constantemente.",
                    "negativa", {}, {"dano_continuo": 5}),
                CaracteristicaBioma("Poder Elemental", "Sua magia de fogo é amplificada.",
                    "positiva", {}, {"magia_fogo": 1.5}),
            ],
            temperaturaBase=70,
            umidade=0.0,
            periculosidade=5,
            tipos_estrutura=["câmara_magma", "palácio_dragão"],
            chance_estrutura=0.15,
            mecanicas_especiais={"lava_morte": True, "erupcoes": True}
        )
    
    @staticmethod
    def obter_alagado() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.ALAGADO,
            nome="Pântano Sombrio",
            descricao="Terras pantanosas cheias de vida e decomposição.",
            cor_base=(85, 107, 47),
            cor_noite=(50, 60, 30),
            ambiance="swamp_ambiance",
            sprite_terreno="mud_swamp",
            sprites_objetos=["willow_tree", "lily_pad", "log_sunken"],
            mobs_nativos=["aranha_gigante", "sapo_gigante", "zumbi", "miasma"],
            densidade_mobs=0.7,
            recursos=[
                RecursoBioma("Lama Negra", "material", 0.6, 3, 6, valor_ouro=8),
                RecursoBioma("Gás Fosforescente", "material", 0.3, 1, 2, valor_ouro=45),
                RecursoBioma("Cogumelo Venenoso", "material", 0.2, 1, 2, valor_ouro=55),
            ],
            recursos_raros=[
                RecursoBioma("Essência de Pântano", "material", 0.03, 1, 1, valor_ouro=250),
            ],
            caracteristicas=[
                CaracteristicaBioma("Terreno Enlameado", "Movimento é mais lento.",
                    "negativa", {"velocidade": -2}),
                CaracteristicaBioma("Miasma Venenoso", "O ar pode ser tóxico.",
                    "negativa", {}, {"veneno_passivo": 1}),
                CaracteristicaBioma("Abundância de Vida", "Recursos orgânicos são abundantes.",
                    "positiva", {}, {"recursos_organicos": 1.5}),
            ],
            temperaturaBase=25,
            umidade=0.95,
            periculosidade=4,
            tipos_estrutura=["santuario_encharcado", "torre_emersa"],
            chance_estrutura=0.08,
            mecanicas_especiais={"movimento_lento": True, "doenca": True}
        )
    
    @staticmethod
    def obter_cemiterio() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.CEMITERIO,
            nome="Cemitério Amaldiçoado",
            descricao="Um lugar de repouso perturbado, cheio de energias sobrenaturais.",
            cor_base=(105, 105, 105),
            cor_noite=(40, 40, 40),
            ambiance="graveyard_haunted",
            sprite_terreno="gravestone",
            sprites_objetos=["tombstone", "dead_tree", "ghost_wisps"],
            mobs_nativos=["espectro", "esqueleto", "zumbi", "banshee"],
            densidade_mobs=0.6,
            recursos=[
                RecursoBioma("Osso Perfeito", "material", 0.4, 2, 4, valor_ouro=25),
                RecursoBioma("Cristal Sombrio", "material", 0.15, 1, 1, valor_ouro=80),
                RecursoBioma("Essência de Alma", "raro", 0.05, 1, 1, valor_ouro=150),
            ],
            recursos_raros=[
                RecursoBioma("Coração Amaldiçoado", "lendario", 0.01, 1, 1, valor_ouro=500),
            ],
            caracteristicas=[
                CaracteristicaBioma("Escuridão Permanente", "Luz é dificil de manter.",
                    "negativa", {"iluminacao": 0.5}),
                CaracteristicaBioma("Fraqueza dos Mortos", "Mana é abundante para magia sombria.",
                    "positiva", {}, {"magia_sombria": 1.5}),
            ],
            temperaturaBase=10,
            umidade=0.4,
            periculosidade=4,
            tipos_estrutura=["mausoléu", "túmulo_antigo", "necrópolis"],
            chance_estrutura=0.15,
            mecanicas_especiais={"maldição": True, "ressurreição": True}
        )
    
    @staticmethod
    def obter_floresta_sombra() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.FLORESTA_SOMBRA,
            nome="Floresta das Sombras",
            descricao="Uma floresta antiga onde a luz do dia raramente chega.",
            cor_base=(47, 79, 79),
            cor_noite=(25, 40, 40),
            ambiance="shadow_forest",
            sprite_terreno="dark_wood",
            sprites_objetos=["ancient_tree", "shadow_fungi", "void_wisps"],
            mobs_nativos=["fada_sombria", "lobo_sombra", "centauro_negro", "espírito"],
            densidade_mobs=0.5,
            recursos=[
                RecursoBioma("Madeira Sombria", "material", 0.5, 1, 2, valor_ouro=35),
                RecursoBioma("Flor de Meia-Noite", "material", 0.2, 1, 1, valor_ouro=70),
                RecursoBioma("Essência Void", "raro", 0.08, 1, 1, valor_ouro=180),
            ],
            recursos_raros=[
                RecursoBioma("Semente Cósmica", "lendario", 0.01, 1, 1, valor_ouro=600),
            ],
            caracteristicas=[
                CaracteristicaBioma("Sombras Vivas", "As sombras podem atacar você.",
                    "negativa", {}, {"ataque_sombra": True}),
                CaracteristicaBioma("Magia Antiga", "Você sente poder mágico antigo.",
                    "positiva", {}, {"exp_magia": 1.5}),
            ],
            temperaturaBase=15,
            umidade=0.7,
            periculosidade=4,
            tipos_estrutura=["árvore_colossal", "templo_degradado"],
            chance_estrutura=0.1,
            mecanicas_especiais={"escuridao_profunda": True, "magia_instavel": True}
        )
    
    @staticmethod
    def obter_tundra() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.TUNDRA,
            nome="Tundra Congelada",
            descricao="Terras áridas de gelo eterno, hostis a toda vida.",
            cor_base=(176, 196, 222),
            cor_noite=(100, 130, 180),
            ambiance="tundra_wind",
            sprite_terreno="ice_tundra",
            sprites_objetos=["ice_formation", "aurora", "frozen_corpse"],
            mobs_nativos=["lobo_branco", "elemental_gelo", "mamute_antigo"],
            densidade_mobs=0.25,
            recursos=[
                RecursoBioma("Gelo Puro", "material", 0.5, 2, 4, valor_ouro=20),
                RecursoBioma("Cristal de Gelo Azul", "material", 0.2, 1, 1, valor_ouro=90),
            ],
            recursos_raros=[
                RecursoBioma("Diamante do Norte", "raro", 0.02, 1, 1, valor_ouro=400),
            ],
            caracteristicas=[
                CaracteristicaBioma("Frio Letal", "Você sofre dano constantemente do frio.",
                    "negativa", {}, {"dano_frio": 5}),
                CaracteristicaBioma("Aurora Boreal", "Uma beleza rara que atrai sorte.",
                    "positiva", {}, {"sorte": 1.2}),
            ],
            temperaturaBase=-20,
            umidade=0.1,
            periculosidade=4,
            tipos_estrutura=["acampamento_antigo", "cripta_congelada"],
            chance_estrutura=0.06,
            mecanicas_especiais={"congealamento": True, "visibilidade_reduzida": True}
        )
    
    @staticmethod
    def obter_caverna() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.CAVERNA,
            nome="Caverna Profunda",
            descricao="Passagens subterrâneas escuras e perigosas.",
            cor_base=(64, 64, 64),
            cor_noite=(30, 30, 30),
            ambiance="cave_dripping",
            sprite_terreno="cave_stone",
            sprites_objetos=["stalagmite", "mineral_vein", "cave_moss"],
            mobs_nativos=["goblin", "aranha_cave", "morcego", "worm"],
            densidade_mobs=0.8,
            recursos=[
                RecursoBioma("Minério de Cobre", "minério", 0.6, 2, 4, valor_ouro=25),
                RecursoBioma("Musgo Luminescente", "material", 0.4, 1, 2, valor_ouro=35),
                RecursoBioma("Diamante Bruto", "raro", 0.1, 1, 1, valor_ouro=200),
            ],
            recursos_raros=[
                RecursoBioma("Gema Perfeita", "lendario", 0.01, 1, 1, valor_ouro=800),
            ],
            caracteristicas=[
                CaracteristicaBioma("Escuridão Total", "Visão é muito limitada.",
                    "negativa", {"iluminacao": 0.3}),
                CaracteristicaBioma("Riquezas Minerais", "Muito minério para extrair.",
                    "positiva", {}, {"minério_abundante": True, "exp_mineracao": 1.3}),
            ],
            temperaturaBase=12,
            umidade=0.85,
            periculosidade=3,
            tipos_estrutura=["mina_profunda", "câmara_cristal", "poço_abissal"],
            chance_estrutura=0.2,
            mecanicas_especiais={"escuridao_total": True, "coletivo_gravitacional": True}
        )
    
    @staticmethod
    def obter_pradaria() -> DadosBioma:
        return DadosBioma(
            tipo=TipoBioma.PRADARIA,
            nome="Pradaria Infinita",
            descricao="Campos de grama verde sem fim, livres e abertos.",
            cor_base=(34, 177, 76),
            cor_noite=(20, 100, 40),
            ambiance="grass_breeze",
            sprite_terreno="grass_plain",
            sprites_objetos=["wildflower", "rock_outcroping", "anthill"],
            mobs_nativos=["coelho", "cervo", "leão", "bison"],
            densidade_mobs=0.4,
            recursos=[
                RecursoBioma("Trigo Selvagem", "plant", 0.7, 2, 4, valor_ouro=10),
                RecursoBioma("Mel de Abelha", "material", 0.3, 1, 2, valor_ouro=40),
            ],
            caracteristicas=[
                CaracteristicaBioma("Céu Aberto", "Você tem visão clara em todas as direções.",
                    "positiva", {"visao": 2}),
                CaracteristicaBioma("Abundância", "Comida é fácil de encontrar.",
                    "positiva", {}, {"coleta_rapida": True}),
            ],
            temperaturaBase=22,
            umidade=0.5,
            periculosidade=1,
            tipos_estrutura=["moinho", "vilarejo", "monumento_pedra"],
            chance_estrutura=0.12,
            mecanicas_especiais={"visibilidade_total": True, "velocidade_aumentada": True}
        )
    
    @staticmethod
    def obter_todos_biomas() -> Dict[TipoBioma, DadosBioma]:
        """Retorna todos os biomas do jogo"""
        return {
            TipoBioma.FLORESTA: ConfiguradorBiomas.obter_floresta(),
            TipoBioma.MONTANHA: ConfiguradorBiomas.obter_montanha(),
            TipoBioma.DESERTO: ConfiguradorBiomas.obter_deserto(),
            TipoBioma.VULCAO: ConfiguradorBiomas.obter_vulcao(),
            TipoBioma.ALAGADO: ConfiguradorBiomas.obter_alagado(),
            TipoBioma.CEMITERIO: ConfiguradorBiomas.obter_cemiterio(),
            TipoBioma.FLORESTA_SOMBRA: ConfiguradorBiomas.obter_floresta_sombra(),
            TipoBioma.TUNDRA: ConfiguradorBiomas.obter_tundra(),
            TipoBioma.CAVERNA: ConfiguradorBiomas.obter_caverna(),
            TipoBioma.PRADARIA: ConfiguradorBiomas.obter_pradaria(),
        }
