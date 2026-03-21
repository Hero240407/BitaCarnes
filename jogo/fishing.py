"""Sistema de Pesca - Stardew Valley inspired"""
from dataclasses import dataclass
from enum import Enum
import random
import time
from typing import Optional


class TipoPeixe(Enum):
    """Tipos de peixes disponíveis"""
    COMUM = "comum"
    INCOMUM = "incomum"
    RARO = "raro"
    LENDARIO = "lendario"


@dataclass(slots=True)
class Peixe:
    """Definição de um peixe"""
    nome: str
    raridade: TipoPeixe
    locais: list[str]  # Água doce, água salgada, subterrâneo
    estacoes: list[str]
    hora_ativa_inicio: int
    hora_ativa_fim: int
    velocidade_fuga: float
    valor_ouro: int
    descricao: str
    
    def pode_pescar_agora(self, hora_decimal: float, estacao: str, local: str) -> bool:
        """Verifica se peixe pode ser pescado agora"""
        hora_int = int(hora_decimal)
        return (self.hora_ativa_inicio <= hora_int < self.hora_ativa_fim and
                estacao in self.estacoes and
                local in self.locais)


PEIXES_DISPONIVEIS = {
    # Água doce comuns
    "truta": Peixe(
        "Truta",
        TipoPeixe.COMUM,
        ["rio", "lago"],
        ["primavera", "verao", "outono", "inverno"],
        6, 19,
        1.5,
        75,
        "Peixe de água doce, relativamente fácil de pescar"
    ),
    "carpa": Peixe(
        "Carpa",
        TipoPeixe.INCOMUM,
        ["lago"],
        ["verao", "outono"],
        9, 17,
        2.0,
        150,
        "Peixe resistente que gosta de fundas"
    ),
    # Água doce raros
    "lúcio_dourado": Peixe(
        "Lúcio Dourado",
        TipoPeixe.RARO,
        ["rio"],
        ["inverno"],
        12, 16,
        3.5,
        500,
        "Lendário peixe de ouro brilhante"
    ),
    # Água salgada
    "atum": Peixe(
        "Atum",
        TipoPeixe.COMUM,
        ["oceano"],
        ["verao", "outono"],
        5, 21,
        2.0,
        100,
        "Peixe oceânico rápido e ativo"
    ),
    "salmao_bravio": Peixe(
        "Salmão Bravio",
        TipoPeixe.RARO,
        ["cascata_sagrada"],
        ["outono"],
        13, 17,
        4.0,
        750,
        "Raro salmão das cachoeiras sagradas"
    ),
    # Subterrâneos
    "peixe_das_sombras": Peixe(
        "Peixe das Sombras",
        TipoPeixe.RARO,
        ["mina_profunda"],
        ["inverno"],
        20, 4,  # Noturno
        2.5,
        400,
        "Misterioso peixe das profundezas"
    ),
    # Lendários
    "lendario_das_aguas": Peixe(
        "Lendário das Águas",
        TipoPeixe.LENDARIO,
        ["rio", "lago", "cascata_sagrada"],
        ["primavera"],
        16, 20,
        5.0,
        2000,
        "A maior captura do reino, praticamente mítica"
    ),
}


@dataclass(slots=True)
class EstadoPesca:
    """Estado atual do minigame de pesca"""
    peixe_atual: Optional[Peixe] = None
    posicao_peixe: float = 0.5  # 0.0 a 1.0 (barra de progresso)
    posicao_anzol: float = 0.5
    velocidade_peixe: float = 0.0
    tempo_decorrido: float = 0.0
    durabilidade_linha: float = 100.0
    estresse_peixe: float = 0.0
    has_puxado_linha: bool = False
    tentativas: int = 0
    
    def atualizar(self, delta_tempo: float, puxar: bool = False) -> None:
        """Atualiza estado da pesca"""
        self.tempo_decorrido += delta_tempo
        
        if not self.peixe_atual:
            return
        
        # Movimento aleatório do peixe
        self.velocidade_peixe += random.uniform(-1, 1) * self.peixe_atual.velocidade_fuga * delta_tempo
        self.velocidade_peixe = max(-3, min(3, self.velocidade_peixe))
        self.posicao_peixe += self.velocidade_peixe * delta_tempo
        self.posicao_peixe = max(0, min(1, self.posicao_peixe))
        
        # Verifica se jogador está puxando
        if puxar:
            # Anzol sobe
            self.posicao_anzol = max(0, self.posicao_anzol - 0.3)
            self.durabilidade_linha -= delta_tempo * 10
            self.estresse_peixe += delta_tempo * 5
        else:
            # Anzol desce (gravidade)
            self.posicao_anzol = min(1, self.posicao_anzol + 0.15)
        
        self.durabilidade_linha = max(0, min(100, self.durabilidade_linha))
    
    def em_zona_sucesso(self, tolerancia: float = 0.15) -> bool:
        """Verifica se peixe está na zona do anzol"""
        return abs(self.posicao_peixe - self.posicao_anzol) < tolerancia
    
    def pode_pescar(self) -> bool:
        """Verifica se ainda pode continuar pescando"""
        return self.durabilidade_linha > 0


