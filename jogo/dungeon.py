"""Sistema de Masmorras - Procedurally Generated Dungeons with Lore"""
from dataclasses import dataclass, field
from enum import Enum
import random
from typing import Optional, List, Dict
from .config import DIRECOES


class TipoBiomaMasmorra(Enum):
    """Tipos de biomas em masmorras"""
    CAVERNA_PEDRA = "caverna_pedra"  # Stone caves - basic dungeons
    CRIPTA_ANTIGA = "cripta_antiga"  # Ancient crypts - undead themed
    TORRE_MALDITA = "torre_maldita"  # Cursed tower - magic/dark
    TEMPLO_ESQUECIDO = "templo_esquecido"  # Forgotten temple - treasure
    MINA_PROFUNDA = "mina_profunda"  # Deep mine - industrial/ore
    FLORESTAS_SOMBRIAS = "florestas_sombrias"  # Dark forest - nature/beasts
    VULCAO = "vulcao"  # Volcano - lava/fire themed


class TipoSala(Enum):
    """Tipos de salas em masmorras"""
    ENTRADA = "entrada"
    CORREDOR = "corredor"
    SALA_COMUM = "sala_comum"
    TESOURO = "tesouro"
    BOSS = "boss"
    ARMADILHAS = "armadilhas"
    REPOUSO = "repouso"  # Safe room


class DificuldadeMasmorra(Enum):
    """Níveis de dificuldade"""
    FACIL = 1
    NORMAL = 2
    DIFICIL = 3
    IMPLACAVEL = 4


@dataclass(slots=True)
class Bauzin:
    """Representa um baú no dungeon"""
    x: int
    y: int
    ouro: int = 0
    itens: List[Dict] = field(default_factory=list)
    foi_aberto: bool = False
    raridade: str = "comum"  # comum, raro, lendario
    
    def abrir(self) -> Dict:
        """Abre o baú e retorna conteúdo"""
        if self.foi_aberto:
            return {}
        self.foi_aberto = True
        return {
            "ouro": self.ouro,
            "itens": self.itens.copy()
        }


@dataclass(slots=True)
class InimigoDungeon:
    """Representa um inimigo em um dungeon"""
    id: int
    x: int
    y: int
    tipo: str  # "goblin", "skeleton", "demon", etc.
    vida_max: int
    vida_atual: int
    ataque: int
    defesa: int
    velocidade: int
    ouro_drop: int
    itens_drop: List[Dict] = field(default_factory=list)
    patrulhando: bool = True
    alerta: bool = False
    visto_jogador: bool = False
    
    @property
    def esta_vivo(self) -> bool:
        return self.vida_atual > 0
    
    def receber_dano(self, dano: int) -> int:
        """Recebe dano e retorna dano real"""
        dano_real = max(1, dano - self.defesa)
        self.vida_atual = max(0, self.vida_atual - dano_real)
        if self.vida_atual > 0:
            self.alerta = True
        return dano_real


@dataclass(slots=True)
class SalaMasmorra:
    """Representa uma sala no dungeon"""
    id: int
    x: int  # Coordenada em grid
    y: int
    tipo: TipoSala
    largura: int = 10
    altura: int = 10
    inimigos: List[InimigoDungeon] = field(default_factory=list)
    bauzins: List[Bauzin] = field(default_factory=list)
    conectada_a: List[int] = field(default_factory=list)  # IDs das salas conectadas
    foi_explorada: bool = False
    tem_chefe: bool = False
    nome: str = ""
    descricao: str = ""
    
    def obter_inimigos_vivos(self) -> List[InimigoDungeon]:
        """Retorna inimigos que ainda estão vivos"""
        return [i for i in self.inimigos if i.esta_vivo]
    
    def esta_vazia(self) -> bool:
        """Verifica se a sala está vazia de inimigos"""
        return len(self.obter_inimigos_vivos()) == 0


