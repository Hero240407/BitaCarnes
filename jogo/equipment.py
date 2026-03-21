"""Sistema de Equipamento - Armas, Armaduras e Acessórios"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class TipoItem(Enum):
    """Categorias de items"""
    CONSUMIVEL = "consumivel"
    ARMA = "arma"
    ARMADURA = "armadura"
    ACESSORIO = "acessorio"
    MATERIAL = "material"


class TipoArma(Enum):
    """Tipos de armas"""
    ESPADA = "espada"
    MACHADO = "machado"
    LANCA = "lanca"
    ARCO = "arco"
    CAJADO = "cajado"
    MARRETA = "marreta"


class TipoArmadura(Enum):
    """Tipos de armadura"""
    PEITORAL = "peitoral"
    CALCAS = "calcas"
    BOTAS = "botas"
    CAPACETE = "capacete"
    LUVAS = "luvas"
    CAPA = "capa"


class Raridade(Enum):
    """Raridade de items"""
    COMUM = "comum"
    INCOMUM = "incomum"
    RARO = "raro"
    EPICO = "epico"
    LENDARIO = "lendario"


@dataclass(slots=True)
class Propriedade:
    """Propriedade mágica de um item"""
    nome: str
    descricao: str
    atributo: str  # "ataque", "defesa", "velocidade", "vida_max", etc.
    valor: int


@dataclass(slots=True)
class Item:
    """Representa um item no inventário"""
    id: int
    nome: str
    tipo: TipoItem
    descricao: str
    raridade: Raridade
    valor_ouro: int
    peso: float  # em unidades arbitrárias
    icone: str = ""  # asset ID para ícone
    
    # Stats para items de equipamento
    ataque: int = 0
    defesa: int = 0
    
    # Propriedades especiais
    propriedades: List[Propriedade] = field(default_factory=list)
    
    # Durabilidade
    durabilidade_max: int = 100
    durabilidade_atual: int = 100
    
    # Consumíveis
    quantidade: int = 1
    quantidade_max: int = 99
    efeito_consumivel: Optional[Dict] = None
    
    def danificar(self, quantidade: int = 1):
        """Reduz durabilidade do item"""
        self.durabilidade_atual = max(0, self.durabilidade_atual - quantidade)
    
    def reparar(self, quantidade: int = -1):
        """Repara item"""
        if quantidade == -1:
            self.durabilidade_atual = self.durabilidade_max
        else:
            self.durabilidade_atual = min(self.durabilidade_max, 
                                         self.durabilidade_atual + quantidade)
    
    @property
    def esta_quebrado(self) -> bool:
        """Verifica se item está completamente quebrado"""
        return self.durabilidade_atual <= 0
    
    @property
    def percentual_durabilidade(self) -> float:
        """Retorna percentual de durabilidade"""
        return (self.durabilidade_atual / self.durabilidade_max * 100) if self.durabilidade_max > 0 else 0


class BancoDados_Items:
    """Banco de dados de items do jogo"""
    
    # ARMAS
    ESPADA_FERRUGEM = Item(
        id=1001, nome="Espada de Ferrugem",
        tipo=TipoItem.ARMA, 
        descricao="Uma espada antiga e enferrujada. De alguma forma ainda funciona.",
        raridade=Raridade.COMUM,
        valor_ouro=30,
        peso=3.0,
        ataque=3,
        icone="sword_rust"
    )
    
    ESPADA_BRONZE = Item(
        id=1002, nome="Espada de Bronze",
        tipo=TipoItem.ARMA,
        descricao="Uma boa espada feita de bronze. Básica, porém confiável.",
        raridade=Raridade.INCOMUM,
        valor_ouro=100,
        peso=3.5,
        ataque=5,
        icone="sword_bronze"
    )
    
    ESPADA_CRISTALIN = Item(
        id=1003, nome="Espada Cristalina",
        tipo=TipoItem.ARMA,
        descricao="Uma espada feita de cristal raro que brilha com luz interna.",
        raridade=Raridade.RARO,
        valor_ouro=400,
        peso=2.5,
        ataque=8,
        propriedades=[
            Propriedade("Brilho", "Emite luz suave", "iluminacao", 5)
        ],
        icone="sword_crystal"
    )
    
    MACHADO_GUERRA = Item(
        id=1004, nome="Machado de Guerra",
        tipo=TipoItem.ARMA,
        descricao="Golpes devastadores com este machado pesado.",
        raridade=Raridade.INCOMUM,
        valor_ouro=120,
        peso=5.0,
        ataque=7,
        icone="axe_war"
    )
    
    ARCO_EFELVADO = Item(
        id=1005, nome="Arco Élfico",
        tipo=TipoItem.ARMA,
        descricao="Um arco delicado feito pela mão élfos antigos.",
        raridade=Raridade.RARO,
        valor_ouro=350,
        peso=1.5,
        ataque=6,
        propriedades=[
            Propriedade("Preciso", "Acertos críticos mais frequentes", "critico", 1)
        ],
        icone="bow_elf"
    )
    
    CAJADO_MAGO = Item(
        id=1006, nome="Cajado do Mago",
        tipo=TipoItem.ARMA,
        descricao="Um cajado que amplifica poder mágico. Requer afinidade com magia.",
        raridade=Raridade.RARO,
        valor_ouro=300,
        peso=2.0,
        ataque=4,
        propriedades=[
            Propriedade("Amplificação Mágica", "Aumenta dano de feiços", "magia", 3)
        ],
        icone="staff_mage"
    )
    
    # ARMADURAS
    ARMADURA_COURO = Item(
        id=2001, nome="Armadura de Couro",
        tipo=TipoItem.ARMADURA,
        descricao="Proteção básica feita de couro trabalhado.",
        raridade=Raridade.COMUM,
        valor_ouro=50,
        peso=4.0,
        defesa=2,
        icone="armor_leather"
    )
    
    ARMADURA_FERRO = Item(
        id=2002, nome="Armadura de Ferro",
        tipo=TipoItem.ARMADURA,
        descricao="Proteção sólida de ferro. Pesada mas confiável.",
        raridade=Raridade.INCOMUM,
        valor_ouro=150,
        peso=6.0,
        defesa=4,
        icone="armor_iron"
    )
    
    ARMADURA_ACODRACAICA = Item(
        id=2003, nome="Armadura de Couro Dracônico",
        tipo=TipoItem.ARMADURA,
        descricao="Feita da pele de um dragão abatido. Extremamente rara e valiosa.",
        raridade=Raridade.LENDARIO,
        valor_ouro=1500,
        peso=3.0,
        defesa=7,
        propriedades=[
            Propriedade("Resistência ao Fogo", "Reduz dano de fogo", "fogo", 50)
        ],
        icone="armor_dragon"
    )
    
    CAPA_INVISIBILIDADE = Item(
        id=2004, nome="Capa de Invisibilidade",
        tipo=TipoItem.ARMADURA,
        descricao="Uma capa lendária que pode tornar o portador invisível por breve tempo.",
        raridade=Raridade.LENDARIO,
        valor_ouro=2000,
        peso=0.5,
        defesa=1,
        propriedades=[
            Propriedade("Invisibilidade", "Pode se tornar invisível", "magia", 10)
        ],
        icone="cloak_invisible"
    )
    
    # ACESSÓRIOS
    ANEL_VITALIDADE = Item(
        id=3001, nome="Anel de Vitalidade",
        tipo=TipoItem.ACESSORIO,
        descricao="Aumenta saúde máxima do portador.",
        raridade=Raridade.RARO,
        valor_ouro=250,
        peso=0.1,
        propriedades=[
            Propriedade("Vitalidade", "Aumenta vida máxima", "vida_max", 20)
        ],
        icone="ring_vitality"
    )
    
    ANEL_VELOCIDADE = Item(
        id=3002, nome="Anel da Velocidade",
        tipo=TipoItem.ACESSORIO,
        descricao="O portador se move e age mais rapidamente.",
        raridade=Raridade.RARO,
        valor_ouro=300,
        peso=0.1,
        propriedades=[
            Propriedade("Haste", "Aumenta velocidade", "velocidade", 2)
        ],
        icone="ring_speed"
    )
    
    AMULETO_PROTECAO = Item(
        id=3003, nome="Amuleto de Proteção",
        tipo=TipoItem.ACESSORIO,
        descricao="Um amuleto que protege o portador de dano.",
        raridade=Raridade.INCOMUM,
        valor_ouro=100,
        peso=0.2,
        defesa=2,
        icone="amulet_protection"
    )
    
    # CONSUMÍVEIS
    POCAO_VIDA = Item(
        id=4001, nome="Poção de Vida",
        tipo=TipoItem.CONSUMIVEL,
        descricao="Restaura 50 pontos de vida quando consumida.",
        raridade=Raridade.COMUM,
        valor_ouro=25,
        peso=0.2,
        quantidade=1,
        quantidade_max=99,
        efeito_consumivel={"tipo": "cura", "valor": 50},
        icone="potion_red"
    )
    
    POCAO_MANA = Item(
        id=4002, nome="Poção de Mana",
        tipo=TipoItem.CONSUMIVEL,
        descricao="Restaura 30 pontos de mana quando consumida.",
        raridade=Raridade.COMUM,
        valor_ouro=20,
        peso=0.2,
        quantidade=1,
        quantidade_max=99,
        efeito_consumivel={"tipo": "mana", "valor": 30},
        icone="potion_blue"
    )
    
    ELIXIR_PODER = Item(
        id=4003, nome="Elixir de Poder",
        tipo=TipoItem.CONSUMIVEL,
        descricao="Aumenta ataque em 50% por 5 minutos.",
        raridade=Raridade.RARO,
        valor_ouro=150,
        peso=0.2,
        quantidade=1,
        quantidade_max=10,
        efeito_consumivel={"tipo": "buff", "atributo": "ataque", "valor": 0.5, "duracao": 300},
        icone="potion_green"
    )
    
    # MATERIAIS
    OSSO_PERFEITO = Item(
        id=5001, nome="Osso Perfeito",
        tipo=TipoItem.MATERIAL,
        descricao="Um osso puro perfeito para crafting.",
        raridade=Raridade.INCOMUM,
        valor_ouro=30,
        peso=0.5,
        quantidade=1,
        quantidade_max=99,
        icone="bone_perfect"
    )
    
    CRISTAL_MAGICO = Item(
        id=5002, nome="Cristal Mágico",
        tipo=TipoItem.MATERIAL,
        descricao="Um cristal que irradia energia mágica pura.",
        raridade=Raridade.RARO,
        valor_ouro=100,
        peso=0.8,
        quantidade=1,
        quantidade_max=20,
        icone="crystal_magic"
    )
    
    ESCAMA_DRAGAO = Item(
        id=5003, nome="Escama de Dragão",
        tipo=TipoItem.MATERIAL,
        descricao="Escama de um dragão antigo. Matéria-prima rara e valiosa.",
        raridade=Raridade.LENDARIO,
        valor_ouro=500,
        peso=1.0,
        quantidade=1,
        quantidade_max=5,
        icone="scale_dragon"
    )
    
    @classmethod
    def obter_todos_items(cls) -> Dict[int, Item]:
        """Retorna todos os items disponíveis"""
        # Coleta todos os atributos que são Items
        items = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Item):
                items[attr.id] = attr
        return items


class Equipamento:
    """Representa o equipamento atual do personagem"""
    
    def __init__(self):
        self.arma: Optional[Item] = None
        self.armadura: Optional[Item] = None
        self.acessorios: List[Item] = []  # Até 3 acessórios
        self.amuleto: Optional[Item] = None
    
    @property
    def bônus_ataque(self) -> int:
        """Calcula bônus total de ataque"""
        total = 0
        if self.arma:
            total += self.arma.ataque
        for prop in self._get_todas_propriedades():
            if prop.atributo == "ataque":
                total += prop.valor
        return total
    
    @property
    def bônus_defesa(self) -> int:
        """Calcula bônus total de defesa"""
        total = 0
        if self.armadura:
            total += self.armadura.defesa
        if self.amuleto:
            total += self.amuleto.defesa
        for prop in self._get_todas_propriedades():
            if prop.atributo == "defesa":
                total += prop.valor
        return total
    
    def _get_todas_propriedades(self) -> List[Propriedade]:
        """Coleta todas as propriedades do equipamento"""
        props = []
        for item in [self.arma, self.armadura, self.amuleto] + self.acessorios:
            if item:
                props.extend(item.propriedades)
        return props
    
    def equipar_arma(self, item: Item) -> bool:
        """Equipa uma arma"""
        if item.tipo == TipoItem.ARMA:
            self.arma = item
            return True
        return False
    
    def equipar_armadura(self, item: Item) -> bool:
        """Equipa uma armadura"""
        if item.tipo == TipoItem.ARMADURA:
            self.armadura = item
            return True
        return False
    
    def adicionar_acessorio(self, item: Item) -> bool:
        """Adiciona um acessório (máximo 3)"""
        if item.tipo == TipoItem.ACESSORIO and len(self.acessorios) < 3:
            self.acessorios.append(item)
            return True
        return False
    
    def remover_acessorio(self, index: int) -> bool:
        """Remove um acessório"""
        if 0 <= index < len(self.acessorios):
            del self.acessorios[index]
            return True
        return False
    
    def obter_peso_total(self) -> float:
        """Calcula peso total de equipamento"""
        peso = 0
        for item in [self.arma, self.armadura, self.amuleto] + self.acessorios:
            if item:
                peso += item.peso
        return peso
