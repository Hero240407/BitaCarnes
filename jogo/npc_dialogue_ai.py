"""AI-powered NPC dialogue system with contextual conversations."""

from __future__ import annotations

import json
import random
from typing import Optional
from .servicos import chamar_ollama_pesado


class DialogoIA:
    """AI-generated contextual dialogue for NPCs."""
    
    def __init__(self, npc_nome: str, npc_info: dict, mundo_contexto: dict):
        self.npc_nome = npc_nome
        self.npc_info = npc_info
        self.mundo_contexto = mundo_contexto
        self.historico_dialogo = []
        self.ultimo_dialogo_hora = -1
        
    def gerar_dialogo_contextual(self, jogador_info: dict, hora_atual: int, momento_dia: str) -> str:
        """Generate contextual dialogue based on NPC and world state."""
        
        # Build context for ollama
        contexto = self._preparar_contexto(jogador_info, hora_atual, momento_dia)
        prompt = self._criar_prompt_dialogo(contexto)
        
        try:
            resposta = chamar_ollama_pesado(
                prompt=prompt,
                timeout=15,
                temperatura=0.8  # Higher for more personality
            )
            
            dialogo = self._extrair_dialogo(resposta)
            self.historico_dialogo.append(dialogo)
            self.ultimo_dialogo_hora = hora_atual
            return dialogo
            
        except Exception as e:
            # Fallback to template dialogues
            return self._dialogo_fallback()
    
    def _preparar_contexto(self, jogador_info: dict, hora: int, momento_dia: str) -> str:
        """Prepare context information for dialogue generation."""
        contexto = f"""
Personagem NPC: {self.npc_nome}
Personalidade: {self.npc_info.get('personalidade', 'Amigável')}
Afetos: {self.npc_info.get('afetos', 'Neutro')}
Profissão: {self.npc_info.get('profissao', 'Habitante')}
Hora do dia: {hora}:00 ({momento_dia})

Jogador:
Nome: {jogador_info.get('nome', 'Viajante')}
Profissão: {jogador_info.get('profissao', 'Desconhecida')}
Relacionamento anterior: {self.npc_info.get('relacionamento_historico', 'Primeiro encontro')}

Contexto Mundial:
Estação: {self.mundo_contexto.get('estacao', 'Primavera')}
Clima: {self.mundo_contexto.get('clima', 'Ensolarado')}
Eventos recentes: {self.mundo_contexto.get('eventos', 'Nenhum')}
        """
        return contexto.strip()
    
    def _criar_prompt_dialogo(self, contexto: str) -> str:
        """Create dialogue generation prompt."""
        return f"""
{contexto}

Você é um dialógista de RPG criando uma conversa natural e envolvente entre um NPC e um jogador.

INSTRUCOES:
1. Gere uma única frase de diálogo (20-60 palavras)
2. O diálogo deve refletir a hora do dia e contexto
3. Deve ser apropriado para a personalidade do NPC
4. Use português (Brasil)
5. Seja natural e conversacional
6. Inclua referências subtis ao mundo, estação ou personagem do jogador, se apropriado

RESPONDA APENAS COM O DIÁLOGO ENTRE ASPAS:
"[diálogo aqui]"
        """
    
    def _extrair_dialogo(self, resposta: str) -> str:
        """Extract dialogue from ollama response."""
        # Look for quoted dialogue
        if '"' in resposta:
            inicio = resposta.find('"')
            fim = resposta.find('"', inicio + 1)
            if inicio != -1 and fim != -1:
                dialogo = resposta[inicio + 1:fim]
                return dialogo.strip()
        
        # Fallback: use whole response if no quotes
        linhas = resposta.strip().split('\n')
        return linhas[0] if linhas else "..."
    
    def _dialogo_fallback(self) -> str:
        """Return fallback dialogue when AI unavailable."""
        templates = [
            f"Olá! Que dia bonito, não é?",
            f"Estava tendo bons pensamentos...você viu algo interessante por aí?",
            f"Temos muito a fazer por aqui. E você, como vai?",
            f"Hmm, parece que temos companhia. Bem-vindo!",
            f"Espero que esteja tendo um bom dia como eu.",
            f"Você é novo por aqui, certo? Bem-vindo ao vale.",
        ]
        return random.choice(templates)
    
    def obter_dialogo_repetido(self) -> str:
        """Get repeated dialogue with some variation."""
        if self.historico_dialogo:
            ultimo = self.historico_dialogo[-1]
            # Small variation on last dialogue
            variacoes = [
                f"{ultimo} (novamente)",
                f"*repete enquanto sorri* {ultimo}",
                f"Como eu dizia... {ultimo}",
            ]
            return random.choice(variacoes)
        return self._dialogo_fallback()