class Gerador_Masmorra:
    """Gera masmorras proceduralmente com profundidade e temática"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.seed = seed or random.randint(0, 999999)
    
    def gerar(self, profundidade: int, bioma: TipoBiomaMasmorra) -> 'Masmorra':
        """Gera uma masmorra completa"""
        num_salas = 5 + profundidade * 2  # Mais profundo = mais salas
        dificuldade = self._calcular_dificuldade(profundidade)
        
        salas = self._gerar_salas(num_salas, bioma, dificuldade)
        mapa_conexoes = self._conectar_salas(salas)
        self._popular_inimigos(salas, bioma, dificuldade)
        self._popular_bauzinhos(salas, dificuldade)
        
        return Masmorra(
            id=self.seed,
            profundidade=profundidade,
            bioma=bioma,
            dificuldade=dificuldade,
            salas=salas,
            sala_atual_id=0
        )
    
    def _calcular_dificuldade(self, profundidade: int) -> DificuldadeMasmorra:
        """Calcula dificuldade baseada na profundidade"""
        if profundidade == 0:
            return DificuldadeMasmorra.FACIL
        elif profundidade <= 2:
            return DificuldadeMasmorra.NORMAL
        elif profundidade <= 4:
            return DificuldadeMasmorra.DIFICIL
        else:
            return DificuldadeMasmorra.IMPLACAVEL
    
    def _gerar_salas(self, num_salas: int, bioma: TipoBiomaMasmorra, 
                     dificuldade: DificuldadeMasmorra) -> List[SalaMasmorra]:
        """Gera salas individuais"""
        salas = []
        
        # Sempre cria sala de entrada
        sala_entrada = SalaMasmorra(
            id=0,
            x=0, y=0,
            tipo=TipoSala.ENTRADA,
            largura=12, altura=10,
            nome="Entrada da Masmorra"
        )
        salas.append(sala_entrada)
        
        # Gera salas intermediárias
        for i in range(1, num_salas - 1):
            tipo = random.choice([TipoSala.SALA_COMUM, TipoSala.CORREDOR, 
                                 TipoSala.ARMADILHAS])
            sala = SalaMasmorra(
                id=i,
                x=random.randint(0, 5),
                y=random.randint(0, 5),
                tipo=tipo,
                largura=random.randint(8, 14),
                altura=random.randint(8, 14),
                nome=self._gerar_nome_sala(bioma, tipo)
            )
            salas.append(sala)
        
        # Cria sala do chefe (boss room)
        sala_boss = SalaMasmorra(
            id=num_salas - 1,
            x=random.randint(3, 7),
            y=random.randint(3, 7),
            tipo=TipoSala.BOSS,
            largura=16, altura=14,
            nome=f"Câmara do {self._gerar_nome_chefe(bioma)}",
            tem_chefe=True
        )
        salas.append(sala_boss)
        
        return salas
    
    def _conectar_salas(self, salas: List[SalaMasmorra]) -> List[List[int]]:
        """Conecta salas de forma a criar um caminho"""
        # Cria caminho linear com algumas conexões aleatórias para exploração
        for i in range(len(salas) - 1):
            salas[i].conectada_a.append(salas[i + 1].id)
            salas[i + 1].conectada_a.append(salas[i].id)
        
        # Adiciona algumas conexões aleatórias para mais exploração
        for _ in range(len(salas) // 2):
            sala1 = random.choice(salas)
            sala2 = random.choice(salas)
            if sala1.id != sala2.id:
                if sala2.id not in sala1.conectada_a:
                    sala1.conectada_a.append(sala2.id)
                if sala1.id not in sala2.conectada_a:
                    sala2.conectada_a.append(sala1.id)
        
        return []  # Retorna vazio por compatibilidade
    
    def _popular_inimigos(self, salas: List[SalaMasmorra], 
                         bioma: TipoBiomaMasmorra, dificuldade: DificuldadeMasmorra):
        """Popula salas com inimigos"""
        tipos_inimigos = self._obter_tipos_inimigos_bioma(bioma)
        stats_base = self._obter_stats_dificuldade(dificuldade)
        
        contador_id = 0
        for sala in salas[1:]:  # Pula sala de entrada
            if sala.tipo == TipoSala.BOSS:
                # Boss único
                chefe = self._gerar_chefe(bioma, stats_base, contador_id)
                sala.inimigos.append(chefe)
                contador_id += 1
            elif sala.tipo != TipoSala.ARMADILHAS:
                # Salas normais têm vários inimigos
                num_inimigos = random.randint(2, 4 + dificuldade.value)
                for _ in range(num_inimigos):
                    tipo = random.choice(tipos_inimigos)
                    inimigo = self._gerar_inimigo(tipo, stats_base, contador_id, sala)
                    sala.inimigos.append(inimigo)
                    contador_id += 1
    
    def _popular_bauzinhos(self, salas: List[SalaMasmorra], 
                          dificuldade: DificuldadeMasmorra):
        """Popula salas com baús de tesouro"""
        for sala in salas:
            if sala.tipo == TipoSala.TESOURO or (sala.tipo == TipoSala.SALA_COMUM and random.random() < 0.4):
                num_bauzinhos = random.randint(1, 2)
                for _ in range(num_bauzinhos):
                    raridade = random.choices(
                        ["comum", "raro", "lendario"],
                        weights=[0.6, 0.3, 0.1]
                    )[0]
                    ouro = {
                        "comum": random.randint(50, 150),
                        "raro": random.randint(200, 400),
                        "lendario": random.randint(500, 1000)
                    }[raridade]
                    
                    bauzin = Bauzin(
                        x=random.randint(1, sala.largura - 2),
                        y=random.randint(1, sala.altura - 2),
                        ouro=ouro,
                        raridade=raridade
                    )
                    sala.bauzins.append(bauzin)
    
    def _gerar_inimigo(self, tipo: str, stats_base: Dict, id: int, 
                      sala: SalaMasmorra) -> InimigoDungeon:
        """Gera um inimigo individual"""
        vida = stats_base["vida"] + random.randint(-5, 15)
        ataque = stats_base["ataque"] + random.randint(-2, 5)
        
        return InimigoDungeon(
            id=id,
            x=random.randint(2, sala.largura - 3),
            y=random.randint(2, sala.altura - 3),
            tipo=tipo,
            vida_max=vida,
            vida_atual=vida,
            ataque=ataque,
            defesa=stats_base["defesa"],
            velocidade=stats_base["velocidade"],
            ouro_drop=stats_base["ouro"]
        )
    
    def _gerar_chefe(self, bioma: TipoBiomaMasmorra, stats_base: Dict, 
                    id: int) -> InimigoDungeon:
        """Gera um chefe único"""
        return InimigoDungeon(
            id=id,
            x=8, y=7,
            tipo=f"chefe_{bioma.value}",
            vida_max=int(stats_base["vida"] * 3),
            vida_atual=int(stats_base["vida"] * 3),
            ataque=int(stats_base["ataque"] * 1.8),
            defesa=int(stats_base["defesa"] * 1.5),
            velocidade=stats_base["velocidade"],
            ouro_drop=stats_base["ouro"] * 5
        )
    
    def _obter_tipos_inimigos_bioma(self, bioma: TipoBiomaMasmorra) -> List[str]:
        """Retorna tipos de inimigos apropriados para o bioma"""
        templates = {
            TipoBiomaMasmorra.CAVERNA_PEDRA: ["goblin", "morcego", "aranha"],
            TipoBiomaMasmorra.CRIPTA_ANTIGA: ["esqueleto", "zumbi", "espectro"],
            TipoBiomaMasmorra.TORRE_MALDITA: ["bruxo", "demonio", "sombra"],
            TipoBiomaMasmorra.TEMPLO_ESQUECIDO: ["golem", "guardiao_antigo", "naga"],
            TipoBiomaMasmorra.MINA_PROFUNDA: ["mineiro_corrompido", "toupeira_gigante", "golem_ferro"],
            TipoBiomaMasmorra.FLORESTAS_SOMBRIAS: ["lobo_negro", "centauro", "fada_sombria"],
            TipoBiomaMasmorra.VULCAO: ["elemental_fogo", "dragao_jovem", "salamandra"]
        }
        return templates.get(bioma, ["goblin", "esqueleto", "aranha"])
    
    def _obter_stats_dificuldade(self, dificuldade: DificuldadeMasmorra) -> Dict:
        """Retorna stats base para dificuldade"""
        stats = {
            DificuldadeMasmorra.FACIL: {"vida": 10, "ataque": 3, "defesa": 0, "velocidade": 2, "ouro": 20},
            DificuldadeMasmorra.NORMAL: {"vida": 20, "ataque": 5, "defesa": 1, "velocidade": 3, "ouro": 40},
            DificuldadeMasmorra.DIFICIL: {"vida": 35, "ataque": 8, "defesa": 2, "velocidade": 4, "ouro": 75},
            DificuldadeMasmorra.IMPLACAVEL: {"vida": 50, "ataque": 12, "defesa": 3, "velocidade": 5, "ouro": 120}
        }
        return stats[dificuldade]
    
    def _gerar_nome_sala(self, bioma: TipoBiomaMasmorra, tipo: TipoSala) -> str:
        """Gera nome temático para sala"""
        nomes_bioma = {
            TipoBiomaMasmorra.CAVERNA_PEDRA: ["Câmara Rochosa", "Gruta Profunda", "Núcleo Pétreo", "Caverna Ressonante"],
            TipoBiomaMasmorra.CRIPTA_ANTIGA: ["Câmara Mortuária", "Vale Esquecido", "Sepulcro Antigo", "Câmara Ossuda"],
            TipoBiomaMasmorra.TORRE_MALDITA: ["Aposento Amaldiçoado", "Torre Escura", "Câmara Mágica", "Hall Corrompido"],
            TipoBiomaMasmorra.TEMPLO_ESQUECIDO: ["Sanctuário Antigo", "Altar Esquecido", "Tesouro Sagrado", "Câmara Divina"],
            TipoBiomaMasmorra.MINA_PROFUNDA: ["Galerias de Minério", "Vulto Profundo", "Câmara Cristalina", "Poços Fundos"],
            TipoBiomaMasmorra.FLORESTAS_SOMBRIAS: ["Bosque Obscuro", "Claro Misterioso", "Árvore Antiga", "Santuário da Floresta"],
            TipoBiomaMasmorra.VULCAO: ["Câmara Vulcânica", "Poço de Lava", "Câmara Ardente", "Magma Hall"]
        }
        return random.choice(nomes_bioma.get(bioma, ["Câmara Desconhecida"]))
    
    def _gerar_nome_chefe(self, bioma: TipoBiomaMasmorra) -> str:
        """Gera nome temático para chefe"""
        nomes_chefes = {
            TipoBiomaMasmorra.CAVERNA_PEDRA: "Titã de Pedra",
            TipoBiomaMasmorra.CRIPTA_ANTIGA: "Rei Esquecido",
            TipoBiomaMasmorra.TORRE_MALDITA: "Lorde da Maldição",
            TipoBiomaMasmorra.TEMPLO_ESQUECIDO: "Deus Antigo",
            TipoBiomaMasmorra.MINA_PROFUNDA: "Verme Ancestral",
            TipoBiomaMasmorra.FLORESTAS_SOMBRIAS: "Rainha da Noite",
            TipoBiomaMasmorra.VULCAO: "Dragão ancestral"
        }
        return nomes_chefes.get(bioma, "Guardião Antigo")


@dataclass(slots=True)
class Masmorra:
    """Representa uma masmorra completa com todas as salas"""
    id: int
    profundidade: int
    bioma: TipoBiomaMasmorra
    dificuldade: DificuldadeMasmorra
    salas: List[SalaMasmorra]
    sala_atual_id: int = 0
    foi_visitada: bool = False
    foi_completada: bool = False
    tempo_explorado: float = 0.0  # em minutos reais
    
    @property
    def sala_atual(self) -> SalaMasmorra:
        """Retorna a sala atual"""
        return self.salas[self.sala_atual_id]
    
    @property
    def num_salas_exploradas(self) -> int:
        """Retorna número de salas exploradas"""
        return sum(1 for sala in self.salas if sala.foi_explorada)
    
    def avancar_para_sala(self, sala_id: int) -> bool:
        """Move para próxima sala se conectada"""
        if sala_id in self.sala_atual.conectada_a:
            self.sala_atual_id = sala_id
            self.salas[sala_id].foi_explorada = True
            return True
        return False
    
    def completar(self):
        """Marca masmorra como completada"""
        self.foi_completada = True
    
    def obter_progresso(self) -> str:
        """Retorna descrição do progresso"""
        total = len(self.salas)
        exploradas = self.num_salas_exploradas
        return f"{exploradas}/{total} salas exploradas"
