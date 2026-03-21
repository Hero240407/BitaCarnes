"""Sistema de Agricultura e Plantações - Stardew Valley inspired"""
from dataclasses import dataclass, field
from enum import Enum
import random
import time
from typing import Optional

from .config import DIRECOES


class EstacaoEnum(Enum):
    """Estações do ano"""
    PRIMAVERA = "primavera"
    VERAO = "verao"
    OUTONO = "outono"
    INVERNO = "inverno"


@dataclass(slots=True)
class PlantaCultivada:
    """Representa uma planta cultivada em uma célula"""
    tipo_planta: str
    dia_plantado: int
    estacao_plantada: str
    dias_crescimento_total: int
    dias_crescidos: int = 0
    foi_regada_hoje: bool = False
    saude_planta: float = 1.0  # 0.0 a 1.0
    
    def atualizar_um_dia(self, foi_regada: bool = True) -> None:
        """Avança um dia no crescimento da planta"""
        self.dias_crescidos += 1
        if not foi_regada:
            self.saude_planta -= 0.15  # Planta perde saúde se não for regada
        self.saude_planta = max(0.0, min(1.0, self.saude_planta))
        
    @property
    def pronta_colher(self) -> bool:
        """Verifica se planta está pronta para colheita"""
        return self.dias_crescidos >= self.dias_crescimento_total
    
    @property
    def percentual_crescimento(self) -> int:
        """Retorna percentual de crescimento (0-100)"""
        return int((self.dias_crescidos / self.dias_crescimento_total) * 100)


@dataclass(slots=True)
class CelulaCultivavel:
    """Representa uma célula de terra cultivável"""
    x: int
    y: int
    foi_arada: bool = False
    foi_regada_hoje: bool = False
    planta_atual: Optional[PlantaCultivada] = None
    tipo_solo: str = "terra"  # terra, areia, lama
    fertilizante_nivel: int = 0  # 0 (nenhum), 1 (básico), 2 (avançado)
    
    def aradir(self) -> bool:
        """Prepara solo para plantio"""
        if not self.foi_arada:
            self.foi_arada = True
            return True
        return False
    
    def regar(self) -> bool:
        """Rega a célula"""
        if not self.foi_regada_hoje and self.foi_arada:
            self.foi_regada_hoje = True
            if self.planta_atual:
                self.planta_atual.foi_regada_hoje = True
            return True
        return False
    
    def plantar(self, tipo_planta: str, dias_crescimento: int, dia_atual: int, estacao: str) -> bool:
        """Planta uma semente"""
        if self.foi_arada and not self.planta_atual:
            self.planta_atual = PlantaCultivada(
                tipo_planta=tipo_planta,
                dia_plantado=dia_atual,
                estacao_plantada=estacao,
                dias_crescimento_total=dias_crescimento
            )
            return True
        return False
    
    def colher(self) -> bool:
        """Colhe a planta se estiver pronta"""
        if self.planta_atual and self.planta_atual.pronta_colher:
            self.planta_atual = None
            self.foi_arada = False
            return True
        return False
    
    def resetar_dia(self) -> None:
        """Reseta flags diárias"""
        self.foi_regada_hoje = False


