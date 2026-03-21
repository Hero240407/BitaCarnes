"""Sistema de Relacionamentos e Comportamento de NPCs - Stardew Valley inspired"""
from dataclasses import dataclass, field
from enum import Enum
import random
import time
from typing import Optional
from datetime import datetime


class SentimentoNPC(Enum):
    """Estados emocionais dos NPCs"""
    FELIZ = "feliz"
    NEUTRO = "neutro"
    TRISTE = "triste"
    FURIOSO = "furioso"
    APAIXONADO = "apaixonado"


@dataclass(slots=True)
class DiaRotinaAtividade:
    """Atividade do NPC em um hora específica"""
    hora_inicio: int  # 6-22
    hora_fim: int
    tipo_atividade: str  # trabalho, comer, dormir, social, descanso
    locacao: tuple[int, int]
    descricao: str


@dataclass(slots=True)
class RotinaDiaria:
    """Rotina diária gerada por IA para NPCs"""
    npc_nome: str
    atividades: list[DiaRotinaAtividade] = field(default_factory=list)
    
    def obter_atividade_atual(self, hora_decimal: float) -> Optional[DiaRotinaAtividade]:
        """Retorna atividade atual baseado na hora"""
        hora_atual = int(hora_decimal)
        for atividade in self.atividades:
            if atividade.hora_inicio <= hora_atual < atividade.hora_fim:
                return atividade
        return None


@dataclass(slots=True)
class RelacaoNPC:
    """Relacionamento entre jogador e NPC"""
    npc_id: str
    npc_nome: str
    coracao: int = 0  # -10 a 10 (máx 10 para romance)
    presenteado_hoje: bool = False
    ultima_conversa: float = 0.0  # timestamp
    conversas_semana: int = 0
    _sentimento_cache: SentimentoNPC = field(default=SentimentoNPC.NEUTRO, init=False)
    
    def adicionar_coracao(self, quantidade: int = 1) -> None:
        """Adiciona corações de relacionamento"""
        self.coracao = min(10, max(-10, self.coracao + quantidade))
    
    def remover_coracao(self, quantidade: int = 1) -> None:
        """Remove corações de relacionamento"""
        self.coracao = min(10, max(-10, self.coracao - quantidade))
    
    @property
    def sentimento(self) -> SentimentoNPC:
        """Retorna sentimento baseado em corações"""
        if self.coracao >= 8:
            return SentimentoNPC.APAIXONADO
        elif self.coracao >= 4:
            return SentimentoNPC.FELIZ
        elif self.coracao >= 0:
            return SentimentoNPC.NEUTRO
        elif self.coracao >= -6:
            return SentimentoNPC.TRISTE
        else:
            return SentimentoNPC.FURIOSO
    
    @property
    def pode_casar(self) -> bool:
        """Verifica se relação permite casamento"""
        return self.coracao >= 8
    
    def resetar_dia(self) -> None:
        """Reseta flags diárias"""
        self.presenteado_hoje = False


class GerenciadorRelacoes:
    """Gerencia todos os relacionamentos do jogador"""
    
    def __init__(self):
        self.relacoes: dict[str, RelacaoNPC] = {}
        self.casado_com: Optional[str] = None
        self.filhos: list[dict] = []
        self.contador_dias_casado: int = 0
        
    def registrar_npc(self, npc_id: str, npc_nome: str) -> RelacaoNPC:
        """Registra um novo NPC"""
        if npc_id not in self.relacoes:
            self.relacoes[npc_id] = RelacaoNPC(npc_id, npc_nome)
        return self.relacoes[npc_id]
    
    def obter_relacao(self, npc_id: str) -> Optional[RelacaoNPC]:
        """Obtém relacionamento com um NPC"""
        return self.relacoes.get(npc_id)
    
    def dar_presente(self, npc_id: str, presente_tipo: str, afinidade: int) -> tuple[bool, str]:
        """Dá presente para NPC"""
        relacao = self.relacoes.get(npc_id)
        if not relacao:
            return False, "NPC não encontrado"
        
        if relacao.presenteado_hoje:
            return False, f"{relacao.npc_nome} já recebeu presente hoje"
        
        # Aumenta corações baseado em afinidade
        relacao.adicionar_coracao(afinidade)
        relacao.presenteado_hoje = True
        
        mensagens = {
            2: f"{relacao.npc_nome} adorou o presente!",
            1: f"{relacao.npc_nome} gostou do presente.",
            0: f"{relacao.npc_nome} achou o presente ok.",
            -1: f"{relacao.npc_nome} não gostou muito...",
        }
        return True, mensagens.get(afinidade, "Presente entregue")
    
    def conversar_npc(self, npc_id: str, assunto: str) -> tuple[bool, str]:
        """Conversa com NPC"""
        relacao = self.relacao.get(npc_id)
        if not relacao:
            return False, "Não há nada para conversar"
        
        tempo_atual = time.time()
        if tempo_atual - relacao.ultima_conversa < 3600:  # Uma conversa por hora
            return False, f"{relacao.npc_nome} ainda está ocupado"
        
        relacao.ultima_conversa = tempo_atual
        relacao.conversas_semana += 1
        relacao.adicionar_coracao(1)
        
        return True, f"Você conversou com {relacao.npc_nome}"
    
    def casar(self, npc_id: str) -> bool:
        """Tenta casar com um NPC"""
        relacao = self.relacoes.get(npc_id)
        if relacao and relacao.pode_casar and not self.casado_com:
            self.casado_com = npc_id
            return True
        return False
    
    def divorciar(self) -> bool:
        """Divorcia do cônjuge"""
        if self.casado_com:
            relacao = self.relacoes.get(self.casado_com)
            if relacao:
                relacao.remover_coracao(5)
            self.casado_com = None
            return True
        return False
    
    def ter_filho(self) -> bool:
        """Tenta ter filho com cônjuge"""
        if self.casado_com and self.contador_dias_casado >= 60:
            # 50% de chance de filho por dia após 60 dias de casamento
            if random.random() < 0.05:
                nome_filho = self._gerar_nome_filho()
                self.filhos.append({"nome": nome_filho, "idade": 0})
                return True
        return False
    
    def _gerar_nome_filho(self) -> str:
        """Gera nome aleatório para filho"""
        nomes = ["Ariel", "Beatriz", "Caio", "Diana", "Enzo", "Fátima", 
                 "Gabriel", "Helena", "Igor", "Joana"]
        return random.choice(nomes)
    
    def avancar_dia(self) -> None:
        """Avança um dia para relacionamentos"""
        for relacao in self.relacoes.values():
            relacao.resetar_dia()
            # Degradação lenta se não conversar
            if relacao.conversas_semana == 0:
                relacao.remover_coracao(0.5)
            relacao.conversas_semana = 0
        
        if self.casado_com:
            self.contador_dias_casado += 1


