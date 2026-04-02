"""
Sistema avançado de geração de backstories complexas para o jogador.
Integra IA para criar histórias ricas em fantasia, baseadas em Anime, Livros e Isekai.
A história impacta nas relações com NPCs e na escolha do spawnpoint.
"""

import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

from .servicos import chamar_ollama_pesado, chamar_ollama_leve


class OrigensComplexas(Enum):
    """Origens complexas para personagens - usadas como base para IA expandir"""
    DESCENDENTE_MESTRES = "Descendente de uma linhagem de mestres esquecida pelo tempo"
    ABANDONADO_SANTUARIO = "Abandonado em um santuário antigo e criado pelos sacerdotes"
    SOBREVIVENTE_APOCALIPSE = "Único sobrevivente de um cataclismo que destruiu sua terra"
    NASCIDO_PROFECIA = "Nascido sob uma profecia antiga, marcado pelo destino"
    FILHO_DUAS_MUNDOS = "Filho de dois mundos - um humano e outro mágico"
    CRIADO_MAGOS = "Criado por uma ordem de magos como experimento arcano"
    FUGITIVO_NOBREZA = "Fugitivo da nobreza corrupt com identidade oculta"
    CRIANCA_SELVAS = "Criança criada entre as selvas selvagens por druidas"
    REENCARNACAO = "Possivelmente a reencarnação de um herói antigo"
    FORSAKEN_MAGIA = "Forsaken pela magia e rejeitado pelo seu povo original"


@dataclass(slots=True)
class BackstoryGerada:
    """Representa uma backstory completa gerada para o jogador"""
    idade: int
    origem_base: str
    origem_expandida: str  # Origem complexa gerada por IA
    nome: str
    backstory_completa: str  # 10-15 linhas de história complexa
    motivacao_principal: str
    segredo: str
    ponto_fraco: str
    habilidade_especial: str
    conexoes_npc: Dict[str, str]  # {"tipo_npc": "descrição da conexão"}
    spawnpoint_ideal: tuple[int, int]  # (x, y) coordenadas no mundo
    bioma_origem: str  # Bioma onde a história começou


