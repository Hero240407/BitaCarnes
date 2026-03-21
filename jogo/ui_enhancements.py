"""Enhanced UI system for Stardew Valley-like visual polish and interactions."""

from __future__ import annotations

import pygame
from .config import ALTURA_HUD, TAMANHO_CELULA, COR_TEXTO


class MenuAnimado:
    """Animated menu with smooth transitions and effects."""
    
    def __init__(self, titulo: str, opcoes: list[str], x: int = 0, y: int = 0):
        self.titulo = titulo
        self.opcoes = opcoes
        self.x = x
        self.y = y
        self.selecionada = 0
        self.tempo_abertura = 0
        self.max_tempo = 30
        self.aberto = True
        
    def animar_abertura(self) -> float:
        """Smooth ease-in animation for menu opening."""
        if self.tempo_abertura < self.max_tempo:
            self.tempo_abertura += 1
        progresso = min(self.tempo_abertura / self.max_tempo, 1.0)
        # Ease-out quad
        return 1 - (1 - progresso) ** 2
    
    def desenhar(self, tela: pygame.Surface, fonte: pygame.font.Font) -> None:
        """Draw animated menu with current state."""
        progresso = self.animar_abertura()
        
        # Draw semi-transparent background
        overlay = pygame.Surface((tela.get_width(), tela.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(180 * progresso)))
        tela.blit(overlay, (0, 0))
        
        # Calculate menu size
        altura_titulo = 40
        altura_opcao = 35
        altura = altura_titulo + (len(self.opcoes) * altura_opcao) + 20
        largura = 400
        
        # Smooth position interpolation
        alpha = int(255 * progresso)
        menu_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (40, 40, 50, int(220 * progresso)), menu_surface.get_rect(), border_radius=10)
        
        # Draw title
        render_titulo = fonte.render(self.titulo, True, COR_TEXTO)
        menu_surface.blit(render_titulo, (20, 10))
        
        # Draw options with highlight
        for i, opcao in enumerate(self.opcoes):
            y_pos = altura_titulo + i * altura_opcao + 10
            
            if i == self.selecionada:
                # Highlight selected option
                pygame.draw.rect(menu_surface, (100, 150, 200, int(150 * progresso)), 
                               (10, y_pos, largura - 20, 30), border_radius=5)
                cor_opcao = (255, 255, 100)
            else:
                cor_opcao = COR_TEXTO
            
            render_opcao = fonte.render(opcao, True, cor_opcao)
            menu_surface.blit(render_opcao, (25, y_pos + 5))
        
        # Blit with fade
        tela.blit(menu_surface, (self.x, self.y))
    
    def proxima(self) -> None:
        """Select next option."""
        self.selecionada = (self.selecionada + 1) % len(self.opcoes)
    
    def anterior(self) -> None:
        """Select previous option."""
        self.selecionada = (self.selecionada - 1) % len(self.opcoes)
    
    def obter_selecionada(self) -> str:
        """Return selected option."""
        return self.opcoes[self.selecionada]


class BarraProgresso:
    """Visual progress bar with animation."""
    
    def __init__(self, largura: int = 200, altura: int = 20, cor_cheia: tuple = (0, 200, 100), cor_vazia: tuple = (100, 100, 100)):
        self.largura = largura
        self.altura = altura
        self.cor_cheia = cor_cheia
        self.cor_vazia = cor_vazia
        self.valor = 0.5
        self.valor_alvo = 0.5
        
    def atualizar(self, novo_valor: float, velocidade: float = 0.1) -> None:
        """Update progress bar with smooth animation toward target."""
        self.valor_alvo = max(0, min(novo_valor, 1.0))
        self.valor += (self.valor_alvo - self.valor) * velocidade
    
    def desenhar(self, tela: pygame.Surface, x: int, y: int, rotulo: str = "") -> None:
        """Draw progress bar."""
        # Background
        pygame.draw.rect(tela, self.cor_vazia, (x, y, self.largura, self.altura), border_radius=5)
        
        # Filled portion
        barra_cheia = int(self.largura * self.valor)
        if barra_cheia > 0:
            pygame.draw.rect(tela, self.cor_cheia, (x, y, barra_cheia, self.altura), border_radius=5)
        
        # Border
        pygame.draw.rect(tela, (200, 200, 200), (x, y, self.largura, self.altura), 2, border_radius=5)
        
        # Label
        if rotulo:
            fonte = pygame.font.SysFont("constantia", 14)
            texto = fonte.render(rotulo, True, (255, 255, 255))
            tela.blit(texto, (x + 5, y + 3))


