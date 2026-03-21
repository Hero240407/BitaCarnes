"""Sistema de Calendário, Estações e Festivais - Stardew Valley inspired"""
from dataclasses import dataclass
from enum import Enum
import random
from typing import Optional, List


class Estacao(Enum):
    """Estações do ano"""
    PRIMAVERA = "primavera"
    VERAO = "verao"
    OUTONO = "outono"
    INVERNO = "inverno"


@dataclass(slots=True)
class Festival:
    """Festival ou evento especial"""
    nome: str
    estacao: Estacao
    dia_mes: int
    descricao: str
    premios: dict
    npcs_participando: list[str]
    tipo_festival: str  # "colheita", "danca", "competicao", "casamento", "celebracao"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "nome": self.nome,
            "estacao": self.estacao.value,
            "dia": self.dia_mes,
            "descricao": self.descricao,
            "tipo": self.tipo_festival
        }


FESTIVAIS_PADRAO = [
    # Primavera
    Festival(
        "Dança da Primavera",
        Estacao.PRIMAVERA,
        13,
        "Celebração do novo começo com danças e festividades",
        {"sementes": 10, "ouro": 50},
        [],
        "danca"
    ),
    # Verão
    Festival(
        "Festa da Colheita Estival",
        Estacao.VERAO,
        16,
        "Celebração da primeira colheita com comidas típicas",
        {"ouro": 100, "receita_especial": 1},
        [],
        "colheita"
    ),
    # Outono
    Festival(
        "Feira de Outono",
        Estacao.OUTONO,
        16,
        "Grande feira com vendas e competições de produtos",
        {"ouro": 150, "ferramentas": 1},
        [],
        "competicao"
    ),
    # Inverno
    Festival(
        "Celebração do Inverno",
        Estacao.INVERNO,
        25,
        "Festa de encerramento do ano com trocas de presentes",
        {"ouro": 50, "presente_especial": 1},
        [],
        "celebracao"
    ),
]


