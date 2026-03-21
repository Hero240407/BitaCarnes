"""Sistema de Relacionamentos e Comportamento de NPCs - Stardew Valley inspired"""
from dataclasses import dataclass, field
from enum import Enum
import random
import time
import json
from typing import Optional
from datetime import datetime
from .servicos import chamar_ollama_pesado


class SentimentoNPC(Enum):
    """Estados emocionais dos NPCs"""
    FELIZ = "feliz"
    NEUTRO = "neutro"
    TRISTE = "triste"
    FURIOSO = "furioso"
    APAIXONADO = "apaixonado"


@dataclass(slots=True)
class DiaRotinaAtividade:
    """Atividade do NPC em um hora específica"""
    hora_inicio: int  # 6-22
    hora_fim: int
    tipo_atividade: str  # trabalho, comer, dormir, social, descanso
    locacao: tuple[int, int]
    descricao: str


@dataclass(slots=True)
class RotinaDiaria:
    """Rotina diária gerada por IA para NPCs"""
    npc_nome: str
    atividades: list[DiaRotinaAtividade] = field(default_factory=list)
    
    def obter_atividade_atual(self, hora_decimal: float) -> Optional[DiaRotinaAtividade]:
        """Retorna atividade atual baseado na hora"""
        hora_atual = int(hora_decimal)
        for atividade in self.atividades:
            if atividade.hora_inicio <= hora_atual < atividade.hora_fim:
                return atividade
        return None


@dataclass(slots=True)
class RelacaoNPC:
    """Relacionamento entre jogador e NPC"""
    npc_id: str
    npc_nome: str
    coracao: int = 0  # -10 a 10 (máx 10 para romance)
    presenteado_hoje: bool = False
    ultima_conversa: float = 0.0  # timestamp
    conversas_semana: int = 0
    _sentimento_cache: SentimentoNPC = field(default=SentimentoNPC.NEUTRO, init=False)
    
    def adicionar_coracao(self, quantidade: int = 1) -> None:
        """Adiciona corações de relacionamento"""
        self.coracao = min(10, max(-10, self.coracao + quantidade))
    
    def remover_coracao(self, quantidade: int = 1) -> None:
        """Remove corações de relacionamento"""
        self.coracao = min(10, max(-10, self.coracao - quantidade))
    
    @property
    def sentimento(self) -> SentimentoNPC:
        """Retorna sentimento baseado em corações"""
        if self.coracao >= 8:
            return SentimentoNPC.APAIXONADO
        elif self.coracao >= 4:
            return SentimentoNPC.FELIZ
        elif self.coracao >= 0:
            return SentimentoNPC.NEUTRO
        elif self.coracao >= -6:
            return SentimentoNPC.TRISTE
        else:
            return SentimentoNPC.FURIOSO
    
    @property
    def pode_casar(self) -> bool:
        """Verifica se relação permite casamento"""
        return self.coracao >= 8
    
    def resetar_dia(self) -> None:
        """Reseta flags diárias"""
        self.presenteado_hoje = False