class TooltipSistema:
    """Dynamic tooltip system for UI elements."""
    
    def __init__(self):
        self.tooltip_atual = ""
        self.tempo_espera = 0
        self.max_tempo_espera = 30  # Frames before showing
        
    def atualizar_tooltip(self, novo_tooltip: str) -> None:
        """Update current tooltip."""
        if novo_tooltip != self.tooltip_atual:
            self.tooltip_atual = novo_tooltip
            self.tempo_espera = 0
        else:
            self.tempo_espera = min(self.tempo_espera + 1, self.max_tempo_espera)
    
    def desenhar_tooltip(self, tela: pygame.Surface, x: int, y: int, fonte: pygame.font.Font) -> None:
        """Draw tooltip if ready."""
        if self.tempo_espera < self.max_tempo_espera or not self.tooltip_atual:
            return
        
        # Render tooltip text
        linhas = self.tooltip_atual.split('\n')
        labels = [fonte.render(linha, True, (255, 255, 200)) for linha in linhas]
        
        largura = max(l.get_width() for l in labels) + 16
        altura = sum(l.get_height() for l in labels) + 12
        
        # Draw background
        tooltip_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (30, 30, 30, 220), tooltip_surface.get_rect(), border_radius=5)
        pygame.draw.rect(tooltip_surface, (200, 200, 100), tooltip_surface.get_rect(), 1, border_radius=5)
        
        # Draw text
        y_offset = 6
        for label in labels:
            tooltip_surface.blit(label, (8, y_offset))
            y_offset += label.get_height()
        
        # Position and blit
        tooltip_x = max(0, min(x, tela.get_width() - largura - 10))
        tooltip_y = max(0, min(y - altura - 5, tela.get_height() - altura - 5))
        tela.blit(tooltip_surface, (tooltip_x, tooltip_y))


class PainelInventarioVisual:
    """Enhanced visual inventory panel."""
    
    def __init__(self, width: int = 300, height: int = 400):
        self.largura = width
        self.altura = height
        self.items = []
        self.scroll_offset = 0
        
    def adicionar_item(self, nome: str, quantidade: int, descricao: str = "") -> None:
        """Add item to inventory."""
        self.items.append({
            'nome': nome,
            'quantidade': quantidade,
            'descricao': descricao,
        })
    
    def desenhar(self, tela: pygame.Surface, x: int, y: int, fonte_pequeno: pygame.font.Font, fonte_normal: pygame.font.Font) -> None:
        """Draw inventory panel."""
        # Background panel
        painel = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        pygame.draw.rect(painel, (40, 30, 50, 200), painel.get_rect(), border_radius=8)
        pygame.draw.rect(painel, (150, 120, 180), painel.get_rect(), 2, border_radius=8)
        
        # Title
        titulo = fonte_normal.render("Inventário", True, (200, 200, 100))
        painel.blit(titulo, (10, 8))
        
        # Items
        y_offset = 40
        for item in self.items:
            # Item background
            if y_offset + 30 < self.altura - 10:
                pygame.draw.rect(painel, (60, 40, 80, 150), (8, y_offset, self.largura - 16, 28), border_radius=4)
                
                # Item name and quantity
                texto_item = f"{item['nome']} x{item['quantidade']}"
                render = fonte_pequeno.render(texto_item, True, (220, 200, 150))
                painel.blit(render, (15, y_offset + 5))
                
                y_offset += 32
        
        tela.blit(painel, (x, y))


class IndicadorSocial:
    """Visual indicator for NPC relationships and emotions."""
    
    def __init__(self, npc_nome: str, coracao: int = 0, emocao: str = "Neutro"):
        self.npc_nome = npc_nome
        self.coracao = coracao  # 0-10
        self.emocao = emocao
        self.pulso = 0
        
    def atualizar(self) -> None:
        """Update pulse animation for hearts."""
        self.pulso = (self.pulso + 1) % 60
    
    def desenhar(self, tela: pygame.Surface, x: int, y: int, fonte: pygame.font.Font) -> None:
        """Draw NPC relationship indicator."""
        # NPC Name
        nome_render = fonte.render(self.npc_nome, True, (255, 200, 100))
        tela.blit(nome_render, (x, y))
        
        # Hearts
        for i in range(10):
            cor = (200, 80, 80) if i < self.coracao else (100, 100, 100)
            
            # Simple heart shape animation
            pulse = 1.0 + 0.1 * (1 if i < self.coracao and self.pulso < 30 else 0)
            tamanho = int(8 * pulse)
            
            pygame.draw.circle(tela, cor, (x + 5 + i * 14, y + 25), tamanho)
        
        # Emotion label
        emocao_render = fonte.render(f"({self.emocao})", True, (200, 200, 200))
        tela.blit(emocao_render, (x, y + 40))
