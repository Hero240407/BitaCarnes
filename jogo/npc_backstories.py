"""Sistema de Histórias de NPCs Geradas por IA"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
import random


class ArchetipoNPC(Enum):
    """Arquetipos de NPCs"""
    GUERREIRO = "guerreiro"
    MAGO = "mago"
    LADRÃO = "ladrão"
    CLÉRIGO = "clérigo"
    MERCADOR = "mercador"
    BARDO = "bardo"
    CAÇADOR = "caçador"
    CAMPONÊS = "camponês"
    NOBRE = "nobre"
    EREMITA = "eremita"


class TraumaMemoria(Enum):
    """Traumas ou eventos marcantes no passado"""
    PERDA_FAMILIAR = "perda_familiar"
    GUERRA = "guerra"
    ESCRAVIDÃO = "escravidão"
    MALDIÇÃO = "maldição"
    AMOR_PERDIDO = "amor_perdido"
    EXÍLIO = "exílio"
    INJUSTIÇA = "injustiça"
    NENHUM = "nenhum"


@dataclass(slots=True)
class HistoriaBackstory:
    """Define a história de vida de um NPC"""
    nome_npc: str
    arquetipo: ArchetipoNPC
    idade_natal: int
    origem_lugar: str
    
    # Personalidade construída
    quem_e: str  # Descrição: "Você é um..."
    por_que_aqui: str  # Por que estão neste lugar
    objetivo_vida: str  # O que quer alcançar
    
    # Histórico de vida
    evento_marcante: str  # Um evento que moldeou sua vida
    trauma: TraumaMemoria  # Ferida emocional (se houver)
    sonho_segredo: str  # Sonho que nunca contaria
    
    # Relacionamentos
    npc_relacionado: Optional[str] = None  # Outro NPC com quem tem conexão
    tipo_relacao: str = "amigo"  # amigo, rival, inimigo, amor
    
    # Segredo
    segredo_escondido: str = ""  # Algo que não quer que saibam
    perigo_segredo: bool = False  # Se revelado causa problemas
    
    # Qualidades
    virtudes: List[str] = field(default_factory=list)  # honesto, corajoso, sábio
    vícios: List[str] = field(default_factory=list)  # ambicioso, covarde, guloso
    
    @property
    def relato_vida(self) -> str:
        """Retorna um relato breve da vida do NPC"""
        texto = f"{self.quem_e}.\\n"
        texto += f"Nascido em {self.origem_lugar}, aos {self.idade_natal} anos.\\n"
        texto += f"Aqui por: {self.por_que_aqui}.\\n"
        texto += f"Objetivo: {self.objetivo_vida}.\\n"
        if self.trauma != TraumaMemoria.NENHUM:
            texto += f"Trauma: {self.evento_marcante}.\\n"
        return texto


class GeradorBackstoryIA:
    """
    Gera histórias de NPCs usando templates estruturados.
    Em um jogo completo, isso seria integrado com Ollama para geração real de IA.
    """
    
    # Templates para geração estruturada
    TEMPLATES_QUEM_E = {
        ArchetipoNPC.GUERREIRO: [
            "Você é um guerreiro endurecido pelas batalhas, marcado pelas cicatrizes de inúmeros conflitos",
            "Você é um soldado disciplinado, treinado desde jovem para defender o reino",
            "Você é um mercenário que vende seus talentos de combate ao melhor pagador",
            "Você é um gladiador que escapou da arena em busca de liberdade"
        ],
        ArchetipoNPC.MAGO: [
            "Você é um mago recluso, dedicado ao estudo das artes arcanas",
            "Você é um feiticeiro que descobriu poderes naturais através da conexão com a magia",
            "Você é um sábio que buscou conhecimento mágico em torreões ancestrais",
            "Você é um bruxo banido por sua comunidade por práticas proibidas"
        ],
        ArchetipoNPC.LADRÃO: [
            "Você é um ladrão talentoso que sobrevive roubando dos ricos",
            "Você é um espião a serviço de forças ocultas",
            "Você é um criminoso reformado tentando deixar o passado para trás",
            "Você é um ninja que ainda segue os códigos da sombra"
        ],
        ArchetipoNPC.MERCADOR: [
            "Você é um mercador astuto que sabe o valor de tudo",
            "Você é um traficante que move mercadorias raras e perigosas",
            "Você é um negociante que construiu império do zero",
            "Você é um cambista que conhece o preço de favores"
        ],
        ArchetipoNPC.CLÉRIGO: [
            "Você é um sacerdote devoto de uma divindade",
            "Você é um monge que seguiu votos de castidade e pobreza",
            "Você é um paladino que defende os fidalgos de seu deus",
            "Você é um herege que rejeita as doutrinas oficiais da igreja"
        ]
    }
    
    TEMPLATES_ORIGEM = [
        "uma aldeia pacífica nas pradarias",
        "uma cidade portuária corrupta",
        "um reino montanhoso isolado",
        "um deserto hostil e árido",
        "uma universidade mágica",
        "uma cripta subterrânea",
        "um castelo nobre",
        "uma floresta selvagem",
        "um mosteiro sagrado"
    ]
    
    TEMPLATES_POR_QUE_AQUI = {
        ArchetipoNPC.GUERREIRO: [
            "fugiu de uma guerra que perdeu tudo",
            "atrado por rumores de batalhas épicas",
            "em busca de redenção por crimes passados"
        ],
        ArchetipoNPC.MAGO: [
            "procurando artefatos mágicos antigos",
            "investigando atividades mágicas suspeitas",
            "escondendo-se de caçadores de bruxas"
        ],
        ArchetipoNPC.MERCADOR: [
            "aberta uma filial de seus negócios",
            "fugindo de dívidas",
            "seguindo uma oportunidade de lucro"
        ]
    }
    
    EVENTOS_MARCANTES = [
        "perdeu sua família numa tragédia",
        "assistiu à destruição de sua cidade natal",
        "foi traído por alguém que amava",
        "recebeu uma maldição sobrenatu",
        "sobreviveu a uma execução",
        "ganhou poderes em circunstâncias estranhas",
        "encontrou um antigo artefato que mudou tudo",
        "foi escolhido por uma divindade",
        "descobriu um segredo capaz de derrubar reinos"
    ]
    
    VIRTUDES = [
        "honesto", "corajoso", "compassivo", "sábio", "leal",
        "justo", "diligente", "humilde", "esperançoso"
    ]
    
    VÍCIOS = [
        "ambicioso", "guloso", "covarde", "preguiçoso", 
        "invejoso", "irado", "luxurioso", "ganancioso"
    ]
    
    SONHOS_SECRETOS = [
        "Quer vencer uma guerra pessoal contra antigo inimigo",
        "Sonha em encontrar amor verdadeiro",
        "Espera ganhar riqueza suficiente para nunca mais sofrer",
        "Busca redenção por erros passados",
        "Quer se tornar imortal",
        "Planeja reunir uma família dispersa",
        "Sonha em conquistar poder político",
        "Busca conhecimento secreto há séculos perdido",
        "Quer se livrar de uma maldição"
    ]
    
    @staticmethod
    def gerar_backstory(npc_nome: str, arquetipo: ArchetipoNPC, 
                       idade: int) -> HistoriaBackstory:
        """Gera uma backstory completa para um NPC usando templates"""
        
        quem_e = random.choice(
            GeradorBackstoryIA.TEMPLATES_QUEM_E.get(arquetipo, ["Você é alguém misterioso"])
        )
        
        origem = random.choice(GeradorBackstoryIA.TEMPLATES_ORIGEM)
        
        por_que = random.choice(
            GeradorBackstoryIA.TEMPLATES_POR_QUE_AQUI.get(arquetipo, 
                ["simplesmente estava de passagem"])
        )
        
        evento = random.choice(GeradorBackstoryIA.EVENTOS_MARCANTES)
        
        trauma = random.choice(list(TraumaMemoria))
        
        sonho = random.choice(GeradorBackstoryIA.SONHOS_SECRETOS)
        
        virtudes = random.sample(GeradorBackstoryIA.VIRTUDES, k=random.randint(1, 3))
        vicios = random.sample(GeradorBackstoryIA.VÍCIOS, k=random.randint(1, 2))
        
        # Objetivo de vida baseado no arquetipo
        objetivo_map = {
            ArchetipoNPC.GUERREIRO: "Honrar sua linhagem através de proezas guerreiras",
            ArchetipoNPC.MAGO: "Desvendar os mistérios das artes arcanas",
            ArchetipoNPC.LADRÃO: "Acumular riqueza suficiente para desaparecer",
            ArchetipoNPC.CLÉRIGO: "Servir sua religião e espalhar suas crenças",
            ArchetipoNPC.MERCADOR: "Construir um império comercial",
            ArchetipoNPC.BARDO: "Tornar-se lendário como trovador",
            ArchetipoNPC.CAÇADOR: "Abater as criaturas mais perigosas do mundo",
            ArchetipoNPC.CAMPONÊS: "Encontrar paz e estabilidade",
            ArchetipoNPC.NOBRE: "Restaurar a glória de sua casa",
            ArchetipoNPC.EREMITA: "Alcançar iluminação espiritual"
        }
        objetivo = objetivo_map.get(arquetipo, "Viver uma vida significativa")
        
        return HistoriaBackstory(
            nome_npc=npc_nome,
            arquetipo=arquetipo,
            idade_natal=idade,
            origem_lugar=origem,
            quem_e=quem_e,
            por_que_aqui=por_que,
            objetivo_vida=objetivo,
            evento_marcante=evento,
            trauma=trauma,
            sonho_segredo=sonho,
            virtudes=virtudes,
            vícios=vicios
        )
    
    @staticmethod
    def gerar_com_ollama(npc_nome: str, contexto: Dict) -> Optional[HistoriaBackstory]:
        """
        Tenta gerar backstory com Ollama para mais originalidade.
        Se falhar, faz fallback para template estruturado.
        """
        # TODO: Implementar integração com Ollama
        # Para agora, retorna None para usar fallback
        return None
    
    @staticmethod
    def gerar_diálogo_contextualizado(backstory: HistoriaBackstory, 
                                      tipo_conversa: str) -> str:
        """Gera um diálogo baseado na backstory do NPC"""
        
        diálogos_saudacao = [
            f"Olá... você é novo por aqui?",
            f"Que traz você a este lugar desolado?",
            f"Hm, mais um viajante. Que irônico.",
            f"Bem-vindo. Ou talvez não, quem sabe?"
        ]
        
        diálogos_passado = [
            f"Prefiro não falar sobre meu passado. Dói ainda.",
            f"Fiz coisas das quais não estou orgulhoso.",
            f"Meu passado me assombra todos os dias.",
            f"Parece que não importa o quanto eu corra, ele sempre me alcança."
        ]
        
        if tipo_conversa == "saudacao":
            return random.choice(diálogos_saudacao)
        elif tipo_conversa == "passado":
            return random.choice(diálogos_passado)
        else:
            return f"Hmm, que pergunta interessante..."


class SistemaBackstories:
    """Gerencia todas as backstories de NPCs no mundo"""
    
    def __init__(self):
        self.backstories: Dict[str, HistoriaBackstory] = {}
    
    def adicionar_npc(self, npc_nome: str, arquetipo: ArchetipoNPC, 
                     idade: int):
        """Gera e adiciona backstory de um NPC"""
        backstory = GeradorBackstoryIA.gerar_backstory(npc_nome, arquetipo, idade)
        self.backstories[npc_nome] = backstory
    
    def obter_backstory(self, npc_nome: str) -> Optional[HistoriaBackstory]:
        """Retorna backstory de um NPC"""
        return self.backstories.get(npc_nome)
    
    def obter_diálogo_contextualizado(self, npc_nome: str, 
                                     tipo: str = "saudacao") -> str:
        """Retorna diálogo contextualizado de um NPC"""
        backstory = self.obter_backstory(npc_nome)
        if backstory:
            return GeradorBackstoryIA.gerar_diálogo_contextualizado(backstory, tipo)
        return "Hmm."