class GerenciadorRelacoes:
    """Gerencia todos os relacionamentos do jogador"""
    
    def __init__(self):
        self.relacoes: dict[str, RelacaoNPC] = {}
        self.casado_com: Optional[str] = None
        self.filhos: list[dict] = []
        self.contador_dias_casado: int = 0
        
    def registrar_npc(self, npc_id: str, npc_nome: str) -> RelacaoNPC:
        """Registra um novo NPC"""
        if npc_id not in self.relacoes:
            self.relacoes[npc_id] = RelacaoNPC(npc_id, npc_nome)
        return self.relacoes[npc_id]
    
    def obter_relacao(self, npc_id: str) -> Optional[RelacaoNPC]:
        """Obtém relacionamento com um NPC"""
        return self.relacoes.get(npc_id)
    
    def dar_presente(self, npc_id: str, presente_tipo: str, afinidade: int) -> tuple[bool, str]:
        """Dá presente para NPC"""
        relacao = self.relacoes.get(npc_id)
        if not relacao:
            return False, "NPC não encontrado"
        
        if relacao.presenteado_hoje:
            return False, f"{relacao.npc_nome} já recebeu presente hoje"
        
        # Aumenta corações baseado em afinidade
        relacao.adicionar_coracao(afinidade)
        relacao.presenteado_hoje = True
        
        mensagens = {
            2: f"{relacao.npc_nome} adorou o presente!",
            1: f"{relacao.npc_nome} gostou do presente.",
            0: f"{relacao.npc_nome} achou o presente ok.",
            -1: f"{relacao.npc_nome} não gostou muito...",
        }
        return True, mensagens.get(afinidade, "Presente entregue")
    
    def conversar_npc(self, npc_id: str, assunto: str) -> tuple[bool, str]:
        """Conversa com NPC"""
        relacao = self.relacao.get(npc_id)
        if not relacao:
            return False, "Não há nada para conversar"
        
        tempo_atual = time.time()
        if tempo_atual - relacao.ultima_conversa < 3600:  # Uma conversa por hora
            return False, f"{relacao.npc_nome} ainda está ocupado"
        
        relacao.ultima_conversa = tempo_atual
        relacao.conversas_semana += 1
        relacao.adicionar_coracao(1)
        
        return True, f"Você conversou com {relacao.npc_nome}"
    
    def casar(self, npc_id: str) -> bool:
        """Tenta casar com um NPC"""
        relacao = self.relacoes.get(npc_id)
        if relacao and relacao.pode_casar and not self.casado_com:
            self.casado_com = npc_id
            return True
        return False
    
    def divorciar(self) -> bool:
        """Divorcia do cônjuge"""
        if self.casado_com:
            relacao = self.relacoes.get(self.casado_com)
            if relacao:
                relacao.remover_coracao(5)
            self.casado_com = None
            return True
        return False
    
    def ter_filho(self) -> bool:
        """Tenta ter filho com cônjuge"""
        if self.casado_com and self.contador_dias_casado >= 60:
            # 50% de chance de filho por dia após 60 dias de casamento
            if random.random() < 0.05:
                nome_filho = self._gerar_nome_filho()
                self.filhos.append({"nome": nome_filho, "idade": 0})
                return True
        return False
    
    def _gerar_nome_filho(self) -> str:
        """Gera nome aleatório para filho"""
        nomes = ["Ariel", "Beatriz", "Caio", "Diana", "Enzo", "Fátima", 
                 "Gabriel", "Helena", "Igor", "Joana"]
        return random.choice(nomes)
    
    def avancar_dia(self) -> None:
        """Avança um dia para relacionamentos"""
        for relacao in self.relacoes.values():
            relacao.resetar_dia()
            # Degradação lenta se não conversar
            if relacao.conversas_semana == 0:
                relacao.remover_coracao(0.5)
            relacao.conversas_semana = 0
        
        if self.casado_com:
            self.contador_dias_casado += 1