class Calendario:
    """Sistema de calendário com estações e festivais"""
    
    def __init__(self, ano_inicial: int = 1):
        self.ano = ano_inicial
        self.estacao = Estacao.PRIMAVERA
        self.dia_mes = 1  # 1-28 (cada mês tem 28 dias)
        self.dia_ano = 1
        self.dias_totais = 0
        
        self.festivais = self._inicializar_festivais()
        self.eventos_criticos: dict[tuple[Estacao, int], str] = {}
        
    def _inicializar_festivais(self) -> dict[str, Festival]:
        """Inicializa festivais padrão"""
        festivais_dict = {}
        for festival in FESTIVAIS_PADRAO:
            chave = f"{festival.estacao.value}_{festival.dia_mes}"
            festivais_dict[chave] = festival
        return festivais_dict
    
    @property
    def estacao_nome(self) -> str:
        """Retorna nome da estação em português"""
        nomes = {
            Estacao.PRIMAVERA: "Primavera",
            Estacao.VERAO: "Verão",
            Estacao.OUTONO: "Outono",
            Estacao.INVERNO: "Inverno"
        }
        return nomes[self.estacao]
    
    @property
    def data_formatada(self) -> str:
        """Retorna data no formato "Dia X de Estação, Ano Y" """
        return f"Dia {self.dia_mes} de {self.estacao_nome}, Ano {self.ano}"
    
    def avancar_dia(self) -> dict:
        """Avança um dia no calendário"""
        self.dia_mes += 1
        self.dia_ano += 1
        self.dias_totais += 1
        
        eventos = {
            "novo_dia": True,
            "novo_mes": False,
            "nova_estacao": False,
            "novo_ano": False,
            "festival": None,
            "mensagem": ""
        }
        
        # Verificar novo mês
        if self.dia_mes > 28:
            self.dia_mes = 1
            eventos["novo_mes"] = True
            old_season = self.estacao
            self._avancar_estacao()
            eventos["nova_estacao"] = old_season != self.estacao
            
            if self.estacao == Estacao.PRIMAVERA and old_season == Estacao.INVERNO:
                self.ano += 1
                eventos["novo_ano"] = True
                eventos["mensagem"] = f"Feliz Ano {self.ano}!"
        
        # Verificar festival
        festival_key = f"{self.estacao.value}_{self.dia_mes}"
        if festival_key in self.festivais:
            eventos["festival"] = self.festivais[festival_key]
            eventos["mensagem"] = f"🎉 {self.festivais[festival_key].nome} acontece hoje!"
        
        return eventos
    
    def _avancar_estacao(self) -> None:
        """Avança para próxima estação"""
        ordem = [Estacao.PRIMAVERA, Estacao.VERAO, Estacao.OUTONO, Estacao.INVERNO]
        idx = ordem.index(self.estacao)
        self.estacao = ordem[(idx + 1) % len(ordem)]
    
    def obter_estacao_atual(self) -> Estacao:
        """Retorna estação atual"""
        return self.estacao
    
    def obter_festival_de_hoje(self) -> Optional[Festival]:
        """Retorna festival de hoje, se houver"""
        festival_key = f"{self.estacao.value}_{self.dia_mes}"
        return self.festivais.get(festival_key)
    
    def obter_proximos_festivais(self, quantidade: int = 5) -> list[Festival]:
        """Retorna próximos festivais"""
        festivais_lista = []
        
        # Ordenar festivais por data
        for estacao in [Estacao.PRIMAVERA, Estacao.VERAO, Estacao.OUTONO, Estacao.INVERNO]:
            for dia in range(1, 29):
                chave = f"{estacao.value}_{dia}"
                if chave in self.festivais:
                    festivais_lista.append(self.festivais[chave])
        
        return festivais_lista[:quantidade]
    
    def obter_dias_para_proxima_colheita(self) -> int:
        """Calcula dias para próxima estação (colheita)"""
        dias_restantes = (28 - self.dia_mes) + 1
        if self.estacao == Estacao.VERAO:
            return dias_restantes + 28  # Falta outono inteiro
        elif self.estacao == Estacao.OUTONO:
            return dias_restantes
        elif self.estacao == Estacao.INVERNO:
            return dias_restantes + (28 * 2)  # Primavera todo + Verão
        else:  # Primavera
            return dias_restantes + 28  # Verão inteiro
    
    def eh_dias_fixos(self) -> bool:
        """Verifica se estamos em dias significativos"""
        significativos = [1, 7, 14, 21, 28]
        return self.dia_mes in significativos
    
    def get_lua_fase(self) -> str:
        """Retorna fase da lua baseado no dia"""
        fases = ["🌑 Lua Nova", "🌒 Lua Crescente", "🌓 Quarto Crescente", 
                 "🌔 Lua Cheia", "🌕 Lua Cheia", "🌖 Quarto Minguante", "🌗 Lua Minguante"]
        indice = (self.dia_mes % len(fases))
        return fases[indice]
    
    def obter_plantas_plantaveis(self) -> list[str]:
        """Retorna plantas que podem ser plantadas nesta estação"""
        plantas_por_estacao = {
            Estacao.PRIMAVERA: ["trigo", "batata", "feijao"],
            Estacao.VERAO: ["milho", "melancia", "trigo_celestial"],
            Estacao.OUTONO: ["batata", "milho", "taro_demonaco"],
            Estacao.INVERNO: ["glowmushroom", "silvervine_lunar"],
        }
        return plantas_por_estacao.get(self.estacao, [])
    
    def avancar_para_dia(self, estacao: str, dia: int) -> bool:
        """Avança para um dia específico"""
        estacoes = {
            "primavera": Estacao.PRIMAVERA,
            "verao": Estacao.VERAO,
            "outono": Estacao.OUTONO,
            "inverno": Estacao.INVERNO,
        }
        
        if estacao.lower() in estacoes and 1 <= dia <= 28:
            self.estacao = estacoes[estacao.lower()]
            self.dia_mes = dia
            return True
        return False


class EventoSazonal:
    """Evento que ocorre em determinada estação"""
    
    def __init__(self, nome: str, estacao: Estacao, raridade: float = 0.1):
        self.nome = nome
        self.estacao = estacao
        self.raridade = raridade  # Probabilidade de ocorrer
        self.descricao = ""
        self.efeitos = {}
    
    def pode_ocorrer(self) -> bool:
        """Verifica se evento pode ocorrer"""
        return random.random() < self.raridade


EVENTOS_SAZONAIS = [
    EventoSazonal("Chuva de Primavera", Estacao.PRIMAVERA, raridade=0.3),
    EventoSazonal("Onda de Calor", Estacao.VERAO, raridade=0.2),
    EventoSazonal("Redemoinhos de Outono", Estacao.OUTONO, raridade=0.25),
    EventoSazonal("Nevasca", Estacao.INVERNO, raridade=0.4),
    EventoSazonal("Aurora Boreal", Estacao.INVERNO, raridade=0.1),
]


class BoliviadoArquivo:
    """Conjunto de datas e marcos importantes"""
    
    def __init__(self):
        self.marcos_importante: dict[str, dict] = {
            "primeiro_cultivo": None,
            "primeira_colheita": None,
            "primeiro_casamento": None,
            "primeiro_filho": None,
            "primeira_mina": None,
            "encontro_especial": None,
        }
    
    def registrar_marco(self, tipo_marco: str, data: str) -> bool:
        """Registra um marco importante"""
        if tipo_marco in self.marcos_importante:
            self.marcos_importante[tipo_marco] = data
            return True
        return False
