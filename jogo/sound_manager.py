"""Audio/Music management system for BitaCarnes with contextual music selection."""

from __future__ import annotations

import random
from enum import Enum
from pathlib import Path
from typing import Optional

import pygame


class MusicaContexto(Enum):
    """Context types for music selection."""
    MENU = "menu"
    EXPLORAR = "explorar"
    CIDADE = "cidade"
    ENCONTRO = "encontro"
    RETORNO = "retorno"
    AVENTURA = "aventura"
    PERIGO = "perigo"
    PAUSA = "pausa"
    TRANSICAO = "transicao"


class GerenciadorSom:
    """Manages game music with context-aware selection and transitions."""
    
    # Map tracks to contexts
    TRILHAS_MUSICA = {
        MusicaContexto.MENU: [
            "1-TITLE.wav",  # Menu theme
        ],
        MusicaContexto.EXPLORAR: [
            "5-EXPLORING.wav",
            "10-EXPLORING.wav",
        ],
        MusicaContexto.CIDADE: [
            "8-A_NEW_TOWN.wav",
            "2-HOMESTEAD.wav",
        ],
        MusicaContexto.ENCONTRO: [
            "9-ENCOUNTER.wav",
            "3-BAD_THING.wav",
        ],
        MusicaContexto.AVENTURA: [
            "4-ADVENTURE.wav",
            "7-SET_SAIL.wav",
            "6-ON_AND_UP.wav",
        ],
        MusicaContexto.RETORNO: [
            "2-HOMESTEAD.wav",
            "6-ON_AND_UP.wav",
        ],
        MusicaContexto.PERIGO: [
            "3-BAD_THING.wav",
            "12-DARKWOOD.wav",
            "13-BARREN.wav",
            "11-SETBACK.wav",
        ],
        MusicaContexto.PAUSA: [
            "2-HOMESTEAD.wav",  # Calm music for paused state
        ],
    }
    
    def __init__(self, pasta_musica: Path | str = None):
        """Initialize sound manager.
        
        Args:
            pasta_musica: Path to music folder. If None, uses default.
        """
        if pasta_musica is None:
            pasta_musica = Path(__file__).parent.parent / "src" / "sounds" / "asset-pack-8-bit"
        else:
            pasta_musica = Path(pasta_musica)
        
        self.pasta_musica = pasta_musica
        self.musica_atual: Optional[str] = None
        self.contexto_atual = MusicaContexto.EXPLORAR
        self.volume = 0.5
        self.musica_ativa = True
        self.tempo_transicao = 0
        self.max_tempo_transicao = 30  # frames for fade-out
        self.volume_alvo = self.volume
        self.historico_trilhas = []  # Track recently played to avoid repetition
        self.max_historico = 5
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[Áudio] Falha ao inicializar mixer: {e}")
        
        print(f"[Áudio] Gerenciador de Som inicializado: {self.pasta_musica}")
        self._verificar_arquivos()
    
    def _verificar_arquivos(self) -> None:
        """Verify that music files exist."""
        arquivos_encontrados = 0
        
        if self.pasta_musica.exists():
            for arquivo in self.pasta_musica.glob("*.wav"):
                arquivos_encontrados += 1
        
        if arquivos_encontrados > 0:
            print(f"[Áudio] {arquivos_encontrados} arquivos de música encontrados")
        else:
            print(f"[Áudio] ⚠️  Nenhum arquivo de música encontrado em {self.pasta_musica}")
    
    def obter_trilha(self, contexto: MusicaContexto) -> Optional[str]:
        """Get appropriate music track for context, avoiding recent repeats.
        
        Args:
            contexto: Music context/scenario
            
        Returns:
            Filename of music track or None if not available
        """
        trilhas = self.TRILHAS_MUSICA.get(contexto, [])
        
        if not trilhas:
            return None
        
        # Filter out recently played to add variety
        trilhas_disponiveis = [t for t in trilhas if t not in self.historico_trilhas[-self.max_historico:]]
        
        # If all tracks recently played, reset and use all
        if not trilhas_disponiveis:
            trilhas_disponiveis = trilhas
        
        # Select random track
        trilha = random.choice(trilhas_disponiveis)
        
        # Add to history
        self.historico_trilhas.append(trilha)
        if len(self.historico_trilhas) > self.max_historico * 2:
            self.historico_trilhas.pop(0)
        
        return trilha
    
    def tocar_musica(self, contexto: MusicaContexto, fade_in: bool = True) -> bool:
        """Play music for given context with optional fade-in.
        
        Args:
            contexto: Music context
            fade_in: Whether to fade in the music
            
        Returns:
            True if music started successfully
        """
        if contexto == self.contexto_atual and pygame.mixer.music.get_busy():
            # Same context and already playing - no need to change
            return True
        
        trilha = self.obter_trilha(contexto)
        
        if not trilha:
            print(f"[Áudio] Nenhuma trilha disponível para {contexto.value}")
            return False
        
        caminho_arquivo = self.pasta_musica / trilha
        
        if not caminho_arquivo.exists():
            print(f"[Áudio] Arquivo não encontrado: {caminho_arquivo}")
            return False
        
        try:
            pygame.mixer.music.load(str(caminho_arquivo))
            
            if fade_in:
                pygame.mixer.music.set_volume(0)
                self.volume_alvo = self.volume
                self.tempo_transicao = 0
            else:
                pygame.mixer.music.set_volume(self.volume)
            
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            
            self.musica_atual = trilha
            self.contexto_atual = contexto
            self.musica_ativa = True
            
            print(f"[Áudio] Tocando: {trilha} ({contexto.value})")
            return True
            
        except Exception as e:
            print(f"[Áudio] Erro ao tocar música: {e}")
            return False
    
    def parar_musica(self, fade_out: bool = True) -> None:
        """Stop music with optional fade-out.
        
        Args:
            fade_out: Whether to fade out
        """
        if fade_out:
            self.volume_alvo = 0
            self.tempo_transicao = 0
        else:
            pygame.mixer.music.stop()
            self.musica_ativa = False
            self.musica_atual = None
    
    def atualizar_musica(self, contexto_novo: MusicaContexto) -> None:
        """Update music context (called each frame).
        
        Args:
            contexto_novo: New context if changed
        """
        if not self.musica_ativa:
            return
        
        # Check if context changed
        if contexto_novo != self.contexto_atual:
            self.tocar_musica(contexto_novo, fade_in=True)
        
        # Handle fade transitions
        if self.tempo_transicao < self.max_tempo_transicao:
            self.tempo_transicao += 1
            
            if self.volume_alvo == 0 and pygame.mixer.music.get_busy():
                # Fading out
                volume_progress = 1.0 - (self.tempo_transicao / self.max_tempo_transicao)
                pygame.mixer.music.set_volume(max(0, self.volume * volume_progress))
                
                if volume_progress <= 0:
                    pygame.mixer.music.stop()
                    self.musica_ativa = False
            elif self.volume_alvo > 0:
                # Fading in
                volume_progress = self.tempo_transicao / self.max_tempo_transicao
                pygame.mixer.music.set_volume(self.volume * volume_progress)
    
    def definir_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0).
        
        Args:
            volume: Volume level (0.0 = silent, 1.0 = full)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.volume_alvo = self.volume
        
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.volume)
    
    def definir_musica_ativa(self, ativa: bool) -> None:
        """Enable or disable music.
        
        Args:
            ativa: Whether music should be active
        """
        if ativa and not self.musica_ativa:
            # Resume music
            self.musica_ativa = True
            pygame.mixer.music.unpause()
        elif not ativa and self.musica_ativa:
            # Pause music
            self.musica_ativa = False
            pygame.mixer.music.pause()
    
    def obter_tempo_musica(self) -> float:
        """Get current playback time in seconds.
        
        Returns:
            Playback position in seconds
        """
        if pygame.mixer.music.get_busy():
            return pygame.mixer.music.get_pos() / 1000.0  # pygame returns ms
        return 0.0
    
    def musica_tocando(self) -> bool:
        """Check if music is currently playing.
        
        Returns:
            True if music is active and playing
        """
        return self.musica_ativa and pygame.mixer.music.get_busy()