class PreferenciasNPC:
    """Preferências e quirks únicos do NPC que variam sua rotina"""
    
    def __init__(self, npc_id: str, npc_perfil: dict):
        self.npc_id = npc_id
        self.npc_perfil = npc_perfil
        self.pula_cafe = False  # Alguns não comem café da manhã
        self.pula_almoco = False
        self.horario_dormir_variavel = 0  # -2 a +2 horas de variação
        self.almocos_favoritos = []  # Tipos de alimento preferidos
        self.atividades_extras = []  # Hobbies/activities adicionais
        self.sensibilidade_frio = 0  # Sai menos em climates frios
        self.energia_base = random.uniform(0.8, 1.2)  # Alguns têm mais/menos energia
        self._gerar_preferencias_ia()
    
    def _gerar_preferencias_ia(self):
        """Gera preferências baseadas na IA personalidade do NPC"""
        perfil = self.npc_perfil
        personalidade = perfil.get("personalidade", "calmo")
        papel = perfil.get("papel", "habitante")
        
        # Personalidade afeta preferências
        traits = perfil.get("traits", []) + perfil.get("virtudes", []) + perfil.get("vicios", [])
        
        # Alguns não comem café (preguiçosos, ocupados)
        if "preguiçoso" in traits or "ocupado" in traits or personalidade in ["obsessivo", "selvagem"]:
            self.pula_cafe = random.random() < 0.4
        
        # Alguns pulam almoço (ocupados, trabalhadores)
        if papel in ["ferreiro", "caçador", "aprendiz"] and random.random() < 0.3:
            self.pula_almoco = random.random() < 0.2
        
        # Variação de horário de dormir (owls/larks)
        if "noturno" in traits or personalidade in ["misterioso", "astuto"]:
            self.horario_dormir_variavel = random.randint(0, 2)
        elif "madrugador" in traits:
            self.horario_dormir_variavel = random.randint(-2, 0)
        else:
            self.horario_dormir_variavel = random.randint(-1, 1)
        
        # Atividades extras baseadas em personalidade
        if "atletico" in traits or personalidade in ["selvagem", "alegre"]:
            self.atividades_extras.append("exercicio")
        if "intelectual" in traits or papel in ["cronista", "curandeiro"]:
            self.atividades_extras.append("estudo")
        if "social" in traits or personalidade in ["alegre", "nobre"]:
            self.atividades_extras.append("conversa")
        if "artistico" in traits:
            self.atividades_extras.append("arte")
        
        self.sensibilidade_frio = 1 if "resistente_frio" in traits else (-1 if "sensivel_frio" in traits else 0)
        
        # Energia varia com traits
        if "energetico" in traits:
            self.energia_base = random.uniform(1.2, 1.5)
        elif "letargico" in traits or "doente" in traits:
            self.energia_base = random.uniform(0.6, 0.9)


