"""Sistema de Mobs Expandido - Expansão de animais selvagens para criaturas variadas"""
from dataclasses import dataclass, field
from enum import Enum
import random
from typing import Optional, List, Dict


class TipoMob(Enum):
    """Tipos de mobs no mundo"""
    # Animais passivos
    ANIMAL_PASSIVO = "animal_passivo"
    # Criaturas basicamente hostis
    GOBLIN = "goblin"
    LOBO = "lobo"
    URSO = "urso"
    ARANHA_GIGANTE = "aranha_gigante"
    MORCEGO = "morcego"
    # Inimigos magicos/fantasmagóricos
    ESPECTRO = "espectro"
    ESQUELETO = "esqueleto"
    ZUMBI = "zumbi"
    # Criaturas raras e perigosas
    DRAGAO = "dragao"
    ELEMENTAL = "elemental"
    GOLEM = "golem"


class BiomaMob(Enum):
    """Biomas e suas criaturas """
    FLORESTA = "floresta"
    PRADARIA = "pradaria"
    MONTANHA = "montanha"
    SUBTERRANEO = "subterraneo"
    ALAGADO = "alagado"
    CEMITERIO = "cemiterio"
    VULCAO = "vulcao"


class RaridadeMob(Enum):
    """Raridade de mobs"""
    COMUM = 1
    INCOMUM = 2
    RARO = 3
    LENDARIO = 4


@dataclass(slots=True)
class DefinicaoMob:
    """Define tipos de mobs disponíveis no mundo"""
    tipo: TipoMob
    nome: str
    descricao: str
    biomas_nativos: List[BiomaMob]
    raridade: RaridadeMob
    vida: int
    ataque: int
    defesa: int
    velocidade: int
    ouro_drop_min: int
    ouro_drop_max: int
    exp_drop: int
    itens_drop_possíveis: List[Dict] = field(default_factory=list)  # {"nome": "osso", "chance": 0.3}
    tamanho: str = "médio"  # pequeno, médio, grande
    comportamento: str = "agressivo"  # agressivo, tímido, patrulhador
    sons: List[str] = field(default_factory=list)