class GerenciadorEfeitosSonoros:
    """Manages sound effects for actions."""
    
    # Simple sound effects - can be expanded
    EFEITOS = {
        "coletar": "collect.wav",  # Would need these files
        "ataque": "attack.wav",
        "dano": "hit.wav",
        "cura": "heal.wav",
        "encontro": "encounter.wav",
        "sucesso": "success.wav",
        "fracasso": "failure.wav",
    }
    
    def __init__(self, pasta_efeitos: Path | str = None):
        """Initialize sound effects manager.
        
        Args:
            pasta_efeitos: Path to sound effects folder
        """
        if pasta_efeitos is None:
            pasta_efeitos = Path(__file__).parent.parent / "src" / "sounds" / "effects"
        
        self.pasta_efeitos = Path(pasta_efeitos)
        self.efeitos_carregados = {}
        self.volume = 0.3
        
        print(f"[Efeitos] Gerenciador de Efeitos Sonoros inicializado")
    
    def carregar_efeito(self, chave: str) -> bool:
        """Load a sound effect.
        
        Args:
            chave: Effect key
            
        Returns:
            True if loaded successfully
        """
        arquivo = self.EFEITOS.get(chave)
        
        if not arquivo:
            return False
        
        caminho = self.pasta_efeitos / arquivo
        
        if not caminho.exists():
            return False
        
        try:
            som = pygame.mixer.Sound(str(caminho))
            som.set_volume(self.volume)
            self.efeitos_carregados[chave] = som
            return True
        except Exception:
            return False
    
    def tocar_efeito(self, chave: str) -> None:
        """Play a sound effect.
        
        Args:
            chave: Effect key
        """
        # Try to load if not already loaded
        if chave not in self.efeitos_carregados:
            if not self.carregar_efeito(chave):
                return
        
        som = self.efeitos_carregados.get(chave)
        if som:
            som.play()


