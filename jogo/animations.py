"""Sistema de Animações Aprimorado - Animations para personagens, efeitos e UI"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Callable, Optional
import time


class TipoAnimacao(Enum):
    """Tipos de animações disponíveis"""
    MOVIMENTO = "movimento"
    ATAQUE = "ataque"
    EFEITO_MAGICO = "efeito_magico"
    CURA = "cura"
    MORTE = "morte"
    DANO = "dano"
    PARADO = "parado"
    CORRIDA = "corrida"
    SALTO = "salto"


class Direcao(Enum):
    """Direções para animações 8-way"""
    NORTE = 0
    NOROESTE = 1
    OESTE = 2
    SUDOESTE = 3
    SUL = 4
    SUDESTE = 5
    LESTE = 6
    NORDESTE = 7


@dataclass(slots=True)
class Frame:
    """Representa um frame individual de uma animação"""
    id_sprite: int
    duracao: float  # segundos
    offset_x: int = 0
    offset_y: int = 0
    escala: float = 1.0
    rotacao: float = 0.0  # em graus
    opacidade: float = 1.0
    modificadores: Dict = field(default_factory=dict)  # efeitos especiais


@dataclass(slots=True)
class Sequencia_Animacao:
    """Define uma sequência de animação completa"""
    nome: str
    tipo: TipoAnimacao
    frames: List[Frame]
    loop: bool = False
    duracao_total: float = 0.0
    evento_fim_callback: Optional[Callable] = None
    som_efeito: Optional[str] = None
    particulas: Optional[str] = None
    
    def __post_init__(self):
        self.duracao_total = sum(f.duracao for f in self.frames)
    
    @property
    def num_frames(self) -> int:
        return len(self.frames)


@dataclass(slots=True)
class Instancia_Animacao:
    """Representa uma instância de animação em execução"""
    id: int
    sequencia: Sequencia_Animacao
    tempo_inicio: float
    tempo_atual: float = 0.0
    completada: bool = False
    frame_atual: int = 0
    num_repeticoes: int = 0
    
    def atualizar(self, delta_tempo: float) -> Frame:
        """Atualiza a animação e retorna o frame atual"""
        self.tempo_atual += delta_tempo
        
        if self.tempo_atual >= self.sequencia.duracao_total:
            if self.sequencia.loop:
                self.tempo_atual = self.tempo_atual % self.sequencia.duracao_total
                self.num_repeticoes += 1
            else:
                self.completada = True
                return self.sequencia.frames[-1]
        
        # Encontra o frame atual baseado no tempo
        tempo_acumulado = 0.0
        for i, frame in enumerate(self.sequencia.frames):
            tempo_acumulado += frame.duracao
            if self.tempo_atual <= tempo_acumulado:
                self.frame_atual = i
                return frame
        
        return self.sequencia.frames[-1]
    
    def esta_completa(self) -> bool:
        return self.completada


class DefinidorAnimacoes:
    """Define todas as animações do jogo"""
    
    # MOVIMENTO
    CAMINHADA_NORTE: Sequencia_Animacao = Sequencia_Animacao(
        "caminhada_norte",
        TipoAnimacao.MOVIMENTO,
        [
            Frame(100, 0.1),
            Frame(101, 0.1),
            Frame(102, 0.1),
            Frame(101, 0.1),
        ],
        loop=True
    )
    
    CAMINHADA_LESTE: Sequencia_Animacao = Sequencia_Animacao(
        "caminhada_leste",
        TipoAnimacao.MOVIMENTO,
        [
            Frame(110, 0.1),
            Frame(111, 0.1),
            Frame(112, 0.1),
            Frame(111, 0.1),
        ],
        loop=True
    )
    
    CAMINHADA_SUL: Sequencia_Animacao = Sequencia_Animacao(
        "caminhada_sul",
        TipoAnimacao.MOVIMENTO,
        [
            Frame(120, 0.1),
            Frame(121, 0.1),
            Frame(122, 0.1),
            Frame(121, 0.1),
        ],
        loop=True
    )
    
    CAMINHADA_OESTE: Sequencia_Animacao = Sequencia_Animacao(
        "caminhada_oeste",
        TipoAnimacao.MOVIMENTO,
        [
            Frame(130, 0.1),
            Frame(131, 0.1),
            Frame(132, 0.1),
            Frame(131, 0.1),
        ],
        loop=True
    )
    
    CORRIDA_NORTE: Sequencia_Animacao = Sequencia_Animacao(
        "corrida_norte",
        TipoAnimacao.CORRIDA,
        [
            Frame(200, 0.06),
            Frame(201, 0.06),
            Frame(202, 0.06),
            Frame(203, 0.06),
        ],
        loop=True
    )
    
    # ATAQUE
    ATAQUE_ESPADA : Sequencia_Animacao = Sequencia_Animacao(
        "ataque_espada",
        TipoAnimacao.ATAQUE,
        [
            Frame(300, 0.05),
            Frame(301, 0.08),
            Frame(302, 0.08),
            Frame(303, 0.08),
            Frame(304, 0.05),
        ],
        loop=False,
        som_efeito="sword_slash"
    )
    
    ATAQUE_MAGICO: Sequencia_Animacao = Sequencia_Animacao(
        "ataque_magico",
        TipoAnimacao.EFEITO_MAGICO,
        [
            Frame(400, 0.06),
            Frame(401, 0.06),
            Frame(402, 0.06),
            Frame(403, 0.08),
            Frame(404, 0.08),
            Frame(405, 0.06),
        ],
        loop=False,
        som_efeito="magic_cast",
        particulas="mana_sparkle"
    )
    
    # DANO E EFEITOS
    RECEBER_DANO: Sequencia_Animacao = Sequencia_Animacao(
        "receber_dano",
        TipoAnimacao.DANO,
        [
            Frame(500, 0.03, 0, -2, modificadores={"cor_flash": (255, 0, 0)}),
            Frame(501, 0.03, 0, 0, modificadores={"cor_flash": (255, 0, 0)}),
            Frame(500, 0.03, 0, -2, modificadores={"cor_flash": (255, 0, 0)}),
            Frame(501, 0.06, 0, 0),
        ],
        loop=False
    )
    
    CURA: Sequencia_Animacao = Sequencia_Animacao(
        "cura",
        TipoAnimacao.CURA,
        [
            Frame(600, 0.1, modificadores={"brilho": 1.2}),
            Frame(601, 0.1, modificadores={"brilho": 1.3}),
            Frame(602, 0.1, modificadores={"brilho": 1.2}),
            Frame(601, 0.1, modificadores={"brilho": 1.1}),
        ],
        loop=False,
        som_efeito="heal",
        particulas="healing_light"
    )
    
    # MORTE
    MORTE: Sequencia_Animacao = Sequencia_Animacao(
        "morte",
        TipoAnimacao.MORTE,
        [
            Frame(700, 0.1),
            Frame(701, 0.1),
            Frame(702, 0.2, opacidade=0.5),
            Frame(703, 0.3, opacidade=0.0),
        ],
        loop=False,
        som_efeito="death"
    )
    
    @staticmethod
    def obter_animacao_movimento(direcao: Direcao) -> Sequencia_Animacao:
        """Retorna animação de movimento para direção"""
        mapa_direcoes = {
            Direcao.NORTE: DefinidorAnimacoes.CAMINHADA_NORTE,
            Direcao.LESTE: DefinidorAnimacoes.CAMINHADA_LESTE,
            Direcao.SUL: DefinidorAnimacoes.CAMINHADA_SUL,
            Direcao.OESTE: DefinidorAnimacoes.CAMINHADA_OESTE,
        }
        return mapa_direcoes.get(direcao, DefinidorAnimacoes.CAMINHADA_NORTE)
    
    @staticmethod
    def obter_todasanimacoes() -> Dict[str, Sequencia_Animacao]:
        """Retorna todas as animações disponíveis"""
        anim = {}
        for attr_name in dir(DefinidorAnimacoes):
            if attr_name.startswith("_"):
                continue
            attr = getattr(DefinidorAnimacoes, attr_name)
            if isinstance(attr, Sequencia_Animacao):
                anim[attr.nome] = attr
        return anim


class GerenciadorAnimações:
    """Gerencia animações de entidades no mundo"""
    
    def __init__(self):
        self.animacoes_ativas: Dict[int, Instancia_Animacao] = {}
        self.contador_id = 0
        self.tempo_total = 0.0
    
    def iniciar_animacao(self, sequencia: Sequencia_Animacao) -> int:
        """Inicia uma nova animação e retorna seu ID"""
        instancia = Instancia_Animacao(
            id=self.contador_id,
            sequencia=sequencia,
            tempo_inicio=self.tempo_total
        )
        self.animacoes_ativas[self.contador_id] = instancia
        self.contador_id += 1
        return instancia.id
    
    def parar_animacao(self, anim_id: int):
        """Para uma animação específica"""
        if anim_id in self.animacoes_ativas:
            del self.animacoes_ativas[anim_id]
    
    def parar_todas_animacoes(self):
        """Para todas as animações"""
        self.animacoes_ativas.clear()
    
    def atualizar(self, delta_tempo: float):
        """Atualiza todas as animações ativas"""
        self.tempo_total += delta_tempo
        
        ids_remover = []
        for anim_id, instancia in self.animacoes_ativas.items():
            frame = instancia.atualizar(delta_tempo)
            
            if instancia.esta_completa():
                # Executa callback se definido
                if instancia.sequencia.evento_fim_callback:
                    instancia.sequencia.evento_fim_callback(instancia)
                
                # Remove animação se não é loop
                if not instancia.sequencia.loop:
                    ids_remover.append(anim_id)
        
        for anim_id in ids_remover:
            del self.animacoes_ativas[anim_id]
    
    def obter_frame_atual(self, anim_id: int) -> Optional[Frame]:
        """Retorna o frame atual de uma animação"""
        if anim_id in self.animacoes_ativas:
            instancia = self.animacoes_ativas[anim_id]
            return instancia.sequencia.frames[instancia.frame_atual]
        return None


class AnimadorEntidade:
    """Anima uma entidade específica (jogador, NPC, mob)"""
    
    def __init__(self, entidade_id: int):
        self.entidade_id = entidade_id
        self.animacao_corrente: Optional[Instancia_Animacao] = None
        self.posicao_x: float = 0.0
        self.posicao_y: float = 0.0
        self.direcao: Direcao = Direcao.SUL
        self.gerenciador = GerenciadorAnimações()
    
    def animar(self, tipo_anim: TipoAnimacao, direcao: Optional[Direcao] = None):
        """Inicia uma animação específica"""
        if direcao:
            self.direcao = direcao
        
        # Se é movimento, usa a animação correspondente à direção
        if tipo_anim == TipoAnimacao.MOVIMENTO:
            seq = DefinidorAnimacoes.obter_animacao_movimento(self.direcao)
        else:
            # Mapeamento simples de tipo para animação
            anim_map = {
                TipoAnimacao.ATAQUE: DefinidorAnimacoes.ATAQUE_ESPADA,
                TipoAnimacao.EFEITO_MAGICO: DefinidorAnimacoes.ATAQUE_MAGICO,
                TipoAnimacao.DANO: DefinidorAnimacoes.RECEBER_DANO,
                TipoAnimacao.CURA: DefinidorAnimacoes.CURA,
                TipoAnimacao.MORTE: DefinidorAnimacoes.MORTE,
            }
            seq = anim_map.get(tipo_anim, DefinidorAnimacoes.CAMINHADA_NORTE)
        
        anim_id = self.gerenciador.iniciar_animacao(seq)
        return anim_id
    
    def atualizar(self, delta_tempo: float):
        """Atualiza as animações da entidade"""
        self.gerenciador.atualizar(delta_tempo)
    
    def obter_frame_renderizacao(self) -> Optional[Frame]:
        """Retorna o frame que deve ser renderizado agora"""
        if self.gerenciador.animacoes_ativas:
            primeira_anim = next(iter(self.gerenciador.animacoes_ativas.values()))
            return self.gerenciador.obter_frame_atual(primeira_anim.id)
        return None
