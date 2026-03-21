"""Sistema de Entrada e Navegação de Masmorras"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random


class EstadoDungeon(Enum):
    """Estados possíveis da masmorra durante exploração"""
    ENTRADA = "entrada"
    EXPLORANDO = "explorando"
    COMBATE = "combate"
    TESOURO = "tesouro"
    VENCEU = "venceu"
    DERROTA = "derrota"


@dataclass(slots=True)
class SessaoDungeon:
    """Representa a sessão ativa do jogador dentro de uma masmorra"""
    dungeon_id: int
    dungeon_obj: object  # Masmorra instance
    sala_id: int = 0
    estado: EstadoDungeon = EstadoDungeon.ENTRADA
    tempo_exploracao_ms: float = 0.0
    inimigos_derrotados: int = 0
    ouro_obtido: int = 0
    itens_obtidos: list = None
    
    def __post_init__(self):
        if self.itens_obtidos is None:
            self.itens_obtidos = []


class GerenciadorDungeonSessao:
    """Gerencia a sessão de exploração de dungeons do jogador"""
    
    def __init__(self):
        self.sessao_ativa: Optional[SessaoDungeon] = None
        self.dungeons_explorados = {}  # ID -> dungeon data
        
    def criar_sessao(self, dungeon_obj, dungeon_id: int) -> SessaoDungeon:
        """Cria uma nova sessão de dungeon"""
        self.sessao_ativa = SessaoDungeon(
            dungeon_id=dungeon_id,
            dungeon_obj=dungeon_obj,
        )
        return self.sessao_ativa
    
    def entrar_dungeon(self, dungeon_obj, dungeon_id: int) -> bool:
        """Entra em uma masmorra"""
        if not dungeon_obj:
            return False
        self.criar_sessao(dungeon_obj, dungeon_id)
        self.sessao_ativa.estado = EstadoDungeon.ENTRADA
        return True
    
    def sair_dungeon(self) -> tuple[bool, dict]:
        """Sai da masmorra e retorna recompensas"""
        if not self.sessao_ativa:
            return False, {}
        
        recompensas = {
            'ouro': self.sessao_ativa.ouro_obtido,
            'inimigos_derrotados': self.sessao_ativa.inimigos_derrotados,
            'itens': self.sessao_ativa.itens_obtidos.copy(),
        }
        
        # Registrar exploração
        self.dungeons_explorados[self.sessao_ativa.dungeon_id] = {
            'completada': self.sessao_ativa.estado == EstadoDungeon.VENCEU,
            'recompensas': recompensas,
        }
        
        self.sessao_ativa = None
        return True, recompensas
    
    def avancar_sala(self, sala_id: int) -> bool:
        """Avança para a próxima sala"""
        if not self.sessao_ativa or not self.sessao_ativa.dungeon_obj:
            return False
        
        dungeon = self.sessao_ativa.dungeon_obj
        sucesso = dungeon.avancar_para_sala(sala_id)
        
        if sucesso:
            self.sessao_ativa.sala_id = sala_id
            self.sessao_ativa.estado = EstadoDungeon.EXPLORANDO
            
            # Verificar tipo de sala
            sala = dungeon.sala_atual
            if sala.inimigos:
                self.sessao_ativa.estado = EstadoDungeon.COMBATE
            elif "tesouro" in sala.tipo.value:
                self.sessao_ativa.estado = EstadoDungeon.TESOURO
        
        return sucesso
    
    def obter_descricao_sala(self) -> str:
        """Retorna descrição da sala atual"""
        if not self.sessao_ativa:
            return "Você não está em uma masmorra."
        
        sala = self.sessao_ativa.dungeon_obj.sala_atual
        desc = f"Você está em: {sala.nome}\n"
        desc += f"Tipo: {sala.tipo.value}\n"
        
        if sala.inimigos:
            desc += f"\n⚔️ {len(sala.inimigos)} inimigo(s) aqui:\n"
            for inimigo in sala.inimigos:
                if inimigo.esta_vivo:
                    desc += f"  - {inimigo.tipo.title()} (HP: {inimigo.vida_atual}/{inimigo.vida_max})\n"
        
        if sala.bauzinhos:
            desc += f"\n💰 {len(sala.bauzinhos)} baú(is) de tesouro\n"
        
        # Saídas disponíveis
        if sala.conectada_a:
            desc += f"\nSaídas para salas: {', '.join(map(str, sala.conectada_a[:3]))}"
        
        return desc
    
    def derrotar_inimigo(self, inimigo_idx: int) -> dict:
        """Marca um inimigo como derrotado e coleta recompensas"""
        if not self.sessao_ativa:
            return {}
        
        sala = self.sessao_ativa.dungeon_obj.sala_atual
        if not (0 <= inimigo_idx < len(sala.inimigos)):
            return {}
        
        inimigo = sala.inimigos[inimigo_idx]
        if not inimigo.esta_vivo:
            return {}
        
        inimigo.vida_atual = 0
        recompensa = {
            'ouro': inimigo.ouro_drop,
            'nome_inimigo': inimigo.tipo,
        }
        
        self.sessao_ativa.inimigos_derrotados += 1
        self.sessao_ativa.ouro_obtido += inimigo.ouro_drop
        
        return recompensa
    
    def abrir_tesouro(self, bauzin_idx: int) -> dict:
        """Abre um baú de tesouro"""
        if not self.sessao_ativa:
            return {}
        
        sala = self.sessao_ativa.dungeon_obj.sala_atual
        if not (0 <= bauzin_idx < len(sala.bauzinhos)):
            return {}
        
        bauzin = sala.bauzinhos[bauzin_idx]
        conteudo = bauzin.abrir()
        
        if conteudo:
            self.sessao_ativa.ouro_obtido += conteudo.get('ouro', 0)
            self.sessao_ativa.itens_obtidos.extend(conteudo.get('itens', []))
        
        return conteudo


class GeneradorEntradaDungeon:
    """Gera entradas de dungeon no mundo"""
    
    NOMES_DUNGEONS = [
        "Caverna Misteriosa",
        "Cripta Antiga",
        "Torre Arruinada",
        "Templo Perdido",
        "Mina Profunda",
        "Floresta Sombria",
        "Câmara Vulcânica",
    ]
    
    @staticmethod
    def gerar_entrada(x: int, y: int, tipo: str = "caverna") -> dict:
        """Gera um objeto de entrada de dungeon"""
        nome = random.choice(GeneradorEntradaDungeon.NOMES_DUNGEONS)
        
        return {
            'id': f"dungeon_{x}_{y}",
            'nome': nome,
            'tipo': tipo,
            'x': x,
            'y': y,
            'descricao': f"Uma entrada para {nome}",
            'interativo': True,
            'profundidade_sugerida': random.randint(1, 3),
            'exploravel': True,
        }
    
    @staticmethod
    def gerar_multiplas_entradas(tamanho_mundo: int, quantidade: int = 3) -> list:
        """Gera múltiplas entradas de dungeon espalhadas no mundo"""
        entradas = []
        tipos_biomas = ["caverna", "cripta", "torre", "templo", "mina", "floresta", "vulcao"]
        
        for _ in range(quantidade):
            x = random.randint(10, tamanho_mundo - 10)
            y = random.randint(10, tamanho_mundo - 10)
            tipo = random.choice(tipos_biomas)
            entradas.append(GeneradorEntradaDungeon.gerar_entrada(x, y, tipo))
        
        return entradas