class ContextoMusica:
    """Helper class to determine music context based on game state."""
    
    @staticmethod
    def determinar_contexto(
        mundo: object,
        tempo_sistema: object,
        evento: Optional[str] = None,
        pausado: bool = False,
    ) -> MusicaContexto:
        """Determine music context based on game state.
        
        Args:
            mundo: Game world object
            tempo_sistema: Time system object
            evento: Current event if any
            pausado: Whether game is paused
            
        Returns:
            Appropriate music context
        """
        # Pause takes priority
        if pausado:
            return MusicaContexto.PAUSA
        
        # Check for active events
        if evento:
            if "encontro" in evento.lower() or "inimigo" in evento.lower():
                return MusicaContexto.ENCONTRO
            elif "aventura" in evento.lower() or "quest" in evento.lower():
                return MusicaContexto.AVENTURA
        
        # Check HP for danger music
        if hasattr(mundo, 'hp') and hasattr(mundo, 'hp_maximo'):
            if mundo.hp < mundo.hp_maximo * 0.3:
                return MusicaContexto.PERIGO
        
        # Check location (if implemented in biome system)
        if hasattr(mundo, 'humano'):
            x, y = mundo.humano
            # Simple heuristic: city is near 0,0 (spawn area)
            distancia_spawn = abs(x) + abs(y)
            
            if distancia_spawn < 20:
                return MusicaContexto.CIDADE
            elif distancia_spawn > 50:
                return MusicaContexto.AVENTURA
        
        # Default to exploration
        return MusicaContexto.EXPLORAR