class FarmManager:
    """Gerencia a fazenda e plantações do jogador"""
    
    def __init__(self, tamanho_farm: int = 10):
        self.tamanho_farm = tamanho_farm
        self.celulas_cultivo: dict[tuple[int, int], CelulaCultivavel] = {}
        self.dinheiro = 500
        self.exp_agricultura = 0
        self.nivel_agricultura = 1
        self.sementes_inventario: dict[str, int] = {}
        self._inicializar_farm()
        
    def _inicializar_farm(self) -> None:
        """Cria celulas cultivas iniciais"""
        # Cria 20 celulas aleatórias na farm inicial
        for _ in range(20):
            x = random.randint(0, self.tamanho_farm - 1)
            y = random.randint(0, self.tamanho_farm - 1)
            if (x, y) not in self.celulas_cultivo:
                self.celulas_cultivo[(x, y)] = CelulaCultivavel(x, y)
    
    def obter_celula(self, x: int, y: int) -> CelulaCultivavel:
        """Obtém ou cria celula cultivável"""
        chave = (x, y)
        if chave not in self.celulas_cultivo:
            self.celulas_cultivo[chave] = CelulaCultivavel(x, y)
        return self.celulas_cultivo[chave]
    
    def aradir_terreno(self, x: int, y: int) -> bool:
        """Ara um terreno"""
        celula = self.obter_celula(x, y)
        sucesso = celula.aradir()
        if sucesso:
            self.exp_agricultura += 1
            self._verificar_nivel()
        return sucesso
    
    def regar_terreno(self, x: int, y: int) -> bool:
        """Rega um terreno"""
        celula = self.obter_celula(x, y)
        sucesso = celula.regar()
        if sucesso:
            self.exp_agricultura += 1
        return sucesso
    
    def plantar_semente(self, x: int, y: int, tipo_planta: str, 
                       dias_crescimento: int, dia_atual: int, estacao: str) -> bool:
        """Planta uma semente"""
        if tipo_planta not in self.sementes_inventario or self.sementes_inventario[tipo_planta] <= 0:
            return False
        
        celula = self.obter_celula(x, y)
        sucesso = celula.plantar(tipo_planta, dias_crescimento, dia_atual, estacao)
        if sucesso:
            self.sementes_inventario[tipo_planta] -= 1
            self.exp_agricultura += 2
        return sucesso
    
    def colher(self, x: int, y: int, plantas_dados: dict) -> tuple[bool, Optional[dict]]:
        """Colhe uma planta e retorna info de colheita"""
        celula = self.obter_celula(x, y)
        if celula.planta_atual and celula.planta_atual.pronta_colher:
            tipo = celula.planta_atual.tipo_planta
            dados_planta = plantas_dados.get(tipo, {})
            
            # Calcular rendimento baseado em saúde
            rendimento_base = dados_planta.get("food_yield", 1.0)
            rendimento_final = int(rendimento_base * celula.planta_atual.saude_planta)
            
            celula.colher()
            self.dinheiro += rendimento_final * 10
            self.exp_agricultura += 5
            self._verificar_nivel()
            
            return True, {
                "tipo": tipo,
                "quantidade": rendimento_final,
                "valor": rendimento_final * 10
            }
        return False, None
    
    def avancar_dia(self) -> None:
        """Avança um dia para todas as plantas"""
        for celula in self.celulas_cultivo.values():
            if celula.planta_atual:
                celula.planta_atual.atualizar_um_dia(celula.foi_regada_hoje)
            celula.resetar_dia()
    
    def _verificar_nivel(self) -> None:
        """Verifica se jogador subiu de nível"""
        novo_nivel = 1 + (self.exp_agricultura // 100)
        if novo_nivel > self.nivel_agricultura:
            self.nivel_agricultura = novo_nivel
    
    def adicionar_sementes(self, tipo_planta: str, quantidade: int = 1) -> None:
        """Adiciona sementes ao inventário"""
        self.sementes_inventario[tipo_planta] = self.sementes_inventario.get(tipo_planta, 0) + quantidade
    
    def obter_sementes_disponiveis(self) -> dict[str, int]:
        """Retorna sementes em estoque"""
        return {k: v for k, v in self.sementes_inventario.items() if v > 0}


class SistemaIrrigacao:
    """Sistema automático de irrigação e rega"""
    
    def __init__(self):
        self.sprinklers: list[tuple[int, int]] = []
        self.nivel_tecnologia = 0
        
    def adicionar_sprinkler(self, x: int, y: int) -> bool:
        """Adiciona um regador automático"""
        if (x, y) not in self.sprinklers:
            self.sprinklers.append((x, y))
            return True
        return False
    
    def obter_alcance_sprinkler(self, x: int, y: int) -> list[tuple[int, int]]:
        """Retorna células regadas por um sprinkler"""
        alcance = 2 + self.nivel_tecnologia
        celulas = []
        for dx in range(-alcance, alcance + 1):
            for dy in range(-alcance, alcance + 1):
                if abs(dx) + abs(dy) <= alcance:
                    celulas.append((x + dx, y + dy))
        return celulas