class GeradorRotinaDiariaIA:
    """Gera rotinas diárias personalizadas usando IA baseado em personalidade do NPC"""
    
    def gerar_rotina_ia(
        self,
        npc_id: str,
        npc_perfil: dict,
        hora_local_trabalho: tuple[int, int],
        hora_taverna: tuple[int, int],
        hora_praca: tuple[int, int],
        hora_preferida_dormir: int = 22,
    ) -> RotinaDiaria:
        """
        Gera rotina personalizada usando IA.
        
        Args:
            npc_id: ID do NPC
            npc_perfil: Dicionário com perfil (nome, personalidade, papel, traits, etc)
            hora_local_trabalho: Coordenadas do local de trabalho
            hora_taverna: Coordenadas da taverna
            hora_praca: Coordenadas da praça
            hora_preferida_dormir: Hora que prefere dormir
        
        Returns:
            RotinaDiaria personalizada do NPC
        """
        prefs = PreferenciasNPC(npc_id, npc_perfil)
        
        # Try to get AI-generated routine, fallback to template if AI unavailable
        try:
            contexto = self._preparar_contexto_rotina(npc_perfil, prefs)
            prompt = self._criar_prompt_rotina(contexto)
            
            resposta = chamar_ollama_pesado(
                prompt=prompt,
                timeout=10,
                temperatura=0.9  # Higher for more personality variation
            )
            
            rotina = self._parsear_rotina_ia(resposta, npc_perfil, prefs)
            if rotina:
                return rotina
        except Exception as e:
            print(f"[Aviso] Falha ao gerar rotina IA para {npc_perfil.get('nome', npc_id)}: {e}")
        
        # Fallback: Generate template routine with preferences applied
        return self._gerar_rotina_template(
            npc_id, npc_perfil, prefs,
            hora_local_trabalho, hora_taverna, hora_praca,
            hora_preferida_dormir
        )
    
    def _preparar_contexto_rotina(self, npc_perfil: dict, prefs: PreferenciasNPC) -> str:
        """Prepara contexto para geração de rotina"""
        return f"""
PERFIL DO NPC:
Nome: {npc_perfil.get('nome', 'Desconhecido')}
Personalidade: {npc_perfil.get('personalidade', 'calmo')}
Papel Social: {npc_perfil.get('papel', 'habitante')}
Idade: {npc_perfil.get('idade', 25)} anos
Virtudes: {', '.join(npc_perfil.get('virtudes', ['honesto']))}
Vícios: {', '.join(npc_perfil.get('vicios', ['nenhum']))}
Traumas: {npc_perfil.get('traumas', 'nenhum')}

TRAÇOS E HÁBITOS:
Pula café da manhã: {'Sim' if prefs.pula_cafe else 'Não'}
Pula almoço: {'Sim' if prefs.pula_almoco else 'Não'}
Variação de horário de dormir: {prefs.horario_dormir_variavel:+d} horas
Atividades extras: {', '.join(prefs.atividades_extras) if prefs.atividades_extras else 'nenhuma'}
Energia natural: {'Alta' if prefs.energia_base > 1.1 else 'Baixa' if prefs.energia_base < 0.9 else 'Normal'}
Sensibilidade ao frio: {'Sensível' if prefs.sensibilidade_frio < 0 else 'Resistente' if prefs.sensibilidade_frio > 0 else 'Normal'}
"""
    
    def _criar_prompt_rotina(self, contexto: str) -> str:
        """Cria prompt para IA gerar rotina personalizada"""
        return f"""
{contexto}

TAREFA:
Gere uma rotina diária personalizada e realista para este NPC que refita sua personalidade e traços.

REQUISITOS:
1. Rotina deve cobrir horas 6-22 (dormir 22-6)
2. Inclua pausas naturais (comer, descansar, socializar)
3. Respeite as preferências listadas acima
4. Atividades devem fazer sentido para o papel social
5. Seja realista e natural

FORMATO DE RESPOSTA (JSON):
[
  {{"hora_inicio": 6, "hora_fim": 8, "tipo": "acordar", "local": "casa", "descricao": "Acordando e se lavando"}},
  {{"hora_inicio": 8, "hora_fim": 12, "tipo": "trabalho", "local": "local_trabalho", "descricao": "Trabalhando no que faz"}},
  ...continue com mais atividades...
]

Responda APENAS com o JSON, sem explicações adicionais. Garanta que as horas não se sobrepõem.
"""
    
    def _parsear_rotina_ia(self, resposta: str, npc_perfil: dict, prefs: PreferenciasNPC) -> Optional[RotinaDiaria]:
        """Parseia resposta JSON da IA e converte para RotinaDiaria"""
        try:
            # Extrair JSON da resposta
            inicio_json = resposta.find('[')
            fim_json = resposta.rfind(']') + 1
            if inicio_json == -1 or fim_json == 0:
                return None
            
            json_str = resposta[inicio_json:fim_json]
            atividades_data = json.loads(json_str)
            
            atividades = []
            for item in atividades_data:
                atividade = DiaRotinaAtividade(
                    hora_inicio=item.get('hora_inicio', 6),
                    hora_fim=item.get('hora_fim', 8),
                    tipo_atividade=item.get('tipo', 'descanso'),
                    locacao=self._gerar_locacao_realista(item.get('local', 'casa')),
                    descricao=item.get('descricao', 'Descansando')
                )
                atividades.append(atividade)
            
            # Validar que rotina cobre 6-22
            if atividades and atividades[0].hora_inicio >= 6 and atividades[-1].hora_fim <= 22:
                rotina = RotinaDiaria(npc_perfil.get('nome', 'NPC'), atividades)
                rotina.preferencias = prefs  # Store preferences in routine
                return rotina
        except Exception as e:
            print(f"Erro ao parsear rotina IA: {e}")
        
        return None
    
    def _gerar_locacao_realista(self, tipo_local: str) -> tuple[int, int]:
        """Gera coordenadas realistas para o tipo de local"""
        # Adiciona variação próxima ao local base
        base_x, base_y = 25, 25  # Centro do mapa
        variacao = random.randint(0, 10)
        return (base_x + random.randint(-variacao, variacao), 
                base_y + random.randint(-variacao, variacao))
    
    def _gerar_rotina_template(
        self,
        npc_id: str,
        npc_perfil: dict,
        prefs: PreferenciasNPC,
        hora_local_trabalho: tuple[int, int],
        hora_taverna: tuple[int, int],
        hora_praca: tuple[int, int],
        hora_preferida_dormir: int,
    ) -> RotinaDiaria:
        """Gera rotina usando template quando IA não está disponível"""
        atividades = []
        
        # Ajusta horários baseado em preferências
        hora_despertar = 6 + prefs.horario_dormir_variavel
        hora_dormir = hora_preferida_dormir + prefs.horario_dormir_variavel
        
        # Acordar e se arrumar
        atividades.append(DiaRotinaAtividade(
            hora_inicio=hora_despertar,
            hora_fim=hora_despertar + 1,
            tipo_atividade="acordar",
            locacao=self._gerar_locacao_realista("casa"),
            descricao="Acordando e se arrumando"
        ))
        
        # Café da manhã (a menos que prefira pular)
        if not prefs.pula_cafe:
            atividades.append(DiaRotinaAtividade(
                hora_inicio=hora_despertar + 1,
                hora_fim=hora_despertar + 2,
                tipo_atividade="comer",
                locacao=self._gerar_locacao_realista("casa"),
                descricao="Tomando café da manhã"
            ))
            trabalho_inicio = hora_despertar + 2
        else:
            trabalho_inicio = hora_despertar + 1
        
        # Trabalho (manhã)
        atividades.append(DiaRotinaAtividade(
            hora_inicio=trabalho_inicio,
            hora_fim=12,
            tipo_atividade="trabalho",
            locacao=hora_local_trabalho,
            descricao=f"Trabalhando como {npc_perfil.get('papel', 'habitante')}"
        ))
        
        # Almoço (a menos que prefira pular)
        if not prefs.pula_almoco:
            atividades.append(DiaRotinaAtividade(
                hora_inicio=12,
                hora_fim=14,
                tipo_atividade="comer",
                locacao=hora_taverna,
                descricao="Almoçando na taverna"
            ))
        
        # Trabalho (tarde)
        atividades.append(DiaRotinaAtividade(
            hora_inicio=14,
            hora_fim=18,
            tipo_atividade="trabalho",
            locacao=hora_local_trabalho,
            descricao=f"Continuando trabalho"
        ))
        
        # Atividades extras (hobbies)
        if prefs.atividades_extras:
            atividade_extra = random.choice(prefs.atividades_extras)
            atividades.append(DiaRotinaAtividade(
                hora_inicio=18,
                hora_fim=19,
                tipo_atividade="hobby",
                locacao=self._gerar_locacao_realista(atividade_extra),
                descricao=f"Dedicado a {atividade_extra}"
            ))
        
        # Social/Relaxamento
        atividades.append(DiaRotinaAtividade(
            hora_inicio=19 if prefs.atividades_extras else 18,
            hora_fim=21,
            tipo_atividade="social",
            locacao=hora_praca,
            descricao="Socializando na praça"
        ))
        
        # Descanso antes de dormir
        atividades.append(DiaRotinaAtividade(
            hora_inicio=21,
            hora_fim=hora_dormir,
            tipo_atividade="descanso",
            locacao=self._gerar_locacao_realista("casa"),
            descricao="Relaxando antes de dormir"
        ))
        
        rotina = RotinaDiaria(npc_perfil.get("nome", npc_id), atividades)
        rotina.preferencias = prefs
        return rotina