class GerenciadorDialogos:
    """Manages all NPC dialogues with caching and context."""
    
    def __init__(self):
        self.dialogos_npcs = {}
        self.cache_dialogos = {}
        self.tempo_ultimo_dialogo = {}
        
    def registrar_npc(self, npc_nome: str, npc_info: dict, mundo_contexto: dict) -> None:
        """Register NPC for dialogue generation."""
        if npc_nome not in self.dialogos_npcs:
            self.dialogos_npcs[npc_nome] = DialogoIA(npc_nome, npc_info, mundo_contexto)
    
    def obter_dialogo(self, npc_nome: str, jogador_info: dict, hora_atual: int, momento_dia: str, force_novo: bool = False) -> str:
        """Get dialogue for NPC, using cache if available."""
        
        # Check if NPC registered
        if npc_nome not in self.dialogos_npcs:
            return "Hmm? Algo que posso ajudar?"
        
        # Check cache (one dialogue per hour per NPC)
        cache_key = f"{npc_nome}_{hora_atual}"
        if cache_key in self.cache_dialogos and not force_novo:
            return self.cache_dialogos[cache_key]
        
        # Generate new dialogue
        dialogo_ia = self.dialogos_npcs[npc_nome]
        dialogo = dialogo_ia.gerar_dialogo_contextual(jogador_info, hora_atual, momento_dia)
        
        # Cache it
        self.cache_dialogos[cache_key] = dialogo
        self.tempo_ultimo_dialogo[npc_nome] = hora_atual
        
        return dialogo
    
    def limpar_cache_hora(self, nova_hora: int) -> None:
        """Clear cache when hour changes (every dialogue should be fresh for new hour)."""
        # Remove old cache entries
        chaves_remover = [k for k in self.cache_dialogos.keys() if k.split('_')[1] != str(nova_hora)]
        for chave in chaves_remover:
            del self.cache_dialogos[chave]


class SistemaConversas:
    """Dialogue system handling interaction flow and choices."""
    
    def __init__(self):
        self.gerenciador = GerenciadorDialogos()
        self.conversas_ativas = {}
        self.historico_conversas = []
        
    def iniciar_conversa(self, npc_nome: str, jogador_info: dict, npc_info: dict, mundo_contexto: dict, hora: int) -> str:
        """Start conversation with NPC."""
        
        # Register if not already
        if npc_nome not in self.gerenciador.dialogos_npcs:
            self.gerenciador.registrar_npc(npc_nome, npc_info, mundo_contexto)
        
        # Get greeting or contextual opening
        momento = self._obter_momento_dia(hora)
        dialogo = self.gerenciador.obter_dialogo(npc_nome, jogador_info, hora, momento)
        
        # Store active conversation
        self.conversas_ativas[npc_nome] = {
            'inicio': hora,
            'dialogo_inicial': dialogo,
            'respostas_npcs': [dialogo],
        }
        
        return dialogo
    
    def continuar_conversa(self, npc_nome: str, opcao_jogador: int, jogador_info: dict, npc_info: dict, mundo_contexto: dict, hora: int) -> str:
        """Continue existing conversation."""
        
        if npc_nome not in self.conversas_ativas:
            return "Conversa não iniciada."
        
        # Generate NPC response based on player choice
        npc_dialogo = self._gerar_resposta_npc(npc_nome, opcao_jogador, jogador_info, npc_info, mundo_contexto, hora)
        
        self.conversas_ativas[npc_nome]['respostas_npcs'].append(npc_dialogo)
        return npc_dialogo
    
    def finalizar_conversa(self, npc_nome: str) -> None:
        """End conversation with NPC."""
        if npc_nome in self.conversas_ativas:
            conversa = self.conversas_ativas[npc_nome]
            self.historico_conversas.append(conversa)
            del self.conversas_ativas[npc_nome]
    
    def _obter_momento_dia(self, hora: int) -> str:
        """Get time of day description."""
        if hora < 6:
            return "Madrugada"
        elif hora < 12:
            return "Manhã"
        elif hora < 18:
            return "Tarde"
        else:
            return "Noite"
    
    def _gerar_resposta_npc(self, npc_nome: str, opcao: int, jogador_info: dict, npc_info: dict, mundo_contexto: dict, hora: int) -> str:
        """Generate NPC response to player choice."""
        
        opcoes_resposta = [
            "Entendo o que você diz...",
            "Interessante pensamento.",
            "Hm, verdade. Você está certo.",
            "Não tinha pensado assim antes.",
        ]
        
        # Try to make AI response more contextual
        try:
            prompt = f"""
NPC {npc_nome} está tendo uma conversa com {jogador_info.get('nome', 'um viajante')}.
O jogador escolheu a opção {opcao + 1}.

Responda com uma única frase natural de {20-60} palavras que mostre que o NPC escutou e reagiu.
Responda APENAS COM AS ASPAS DO DIÁLOGO:
"[resposta aqui]"
            """
            
            resposta = chamar_ollama_pesado(prompt=prompt, timeout=10, temperatura=0.7)
            dialogo = self._extrair_dialogo_resposta(resposta)
            return dialogo
            
        except:
            return random.choice(opcoes_resposta)
    
    def _extrair_dialogo_resposta(self, resposta: str) -> str:
        """Extract dialogue from response."""
        if '"' in resposta:
            inicio = resposta.find('"')
            fim = resposta.find('"', inicio + 1)
            if inicio != -1 and fim != -1:
                return resposta[inicio + 1:fim].strip()
        return resposta.strip().split('\n')[0]