MOBS_DATABASE = {
    "goblin": DefinicaoMob(
        tipo=TipoMob.GOBLIN,
        nome="Goblin",
        descricao="Pequena criatura verde e maldosa",
        biomas_nativos=[BiomaMob.FLORESTA, BiomaMob.SUBTERRANEO],
        raridade=RaridadeMob.COMUM,
        vida=8, ataque=3, defesa=0, velocidade=3,
        ouro_drop_min=10, ouro_drop_max=30,
        exp_drop=50,
        tamanho="pequeno",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "faca_goblin", "chance": 0.2},
            {"nome": "moeda_ferida", "chance": 0.15}
        ]
    ),
    "lobo": DefinicaoMob(
        tipo=TipoMob.LOBO,
        nome="Lobo",
        descricao="Criatura selvagem e predadora",
        biomas_nativos=[BiomaMob.FLORESTA, BiomaMob.PRADARIA],
        raridade=RaridadeMob.COMUM,
        vida=12, ataque=4, defesa=1, velocidade=5,
        ouro_drop_min=15, ouro_drop_max=40,
        exp_drop=75,
        tamanho="grande",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "pelagem_lobo", "chance": 0.5},
            {"nome": "dente_lobo", "chance": 0.3}
        ]
    ),
    "urso": DefinicaoMob(
        tipo=TipoMob.URSO,
        nome="Urso Selvagem",
        descricao="Fera poderosa e territorial",
        biomas_nativos=[BiomaMob.FLORESTA, BiomaMob.MONTANHA],
        raridade=RaridadeMob.INCOMUM,
        vida=25, ataque=6, defesa=2, velocidade=2,
        ouro_drop_min=50, ouro_drop_max=100,
        exp_drop=200,
        tamanho="grande",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "garra_urso", "chance": 0.4},
            {"nome": "ouro_bruto", "chance": 0.2}
        ]
    ),
    "aranha_gigante": DefinicaoMob(
        tipo=TipoMob.ARANHA_GIGANTE,
        nome="Aranha Gigante",
        descricao="Aracnídeo venenoso com tamanho anormal",
        biomas_nativos=[BiomaMob.SUBTERRANEO, BiomaMob.ALAGADO],
        raridade=RaridadeMob.INCOMUM,
        vida=15, ataque=5, defesa=0, velocidade=4,
        ouro_drop_min=25, ouro_drop_max=60,
        exp_drop=120,
        tamanho="grande",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "veneno_aranha", "chance": 0.5},
            {"nome": "teia_resina", "chance": 0.3}
        ]
    ),
    "morcego": DefinicaoMob(
        tipo=TipoMob.MORCEGO,
        nome="Morcego",
        descricao="Criatura voadora da noite",
        biomas_nativos=[BiomaMob.SUBTERRANEO, BiomaMob.CEMITERIO],
        raridade=RaridadeMob.COMUM,
        vida=6, ataque=2, defesa=0, velocidade=6,
        ouro_drop_min=5, ouro_drop_max=15,
        exp_drop=30,
        tamanho="pequeno",
        comportamento="tímido",
        itens_drop_possíveis=[
            {"nome": "asa_morcego", "chance": 0.2}
        ]
    ),
    "esqueleto": DefinicaoMob(
        tipo=TipoMob.ESQUELETO,
        nome="Esqueleto",
        descricao="Ossos amaldiçoados animados por magia negra",
        biomas_nativos=[BiomaMob.CEMITERIO, BiomaMob.SUBTERRANEO],
        raridade=RaridadeMob.INCOMUM,
        vida=18, ataque=4, defesa=1, velocidade=2,
        ouro_drop_min=30, ouro_drop_max=70,
        exp_drop=100,
        tamanho="médio",
        comportamento="patrulhador",
        itens_drop_possíveis=[
            {"nome": "osso_perfeito", "chance": 0.4},
            {"nome": "cristal_sombrio", "chance": 0.1}
        ]
    ),
    "zumbi": DefinicaoMob(
        tipo=TipoMob.ZUMBI,
        nome="Zumbi",
        descricao="Cadáver ressuscitado, lento mas obstinado",
        biomas_nativos=[BiomaMob.CEMITERIO, BiomaMob.ALAGADO],
        raridade=RaridadeMob.INCOMUM,
        vida=20, ataque=3, defesa=2, velocidade=1,
        ouro_drop_min=25, ouro_drop_max=60,
        exp_drop=90,
        tamanho="médio",
        comportamento="patrulhador",
        itens_drop_possíveis=[
            {"nome": "carne_podre", "chance": 0.3}
        ]
    ),
    "espectro": DefinicaoMob(
        tipo=TipoMob.ESPECTRO,
        nome="Espectro",
        descricao="Espírito amaldiçoado que não encontra descanso",
        biomas_nativos=[BiomaMob.CEMITERIO, BiomaMob.SUBTERRANEO],
        raridade=RaridadeMob.RARO,
        vida=22, ataque=6, defesa=1, velocidade=5,
        ouro_drop_min=100, ouro_drop_max=200,
        exp_drop=250,
        tamanho="médio",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "essencia_espectral", "chance": 0.6},
            {"nome": "colar_antigo", "chance": 0.2}
        ]
    ),
    "elemental_fogo": DefinicaoMob(
        tipo=TipoMob.ELEMENTAL,
        nome="Elemental de Fogo",
        descricao="Criatura viva feita de chamas ardentes",
        biomas_nativos=[BiomaMob.VULCAO, BiomaMob.MONTANHA],
        raridade=RaridadeMob.RARO,
        vida=28, ataque=7, defesa=1, velocidade=3,
        ouro_drop_min=150, ouro_drop_max=300,
        exp_drop=350,
        tamanho="médio",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "cristal_fogo", "chance": 0.7},
            {"nome": "cinzas_magicas", "chance": 0.4}
        ]
    ),
    "dragao_jovem": DefinicaoMob(
        tipo=TipoMob.DRAGAO,
        nome="Dragão Jovem",
        descricao="Dragão imaturo, ainda perigoso e arrogante",
        biomas_nativos=[BiomaMob.MONTANHA, BiomaMob.VULCAO],
        raridade=RaridadeMob.LENDARIO,
        vida=60, ataque=12, defesa=4, velocidade=4,
        ouro_drop_min=500, ouro_drop_max=1000,
        exp_drop=1000,
        tamanho="grande",
        comportamento="agressivo",
        itens_drop_possíveis=[
            {"nome": "escama_dragao", "chance": 0.8},
            {"nome": "orbe_draconica", "chance": 0.3}
        ]
    ),
}