class ComportamentoNPC:
    """Define comportamento e IA do NPC"""
    
    def __init__(self, npc_id: str, npc_perfil: dict):
        self.npc_id = npc_id
        self.npc_perfil = npc_perfil
        self.rotina: Optional[RotinaDiaria] = None
        self.preferencias: Optional[PreferenciasNPC] = None
        self.energia = 100  # 0-100
        self.felicidade = 50  # 0-100
        self.objetivo_atual: Optional[str] = None
        self.contador_atividade = 0
        self._gerador_rotina = GeradorRotinaDiariaIA()
        
    def gerar_rotina_ia(
        self,
        hora_local_trabalho: tuple[int, int] = (25, 25),
        hora_taverna: tuple[int, int] = (20, 20),
        hora_praca: tuple[int, int] = (25, 15),
    ) -> RotinaDiaria:
        """Gera rotina personalizada usando IA"""
        self.rotina = self._gerador_rotina.gerar_rotina_ia(
            self.npc_id,
            self.npc_perfil,
            hora_local_trabalho,
            hora_taverna,
            hora_praca,
            hora_preferida_dormir=22
        )
        self.preferencias = self.rotina.preferencias if hasattr(self.rotina, 'preferencias') else PreferenciasNPC(self.npc_id, self.npc_perfil)
        return self.rotina
        
    def gerar_rotina_randomica(self) -> RotinaDiaria:
        """Gera rotina randomica para o NPC (legado)"""
        atividades = []
        
        # Padrão básico: dormir, trabalho, comer, social, descanso
        rotina_base = [
            (6, 8, "acordar", "casa", "Acordando e se arrumando"),
            (8, 12, "trabalho", "local_trabalho", "Trabalhando"),
            (12, 14, "comer", "taverna", "Comendo e descansando"),
            (14, 18, "trabalho", "local_trabalho", "Continuando o trabalho"),
            (18, 20, "social", "praca", "Socializando com amigos"),
            (20, 22, "descanso", "casa", "Descansando"),
            (22, 6, "dormir", "casa", "Dormindo"),
        ]
        
        # Randomizar um pouco
        for hora_ini, hora_fim, tipo, local, desc in rotina_base:
            atividade = DiaRotinaAtividade(
                hora_inicio=hora_ini,
                hora_fim=hora_fim,
                tipo_atividade=tipo,
                locacao=(random.randint(0, 50), random.randint(0, 50)),
                descricao=desc + f" ({self.npc_perfil.get('papel', 'habitante')})"
            )
            atividades.append(atividade)
        
        self.rotina = RotinaDiaria(self.npc_perfil.get("nome", self.npc_id), atividades)
        return self.rotina
    
    def atualizar_estado(self, horas_passadas: float = 1.0) -> None:
        """Atualiza estado do NPC"""
        # Usa multiplicador de energia das preferências
        energia_mult = self.preferencias.energia_base if self.preferencias else 1.0
        self.energia = max(0, self.energia - horas_passadas * random.uniform(0.5, 2.0) * energia_mult)
        
        # Recupera energia uma pouco durante atividades de descanso
        if self.rotina:
            atividade = self.rotina.obter_atividade_atual(6)  # Default 6 da manhã
            if atividade and "descanso" in atividade.tipo_atividade.lower():
                self.energia = min(100, self.energia + 5 * horas_passadas)

    
    def obter_proximidade_reacao(self, distancia_celulas: float) -> str:
        """Retorna reação baseada em distância"""
        if distancia_celulas < 2:
            return "muito_perto"
        elif distancia_celulas < 5:
            return "perto"
        elif distancia_celulas < 10:
            return "visivel"
        return "distante"
    
    def interagir_jogador(self, tipo_interacao: str) -> str:
        """Gera resposta à interação do jogador"""
        respostas_base = {
            "conversa": "Como vai?",
            "presente": "Obrigado pelo presente!",
            "trabalho": "Ocupado no momento",
            "saudacao": "Olá!",
        }
        
        # Modifica baseado no humor
        base = respostas_base.get(tipo_interacao, "...")
        
        if self.felicidade > 70:
            base = f"😊 {base}"
        elif self.felicidade < 30:
            base = f"😔 {base}"
        
        return base
