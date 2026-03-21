"""Sistema de Clima e Ambiente - Stardew Valley inspired"""
from enum import Enum
import random
import math
from typing import Optional
from dataclasses import dataclass


class TipoClima(Enum):
    """Tipos de clima"""
    ENSOLARADO = "ensolarado"
    NUBLADO = "nublado"
    CHUVOSO = "chuvoso"
    TEMPESTADE = "tempestade"
    NEVE = "neve"
    NEBLINA = "neblina"
    ARCO_IRIS = "arco_iris"


@dataclass(slots=True)
class CondClima:
    """Condições de clima"""
    tipo: TipoClima
    temperatura: float  # -20 a 35 graus Celsius
    umidade: float  # 0 a 100%
    velocidade_vento: float  # 0 a 100 km/h
    visibilidade: float  # 0 a 100 (percentual)
    probabilidade_raio: float  # 0 a 1.0
    descricao: str
    emoji: str


class SistemaClima:
    """Gerencia o clima do mundo"""
    
    def __init__(self):
        self.climas = self._criar_climas_padrao()
        self.clima_atual = TipoClima.ENSOLARADO
        self.condicoes_atuais = self.climas[TipoClima.ENSOLARADO]
        self.dias_clima_sequencia = 0
        self.mudanca_clima_em_dias = random.randint(1, 5)
        
    def _criar_climas_padrao(self) -> dict[TipoClima, CondClima]:
        """Cria condições padrão para cada tipo de clima"""
        return {
            TipoClima.ENSOLARADO: CondClima(
                tipo=TipoClima.ENSOLARADO,
                temperatura=22,
                umidade=30,
                velocidade_vento=5,
                visibilidade=100,
                probabilidade_raio=0,
                descricao="Dia ensolarado e belo",
                emoji="☀️"
            ),
            TipoClima.NUBLADO: CondClima(
                tipo=TipoClima.NUBLADO,
                temperatura=18,
                umidade=60,
                velocidade_vento=10,
                visibilidade=90,
                probabilidade_raio=0,
                descricao="Dia nublado",
                emoji="☁️"
            ),
            TipoClima.CHUVOSO: CondClima(
                tipo=TipoClima.CHUVOSO,
                temperatura=15,
                umidade=95,
                velocidade_vento=20,
                visibilidade=70,
                probabilidade_raio=0.1,
                descricao="Chovendo moderadamente",
                emoji="🌧️"
            ),
            TipoClima.TEMPESTADE: CondClima(
                tipo=TipoClima.TEMPESTADE,
                temperatura=12,
                umidade=100,
                velocidade_vento=50,
                visibilidade=40,
                probabilidade_raio=0.4,
                descricao="Tempestade severa!",
                emoji="⛈️"
            ),
            TipoClima.NEVE: CondClima(
                tipo=TipoClima.NEVE,
                temperatura=-5,
                umidade=85,
                velocidade_vento=25,
                visibilidade=60,
                probabilidade_raio=0.05,
                descricao="Nevando",
                emoji="❄️"
            ),
            TipoClima.NEBLINA: CondClima(
                tipo=TipoClima.NEBLINA,
                temperatura=10,
                umidade=90,
                velocidade_vento=2,
                visibilidade=30,
                probabilidade_raio=0,
                descricao="Neblina densa",
                emoji="🌫️"
            ),
            TipoClima.ARCO_IRIS: CondClima(
                tipo=TipoClima.ARCO_IRIS,
                temperatura=16,
                umidade=50,
                velocidade_vento=5,
                visibilidade=100,
                probabilidade_raio=0,
                descricao="Lindo arco-íris no céu!",
                emoji="🌈"
            ),
        }
    
    def avancar_dia(self, estacao: str = "primavera") -> tuple[TipoClima, str]:
        """Avança um dia e potencialmente muda o clima"""
        self.dias_clima_sequencia += 1
        
        if self.dias_clima_sequencia >= self.mudanca_clima_em_dias:
            novo_clima = self._selecionar_novo_clima(estacao)
            self.clima_atual = novo_clima
            self.condicoes_atuais = self.climas[novo_clima]
            self.dias_clima_sequencia = 0
            self.mudanca_clima_em_dias = random.randint(1, 5)
            
            mensagem = f"Clima mudou para: {self.condicoes_atuais.descricao}"
        else:
            mensagem = f"{self.condicoes_atuais.emoji} {self.condicoes_atuais.descricao}"
        
        return self.clima_atual, mensagem
    
    def _selecionar_novo_clima(self, estacao: str) -> TipoClima:
        """Seleciona novo clima baseado na estação"""
        clima_chances = {
            "primavera": {
                TipoClima.ENSOLARADO: 0.4,
                TipoClima.NUBLADO: 0.3,
                TipoClima.CHUVOSO: 0.25,
                TipoClima.TEMPESTADE: 0.03,
                TipoClima.ARCO_IRIS: 0.02,
            },
            "verao": {
                TipoClima.ENSOLARADO: 0.6,
                TipoClima.NUBLADO: 0.2,
                TipoClima.CHUVOSO: 0.15,
                TipoClima.TEMPESTADE: 0.04,
                TipoClima.NEBLINA: 0.01,
            },
            "outono": {
                TipoClima.ENSOLARADO: 0.35,
                TipoClima.NUBLADO: 0.35,
                TipoClima.CHUVOSO: 0.25,
                TipoClima.TEMPESTADE: 0.04,
                TipoClima.NEBLINA: 0.01,
            },
            "inverno": {
                TipoClima.NEVE: 0.4,
                TipoClima.ENSOLARADO: 0.2,
                TipoClima.NUBLADO: 0.25,
                TipoClima.TEMPESTADE: 0.1,
                TipoClima.NEBLINA: 0.05,
            },
        }
        
        chances = clima_chances.get(estacao, clima_chances["primavera"])
        climas_list = list(chances.keys())
        pesos = list(chances.values())
        
        return random.choices(climas_list, weights=pesos)[0]
    
    def obter_info_clima(self) -> dict:
        """Retorna informações detalhadas do clima"""
        return {
            "tipo": self.clima_atual.value,
            "descricao": self.condicoes_atuais.descricao,
            "emoji": self.condicoes_atuais.emoji,
            "temperatura": round(self.condicoes_atuais.temperatura, 1),
            "umidade": int(self.condicoes_atuais.umidade),
            "vento": int(self.condicoes_atuais.velocidade_vento),
            "visibilidade": int(self.condicoes_atuais.visibilidade),
        }
    
    def afeta_agricultura(self) -> dict:
        """Retorna efeitos do clima na agricultura"""
        efeitos = {
            "pode_plantar": True,
            "pode_colher": True,
            "regadura_automatica": False,
            "bonus_crescimento": 0,
            "perda_saude_plantas": 0,
        }
        
        if self.clima_atual == TipoClima.CHUVOSO:
            efeitos["regadura_automatica"] = True
            efeitos["bonus_crescimento"] = 0.2
        elif self.clima_atual == TipoClima.TEMPESTADE:
            efeitos["regadura_automatica"] = True
            efeitos["pode_plantar"] = False
            efeitos["perda_saude_plantas"] = 0.1
        elif self.clima_atual == TipoClima.NEVE:
            efeitos["pode_plantar"] = False
            efeitos["pode_colher"] = False
            efeitos["perda_saude_plantas"] = 0.2
        elif self.clima_atual == TipoClima.ENSOLARADO:
            efeitos["bonus_crescimento"] = 0.1
        
        return efeitos
    
    def afeta_pesca(self) -> dict:
        """Retorna efeitos do clima na pesca"""
        efeitos = {
            "pode_pescar": True,
            "taxa_acelerada": 1.0,
            "peixes_raros_aumentado": False,
        }
        
        if self.clima_atual == TipoClima.CHUVOSO:
            efeitos["taxa_acelerada"] = 1.5
            efeitos["peixes_raros_aumentado"] = True
        elif self.clima_atual == TipoClima.TEMPESTADE:
            efeitos["pode_pescar"] = False
        elif self.clima_atual == TipoClima.ENSOLARADO:
            efeitos["taxa_acelerada"] = 0.9
        elif self.clima_atual == TipoClima.NEVE:
            efeitos["taxa_acelerada"] = 0.8
        
        return efeitos
    
    def afeta_npcs(self) -> dict:
        """Retorna efeitos do clima nos NPCs"""
        efeitos = {
            "npcs_dentro_casa": False,
            "mood_ajuste": 0,
            "atividades_alteradas": False,
        }
        
        if self.clima_atual == TipoClima.TEMPESTADE:
            efeitos["npcs_dentro_casa"] = True
            efeitos["mood_ajuste"] = -1
            efeitos["atividades_alteradas"] = True
        elif self.clima_atual == TipoClima.NEVE:
            efeitos["npcs_dentro_casa"] = True
            efeitos["atividades_alteradas"] = True
        elif self.clima_atual == TipoClima.ENSOLARADO:
            efeitos["mood_ajuste"] = 1
        
        return efeitos
    
    def calcula_iluminacao_dia(self, hora_decimal: float) -> float:
        """Calcula iluminação (0-1) baseado na hora e clima"""
        # Criar curva de iluminação natural (6h a 22h)
        if hora_decimal < 6 or hora_decimal >= 22:
            iluminacao_base = 0.1
        elif 6 <= hora_decimal < 8:
            iluminacao_base = 0.1 + (hora_decimal - 6) * 0.45
        elif 8 <= hora_decimal < 18:
            iluminacao_base = 1.0
        elif 18 <= hora_decimal < 20:
            iluminacao_base = 1.0 - (hora_decimal - 18) * 0.5
        else:
            iluminacao_base = 0.1 + (22 - hora_decimal) * 0.5
        
        # Ajustar por clima
        multiplicador_clima = {
            TipoClima.ENSOLARADO: 1.0,
            TipoClima.NUBLADO: 0.75,
            TipoClima.CHUVOSO: 0.6,
            TipoClima.TEMPESTADE: 0.4,
            TipoClima.NEVE: 0.85,
            TipoClima.NEBLINA: 0.5,
            TipoClima.ARCO_IRIS: 1.1,
        }
        
        mult = multiplicador_clima.get(self.clima_atual, 1.0)
        iluminacao_final = iluminacao_base * mult
        
        return max(0.0, min(1.0, iluminacao_final))


class AlertasClimaticos:
    """Sistema de alertas para eventos climáticos perigosos"""
    
    def __init__(self):
        self.alertas_ativos: list[dict] = []
        self.alertas_historico: list[dict] = []
        
    def adicionar_alerta(self, tipo: str, severidade: int, mensagem: str, duracao_horas: int = 12) -> None:
        """Adiciona um novo alerta climático"""
        alerta = {
            "tipo": tipo,
            "severidade": severidade,  # 1-5
            "mensagem": mensagem,
            "duracao_horas": duracao_horas,
            "timestamp": 0,
        }
        self.alertas_ativos.append(alerta)
        self.alertas_historico.append(alerta)
    
    def obter_alertas_ativos(self) -> list[dict]:
        """Retorna alertas em vigor"""
        return self.alertas_ativos
    
    def limpar_alertas_expirados(self) -> None:
        """Remove alertas que expiraram"""
        self.alertas_ativos = [a for a in self.alertas_ativos if a["duracao_horas"] > 0]
        for alerta in self.alertas_ativos:
            alerta["duracao_horas"] -= 1