class ComportamentoNPC:
    """Define comportamento e IA do NPC"""
    
    def __init__(self, npc_id: str, npc_perfil: dict):
        self.npc_id = npc_id
        self.npc_perfil = npc_perfil
        self.rotina: Optional[RotinaDiaria] = None
        self.energia = 100  # 0-100
        self.felicidade = 50  # 0-100
        self.objetivo_atual: Optional[str] = None
        self.contador_atividade = 0
        
    def gerar_rotina_randomica(self) -> RotinaDiaria:
        """Gera rotina randomica para o NPC"""
        atividades = []
        
        # Padrão básico: dormir, trabalho, comer, social, descanso
        rotina_base = [
            (6, 8, "acordar", "casa", "Acordando e se arrumando"),
            (8, 12, "trabalho", "local_trabalho", "Trabalhando"),
            (12, 14, "comer", "taverna", "Comendo e descansando"),
            (14, 18, "trabalho", "local_trabalho", "Continuando o trabalho"),
            (18, 20, "social", "praca", "Socializando com amigos"),
            (20, 22, "descanso", "casa", "Descansando"),
            (22, 6, "dormir", "casa", "Dormindo"),
        ]
        
        # Randomizar um pouco
        for hora_ini, hora_fim, tipo, local, desc in rotina_base:
            atividade = DiaRotinaAtividade(
                hora_inicio=hora_ini,
                hora_fim=hora_fim,
                tipo_atividade=tipo,
                locacao=(random.randint(0, 50), random.randint(0, 50)),
                descricao=desc + f" ({self.npc_perfil.get('papel', 'habitante')})"
            )
            atividades.append(atividade)
        
        self.rotina = RotinaDiaria(self.npc_perfil.get("nome", self.npc_id), atividades)
        return self.rotina
    
    def atualizar_estado(self, horas_passadas: float = 1.0) -> None:
        """Atualiza estado do NPC"""
        self.energia = max(0, self.energia - horas_passadas * random.uniform(0.5, 2.0))
        
        # Recupera energia uma pouco durante atividades de descanso
        if self.rotina:
            atividade = self.rotina.obter_atividade_atual(6)  # Default 6 da manhã
            if atividade and "descanso" in atividade.tipo_atividade.lower():
                self.energia = min(100, self.energia + 5 * horas_passadas)
    
    def obter_proximidade_reacao(self, distancia_celulas: float) -> str:
        """Retorna reação baseada em distância"""
        if distancia_celulas < 2:
            return "muito_perto"
        elif distancia_celulas < 5:
            return "perto"
        elif distancia_celulas < 10:
            return "visivel"
        return "distante"
    
    def interagir_jogador(self, tipo_interacao: str) -> str:
        """Gera resposta à interação do jogador"""
        respostas_base = {
            "conversa": "Como vai?",
            "presente": "Obrigado pelo presente!",
            "trabalho": "Ocupado no momento",
            "saudacao": "Olá!",
        }
        
        # Modifica baseado no humor
        base = respostas_base.get(tipo_interacao, "...")
        
        if self.felicidade > 70:
            base = f"😊 {base}"
        elif self.felicidade < 30:
            base = f"😔 {base}"
        
        return base
