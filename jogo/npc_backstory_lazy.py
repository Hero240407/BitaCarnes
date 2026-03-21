"""
NPC Family Relations and Backstory Lazy-Loading System
Generates basic backstories initially, detailed backstories on first interaction
Supports family trees: parents, siblings, spouse, children
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class TipoFamiliar(Enum):
    """Family relationship types"""
    PAI = "Pai"
    MAE = "Mãe"
    IRMAO = "Irmão"
    IRMA = "Irmã"
    AVOO = "Avô"
    AVOA = "Avó"
    TIO = "Tio"
    TIA = "Tia"
    SOBRINHO = "Sobrinho"
    SOBRINHA = "Sobrinha"
    PRIMO = "Primo"
    PRIMA = "Prima"
    MARIDO = "Marido"
    ESPOSA = "Esposa"
    FILHO = "Filho"
    FILHA = "Filha"
    ENTEADO = "Enteado"
    ENTEADA = "Enteada"


@dataclass
class FamiliarInfo:
    """Information about a family member"""
    nome: str
    tipo_relacao: TipoFamiliar
    idade: int
    status: str = "vivo"  # vivo, falecido, desaparecido
    local: str = "desconhecido"
    descricao_rapida: str = ""
    vivo: bool = True


@dataclass
class HistoriaBackstoryDetalhada:
    """Detailed backstory - generated on first NPC interaction"""
    nome_npc: str
    idade_natal: int
    
    # Narrative
    quem_e: str  # Full description
    como_cresceu: str  # Childhood events
    evento_marcante: str  # Life-changing event
    trauma: Optional[str] = None
    sonho_segredo: str = ""
    objetivo_vida: str = ""
    
    # Relationships
    familia: List[FamiliarInfo] = field(default_factory=list)
    npc_amigos: List[str] = field(default_factory=list)
    npc_rivais: List[str] = field(default_factory=list)
    npc_inimigos: List[str] = field(default_factory=list)
    npc_amor: Optional[str] = None
    
    # Character traits
    virtudes: List[str] = field(default_factory=list)
    vícios: List[str] = field(default_factory=list)
    medo: str = ""
    paixao: str = ""
    
    # Secrets
    segredo_escondido: str = ""
    perigo_segredo: bool = False
    
    # Status
    revelada: bool = False  # Has been revealed to player?
    tempo_revelacao_ms: int = 0  # When backstory was revealed


@dataclass
class HistoriaBackstoryBasica:
    """Basic backstory - always loaded"""
    nome_npc: str
    papel_social: str
    idade: int
    origem: str
    descricao_rapida: str = ""
    tem_familia: bool = False
    
    # Status
    detalhada_gerada: bool = False  # Has detailed version been created?
    detalhada: Optional[HistoriaBackstoryDetalhada] = None


class GeradorBackstoryLazyLoading:
    """Generates backstories on-demand (lazy loading)"""
    
    # Basic origins
    ORIGENS_RAPIDAS = {
        "aldeão": "Cresceu em uma pequena aldeia rural",
        "cidade": "Cresceu em uma cidade grande e movimentada",
        "floresta": "Cresceu em isolamento nas florestas",
        "castelo": "Nasceu na nobreza de um grande castelo",
        "masmorra": "Cresceu em um dungeon ou caverna",
        "viagem": "Passou a vida inteira viajando",
        "temple": "Cresceu em um templo religioso",
        "navio": "Cresceu em um navio pirata ou mercante",
        "rua": "Cresceu nas ruas como órfão",
    }
    
    # Character archetypes for backstories
    ARQUETIPO_DESCRICOES = {
        "Guerreiro": "Treinado em combate desde jovem",
        "Mago": "Descobriu talento mágico cedo",
        "Ladrão": "Aprendeu a sobreviver pela astúcia",
        "Clérigo": "Dedicado a uma fé ou deus",
        "Mercador": "Sempre teve talento para negócios",
        "Bardo": "Nascido para entretainment e carisma",
        "Caçador": "Conhece a natureza desde sempre",
        "Camponês": "Trabalhador da terra",
        "Nobre": "Nascido com privilégio",
        "Eremita": "Preferiu isolamento voluntário",
    }
    
    # Family generation chances
    TAMANHO_FAMILIA_CHANCE = {
        "pai": 0.7,
        "mae": 0.8,
        "irmaos": 0.6,  # Has siblings
        "avos": 0.4,
        "primos": 0.3,
    }
    
    # Life secrets and traumas
    TRAUMAS = [
        "Perdeu alguém querido quando criança",
        "Foi abandonado pela família",
        "Testemunhou uma tragédia",
        "Foi traído por alguém de confiança",
        "Perdeu tudo em um incêndio",
        "Foi escravizado por um tempo",
        "Quase morreu de doença",
        "Foi traído em amor",
    ]
    
    SONHOS = [
        "Quer encontrar sua verdadeira família",
        "Sonha em ficar rico",
        "Deseja se redimir de um pecado",
        "Quer resolver um mistério do passado",
        "Busca vingança contra alguém",
        "Sonha em viajar para terras distantes",
        "Quer proteger os inocentes",
        "Deseja descobrir magia antiga",
        "Sonha em ter uma família própria",
    ]
    
    VIRTUDES = [
        "Honesto", "Corajoso", "Compassivo", "Generoso",
        "Inteligente", "Disciplinado", "Leal", "Criativo", "Humilde"
    ]
    
    VICIOS = [
        "Ganancioso", "Preguiçoso", "Arrogante", "Impulsivo",
        "Medroso", "Mentiroso", "Ciumento", "Vingativo"
    ]
    
    @classmethod
    def criar_backstory_basica(cls, nome: str, papel_social: str, idade: int, origem: str) -> HistoriaBackstoryBasica:
        """Create a quick basic backstory"""
        descricao = cls.ORIGENS_RAPIDAS.get(origem, "Origem desconhecida")
        
        return HistoriaBackstoryBasica(
            nome_npc=nome,
            papel_social=papel_social,
            idade=idade,
            origem=origem,
            descricao_rapida=descricao,
            tem_familia=True,  # Assume everyone has family
            detalhada_gerada=False,
        )
    
    @classmethod
    def criar_backstory_detalhada(cls, basica: HistoriaBackstoryBasica, 
                                   arquetipo: str = "Heróis", seed: int = None) -> HistoriaBackstoryDetalhada:
        """Generate detailed backstory on first NPC interaction"""
        import random
        
        if seed:
            random.seed(seed)
        
        # Basic narrative
        descricao_tipo = cls.ARQUETIPO_DESCRICOES.get(arquetipo, "Um aventureiro")
        quem_e = f"{basica.descricao_rapida}. {descricao_tipo}, {basica.papel_social}."
        
        # Generate family
        familia = cls._gerar_familia(basica.nome_npc, basica.idade)
        
        # Random traits
        sofrimento = random.choice(cls.TRAUMAS) if random.random() > 0.4 else None
        sonho = random.choice(cls.SONHOS)
        virtudes = random.sample(cls.VIRTUDES, k=random.randint(2, 3))
        vicios = random.sample(cls.VICIOS, k=random.randint(1, 2))
        
        return HistoriaBackstoryDetalhada(
            nome_npc=basica.nome_npc,
            idade_natal=basica.idade,
            quem_e=quem_e,
            como_cresceu=basica.descricao_rapida,
            evento_marcante=sofrimento or "Uma experiência que mudou sua vida",
            trauma=sofrimento,
            sonho_segredo=sonho,
            objetivo_vida=f"Seus objetivos refletem seu {random.choice(['passado', 'sonho', 'obrigação'])}",
            familia=familia,
            virtudes=virtudes,
            vícios=vicios,
            medo=random.choice(["Solidão", "Fracasso", "Morte", "Atrição"]),
            paixao=random.choice(["Aventura", "Conhecimento", "Riqueza", "Redenção"]),
            segredo_escondido=random.choice([
                f"Tem um passado que prefere manter escondido",
                f"Está fugindo de algo ou alguém",
                f"Tem um objetivo secreto que poucos conhecem",
            ]),
            perigo_segredo=random.random() > 0.6,
        )
    
    @classmethod
    def _gerar_familia(cls, nome_npc: str, idade_npc: int) -> List[FamiliarInfo]:
        """Generate NPC's family members"""
        import random
        import string
        
        familia = []
        
        # Pais (80% chance)
        if random.random() < 0.8:
            idade_pai = idade_npc + random.randint(25, 40)
            status_pai = random.choice(
                ["vivo"] * 8 + ["falecido"] * 2
            )
            familia.append(FamiliarInfo(
                nome=f"Pai de {nome_npc}",
                tipo_relacao=TipoFamiliar.PAI,
                idade=idade_pai,
                status=status_pai,
                local="aldeã" if status_pai == "vivo" else "descansando",
                descricao_rapida=random.choice(["Protetor", "Guerreiro", "Comerciante", "Sábio"])
            ))
        
        if random.random() < 0.85:
            idade_mae = idade_npc + random.randint(22, 38)
            status_mae = random.choice(
                ["vivo"] * 8 + ["falecido", "desaparecido"] * 2
            )
            familia.append(FamiliarInfo(
                nome=f"Mãe de {nome_npc}",
                tipo_relacao=TipoFamiliar.MAE,
                idade=idade_mae,
                status=status_mae,
                local="aldeã" if status_mae == "vivo" else "desconhecido",
                descricao_rapida=random.choice(["Determinada", "Amorosa", "Sábia", "Forte"])
            ))
        
        # Siblings (60% chance)
        num_irmaos = 0
        if random.random() < 0.6:
            num_irmaos = random.randint(0, 3)
        
        for i in range(num_irmaos):
            idade_irmao = idade_npc + random.randint(-8, 8)
            tipo = TipoFamiliar.IRMA if random.random() > 0.5 else TipoFamiliar.IRMAO
            familia.append(FamiliarInfo(
                nome=f"{tipo.value} #{i+1}",
                tipo_relacao=tipo,
                idade=idade_irmao,
                status=random.choice(["vivo"] * 9 + ["falecido"]),
                local="aldeã" if random.random() > 0.3 else "distante",
            ))
        
        # Grandparents (40% chance)
        if random.random() < 0.4:
            familia.append(FamiliarInfo(
                nome="Avô",
                tipo_relacao=TipoFamiliar.AVOO,
                idade=idade_npc + random.randint(55, 75),
                status=random.choice(["vivo"] * 6 + ["falecido"] * 4),
                descricao_rapida="Conta histórias do passado"
            ))
        
        return familia
    
    @classmethod
    def revelar_backstory(cls, basica: HistoriaBackstoryBasica, arquetipo: str = "Heróis") -> HistoriaBackstoryDetalhada:
        """Reveal full backstory when player interacts with NPC"""
        if not basica.detalhada_gerada:
            basica.detalhada = cls.criar_backstory_detalhada(basica, arquetipo)
            basica.detalhada_gerada = True
        
        return basica.detalhada