class MiniGamePesca:
    """Minigame de pesca estilo Stardew Valley"""
    
    def __init__(self):
        self.estado = EstadoPesca()
        self.em_jogo = False
        self.ganho_ouro = 0
        self.ganho_exp = 0
        self.peixe_capturado_nome = ""
        
    def iniciar_pesca(self, local: str, hora_decimal: float, estacao: str) -> bool:
        """Inicia o minigame de pesca"""
        # Seleciona peixe disponível aleatoriamente
        peixes_possiveis = [
            peixe for peixe in PEIXES_DISPONIVEIS.values()
            if peixe.pode_pescar_agora(hora_decimal, estacao, local)
        ]
        
        if not peixes_possiveis:
            return False
        
        # Chance de não pegar nada
        if random.random() < 0.3:
            return False
        
        # Pesos baseados em raridade
        pesos = [
            0.6 if p.raridade == TipoPeixe.COMUM else
            0.25 if p.raridade == TipoPeixe.INCOMUM else
            0.12 if p.raridade == TipoPeixe.RARO else
            0.03
            for p in peixes_possiveis
        ]
        
        self.estado.peixe_atual = random.choices(peixes_possiveis, weights=pesos)[0]
        self.estado.posicao_peixe = random.random()
        self.estado.velocidade_peixe = random.uniform(-1, 1)
        self.em_jogo = True
        self.estado.tentativas = 0
        
        return True
    
    def tentar_pescagem(self, duracao_minutos: int = 5) -> tuple[bool, str]:
        """Tenta pescar durante um tempo"""
        if not self.estado.peixe_atual:
            return False, "Nada mordeu a isca..."
        
        # Simulação do minigame
        sucesso = False
        mensagens = []
        
        for _ in range(int(duracao_minutos * 10)):
            # 10% de chance de sucesso se estiver na zona
            if self.estado.em_zona_sucesso(0.2):
                if random.random() < 0.15:
                    sucesso = True
                    break
            
            # Atualizar estado
            puxar = self.estado.em_zona_sucesso() if random.random() < 0.5 else False
            self.estado.atualizar(0.1, puxar)
            
            if self.estado.durabilidade_linha <= 0:
                mensagens.append("Linha quebrou!")
                break
            
            if self.estado.estresse_peixe > 100:
                mensagens.append("Peixe escapou!")
                break
        
        if sucesso:
            self.peixe_capturado_nome = self.estado.peixe_atual.nome
            self.ganho_ouro = self.estado.peixe_atual.valor_ouro
            self.ganho_exp = 5 + (10 if self.estado.peixe_atual.raridade == TipoPeixe.RARO else 0)
            mensagem = f"🎣 Você pescou um {self.peixe_capturado_nome}! (+{self.ganho_ouro} ouro)"
        else:
            mensagem = "Você não conseguiu pegar nada" + ("." if not mensagens else f": {mensagens[-1]}")
        
        self.em_jogo = False
        return sucesso, mensagem
    
    def obter_info_peixe_atual(self) -> Optional[dict]:
        """Retorna informações sobre o peixe atual"""
        if not self.estado.peixe_atual:
            return None
        
        peixe = self.estado.peixe_atual
        return {
            "nome": peixe.nome,
            "raridade": peixe.raridade.value,
            "valor": peixe.valor_ouro,
            "descricao": peixe.descricao,
            "durabilidade_linha": int(self.estado.durabilidade_linha),
            "posicao_peixe": self.estado.posicao_peixe,
            "posicao_anzol": self.estado.posicao_anzol,
        }


class HistoricoPesca:
    """Mantém histórico de peixes capturados"""
    
    def __init__(self):
        self.peixes_capturados: dict[str, int] = {}
        self.total_ouro_ganho = 0
        self.melhor_captura = None
        self.melhor_captura_valor = 0
        
    def registrar_captura(self, peixe_nome: str, valor_ouro: int) -> None:
        """Registra um peixe capturado"""
        self.peixes_capturados[peixe_nome] = self.peixes_capturados.get(peixe_nome, 0) + 1
        self.total_ouro_ganho += valor_ouro
        
        if valor_ouro > self.melhor_captura_valor:
            self.melhor_captura = peixe_nome
            self.melhor_captura_valor = valor_ouro
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas de pesca"""
        return {
            "total_peixes": sum(self.peixes_capturados.values()),
            "tipos_capturados": len(self.peixes_capturados),
            "melhor_captura": self.melhor_captura,
            "valor_melhor": self.melhor_captura_valor,
            "total_ganho": self.total_ouro_ganho,
            "peixes": self.peixes_capturados,
        }
    
    def obter_peixes_nao_capturados(self) -> list[str]:
        """Retorna peixes ainda não capturados"""
        todos_peixes = set(PEIXES_DISPONIVEIS.keys())
        capturados = set(self.peixes_capturados.keys())
        return list(todos_peixes - capturados)