class GeradorBackstoryAvancado:
    """Gera backstories complexas e coerentes para o jogador usando IA pesada"""
    
    # Referências de fantasias e isekai para inspirar a IA
    REFERENCIAS_FANTASIAS = [
        "As Aventuras de Conan em terras hostis",
        "O Sistema de Classe de Re:Zero",
        "As profundezas de conhecimento de Harry Potter",
        "A magia visceral de Fullmetal Alchemist",
        "As linhagens de Game of Thrones",
        "Os poderes latentes de My Hero Academia",
        "As vidas passadas de Fate series",
        "Jujutsu Kaisen com maldições e pactos",
        "A morte como moeda de Attack on Titan",
        "Isekai Quartet com múltiplos mundos colidindo",
        "Sword Art Online com limite entre realidade",
        "Tower of God com mistérios em camadas",
        "Solo Leveling com despertar de poderes",
        "Shadow and Bone com mágica como divisão",
    ]
    
    BIOMAS_DISPONIVEIS = [
        ("floresta", "uma floresta antiga e mística"),
        ("montanha", "picos de montanhas isoladas"),
        ("costa", "terras litorâneas ventosas"),
        ("deserto", "areias áridas e primitivas"),
        ("cidade", "ruínas de uma cidade esquecida"),
        ("caverna", "cavernas profundas e escuras"),
        ("rio", "junto a um rio sagrado"),
        ("templo", "um templo antigo de pedra"),
    ]
    
    def __init__(self):
        pass
    
    def gerar_idade_personalizada(self, 
                                  tipo_personagem: str = "heroi") -> int:
        """
        Gera idade apropriada para o tipo de personagem.
        
        Args:
            tipo_personagem: "heroi", "mago", "guerreiro", etc.
            
        Returns:
            Idade do personagem (9-35 para heróis, variado para outros)
        """
        if tipo_personagem == "heroi":
            # Mais comum entre 16-28 (início da jornada)
            if random.random() < 0.4:
                return random.randint(16, 22)
            elif random.random() < 0.4:
                return random.randint(23, 28)
            else:
                return random.randint(9, 35)
        
        # Para outros tipos, mais liberdade
        return random.randint(12, 60)
    
    def gerar_origem_complexa_ai(self, idade: int) -> str:
        """
        Gera uma origem complexa e coerente usando IA, baseada na idade.
        
        Args:
            idade: Idade do personagem
            
        Returns:
            String descrevendo a origem complexa
        """
        origem_base = random.choice([e.value for e in OrigensComplexas])
        referencia = random.choice(self.REFERENCIAS_FANTASIAS)
        
        prompt = f"""Você é um escritor de narrativas épicas de fantasia e isekai.

Baseado na seguinte origem base:
"{origem_base}"

E inspirado por: {referencia}

Gere uma ORIGEM COMPLEXA E COERENTE para um personagem com {idade} anos que:
1. Explique como o personagem chegou a idade {idade} com essa origem
2. Inclua eventos traumáticos, maravilhosos ou formadores
3. Mostre como a idade influenciou sua compreensão do mundo
4. Mencione criadores, tutores ou eventos-chave
5. Seja específica e narrativa (3-4 frases)
6. Use referências de fantasia apropriadas

Responda APENAS com a descrição de origem, sem explicações extras:"""
        
        resposta = chamar_ollama_pesado(prompt, timeout=20, temperature=0.8)
        
        if not resposta:
            return f"{origem_base}. Aos {idade} anos, ainda carregam essa marca em suas cicatrizes e memórias."
        
        return resposta.strip()
    
    def gerar_nome_pela_historia(self, 
                                 origem: str, 
                                 idade: int) -> str:
        """
        Gera um nome apropriado baseado na origem e história do personagem.
        
        Args:
            origem: Descrição da origem do personagem
            idade: Idade do personagem
            
        Returns:
            Nome do personagem
        """
        prompt = f"""Você cria nomes para personagens de fantasia épica.

Origem do personagem: {origem}
Idade: {idade} anos

Gere UM NOME apropriado que:
1. Reflita a origem e história do personagem
2. Seja memorável e épico
3. Se apropriado, mostre que foi dado por:
   - Seus pais (soe natural)
   - Monges/padres (soe sagrado)
   - Tutores (soe marcante)
   - Ele mesmo (soe rebelde se abandonado)
4. Máximo 20 caracteres
5. Em português ou com sotaque de fantasia

Se foi abandonado sem nome até alguém encontrá-lo, explique quem o nomeou.

Responda APENAS com o nome e um breve contexto (1 frase):"""
        
        resposta = chamar_ollama_pesado(prompt, timeout=15, temperature=0.7)
        
        if not resposta:
            # Fallback: gerar nome simples
            nomes = ["Kael", "Sora", "Eron", "Iris", "Mika", "Toren", "Lira", "Vex"]
            return random.choice(nomes)
        
        # Extrair primeiro nome da resposta
        linhas = resposta.split('\n')
        nome = linhas[0].strip().split()[0]  # Pega primeira palavra
        
        # Limpar caracteres inválidos
        nome = re.sub(r'[^a-zA-Zàáâãäèéêëìíîïòóôõöùúûü]', '', nome)
        
        return nome[:20] if nome else "Herói"
    
    def gerar_backstory_completa(self,
                                 nome: str,
                                 idade: int,
                                 origem: str) -> Dict[str, str]:
        """
        Gera a backstory completa e complexa do personagem usando IA pesada.
        
        Args:
            nome: Nome do personagem
            idade: Idade do personagem
            origem: Descrição da origem
            
        Returns:
            Dicionário com backstory_completa, motivacao, segredo, ponto_fraco, habilidade_especial
        """
        referencia = random.choice(self.REFERENCIAS_FANTASIAS)
        
        prompt = f"""Você é um autor épico de histórias de fantasia e isekai como {referencia}.

PERSONAGEM:
- Nome: {nome}
- Idade: {idade} anos
- Origem: {origem}

Gere a BACKSTORY COMPLETA deste personagem que:
1. Narre sua vida desde nascimento até idade {idade}
2. Inclua eventos traumáticos, alegres, mágicos e formadores
3. Mostre motivações, sonhos e segredos ocultos
4. Tenha 10-15 linhas detalhadas e coerentes
5. Explique por que começaria a jogar AGORA neste mundo
6. Mostre um ponto fraco emocional e uma habilidade especial
7. Seja épica, narrativa e memorável
8. Use linguagem dramática apropriada para fantasia

Responda em JSON válido APENAS (sem ```json, sem explicação):
{{
    "backstory_completa": "10-15 linhas narrando a vida até agora...",
    "motivacao_principal": "Por que começar essa jornada agora",
    "segredo": "Um segredo oculto que ninguém deve saber",
    "ponto_fraco": "Fraqueza emocional ou física",
    "habilidade_especial": "Uma habilidade especial ou conhecimento único"
}}"""
        
        resposta = chamar_ollama_pesado(prompt, timeout=30, temperature=0.6)
        
        if not resposta:
            return self._backstory_fallback(nome, idade, origem)
        
        try:
            resposta = resposta.strip()
            if resposta.startswith("```json"):
                resposta = resposta[7:]
            if resposta.startswith("```"):
                resposta = resposta[3:]
            if resposta.endswith("```"):
                resposta = resposta[:-3]
            
            dados = json.loads(resposta.strip())
            
            campos_obrigatorios = ["backstory_completa", "motivacao_principal", "segredo", "ponto_fraco", "habilidade_especial"]
            if not all(c in dados for c in campos_obrigatorios):
                return self._backstory_fallback(nome, idade, origem)
            
            return dados
            
        except json.JSONDecodeError:
            return self._backstory_fallback(nome, idade, origem)
    
    def definir_spawnpoint_ideal(self,
                                origen: str,
                                backstory: str,
                                idade: int,
                                mundo_tamanho: int = 128) -> tuple[int, int]:
        """
        Define o melhor spawnpoint baseado na história do personagem.
        
        Args:
            origen: Origem do personagem
            backstory: Backstory completa
            idade: Idade atual
            mundo_tamanho: Tamanho do grid do mundo
            
        Returns:
            Tupla (x, y) com coordenadas ideais para spawn
        """
        # Extrair contexto da história para IA decidir melhor bioma
        prompt = f"""Você analisa histórias para encontrar o melhor ponto de partida.

HISTÓRIA DO PERSONAGEM:
Origem: {origen}
Backstory: {backstory}
Idade: {idade} anos

Baseado nessa história, qual seria o melhor BIOMA para começar?
Escolha entre: floresta, montanha, costa, deserto, cidade, caverna, rio, templo

Explique em 1 frase por que esse bioma é ideal para seguir nessa jornada.

Responda APENAS com: BIOMA: [escolha]
Motivo: [1 frase]"""
        
        resposta = chamar_ollama_leve(prompt, timeout=15, temperature=0.6)
        
        bioma_escolhido = "floresta"  # Padrão
        if resposta and "BIOMA:" in resposta:
            try:
                linhas = resposta.split('\n')
                linha_bioma = [l for l in linhas if "BIOMA:" in l][0]
                bioma_list = [b[0] for b in self.BIOMAS_DISPONIVEIS]
                for bioma in bioma_list:
                    if bioma.lower() in linha_bioma.lower():
                        bioma_escolhido = bioma
                        break
            except:
                pass
        
        # Gerar coordenadas aleatórias no bioma (será refino mais tarde no mundo)
        # Por agora, retornar centrado com pequeno offset
        centro = mundo_tamanho // 2
        offset = random.randint(-10, 10)
        return (centro + offset, centro + offset)
    
    def gerar_conexoes_npc(self,
                           backstory: str,
                           nome: str,
                           idade: int) -> Dict[str, str]:
        """
        Gera conexões potenciais entre o jogador e tipos de NPCs baseado na história.
        
        Args:
            backstory: Backstory completa do personagem
            nome: Nome do personagem
            idade: Idade do personagem
            
        Returns:
            Dicionário mapeando tipos de NPC para tipos de conexão
        """
        tipos_npc = ["guerreiro", "mago", "mercador", "sacerdote", "bardo", "nobre", "camponês", "eremita"]
        
        prompt = f"""Você previsualiza relacionamentos em uma história de fantasia.

PERSONAGEM: {nome} ({idade} anos)
BACKSTORY: {backstory}

Para cada tipo de NPC abaixo, qual seria a conexão natural com {nome}?
(Se nenhuma conexão óbvia, deixe em branco)

Tipos: {', '.join(tipos_npc)}

Para CADA tipo, responda em 1 frase:
- Se seria amigo, rival, inimigo, mentor, estudante, familiar, etc.
- Por que baseado na história

Responda em formato:
guerreiro: [tipo de conexão]
mago: [tipo de conexão]
etc."""
        
        resposta = chamar_ollama_leve(prompt, timeout=15, temperature=0.5)
        
        conexoes = {}
        if resposta:
            for linha in resposta.split('\n'):
                if ':' in linha:
                    tipo, descrição = linha.split(':', 1)
                    tipo = tipo.strip().lower()
                    if tipo in tipos_npc and descrição.strip():
                        conexoes[tipo] = descrição.strip()[:80]
        
        return conexoes
    
    def gerar_backstory_completa_personagem(self,
                                           nome_forcado: Optional[str] = None) -> BackstoryGerada:
        """
        Pipeline completo: gera idade → origem → nome → backstory → conexões → spawnpoint
        
        Args:
            nome_forcado: Se fornecido, usar este nome ao invés de gerar
            
        Returns:
            Objeto BackstoryGerada com história completa
        """
        # Passo 1: Gerar idade
        idade = self.gerar_idade_personalizada()
        print(f"[BackstoryGenerator] Idade gerada: {idade} anos")
        
        # Passo 2: Gerar origem complexa
        origem_expandida = self.gerar_origem_complexa_ai(idade)
        print(f"[BackstoryGenerator] Origem gerada: {origem_expandida[:80]}...")
        
        # Passo 3: Gerar nome
        nome = nome_forcado or self.gerar_nome_pela_historia(origem_expandida, idade)
        print(f"[BackstoryGenerator] Nome gerado: {nome}")
        
        # Passo 4: Gerar backstory completa
        backstory_data = self.gerar_backstory_completa(nome, idade, origem_expandida)
        print(f"[BackstoryGenerator] Backstory gerada com {len(backstory_data.get('backstory_completa', ''))} caracteres")
        
        # Passo 5: Definir spawnpoint ideal
        spawnpoint = self.definir_spawnpoint_ideal(
            origem_expandida,
            backstory_data.get('backstory_completa', ''),
            idade
        )
        print(f"[BackstoryGenerator] Spawnpoint ideal: {spawnpoint}")
        
        # Passo 6: Gerar conexões com NPCs
        conexoes_npc = self.gerar_conexoes_npc(
            backstory_data.get('backstory_completa', ''),
            nome,
            idade
        )
        print(f"[BackstoryGenerator] Conexões NPC geradas: {len(conexoes_npc)} tipos")
        
        # Passo 7: Escolher bioma aleatório (será refino)
        bioma_origem = random.choice([b[0] for b in self.BIOMAS_DISPONIVEIS])
        
        return BackstoryGerada(
            idade=idade,
            origem_base=random.choice([e.value for e in OrigensComplexas]),
            origem_expandida=origem_expandida,
            nome=nome,
            backstory_completa=backstory_data.get('backstory_completa', 'Sem história'),
            motivacao_principal=backstory_data.get('motivacao_principal', 'Sobreviver'),
            segredo=backstory_data.get('segredo', 'Oculto'),
            ponto_fraco=backstory_data.get('ponto_fraco', 'Desconhecido'),
            habilidade_especial=backstory_data.get('habilidade_especial', 'Nenhuma'),
            conexoes_npc=conexoes_npc,
            spawnpoint_ideal=spawnpoint,
            bioma_origem=bioma_origem,
        )
    
    def _backstory_fallback(self, nome: str, idade: int, origem: str) -> Dict[str, str]:
        """Fallback para quando IA falha na geração de backstory"""
        return {
            "backstory_completa": f"{nome} nasceu sob circunstâncias especiais descritas por: {origem}. Aos {idade} anos, carrega as marcas dessa vida, com cicatrizes visíveis e invisíveis. Cada dia trouxe lições, perdas e vitórias que moldaram seu caráter. Agora, em idade de buscar seu próprio destino, {nome} sente o chamado de uma jornada maior, onde seus talentos únicos finalmente encontrarão propósito no vasto mundo que o aguarda.",
            "motivacao_principal": f"Provar que a própria existência tem significado, apesar das circunstâncias de seu nascimento",
            "segredo": f"Ainda questiona se realmente merecia sobreviver quando tantos não sobreviveram",
            "ponto_fraco": f"A sensação de não pertencer completamente a nenhum lugar",
            "habilidade_especial": f"Capacidade de sobrevivência e intuição aguçada sobre perigos",
        }


