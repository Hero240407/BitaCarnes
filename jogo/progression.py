"""Sistema de Habilidades e Progressão - Leveling, skills, e desenvolvimento do personagem"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
import random


class TipoHabilidade(Enum):
    """Categorias de habilidades"""
    COMBATE = "combate"
    MAGIA = "magia"
    NATUREZA = "natureza"
    CONHECIMENTO = "conhecimento"
    SOBREVIVENCIA = "sobrevivencia"


class Raridade_Habilidade(Enum):
    """Raridade de habilidades"""
    COMUM = 1
    INCOMUM = 2
    RARA = 3
    EPICA = 4
    LENDARIA = 5


@dataclass(slots=True)
class Habilidade:
    """Define uma habilidade que o jogador pode aprender"""
    id: int
    nome: str
    tipo: TipoHabilidade
    descricao: str
    raridade: Raridade_Habilidade
    nivel_requerido: int
    pré_requisitos: List[int] = field(default_factory=list)  # IDs de habilidades
    
    # Efeitos da habilidade
    custo_mana: int = 0
    tempo_recarga: float = 0.0  # segundos
    dano_base: int = 0
    modificador_defesa: int = 0
    cura_base: int = 0
    
    # Scaling com stats
    escala_ataque: float = 0.0  # Multiplicador do ataque do jogador
    escala_defesa: float = 0.0
    escala_inteligencia: float = 0.0
    
    # Efeitos especiais
    efeitos: List[Dict] = field(default_factory=list)
    
    def obter_dano_final(self, ataque_jogador: int, inteligencia: int) -> int:
        """Calcula dano linal da habilidade"""
        dano = self.dano_base
        dano += int(ataque_jogador * self.escala_ataque)
        dano += int(inteligencia * self.escala_inteligencia)
        return max(1, dano)


@dataclass(slots=True)
class HabilidadeAprendida:
    """Representa uma habilidade que o jogador aprendeu"""
    habilidade_id: int
    nome: str
    nivel: int = 1  # 1-10
    experiencia: int = 0  # Progresso para próximo nível
    tempo_ultima_uso: float = 0.0
    
    @property
    def exp_restante(self) -> int:
        """EXP necessária para próximo nível"""
        return (self.nivel * 100) - self.experiencia
    
    def ganhar_exp(self, quantidade: int) -> bool:
        """Ganha EXP e sobe de nível se necessário"""
        self.experiencia += quantidade
        if self.experiencia >= self.nivel * 100:
            self.nivel = min(10, self.nivel + 1)
            self.experiencia = 0
            return True  # Levou up
        return False
    
    def pode_usar(self, tempo_atual: float) -> bool:
        """Verifica se habilidade pode ser usada (recarga)"""
        # To be implemented with timing system
        return True


class BancoDados_Habilidades:
    """Banco de dados de todas as habilidades disponíveis"""
    
    # COMBATE
    GOLPE_CRITICO = Habilidade(
        id=101, nome="Golpe Crítico",
        tipo=TipoHabilidade.COMBATE,
        descricao="Um ataque poderoso que ignora 50% da defesa inimiga.",
        raridade=Raridade_Habilidade.COMUM,
        nivel_requerido=1,
        dano_base=10,
        escala_ataque=1.5,
        custo_mana=0,
        tempo_recarga=2.0
    )
    
    ATAQUE_TORNADO = Habilidade(
        id=102, nome="Ataque Tornado",
        tipo=TipoHabilidade.COMBATE,
        descricao="Gira o corpo inteiro atacando tudo ao redor.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=5,
        dano_base=15,
        escala_ataque=1.2,
        custo_mana=10,
        tempo_recarga=3.0,
        efeitos=[{"tipo": "AOE", "raio": 2}]
    )
    
    DEFESA_FERREA = Habilidade(
        id=103, nome="Defesa Férrea",
        tipo=TipoHabilidade.COMBATE,
        descricao="Prepara uma posição defensiva, aumentando defesa temporariamente.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=8,
        modificador_defesa=5,
        custo_mana=0,
        tempo_recarga=4.0,
        efeitos=[{"tipo": "defesa", "duracao": 5}]
    )
    
    LÂMINA_MÃGICA = Habilidade(
        id=104, nome="Lâmina Mágica",
        tipo=TipoHabilidade.COMBATE,
        descricao="Encanta sua arma com magia, aumentando dano significativamente.",
        raridade=Raridade_Habilidade.RARA,
        nivel_requerido=15,
        dano_base=20,
        escala_ataque=1.8,
        escala_inteligencia=0.5,
        custo_mana=30,
        tempo_recarga=5.0,
        efeitos=[{"tipo": "buff", "atributo": "ataque", "duracao": 8}]
    )
    
    # MAGIA
    BOLA_FOGO = Habilidade(
        id=201, nome="Bola de Fogo",
        tipo=TipoHabilidade.MAGIA,
        descricao="Lança uma esfera de chamas que explode ao acertar.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=10,
        dano_base=25,
        escala_inteligencia=1.5,
        custo_mana=25,
        tempo_recarga=2.5,
        efeitos=[{"tipo": "AOE", "raio": 2}, {"tipo": "fogo", "duracao": 3}]
    )
    
    ESCUDO_MAGICO = Habilidade(
        id=202, nome="Escudo Mágico",
        tipo=TipoHabilidade.MAGIA,
        descricao="Cria um escudo mágico que absorve dano.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=8,
        modificador_defesa=4,
        custo_mana=20,
        tempo_recarga=3.0,
        efeitos=[{"tipo": "escudo", "duracao": 6, "valor": 40}]
    )
    
    RAIO = Habilidade(
        id=203, nome="Raio",
        tipo=TipoHabilidade.MAGIA,
        descricao="Invoca um raio que ataca inimigos múltiplos.",
        raridade=Raridade_Habilidade.RARA,
        nivel_requerido=20,
        dano_base=35,
        escala_inteligencia=2.0,
        custo_mana=40,
        tempo_recarga=4.0,
        efeitos=[{"tipo": "AOE", "raio": 3}, {"tipo": "paralisia", "chance": 0.3}]
    )
    
    TELEPORTE = Habilidade(
        id=204, nome="Teleporte",
        tipo=TipoHabilidade.MAGIA,
        descricao="Se move instantaneamente para um local observado.",
        raridade=Raridade_Habilidade.EPICA,
        nivel_requerido=25,
        custo_mana=50,
        tempo_recarga=6.0,
        efeitos=[{"tipo": "movimento", "alcance": 5}]
    )
    
    # NATUREZA
    REGENERACAO = Habilidade(
        id=301, nome="Regeneração",
        tipo=TipoHabilidade.NATUREZA,
        descricao="Recupera vida lentamente ao longo do tempo.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=12,
        cura_base=10,
        custo_mana=15,
        tempo_recarga=3.0,
        efeitos=[{"tipo": "cura", "duracao": 10, "tick_frequencia": 1}]
    )
    
    ACELERAÇÃO_VEGETAL = Habilidade(
        id=302, nome="Aceleração Vegetal",
        tipo=TipoHabilidade.NATUREZA,
        descricao="Acelera o crescimento de plantas, útil para agricultura.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=10,
        custo_mana=20,
        tempo_recarga=2.0,
        efeitos=[{"tipo": "agricultura", "efeito": "crescimento"}]
    )
    
    INVOCACAO_ANIMAL = Habilidade(
        id=303, nome="Invocação Animal",
        tipo=TipoHabilidade.NATUREZA,
        descricao="Chama um animal para ajudá-lo em combate.",
        raridade=Raridade_Habilidade.RARA,
        nivel_requerido=18,
        custo_mana=35,
        tempo_recarga=5.0,
        efeitos=[{"tipo": "invocacao", "animal": "lobo"}]
    )
    
    # SOBREVIVÊNCIA
    RASTREAMENTO = Habilidade(
        id=401, nome="Rastreamento",
        tipo=TipoHabilidade.SOBREVIVENCIA,
        descricao="Detecta presença de mobs, NPCs e objetos próximos.",
        raridade=Raridade_Habilidade.COMUM,
        nivel_requerido=5,
        custo_mana=5,
        tempo_recarga=1.5,
        efeitos=[{"tipo": "deteccao", "raio": 10}]
    )
    
    COLETA_EFICIENTE = Habilidade(
        id=402, nome="Coleta Eficiente",
        tipo=TipoHabilidade.SOBREVIVENCIA,
        descricao="Coleta recursos mais rápido e com mais quantidade.",
        raridade=Raridade_Habilidade.INCOMUM,
        nivel_requerido=7,
        efeitos=[{"tipo": "coleta", "multiplicador": 1.5}]
    )
    
    CAMUFLAGEM = Habilidade(
        id=403, nome="Camuflagem",
        tipo=TipoHabilidade.SOBREVIVENCIA,
        descricao="Se mistura com o ambiente, ficando invisível temporariamente.",
        raridade=Raridade_Habilidade.RARA,
        nivel_requerido=16,
        custo_mana=25,
        tempo_recarga=4.0,
        efeitos=[{"tipo": "invisibilidade", "duracao": 5}]
    )
    
    @classmethod
    def obter_todasabilidades(cls) -> Dict[int, Habilidade]:
        """Retorna todas as habilidades disponíveis"""
        habilidades = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Habilidade):
                habilidades[attr.id] = attr
        return habilidades
    
    @classmethod
    def obter_habilidades_nivel(cls, nivel: int) -> List[Habilidade]:
        """Retorna habilidades disponíveis para um nível"""
        return [h for h in cls.obter_todasabilidades().values() 
                if h.nivel_requerido <= nivel]


class SistemaProgression:
    """Gerencia leveling e progressão do personagem"""
    
    def __init__(self):
        self.nivel: int = 1
        self.experiencia: int = 0
        self.habilidades_aprendidas: Dict[int, HabilidadeAprendida] = {}
        self.pontos_skill_disponiveis: int = 0
        
        # Stats base
        self.ataque_base: int = 5
        self.defesa_base: int = 2
        self.velocidade_base: int = 3
        self.inteligencia_base: int = 3
        self.vida_max_base: int = 100
        
        # Multiplicadores de skill
        self.multiplicador_ataque: float = 1.0
        self.multiplicador_defesa: float = 1.0
        self.multiplicador_inteligencia: float = 1.0
    
    @property
    def exp_para_proximonivel(self) -> int:
        """EXP necessária para próximo nível"""
        return self.nivel * 100
    
    @property
    def ataque_total(self) -> int:
        """Ataque total com modificadores"""
        return int(self.ataque_base * self.multiplicador_ataque)
    
    @property
    def defesa_total(self) -> int:
        """Defesa total com modificadores"""
        return int(self.defesa_base * self.multiplicador_defesa)
    
    @property
    def inteligencia_total(self) -> int:
        """Inteligência total com modificadores"""
        return int(self.inteligencia_base * self.multiplicador_inteligencia)
    
    @property
    def vida_max(self) -> int:
        """Vida máxima"""
        return self.vida_max_base + (self.nivel - 1) * 10
    
    def ganhar_experiencia(self, quantidade: int) -> bool:
        """Ganha EXP e sobe de nível se necessário"""
        self.experiencia += quantidade
        levouup = False
        
        while self.experiencia >= self.exp_para_proximonivel:
            self.experiencia -= self.exp_para_proximonivel
            self.nivel += 1
            self.pontos_skill_disponiveis += 1
            levouup = True
        
        return levouup
    
    def aprender_habilidade(self, habilidade_id: int) -> bool:
        """Aprende uma nova habilidade"""
        if habilidade_id in self.habilidades_aprendidas:
            return False  # Já aprendeu
        
        todas_habilidades = BancoDados_Habilidades.obter_todasabilidades()
        if habilidade_id not in todas_habilidades:
            return False
        
        hab_def = todas_habilidades[habilidade_id]
        
        # Verifica pré-requisitos
        if hab_def.nivel_requerido > self.nivel:
            return False
        
        if hab_def.pré_requisitos:
            for pre_req_id in hab_def.pré_requisitos:
                if pre_req_id not in self.habilidades_aprendidas:
                    return False
        
        # Aprende a habilidade
        self.habilidades_aprendidas[habilidade_id] = HabilidadeAprendida(
            habilidade_id=habilidade_id,
            nome=hab_def.nome
        )
        return True
    
    def aumentar_habilidade(self, habilidade_id: int) -> bool:
        """Aumenta o nível de uma habilidade aprendida"""
        if habilidade_id not in self.habilidades_aprendidas:
            return False
        
        habilidade = self.habilidades_aprendidas[habilidade_id]
        if habilidade.nivel < 10:
            habilidade.nivel += 1
            return True
        return False
    
    def obter_habilidades_disponiveis(self) -> List[Habilidade]:
        """Retorna habilidades que podem ser aprendidas"""
        disponiveis = []
        todas = BancoDados_Habilidades.obter_todasabilidades()
        
        for hab_def in todas.values():
            if hab_def.nivel_requerido > self.nivel:
                continue
            if hab_def.id in self.habilidades_aprendidas:
                continue
            
            # Verifica pré-requisitos
            if hab_def.pré_requisitos:
                if not all(pre_req in self.habilidades_aprendidas 
                          for pre_req in hab_def.pré_requisitos):
                    continue
            
            disponiveis.append(hab_def)
        
        return disponiveis
    
    def calcular_dano_habilidade(self, habilidade_id: int) -> int:
        """Calcula dano de uma habilidade"""
        todas = BancoDados_Habilidades.obter_todasabilidades()
        if habilidade_id not in todas:
            return 0
        
        habilidade = todas[habilidade_id]
        return habilidade.obter_dano_final(self.ataque_total, self.inteligencia_total)
    
    def debugar_stats(self) -> Dict:
        """Retorna stats atuais para debug"""
        return {
            "nivel": self.nivel,
            "experiencia": f"{self.experiencia}/{self.exp_para_proximonivel}",
            "ataque": self.ataque_total,
            "defesa": self.defesa_total,
            "inteligencia": self.inteligencia_total,
            "vida_max": self.vida_max,
            "habilidades": len(self.habilidades_aprendidas),
            "pontos_skill": self.pontos_skill_disponiveis
        }