@dataclass(slots=True)
class Mob:
    """Representa uma instância de um mob no mundo"""
    id: int
    x: int
    y: int
    tipo: TipoMob
    nome: str
    vida_max: int
    vida_atual: int
    ataque: int
    defesa: int
    velocidade: int
    ouro_drop: int
    exp_drop: int
    raridade: RaridadeMob
    bioma: BiomaMob
    comportamento: str
    # Estado dinâmico
    alerta: bool = False
    visto_jogador: bool = False
    em_combate: bool = False
    tempo_ultima_acao: float = 0.0
    tempo_último_dano: float = 0.0
    
    @property
    def esta_vivo(self) -> bool:
        return self.vida_atual > 0
    
    @property
    def percentual_vida(self) -> float:
        """Retorna percentual de vida (0-100)"""
        return (self.vida_atual / self.vida_max) * 100 if self.vida_max > 0 else 0
    
    def receber_dano(self, dano: int) -> int:
        """Recebe dano, reduzido pela defesa"""
        dano_real = max(1, dano - self.defesa)
        self.vida_atual = max(0, self.vida_atual - dano_real)
        self.alerta = True
        self.em_combate = self.vida_atual > 0
        return dano_real
    
    def curar(self, quantidade: int):
        """Cura o mob"""
        self.vida_atual = min(self.vida_max, self.vida_atual + quantidade)
    
    def infligir_status(self, status: str, duracao: int):
        """Aplica efeito de status"""
        # To be extended with status effects in future
        pass


class GerenciadorMobs:
    """Gerencia spawning, comportamento e atualização de mobs"""
    
    def __init__(self):
        self.mobs: Dict[int, Mob] = {}
        self.contador_id = 0
        self.tempo_ultimo_spawn = 0.0
    
    def spawan_mob_random(self, bioma: BiomaMob, x: int, y: int) -> Mob:
        """Spawna um mob aleatório apropriado para o bioma"""
        mobs_bioma = [db for db in MOBS_DATABASE.values() 
                      if bioma in db.biomas_nativos]
        
        if not mobs_bioma:
            # Fallback a goblin
            def_mob = MOBS_DATABASE["goblin"]
        else:
            # Pesa por raridade (mais comum = mais provável)
            def_mob = random.choices(
                mobs_bioma,
                weights=[4 - m.raridade.value for m in mobs_bioma]
            )[0]
        
        return self.criar_mob(def_mob, x, y, bioma)
    
    def criar_mob(self, definicao: DefinicaoMob, x: int, y: int, 
                 bioma: BiomaMob) -> Mob:
        """Cria uma instância de mob"""
        # Varia stats em ±20%
        variacao = 0.2
        vida = int(definicao.vida * random.uniform(1 - variacao, 1 + variacao))
        ataque = int(definicao.ataque * random.uniform(1 - variacao, 1 + variacao))
        defesa = int(definicao.defesa * random.uniform(1 - variacao, 1 + variacao))
        velocidade = int(definicao.velocidade * random.uniform(1 - variacao, 1 + variacao))
        ouro = random.randint(definicao.ouro_drop_min, definicao.ouro_drop_max)
        
        mob = Mob(
            id=self.contador_id,
            x=x, y=y,
            tipo=definicao.tipo,
            nome=definicao.nome,
            vida_max=vida,
            vida_atual=vida,
            ataque=ataque,
            defesa=defesa,
            velocidade=velocidade,
            ouro_drop=ouro,
            exp_drop=definicao.exp_drop,
            raridade=definicao.raridade,
            bioma=bioma,
            comportamento=definicao.comportamento
        )
        
        self.mobs[self.contador_id] = mob
        self.contador_id += 1
        return mob
    
    def remover_mob(self, mob_id: int):
        """Remove um mob do mundo"""
        if mob_id in self.mobs:
            del self.mobs[mob_id]
    
    def obter_mobs_vivos(self) -> List[Mob]:
        """Retorna todos os mobs vivos"""
        return [m for m in self.mobs.values() if m.esta_vivo]
    
    def obter_mobs_em_area(self, x: int, y: int, raio: int) -> List[Mob]:
        """Retorna mobs em uma área específica"""
        resultado = []
        for mob in self.mobs.values():
            distancia = ((mob.x - x) ** 2 + (mob.y - y) ** 2) ** 0.5
            if distancia <= raio and mob.esta_vivo:
                resultado.append(mob)
        return resultado
    
    def atualizar_mobs(self, tempo_delta: float):
        """Atualiza comportamento de todos os mobs"""
        # Remove mobs mortos
        mobs_mortos = [m for m in self.mobs.values() if not m.esta_vivo]
        for mob in mobs_mortos:
            self.remover_mob(mob.id)
        
        # Atualiza tempo de alerta
        for mob in self.mobs.values():
            if mob.alerta:
                # Alerta decai com o tempo
                pass  # To be implemented with AI behavior
    
    def debugar_stats_mob(self, tipo: str) -> Dict:
        """Retorna stats de um tipo de mob"""
        if tipo in MOBS_DATABASE:
            db = MOBS_DATABASE[tipo]
            return {
                "nome": db.nome,
                "vida": db.vida,
                "ataque": db.ataque,
                "defesa": db.defesa,
                "velocidade": db.velocidade,
                "raridade": db.raridade.name,
                "biomas": [b.value for b in db.biomas_nativos]
            }
        return {}