def extrair_resumo_backstory(backstory_completa: str, max_linhas: int = 5) -> str:
    """
    Extrai um resumo curto (máx 5 linhas) da backstory completa para exibir na UI.
    
    Args:
        backstory_completa: Texto completo da backstory
        max_linhas: Máximo de linhas para o resumo
        
    Returns:
        Resumo formatado
    """
    linhas = backstory_completa.split('\n')
    # Pegar primeiras N linhas
    resumo_linhas = linhas[:max_linhas]
    # Se for muito longo, truncar
    resumo = '\n'.join(resumo_linhas)
    if len(resumo) > 500:
        resumo = resumo[:497] + "..."
    return resumo


def gerar_impacto_relacoes_npc(backstory_dados: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Gera impactos de relações com NPCs baseado na backstory do personagem.
    
    Args:
        backstory_dados: Dicionário com dados da backstory gerada
        
    Returns:
        Dicionário mapeando tipo_npc -> {moralidade_impacto, descrição}
    """
    impactos = {}
    
    conexoes_npc = backstory_dados.get("conexoes_npc", {})
    habilidade = backstory_dados.get("habilidade_especial", "").lower()
    segredo = backstory_dados.get("segredo", "").lower()
    ponto_fraco = backstory_dados.get("ponto_fraco", "").lower()
    origem = backstory_dados.get("origem_expandida", "").lower()
    
    # Mapear conexões para impactos
    for tipo_npc, conexao in conexoes_npc.items():
        if not conexao:
            continue
        
        conexao_lower = str(conexao).lower()
        
        if "mentor" in conexao_lower or "profesor" in conexao_lower or "instrutor" in conexao_lower:
            impactos[tipo_npc] = {
                "moralidade_inicial": 15,
                "descrição": f"Reconhecem você como alguém que buscou conhecimento: {conexao}"
            }
        elif "amigo" in conexao_lower or "aliado" in conexao_lower:
            impactos[tipo_npc] = {
                "moralidade_inicial": 8,
                "descrição": f"Compartilham uma conexão natural: {conexao}"
            }
        elif "rival" in conexao_lower or "competidor" in conexao_lower:
            impactos[tipo_npc] = {
                "moralidade_inicial": -5,
                "descrição": f"Há tensão entre vocês: {conexao}"
            }
        elif "inimigo" in conexao_lower:
            impactos[tipo_npc] = {
                "moralidade_inicial": -15,
                "descrição": f"Existe animosidade: {conexao}"
            }
        elif "familiar" in conexao_lower or "parente" in conexao_lower:
            impactos[tipo_npc] = {
                "moralidade_inicial": 10,
                "descrição": f"Existe laço familiar: {conexao}"
            }
        else:
            # Impacto neutro com descrição genérica
            impactos[tipo_npc] = {
                "moralidade_inicial": 0,
                "descrição": conexao[:80]
            }
    
    # Se não houver conexões específicas, gerar impacto genérico baseado em características
    if not impactos:
        if "guerreiro" in habilidade or "combate" in habilidade or "luta" in habilidade:
            impactos["guerreiro"] = {
                "moralidade_inicial": 5,
                "descrição": "Respeitam sua experiência em combate"
            }
        
        if "mago" in habilidade or "magia" in habilidade or "arcano" in habilidade:
            impactos["mago"] = {
                "moralidade_inicial": 8,
                "descrição": "Reconhecem seu conhecimento mágico"
            }
        
        if "roubou" in segredo or "roubo" in segredo or "ladrão" in origem:
            impactos["guardião"] = {
                "moralidade_inicial": -8,
                "descrição": "Desconfiança devido ao seu passado"
            }
            impactos["mercador"] = {
                "moralidade_inicial": -10,
                "descrição": "Preocupação com seus antecedentes"
            }
    
    return impactos


def aplicar_impactos_backstory_ao_mundo(mundo, backstory_dados: Dict[str, Any]) -> None:
    """
    Aplica os impactos da backstory às relações de NPCs no mundo.
    
    Args:
        mundo: Objeto Mundo
        backstory_dados: Dicionário com dados da backstory
    """
    try:
        # Tentar importar gerenciador de relações se disponível
        from .npc_relations import GerenciadorRelacoes
        
        impactos = gerar_impacto_relacoes_npc(backstory_dados)
        
        # Armazenar impactos nos dados do mundo para aplicar ao carregar
        if not hasattr(mundo, "impactos_backstory"):
            mundo.impactos_backstory = {}
        
        mundo.impactos_backstory = impactos
        
        print(f"[BackstoryImpact] Impactos da backstory registrados: {len(impactos)} tipos de NPC afetados")
        
    except Exception as e:
        print(f"[BackstoryImpact] Não foi possível aplicar impactos: {e}")
