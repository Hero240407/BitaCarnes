"""Expanded world interaction system for more immersive gameplay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
import random


class TipoObjeto(Enum):
    """Types of interactive world objects."""
    RECURSO = "recurso"
    DECORACAO = "decoracao"
    ESTRUTURA = "estrutura"
    CRIATURA = "criatura"
    ARTEFATO = "artefato"
    PORTAL = "portal"
    TUMULO = "tumulo"
    MONUMENTO = "monumento"


@dataclass
class ObjetoMundo:
    """An interactive object in the world."""
    id: str
    nome: str
    tipo: TipoObjeto
    x: int
    y: int
    descricao: str
    acessivel: bool
    recompensa_interacao: dict
    tempo_regeneracao: int  # Turns until next interaction
    foi_interagido: bool = False
    
    def pode_interagir(self) -> bool:
        """Check if object can be interacted with."""
        return self.acessivel and self.tempo_regeneracao == 0
    
    def registrar_interacao(self) -> None:
        """Mark as interacted and set regeneration timer."""
        self.foi_interagido = True
        self.tempo_regeneracao = self.tempo_regeneracao


class GerenciadorObjetos:
    """Manages all interactive objects in the world."""
    
    OBJETOS_PADRAO = {
        "pedra_antiga": {
            "nome": "Pedra Antiga",
            "tipo": TipoObjeto.MONUMENTO,
            "descricao": "Uma pedra misteriosamente inscrita com símbolos antigos.",
            "recompensa": {"sabedoria_mundana": 1, "conhecimento": 5},
            "cooldown": 360,  # 15 turns
        },
        "tumulo_aventureiro": {
            "nome": "Túmulo de um Aventureiro",
            "tipo": TipoObjeto.TUMULO,
            "descricao": "Um túmulo desgastado marca o repouso de um antigo viajante.",
            "recompensa": {"ouro": random.randint(50, 150), "lore_encontrada": True},
            "cooldown": 0,  # Uma única descida
        },
        "cachoeira_sagrada": {
            "nome": "Cachoeira Sagrada",
            "tipo": TipoObjeto.DECORACAO,
            "descricao": "Água cristalina cai graciosamente de uma altura.",
            "recompensa": {"restauracao": 30, "morale": 2},
            "cooldown": 120,
        },
        "arvore_cristal": {
            "nome": "Árvore de Cristal",
            "tipo": TipoObjeto.ARTEFATO,
            "descricao": "Uma árvore luminosa feita de cristal puro, pulsando com mana.",
            "recompensa": {"mana": 20, "ouro": 75},
            "cooldown": 480,
        },
        "ruinas_cidade_antiga": {
            "nome": "Ruínas de Cidade Antiga",
            "tipo": TipoObjeto.ESTRUTURA,
            "descricao": "Os restos erguidos de uma civilização esquecida.",
            "recompensa": {"conhecimento": 10, "artefatos": random.randint(1, 3)},
            "cooldown": 720,
        },
        "santuario_perdido": {
            "nome": "Santuário Perdido",
            "tipo": TipoObjeto.PORTAL,
            "descricao": "Um local sagrado irradia energia ancestral.",
            "recompensa": {"bencao": 2, "conhecimento": 15},
            "cooldown": 1440,
        },
        "ninho_raro": {
            "nome": "Ninho Raro",
            "tipo": TipoObjeto.CRIATURA,
            "descricao": "Um ninho onde criatura rara repousa.",
            "recompensa": {"criatura_rara": 1, "ouro": 100},
            "cooldown": 0,
        },
        "floresta_encantada": {
            "nome": "Floresta Encantada",
            "tipo": TipoObjeto.ESTRUTURA,
            "descricao": "Árvores antigas balançam com uma vida própria.",
            "recompensa": {"madeira_magica": random.randint(2, 5), "sementes_raras": random.randint(1, 3)},
            "cooldown": 240,
        },
        "poco_dos_desejos": {
            "nome": "Poço dos Desejos",
            "tipo": TipoObjeto.MONUMENTO,
            "descricao": "Água profunda e misteriosamente clara. Os antigos vinham até aqui.",
            "recompensa": {"sorte_temporaria": 5, "ouro": 50},
            "cooldown": 600,
        },
        "templo_ruinas": {
            "nome": "Templo em Ruínas",
            "tipo": TipoObjeto.PORTAL,
            "descricao": "Uma estrutura sagrada onde o tempo parece se mover diferente.",
            "recompensa": {"reliquias": random.randint(1, 2), "conhecimento": 8},
            "cooldown": 840,
        },
    }
    
    def __init__(self):
        self.objetos_mundo = {}
        self.contador_id = 0
        self.objetos_visitados = set()
        
    def gerar_objetos_procedural(self, tamanho_mundo: int, densidade: float = 0.02) -> None:
        """Generate world objects based on world size and density."""
        
        num_objetos = int(tamanho_mundo * tamanho_mundo * densidade)
        
        for _ in range(num_objetos):
            x = random.randint(0, tamanho_mundo - 1)
            y = random.randint(0, tamanho_mundo - 1)
            
            tipo_chave = random.choice(list(self.OBJETOS_PADRAO.keys()))
            config = self.OBJETOS_PADRAO[tipo_chave]
            
            obj_id = f"obj_{self.contador_id}"
            self.contador_id += 1
            
            obj = ObjetoMundo(
                id=obj_id,
                nome=config["nome"],
                tipo=config["tipo"],
                x=x,
                y=y,
                descricao=config["descricao"],
                acessivel=True,
                recompensa_interacao=config["recompensa"],
                tempo_regeneracao=config["cooldown"],
            )
            
            self.objetos_mundo[obj_id] = obj
    
    def obter_objetos_proximo(self, x: int, y: int, raio: int = 5) -> list[ObjetoMundo]:
        """Get all objects within radius of position."""
        proximos = []
        
        for obj in self.objetos_mundo.values():
            distancia = abs(obj.x - x) + abs(obj.y - y)
            if distancia <= raio:
                proximos.append(obj)
        
        return sorted(proximos, key=lambda o: abs(o.x - x) + abs(o.y - y))
    
    def interagir_objeto(self, obj_id: str) -> dict:
        """Interact with an object and return rewards."""
        
        if obj_id not in self.objetos_mundo:
            return {"sucesso": False, "mensagem": "Objeto não encontrado."}
        
        obj = self.objetos_mundo[obj_id]
        
        if not obj.pode_interagir():
            return {
                "sucesso": False,
                "mensagem": f"Este local não pode ser acessado agora. Volte depois.",
            }
        
        # Register interaction
        obj.registrar_interacao()
        self.objetos_visitados.add(obj_id)
        
        return {
            "sucesso": True,
            "nome": obj.nome,
            "descricao": obj.descricao,
            "recompensa": obj.recompensa_interacao,
            "mensagem": f"Você interagiu com {obj.nome}!",
        }
    
    def atualizar_cooldowns(self) -> None:
        """Decrease cooldowns for all objects."""
        for obj in self.objetos_mundo.values():
            if obj.tempo_regeneracao > 0:
                obj.tempo_regeneracao -= 1
    
    def obter_progresso_exploracao(self) -> dict:
        """Get exploration statistics."""
        total = len(self.objetos_mundo)
        descobertos = len(self.objetos_visitados)
        percentual = (descobertos / total * 100) if total > 0 else 0
        
        return {
            "total_objetos": total,
            "objetos_descobertos": descobertos,
            "percentual_exploracao": percentual,
        }


class SistemaPovoado:
    """Populates world with dynamic events and encounters."""
    
    def __init__(self):
        self.eventos_ativos = []
        self.encontros_chance = 0.05  # 5% chance per location per update
        
    def gerar_evento(self, x: int, y: int) -> Optional[dict]:
        """Generate a random world event at location."""
        
        if random.random() > self.encontros_chance:
            return None
        
        eventos_possiveis = [
            {
                "tipo": "comerciante",
                "nome": "Um comerciante ambulante",
                "descricao": "Um viajante que compra e vende itens.",
                "reacao": "Mercadoria para vender? Tenho ofertas especiais!",
            },
            {
                "tipo": "npc_perdido",
                "nome": "Um viajante perdido",
                "descricao": "Alguém que se perdeu no caminho.",
                "reacao": "Você sabe o caminho para... (um lugar)?",
                "quest": "Ajudar a encontrar o caminho",
            },
            {
                "tipo": "inimigo",
                "nome": "Uma criatura selvagem",
                "descricao": "Um predador territorial bloqueia seu caminho.",
                "reacao": "Um rosnado ameaçador... Luta ou fuga!",
            },
            {
                "tipo": "tesouro",
                "nome": "Achado valioso",
                "descricao": "Algo brilha entre as plantas.",
                "reacao": "Um achado fortunado!",
                "recompensa": {"ouro": random.randint(20, 100)},
            },
            {
                "tipo": "festival",
                "nome": "Preparativos de Festival",
                "descricao": "Pessoas se movimentam preparando uma celebração.",
                "reacao": "Um festival vem por aí!",
            },
        ]
        
        evento = random.choice(eventos_possiveis)
        evento["posicao"] = (x, y)
        evento["id"] = f"event_{random.randint(1000, 9999)}"
        
        return evento
    
    def gerar_patrulha_npc(self) -> dict:
        """Generate a patrol of NPCs that move through world."""
        profissoes = ["Guarda", "Caçador", "Ferreiro Itinerante", "Curandeira"]
        
        return {
            "nome": random.choice(profissoes),
            "rota": self._gerar_rota_patrulha(),
            "tempo_patrulha": random.randint(5, 15),
        }
    
    def _gerar_rota_patrulha(self) -> list[tuple[int, int]]:
        """Generate a patrol route (list of positions)."""
        rota = [(0, 0)]
        x, y = 0, 0
        
        for _ in range(random.randint(3, 8)):
            direcao = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            passos = random.randint(2, 5)
            
            for _ in range(passos):
                x += direcao[0]
                y += direcao[1]
                rota.append((x, y))
        
        return rota


class SistemaProgresso:
    """Track world progression and changes."""
    
    def __init__(self):
        self.dias_passados = 0
        self.areas_descobertas = set()
        self.eventos_completados = set()
        self.mudancas_mundo = {}
        
    def registrar_descoberta(self, area_nome: str) -> None:
        """Register discovery of new area."""
        self.areas_descobertas.add(area_nome)
    
    def registrar_evento(self, evento_id: str) -> None:
        """Register completion of event."""
        self.eventos_completados.add(evento_id)
    
    def aplicar_mudanca_mundo(self, chave: str, mudanca: dict) -> None:
        """Apply a world change (e.g., destroyed object, built structure)."""
        self.mudancas_mundo[chave] = mudanca
    
    def obter_mundo_alterado(self, x: int, y: int) -> Optional[dict]:
        """Get any world changes at this location."""
        chave = f"{x}_{y}"
        return self.mudancas_mundo.get(chave)