class SistemaBackstoriesLazyLoading:
    """Manages all NPC backstories with lazy loading"""
    
    def __init__(self):
        self.backstories_basicas: Dict[str, HistoriaBackstoryBasica] = {}
        self.backstories_detalhadas: Dict[str, HistoriaBackstoryDetalhada] = {}
    
    def criar_npc_backstory(self, nome: str, papel_social: str, idade: int, origem: str) -> HistoriaBackstoryBasica:
        """Create and store basic backstory for NPC"""
        basica = GeradorBackstoryLazyLoading.criar_backstory_basica(nome, papel_social, idade, origem)
        self.backstories_basicas[nome] = basica
        return basica
    
    def revelar_backstory_npc(self, nome: str, arquetipo: str = "Heróis") -> Optional[HistoriaBackstoryDetalhada]:
        """Reveal detailed backstory when player interacts"""
        if nome not in self.backstories_basicas:
            return None
        
        basica = self.backstories_basicas[nome]
        detalhada = GeradorBackstoryLazyLoading.revelar_backstory(basica, arquetipo)
        self.backstories_detalhadas[nome] = detalhada
        return detalhada
    
    def obter_backstory_basica(self, nome: str) -> Optional[HistoriaBackstoryBasica]:
        """Get basic backstory (always available)"""
        return self.backstories_basicas.get(nome)
    
    def obter_backstory_detalhada(self, nome: str) -> Optional[HistoriaBackstoryDetalhada]:
        """Get detailed backstory if revealed"""
        if not self.backstories_detalhadas.get(nome):
            return self.revelar_backstory_npc(nome)
        return self.backstories_detalhadas.get(nome)
    
    def obter_familia_npc(self, nome: str) -> List[FamiliarInfo]:
        """Get NPC's family members"""
        detalhada = self.obter_backstory_detalhada(nome)
        if detalhada:
            return detalhada.familia
        return []
    
    def foi_revelada_backstory(self, nome: str) -> bool:
        """Check if backstory has been revealed to player"""
        return nome in self.backstories_detalhadas
