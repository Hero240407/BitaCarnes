"""Location-based ambiance system for world atmosphere and immersion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
from typing import Optional


class TipoBioma(Enum):
    """Biome types for world regions."""
    CAMPO = "campo"
    FLORESTA = "floresta"
    MONTANHA = "montanha"
    AGUA = "agua"
    DESERTO = "deserto"
    CAVERNA = "caverna"
    CIDADE = "cidade"
    SANTUARIO = "santuario"


@dataclass
class Ambiance:
    """Visual and audio ambiance for a location."""
    bioma: TipoBioma
    descricao: str
    cores_ambiente: tuple[int, int, int]
    cor_neblina: tuple[int, int, int]
    intensidade_neblina: float  # 0.0 to 1.0
    efeitos_particulas: list[str]
    sons_ambiente: list[str]
    temperatura: int  # -20 to 50
    umidade: int  # 0 to 100
    

class GerenciadorAmbiance:
    """Manages location-based ambiance and atmosphere."""
    
    # Predefined biome ambiances
    BIOMAS_PADRAO = {
        TipoBioma.CAMPO: Ambiance(
            bioma=TipoBioma.CAMPO,
            descricao="Um campo tranquilo com grama ondulante e flores silvestres.",
            cores_ambiente=(34, 139, 34),
            cor_neblina=(200, 220, 200),
            intensidade_neblina=0.1,
            efeitos_particulas=["polen", "sementes"],
            sons_ambiente=["vento_suave", "pássaros"],
            temperatura=15,
            umidade=60,
        ),
        
        TipoBioma.FLORESTA: Ambiance(
            bioma=TipoBioma.FLORESTA,
            descricao="Uma floresta densa com árvores antigas e luz filtrada.",
            cores_ambiente=(34, 89, 34),
            cor_neblina=(150, 180, 150),
            intensidade_neblina=0.3,
            efeitos_particulas=["folhas", "luz_solar"],
            sons_ambiente=["vento_floresta", "pássaros_floresta", "água_corrente"],
            temperatura=12,
            umidade=80,
        ),
        
        TipoBioma.MONTANHA: Ambiance(
            bioma=TipoBioma.MONTANHA,
            descricao="Picos montanhosos com vista panorâmica e ar frio.",
            cores_ambiente=(105, 105, 105),
            cor_neblina=(200, 200, 220),
            intensidade_neblina=0.5,
            efeitos_particulas=["neve", "vento_forte"],
            sons_ambiente=["vento_montanha", "ecos"],
            temperatura=-5,
            umidade=40,
        ),
        
        TipoBioma.AGUA: Ambiance(
            bioma=TipoBioma.AGUA,
            descricao="Uma água clara e refrescante, perfeita para pescar.",
            cores_ambiente=(30, 100, 200),
            cor_neblina=(100, 150, 200),
            intensidade_neblina=0.2,
            efeitos_particulas=["ondas", "respingos", "bolhas"],
            sons_ambiente=["água_fluindo", "pássaros_água"],
            temperatura=10,
            umidade=95,
        ),
        
        TipoBioma.DESERTO: Ambiance(
            bioma=TipoBioma.DESERTO,
            descricao="Areia dourada sob um sol escaldante.",
            cores_ambiente=(210, 180, 140),
            cor_neblina=(220, 200, 170),
            intensidade_neblina=0.4,
            efeitos_particulas=["areia_redemoinho", "calor"],
            sons_ambiente=["vento_deserto", "areia_sussurro"],
            temperatura=35,
            umidade=15,
        ),
        
        TipoBioma.CAVERNA: Ambiance(
            bioma=TipoBioma.CAVERNA,
            descricao="Uma caverna escura com mistério e cristais brilhantes.",
            cores_ambiente=(50, 50, 60),
            cor_neblina=(80, 80, 100),
            intensidade_neblina=0.6,
            efeitos_particulas=["cristais_brilho", "sombras"],
            sons_ambiente=["gotas_agua", "ecos_caverna"],
            temperatura=8,
            umidade=70,
        ),
        
        TipoBioma.CIDADE: Ambiance(
            bioma=TipoBioma.CIDADE,
            descricao="Uma pequena cidade aconchegante com casas e ruas.",
            cores_ambiente=(200, 200, 180),
            cor_neblina=(200, 200, 200),
            intensidade_neblina=0.1,
            efeitos_particulas=["fumaça", "luz_artificial"],
            sons_ambiente=["circulação", "conversas_fundo"],
            temperatura=18,
            umidade=50,
        ),
        
        TipoBioma.SANTUARIO: Ambiance(
            bioma=TipoBioma.SANTUARIO,
            descricao="Um local sagrado com mana milenosa impregnada.",
            cores_ambiente=(100, 80, 150),
            cor_neblina=(150, 120, 200),
            intensidade_neblina=0.4,
            efeitos_particulas=["runas", "luz_mana", "petálas"],
            sons_ambiente=["melodia_sagrada", "silêncio_tranquilo"],
            temperatura=14,
            umidade=60,
        ),
    }
    
    def __init__(self):
        self.ambiance_atual = None
        self.tempo_transicao = 0
        self.ambiance_alvo = None
        
    def obter_ambiance(self, x: int, y: int, biomas_mapa: dict) -> Ambiance:
        """Get ambiance for current location based on map biome."""
        
        # Determine biome based on world position
        bioma = self._determinar_bioma_posicao(x, y, biomas_mapa)
        
        ambiance = self.BIOMAS_PADRAO.get(bioma, self.BIOMAS_PADRAO[TipoBioma.CAMPO])
        return ambiance
    
    def _determinar_bioma_posicao(self, x: int, y: int, biomas_mapa: dict) -> TipoBioma:
        """Determine biome at given world position."""
        # Try to get from bioma_mapa if available
        pos_key = (x, y)
        if pos_key in biomas_mapa:
            return biomas_mapa[pos_key]
        
        # Fallback to procedural determination based on position
        distrito = (x // 20, y // 20)  # Divide world into 20x20 districts
        
        # Use deterministic randomness for consistent biomes
        seed = sum(distrito) * 73856093 ^ (distrito[0] * 19349663) ^ (distrito[1] * 83492791)
        random.seed(seed)
        bioma_roll = random.random()
        
        if bioma_roll < 0.3:
            return TipoBioma.CAMPO
        elif bioma_roll < 0.55:
            return TipoBioma.FLORESTA
        elif bioma_roll < 0.7:
            return TipoBioma.AGUA
        elif bioma_roll < 0.85:
            return TipoBioma.MONTANHA
        else:
            return TipoBioma.DESERTO
    
    def atualizar_ambiance(self, x: int, y: int, biomas_mapa: dict) -> None:
        """Update ambiance for new location."""
        nova_ambiance = self.obter_ambiance(x, y, biomas_mapa)
        
        if self.ambiance_atual != nova_ambiance:
            self.ambiance_alvo = nova_ambiance
            self.tempo_transicao = 0
    
    def _transicionar_suave(self) -> Ambiance:
        """Get current ambiance with smooth transition."""
        if self.ambiance_alvo is None:
            return self.ambiance_atual
        
        self.tempo_transicao = min(self.tempo_transicao + 1, 60)  # 60 frames transition
        progresso = self.tempo_transicao / 60.0
        
        if progresso >= 1.0:
            self.ambiance_atual = self.ambiance_alvo
            self.ambiance_alvo = None
        
        return self.ambiance_atual or self.ambiance_alvo
    
    def obter_descricao_localizacao(self, x: int, y: int, biomas_mapa: dict) -> str:
        """Get detailed location description."""
        ambiance = self.obter_ambiance(x, y, biomas_mapa)
        
        # Enhance description with context
        distancia_cidade = abs(x) + abs(y) % 30
        profundidade = max(0, 20 - (distancia_cidade // 5))
        
        descricoes_adicionais = {
            TipoBioma.CAMPO: [
                "As flores locais balançam suavemente.",
                "Você sente o cheiro de terra fértil.",
                "Um abrigo de pedra antigo está ao longe.",
            ],
            TipoBioma.FLORESTA: [
                "A luz solar filtra através das folhas.",
                "Você escuta o som de uma pequena fonte.",
                "Marcas antigos podem ser vistas nas árvores.",
            ],
            TipoBioma.MONTANHA: [
                "O ar é frio e nítido.",
                "Você tem uma vista clara de todo o vale.",
                "Há minerais brilhantes visíveis nas rochas.",
            ],
            TipoBioma.AGUA: [
                "A água parece especialmente cristalina hoje.",
                "Você pode ver peixes nas águas claras.",
                "A margem é macia e arenosa.",
            ],
            TipoBioma.DESERTO: [
                "O calor é quase visível acima da areia.",
                "Você vê topos de estruturas antigas sob areia.",
                "O vento carrega areia fino.",
            ],
        }
        
        descricoes = descricoes_adicionais.get(ambiance.bioma, [])
        return f"{ambiance.descricao} {random.choice(descricoes) if descricoes else ''}"


class SistemaTempoAmbiane:
    """Weather and time effects on ambiance."""
    
    def __init__(self):
        self.clima_atual = "Ensolarado"
        self.hora_atual = 12
        self.intensidade_clima = 0.5
        
    def obter_modificador_cores(self) -> tuple[float, float, float]:
        """Get color modifier based on time and weather."""
        
        # Time of day effects
        if self.hora_atual < 6:
            # Madrugada - azul escuro
            r, g, b = 0.3, 0.3, 0.5
        elif self.hora_atual < 12:
            # Manhã - aquecendo
            progresso = (self.hora_atual - 6) / 6
            r = 0.5 + 0.5 * progresso
            g = 0.4 + 0.6 * progresso
            b = 0.3 + 0.5 * progresso
        elif self.hora_atual < 18:
            # Tarde - quente e claro
            r, g, b = 1.0, 0.85, 0.6
        else:
            # Noite - azul/roxo
            progresso = (self.hora_atual - 18) / 6
            r = 1.0 - 0.7 * progresso
            g = 0.85 - 0.55 * progresso
            b = 0.6 + 0.4 * progresso
        
        # Weather effects
        if self.clima_atual == "Nublado":
            r *= 0.85
            g *= 0.85
            b *= 0.85
        elif self.clima_atual == "Chuvoso":
            r *= 0.7
            g *= 0.7
            b *= 0.8
        elif self.clima_atual == "Tempestade":
            r *= 0.5
            g *= 0.5
            b *= 0.6
        
        return (r, g, b)
    
    def obter_intensidade_luz(self) -> float:
        """Get lighting intensity (0.0 to 1.0)."""
        if self.hora_atual < 6:
            return 0.1
        elif self.hora_atual < 8:
            return 0.1 + 0.3 * (self.hora_atual - 6) / 2
        elif self.hora_atual < 18:
            return 0.8
        elif self.hora_atual < 20:
            return 0.8 - 0.3 * (self.hora_atual - 18) / 2
        else:
            return 0.1
