"""Sistema de Quests e Objetivos - Stardew Valley inspired"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Callable
import random
import time


class TipoQuest(Enum):
    """Tipos de quests disponíveis"""
    COLETA = "coleta"  # Coletar X itens
    ENTREGA = "entrega"  # Entregar itens a NPCs
    DERROTA = "derrota"  # Derrotar inimigos
    DESCOBERTA = "descoberta"  # Descobrir locais
    MELHORIA = "melhoria"  # Melhorar algo
    CRIACAO = "criacao"  # Criar itens
    RELACIONAMENTO = "relacionamento"  # Aumentar relacionamento
    EVENTO = "evento"  # Participar de evento
    MINIGAME = "minigame"  # Completar minigame


class StatusQuest(Enum):
    """Status de uma quest"""
    DISPONIVEL = "disponivel"
    ATIVA = "ativa"
    COMPLETA = "completa"
    FALHADA = "falhada"
    ABANDONADA = "abandonada"


@dataclass(slots=True)
class Recompensa:
    """Recompensa de uma quest"""
    ouro: int = 0
    exp: int = 0
    itens: dict = field(default_factory=lambda: {})
    desbloqueios: list[str] = field(default_factory=list)
    aumentos_relacao: dict[str, int] = field(default_factory=lambda: {})


@dataclass(slots=True)
class Quest:
    """Uma quest/missão"""
    id: str
    nome: str
    descricao: str
    tipo: TipoQuest
    status: StatusQuest = StatusQuest.DISPONIVEL
    npc_giver: Optional[str] = None
    npc_target: Optional[str] = None
    locacao_target: Optional[tuple[int, int]] = None
    
    # Requisitos
    requisitos_nivel: int = 1
    requisitos_skills: dict[str, int] = field(default_factory=lambda: {})
    requisitos_itens: dict[str, int] = field(default_factory=lambda: {})
    
    # Progresso
    objetivo_quantidade: int = 1
    quantidade_completa: int = 0
    limite_tempo_horas: int = 0
    tempo_inician: float = 0.0
    
    # Recompensas
    recompensa: Recompensa = field(default_factory=Recompensa)
    
    # Complexidade
    dificuldade: int = 1  # 1-5
    diaria: bool = False
    semanal: bool = False
    repetiavel: bool = False
    
    def marcar_ativa(self) -> None:
        """Marca quest como ativa"""
        self.status = StatusQuest.ATIVA
        self.tempo_inicio = time.time()
    
    def avancar_progresso(self, quantidade: int = 1) -> bool:
        """Avança progresso da quest"""
        if self.status != StatusQuest.ATIVA:
            return False
        
        self.quantidade_completa += quantidade
        
        if self.quantidade_completa >= self.objetivo_quantidade:
            self.status = StatusQuest.COMPLETA
            return True
        
        return False
    
    def completar(self) -> bool:
        """Marca quest como completa"""
        if self.status == StatusQuest.ATIVA:
            self.status = StatusQuest.COMPLETA
            return True
        return False
    
    def falhar(self) -> None:
        """Marca quest como falhada"""
        self.status = StatusQuest.FALHADA
    
    def abandonar(self) -> None:
        """Marca quest como abandonada"""
        self.status = StatusQuest.ABANDONADA
    
    def passou_tempo_limite(self) -> bool:
        """Verifica se passou do tempo limite"""
        if self.limite_tempo_horas <= 0:
            return False
        tempo_decorrido = (time.time() - self.tempo_inicio) / 3600
        return tempo_decorrido >= self.limite_tempo_horas
    
    @property
    def em_andamento(self) -> bool:
        """Verifica se quest está em andamento"""
        return self.status == StatusQuest.ATIVA
    
    @property
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "tipo": self.tipo.value,
            "status": self.status.value,
            "progresso": f"{self.quantidade_completa}/{self.objetivo_quantidade}",
            "dificuldade": self.dificuldade,
        }


class QuestManager:
    """Gerencia todas as quests do jogador"""
    
    def __init__(self):
        self.quests: dict[str, Quest] = {}
        self.quests_ativas: list[str] = []
        self.quests_completas: list[str] = []
        self.quests_falhadas: list[str] = []
        self.historico_quests: list[dict] = []
        self._inicializar_quests_padrao()
    
    def _inicializar_quests_padrao(self) -> None:
        """Inicializa algumas quests padrão"""
        quests_base = [
            self._criar_quest_colheita(),
            self._criar_quest_encontro_npc(),
            self._criar_quest_melhoria_ferramenta(),
            self._criar_quest_festival(),
        ]
        for quest in quests_base:
            self.quests[quest.id] = quest
    
    def _criar_quest_colheita(self) -> Quest:
        """Cria quest de colheita"""
        return Quest(
            id="quest_colheita_inicial",
            nome="Primeira Colheita",
            descricao="Colha 5 itens da primeira plantação",
            tipo=TipoQuest.COLETA,
            objetivo_quantidade=5,
            dificuldade=1,
            recompensa=Recompensa(ouro=50, exp=10, itens={"semente_bônus": 5}),
            npc_giver="Raphael"
        )
    
    def _criar_quest_encontro_npc(self) -> Quest:
        """Cria quest de encontro com NPCs"""
        return Quest(
            id="quest_encontro_npc",
            nome="Conheça os Habitantes",
            descricao="Converse com 3 NPCs diferentes",
            tipo=TipoQuest.RELACIONAMENTO,
            objetivo_quantidade=3,
            dificuldade=1,
            recompensa=Recompensa(ouro=75, exp=15),
        )
    
    def _criar_quest_melhoria_ferramenta(self) -> Quest:
        """Cria quest de melhoria de ferramenta"""
        return Quest(
            id="quest_ferramenta_melhorada",
            nome="Ferramentas Melhores",
            descricao="Melhore uma ferramenta no ferreiro",
            tipo=TipoQuest.MELHORIA,
            objetivo_quantidade=1,
            dificuldade=2,
            requisitos_itens={"ouro": 100},
            recompensa=Recompensa(ouro=100, exp=20),
        )
    
    def _criar_quest_festival(self) -> Quest:
        """Cria quest de festival"""
        return Quest(
            id="quest_festival",
            nome="Celebrar Juntos",
            descricao="Participe de um festival",
            tipo=TipoQuest.EVENTO,
            objetivo_quantidade=1,
            dificuldade=1,
            recompensa=Recompensa(ouro=80, exp=15, itens={"prêmio_festival": 1}),
        )
    
    def registrar_quest(self, quest: Quest) -> bool:
        """Registra uma nova quest"""
        if quest.id not in self.quests:
            self.quests[quest.id] = quest
            return True
        return False
    
    def obter_quest(self, quest_id: str) -> Optional[Quest]:
        """Obtém uma quest"""
        return self.quests.get(quest_id)
    
    def ativar_quest(self, quest_id: str) -> bool:
        """Ativa uma quest"""
        quest = self.quests.get(quest_id)
        if quest and quest.status == StatusQuest.DISPONIVEL:
            quest.marcar_ativa()
            self.quests_ativas.append(quest_id)
            return True
        return False
    
    def completar_quest(self, quest_id: str) -> tuple[bool, Optional[Recompensa]]:
        """Completa uma quest"""
        quest = self.quests.get(quest_id)
        if quest and quest.completar():
            if quest_id in self.quests_ativas:
                self.quests_ativas.remove(quest_id)
            self.quests_completas.append(quest_id)
            
            # Registrar no histórico
            self.historico_quests.append({
                "nome": quest.nome,
                "data": time.time(),
                "recompensa": quest.recompensa.ouro
            })
            
            return True, quest.recompensa
        return False, None
    
    def falhar_quest(self, quest_id: str) -> bool:
        """Marca quest como falhada"""
        quest = self.quests.get(quest_id)
        if quest:
            quest.falhar()
            if quest_id in self.quests_ativas:
                self.quests_ativas.remove(quest_id)
            self.quests_falhadas.append(quest_id)
            return True
        return False
    
    def gerar_quest_randomica(self) -> Quest:
        """Gera uma quest aleatória"""
        tipos_quest = [TipoQuest.COLETA, TipoQuest.ENTREGA, TipoQuest.MELHORIA]
        tipo = random.choice(tipos_quest)
        
        quest = Quest(
            id=f"quest_random_{int(time.time())}",
            nome=self._gerar_nome_quest(tipo),
            descricao=self._gerar_descricao_quest(tipo),
            tipo=tipo,
            objetivo_quantidade=random.randint(1, 5),
            dificuldade=random.randint(1, 3),
            recompensa=Recompensa(
                ouro=random.randint(50, 500),
                exp=random.randint(10, 100)
            )
        )
        return quest
    
    def _gerar_nome_quest(self, tipo: TipoQuest) -> str:
        """Gera nome aleatório para quest"""
        nomes = {
            TipoQuest.COLETA: [
                "Coleta de Recursos", "Busca de Itens", "Encontre Tesouros",
                "Recolha do Dia", "Mineração Necessária"
            ],
            TipoQuest.ENTREGA: [
                "Entregar Pacote", "Missão de Entrega", "Levar Presente",
                "Correspondência Importante", "Comida para Amigos"
            ],
            TipoQuest.MELHORIA: [
                "Melhoria da Fazenda", "Ferramentas Melhores", "Upgrade Necessário",
                "Expansão da Casa", "Novos Equipamentos"
            ],
        }
        return random.choice(nomes.get(tipo, ["Quest Aleatória"]))
    
    def _gerar_descricao_quest(self, tipo: TipoQuest) -> str:
        """Gera descrição aleatória para quest"""
        descricoes = {
            TipoQuest.COLETA: "Colete os itens necessários para completar essa tarefa",
            TipoQuest.ENTREGA: "Entregue os itens para a pessoa correta",
            TipoQuest.MELHORIA: "Melhore seus equipamentos e habilidades",
        }
        return descricoes.get(tipo, "Complete essa missão")
    
    def obter_quests_ativas(self) -> list[Quest]:
        """Retorna todas as quests ativas"""
        return [self.quests[qid] for qid in self.quests_ativas if qid in self.quests]
    
    def obter_quests_disponiveis(self) -> list[Quest]:
        """Retorna quests não iniciadas"""
        return [q for q in self.quests.values() if q.status == StatusQuest.DISPONIVEL]
    
    def obter_quests_completas(self) -> list[Quest]:
        """Retorna quests completas"""
        return [self.quests[qid] for qid in self.quests_completas if qid in self.quests]
    
    def avancar_dia(self) -> None:
        """Verifica quests expirando por tempo"""
        for quest_id in self.quests_ativas[:]:
            quest = self.quests[quest_id]
            if quest.passou_tempo_limite():
                self.falhar_quest(quest_id)


class ObjetivoGeral:
    """Objetivo geral/missão principal do jogo"""
    
    def __init__(self):
        self.objetivo_principal = "Construir um reino próspero e unir seus habitantes"
        self.sub_objetivos = [
            "Expandir a fazenda e aumentar produções",
            "Desenvolver relacionamentos com NPCs",
            "Desbloquear áreas secretas",
            "Participar de todos os festivais",
            "Encontrar e entender os segredos de Raphael",
        ]
        self.progresso_sub: dict[str, float] = {obj: 0 for obj in self.sub_objetivos}
    
    def atualizar_progresso(self, sub_objetivo: str, valor: float) -> None:
        """Atualiza progresso de sub-objetivo"""
        if sub_objetivo in self.progresso_sub:
            self.progresso_sub[sub_objetivo] = min(100, max(0, valor))
    
    def obter_percentual_completo(self) -> int:
        """Retorna percentual total de completo"""
        if not self.progresso_sub:
            return 0
        return int(sum(self.progresso_sub.values()) / len(self.progresso_sub))
