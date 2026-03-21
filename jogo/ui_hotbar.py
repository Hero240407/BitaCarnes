"""
Hotbar Mode System - Manages game modes and displays available actions
Modes: EXPLORE, COMBAT, FARMING, QUESTS, INVENTORY, STATS
"""
import pygame
from enum import Enum
from typing import Dict, List, Tuple


class GameMode(Enum):
    """Available game modes"""
    EXPLORE = "EXPLORAÇÃO"
    COMBAT = "COMBATE"
    FARMING = "FAZENDA"
    QUESTS = "MISSÕES"
    INVENTORY = "INVENTÁRIO"
    STATS = "ESTATÍSTICAS"


class HotbarManager:
    """Manages game modes and hotbar display"""
    
    def __init__(self):
        self.modo_atual = GameMode.EXPLORE
        self.modos = list(GameMode)
        self.indice_modo = 0
        
        # Mode-specific actions
        self.modo_acoes: Dict[GameMode, List[Tuple[str, str]]] = {
            GameMode.EXPLORE: [
                ("P", "Pescar"),
                ("H", "Dungeon"),
                ("T", "Conversar"),
                ("I", "Inventário"),
            ],
            GameMode.COMBAT: [
                ("SPACE", "Atacar"),
                ("A/D", "Mover"),
                ("R", "Correr"),
            ],
            GameMode.FARMING: [
                ("J", "Arar"),
                ("M", "Plantar"),
                ("N", "Regar"),
                ("H", "Colher"),
            ],
            GameMode.QUESTS: [
                ("Q", "Ver Missões"),
                ("E", "Entregar"),
                ("SETAS", "Navegar"),
            ],
            GameMode.INVENTORY: [
                ("I", "Abrir/Fechar"),
                ("SETAS", "Navegar"),
                ("ENTER", "Usar Item"),
            ],
            GameMode.STATS: [
                ("L", "Estatísticas"),
                ("K", "Habilidades"),
                ("E", "Equipamento"),
                ("V", "Fazer Farol"),
            ],
        }
    
    def ciclar_modo_frente(self) -> GameMode:
        """Move to next mode"""
        self.indice_modo = (self.indice_modo + 1) % len(self.modos)
        self.modo_atual = self.modos[self.indice_modo]
        return self.modo_atual
    
    def ciclar_modo_atras(self) -> GameMode:
        """Move to previous mode"""
        self.indice_modo = (self.indice_modo - 1) % len(self.modos)
        self.modo_atual = self.modos[self.indice_modo]
        return self.modo_atual
    
    def setar_modo(self, modo: GameMode):
        """Set specific mode"""
        self.modo_atual = modo
        self.indice_modo = self.modos.index(modo)
    
    def obter_acoes_atuais(self) -> List[Tuple[str, str]]:
        """Get actions for current mode"""
        return self.modo_acoes.get(self.modo_atual, [])
    
    def renderizar_hotbar(self, tela: pygame.Surface, y_position: int = None) -> None:
        """Render the hotbar as a horizontal bar at the bottom left, above player info bars."""
        altura_tela = tela.get_height()
        largura_tela = tela.get_width()
        altura_barra = 54  # Height of the hotbar
        margem_lateral = 12
        margem_inferior = 120  # Space above the player info bars (adjust as needed)
        barra_y = altura_tela - margem_inferior - altura_barra if y_position is None else y_position
        barra_x = margem_lateral
        barra_largura = 520  # Enough for all actions horizontally
        
        # Draw background for the hotbar
        pygame.draw.rect(tela, (60, 45, 30), pygame.Rect(barra_x, barra_y, barra_largura, altura_barra), border_radius=12)
        pygame.draw.rect(tela, (100, 70, 50), pygame.Rect(barra_x, barra_y, barra_largura, altura_barra), 2, border_radius=12)
        
        # Fonts
        fonte_titulo = pygame.font.Font(None, 22)
        fonte_acoes = pygame.font.Font(None, 18)
        fonte_nav = pygame.font.Font(None, 14)
        
        # Mode title with highlight (left side)
        modo_nome = self.modo_atual.value
        texto_modo = fonte_titulo.render(f">> {modo_nome}", True, (255, 200, 100))
        tela.blit(texto_modo, (barra_x + 12, barra_y + 8))
        
        # Actions for current mode - displayed horizontally
        acoes = self.obter_acoes_atuais()
        x_acao = barra_x + 160
        y_acao = barra_y + 12
        for i, (tecla, acao) in enumerate(acoes):
            cor = (200, 255, 150) if i == 0 else (180, 180, 200)
            texto_acao = fonte_acoes.render(f"[{tecla}] {acao}", True, cor)
            tela.blit(texto_acao, (x_acao, y_acao))
            x_acao += texto_acao.get_width() + 28
        
        # Mode indicators (circles at the right end of the bar)
        indicador_y = barra_y + altura_barra - 18
        indicador_x_start = barra_x + barra_largura - (len(self.modos) * 32) - 12
        for i, modo in enumerate(self.modos):
            cor = (200, 150, 50) if modo == self.modo_atual else (80, 60, 40)
            pygame.draw.circle(tela, cor, (indicador_x_start + (i * 32), indicador_y), 8)
            pygame.draw.circle(tela, (50, 50, 50), (indicador_x_start + (i * 32), indicador_y), 9, 1)
        
        # Navigation help text at the bottom left
        texto_nav = fonte_nav.render("TAB=Modo", True, (150, 150, 100))
        tela.blit(texto_nav, (barra_x + 12, barra_y + altura_barra - 20))
        
        # Store bar dimensions for other UI elements to avoid overlap
        self.bar_x = barra_x
        self.bar_y = barra_y
        self.bar_width = barra_largura
        self.bar_height = altura_barra


def renderizar_overlay_modo(tela: pygame.Surface, hotbar: HotbarManager) -> None:
    """Show a full-screen mode selection overlay when switching modes"""
    # Semi-transparent overlay
    overlay = pygame.Surface((tela.get_width(), tela.get_height()))
    overlay.set_alpha(100)
    overlay.fill((0, 0, 0))
    tela.blit(overlay, (0, 0))
    
    # Mode name in center
    fonte_grande = pygame.font.Font(None, 72)
    texto = fonte_grande.render(hotbar.modo_atual.value, True, (255, 200, 100))
    tela.blit(texto, (
        tela.get_width() // 2 - texto.get_width() // 2,
        tela.get_height() // 2 - texto.get_height() // 2
    ))
    
    # Subtext
    fonte_pequena = pygame.font.Font(None, 24)
    texto_sub = fonte_pequena.render("Pressione TAB para mudar de modo", True, (200, 200, 200))
    tela.blit(texto_sub, (
        tela.get_width() // 2 - texto_sub.get_width() // 2,
        tela.get_height() // 2 + 80
    ))
