"""Interface Aprimorada - novos menus e telas UI"""
import pygame
from typing import Optional, Tuple
from .calendar import Calendario
from .weather import SistemaClima
from .fishing import MiniGamePesca
from .farming import FarmManager
from .npc_relations import GerenciadorRelacoes
from .quests import QuestManager
from .config import COR_TEXTO, COR_BG, COR_HUD


def renderizar_calendario_expandido(tela: pygame.Surface, calendario: Calendario, 
                                    rect: pygame.Rect) -> None:
    """Renderiza calendário interativo expandido"""
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=10)
    pygame.draw.rect(tela, (66, 89, 102), rect, 2, border_radius=10)
    
    fonte_titulo = pygame.font.SysFont("cambria", 20, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 14)
    
    # Título
    titulo = fonte_titulo.render(f"{calendario.estacao_nome} - Ano {calendario.ano}", 
                                 True, COR_TEXTO)
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Data atual
    data_texto = fonte_normal.render(f"Dia {calendario.dia_mes} de 28", True, COR_TEXTO)
    tela.blit(data_texto, (rect.x + 15, rect.y + 35))
    
    # Fase da lua
    fase_lua = fonte_normal.render(calendario.get_lua_fase(), True, (200, 150, 100))
    tela.blit(fase_lua, (rect.x + 15, rect.y + 55))
    
    # Próximos festivais
    festivais = calendario.obter_proximos_festivais(3)
    y_offset = 75
    for festival in festivais:
        texto_festival = fonte_normal.render(
            f"🎉 {festival.nome} (Dia {festival.dia_mes})", 
            True, (200, 200, 150)
        )
        tela.blit(texto_festival, (rect.x + 15, rect.y + y_offset))
        y_offset += 20
    
    # Barra de progressão da estação
    barra_y = rect.y + rect.height - 25
    barra_rect = pygame.Rect(rect.x + 15, barra_y, rect.width - 30, 12)
    pygame.draw.rect(tela, (50, 50, 50), barra_rect, border_radius=6)
    
    # Preenchimento
    progresso = calendario.dia_mes / 28
    preenchida = barra_rect.inflate(-2, -2)
    preenchida.width = int((barra_rect.width - 4) * progresso)
    pygame.draw.rect(tela, (100, 200, 100), preenchida, border_radius=5)
    
    pct = fonte_normal.render(f"{int(progresso * 100)}%", True, COR_TEXTO)
    tela.blit(pct, (rect.right - 40, barra_y + 2))


def renderizar_clima_detalhado(tela: pygame.Surface, clima: SistemaClima, 
                               rect: pygame.Rect) -> None:
    """Renderiza informações detalhadas do clima"""
    info_clima = clima.obter_info_clima()
    
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=10)
    pygame.draw.rect(tela, (66, 89, 102), rect, 2, border_radius=10)
    
    fonte_titulo = pygame.font.SysFont("cambria", 18, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 13)
    
    # Clima e emoji
    titulo = fonte_titulo.render(
        f"{info_clima['emoji']} {info_clima['descricao']}", 
        True, COR_TEXTO
    )
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Dados
    y = rect.y + 35
    dados = [
        f"🌡️ Temperatura: {info_clima['temperatura']}°C",
        f"💧 Umidade: {info_clima['umidade']}%",
        f"💨 Vento: {info_clima['vento']} km/h",
        f"👁️ Visibilidade: {info_clima['visibilidade']}%",
    ]
    
    for dado in dados:
        texto = fonte_normal.render(dado, True, (200, 200, 200))
        tela.blit(texto, (rect.x + 15, y))
        y += 18


def renderizar_painel_fazenda(tela: pygame.Surface, farm: FarmManager, 
                             rect: pygame.Rect) -> None:
    """Renderiza painel com informações da fazenda"""
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=10)
    pygame.draw.rect(tela, (66, 89, 102), rect, 2, border_radius=10)
    
    fonte_titulo = pygame.font.SysFont("cambria", 18, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 14)
    
    # Título
    titulo = fonte_titulo.render("🌾 Sua Fazenda", True, COR_TEXTO)
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Dados
    y = rect.y + 35
    dados = [
        f"Dinheiro: {farm.dinheiro} 💰",
        f"Nível: {farm.nivel_agricultura}",
        f"EXP: {farm.exp_agricultura}",
        f"Celulas cultivadas: {len(farm.celulas_cultivo)}",
        f"Sementes em estoque: {sum(farm.sementes_inventario.values())}",
    ]
    
    for dado in dados:
        texto = fonte_normal.render(dado, True, (200, 200, 200))
        tela.blit(texto, (rect.x + 15, y))
        y += 20


def renderizar_relacoes_npcs(tela: pygame.Surface, relacoes: GerenciadorRelacoes, 
                             rect: pygame.Rect, max_npcs: int = 5) -> None:
    """Renderiza painel de relacionamentos com NPCs"""
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=10)
    pygame.draw.rect(tela, (66, 89, 102), rect, 2, border_radius=10)
    
    fonte_titulo = pygame.font.SysFont("cambria", 16, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 12)
    
    # Título
    titulo = fonte_titulo.render("💝 Relacionamentos", True, COR_TEXTO)
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Listar NPCs com mais corações
    relacoes_ordenadas = sorted(
        relacoes.relacoes.values(), 
        key=lambda r: r.coracao, 
        reverse=True
    )[:max_npcs]
    
    y = rect.y + 35
    for rel in relacoes_ordenadas:
        # Nome e corações
        coracao_str = "❤️" * max(0, rel.coracao) + "🤍" * (10 - max(0, rel.coracao))
        texto_nome = fonte_normal.render(f"{rel.npc_nome}: {coracao_str}", 
                                        True, (200, 150, 220))
        tela.blit(texto_nome, (rect.x + 15, y))
        y += 18
    
    # Marido/Esposa se casado
    if relacoes.casado_com:
        relacao_marido = relacoes.relacoes.get(relacoes.casado_com)
        if relacao_marido:
            texto_casado = fonte_normal.render(
                f"💒 Casado(a) com {relacao_marido.npc_nome}", 
                True, (255, 150, 150)
            )
            tela.blit(texto_casado, (rect.x + 15, y))


def renderizar_quests_painel(tela: pygame.Surface, quest_manager: QuestManager, 
                            rect: pygame.Rect, max_quests: int = 4) -> None:
    """Renderiza painel com quests ativas"""
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=10)
    pygame.draw.rect(tela, (66, 89, 102), rect, 2, border_radius=10)
    
    fonte_titulo = pygame.font.SysFont("cambria", 16, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 11)
    
    # Título
    titulo = fonte_titulo.render("📋 Quests Ativas", True, COR_TEXTO)
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Listar quests ativas
    quests_ativas = quest_manager.obter_quests_ativas()[:max_quests]
    
    if not quests_ativas:
        texto_vazio = fonte_normal.render("Nenhuma quest ativa", True, (150, 150, 150))
        tela.blit(texto_vazio, (rect.x + 15, rect.y + 35))
        return
    
    y = rect.y + 35
    for quest in quests_ativas:
        # Nome da quest
        texto_nome = fonte_normal.render(f"> {quest.nome}", True, (200, 220, 100))
        tela.blit(texto_nome, (rect.x + 15, y))
        y += 15
        
        # Progresso
        progresso_str = f"{quest.quantidade_completa}/{quest.objetivo_quantidade}"
        texto_prog = fonte_normal.render(f"  Progresso: {progresso_str}", 
                                        True, (150, 200, 150))
        tela.blit(texto_prog, (rect.x + 15, y))
        y += 18


def renderizar_hud_expandida(tela: pygame.Surface, 
                            calendario: Calendario,
                            clima: SistemaClima,
                            farm: FarmManager,
                            relacoes: GerenciadorRelacoes,
                            quest_manager: QuestManager,
                            rect_disponivel: pygame.Rect) -> None:
    """Renderiza HUD completo com todas as informações"""
    
    # Dividir área disponível em seções
    col_width = rect_disponivel.width // 2
    row_height = rect_disponivel.height // 3
    
    # Linha 1
    renderizar_calendario_expandido(
        tela, calendario,
        pygame.Rect(rect_disponivel.x, rect_disponivel.y, col_width - 5, row_height - 5)
    )
    
    renderizar_clima_detalhado(
        tela, clima,
        pygame.Rect(rect_disponivel.x + col_width + 5, rect_disponivel.y, 
                   col_width - 5, row_height - 5)
    )
    
    # Linha 2
    renderizar_painel_fazenda(
        tela, farm,
        pygame.Rect(rect_disponivel.x, rect_disponivel.y + row_height + 5, 
                   col_width - 5, row_height - 5)
    )
    
    renderizar_relacoes_npcs(
        tela, relacoes,
        pygame.Rect(rect_disponivel.x + col_width + 5, 
                   rect_disponivel.y + row_height + 5,
                   col_width - 5, row_height - 5)
    )
    
    # Linha 3 - Quests
    renderizar_quests_painel(
        tela, quest_manager,
        pygame.Rect(rect_disponivel.x, rect_disponivel.y + (row_height + 5) * 2, 
                   rect_disponivel.width - 10, row_height - 10)
    )


def renderizar_tela_pesca(tela: pygame.Surface, pesca: MiniGamePesca, 
                         rect: pygame.Rect) -> None:
    """Renderiza minigame de pesca"""
    pygame.draw.rect(tela, (20, 60, 100), rect)  # Água
    pygame.draw.rect(tela, (66, 89, 102), rect, 3)
    
    fonte_titulo = pygame.font.SysFont("cambria", 20, bold=True)
    fonte_normal = pygame.font.SysFont("constantia", 14)
    
    info = pesca.obter_info_peixe_atual()
    
    if not info:
        texto = fonte_titulo.render("Nenhum peixe na linha", True, COR_TEXTO)
        tela.blit(texto, (rect.centerx - texto.get_width() // 2, 
                         rect.centery - texto.get_height() // 2))
        return
    
    # Informações do peixe
    titulo = fonte_titulo.render(info["nome"], True, (100, 200, 255))
    tela.blit(titulo, (rect.x + 15, rect.y + 10))
    
    # Raridade
    cores_raridade = {
        "comum": (150, 150, 150),
        "incomum": (100, 200, 100),
        "raro": (255, 200, 100),
        "lendario": (255, 100, 200),
    }
    cor_raridade = cores_raridade.get(info["raridade"], COR_TEXTO)
    texto_raridade = fonte_normal.render(f"Raridade: {info['raridade']}", 
                                        True, cor_raridade)
    tela.blit(texto_raridade, (rect.x + 15, rect.y + 35))
    
    # Barra de pesca (peixe vs anzol)
    barra_altura = 30
    barra_y = rect.centery - barra_altura // 2
    barra_rect = pygame.Rect(rect.x + 50, barra_y, rect.width - 100, barra_altura)
    pygame.draw.rect(tela, (60, 60, 80), barra_rect)
    pygame.draw.rect(tela, (100, 100, 120), barra_rect, 1)
    
    # Peixe
    peixe_x = barra_rect.x + (barra_rect.width * info["posicao_peixe"])
    pygame.draw.circle(tela, (255, 120, 0), (int(peixe_x), int(barra_rect.centery)), 6)
    
    # Anzol
    anzol_x = barra_rect.x + (barra_rect.width * info["posicao_anzol"])
    pygame.draw.circle(tela, (200, 200, 100), (int(anzol_x), int(barra_rect.centery)), 5)
    
    # Durabilidade da linha
    y_durabilidade = rect.bottom - 50
    barra_durabilidade = pygame.Rect(rect.x + 50, y_durabilidade, 
                                     rect.width - 100, 15)
    pygame.draw.rect(tela, (50, 50, 50), barra_durabilidade)
    
    durabilidade_preenchida = barra_durabilidade.copy()
    durabilidade_preenchida.width = int((info["durabilidade_linha"]/100) * barra_durabilidade.width)
    cor_durabilidade = (100, 200, 100) if info["durabilidade_linha"] > 50 else (200, 100, 100)
    pygame.draw.rect(tela, cor_durabilidade, durabilidade_preenchida)
    
    texto_durabilidade = fonte_normal.render(f"Linha: {info['durabilidade_linha']:.0f}%", 
                                            True, COR_TEXTO)
    tela.blit(texto_durabilidade, (barra_durabilidade.right + 10, y_durabilidade))


def renderizar_status_plantacao(tela: pygame.Surface, planta, rect: pygame.Rect) -> None:
    """Renderiza status de uma plantação"""
    pygame.draw.rect(tela, COR_HUD, rect, border_radius=8)
    pygame.draw.rect(tela, (100, 150, 100), rect, 2, border_radius=8)
    
    fonte_normal = pygame.font.SysFont("constantia", 12)
    
    # Nome da planta
    texto_nome = fonte_normal.render(planta.tipo_planta.title(), True, COR_TEXTO)
    tela.blit(texto_nome, (rect.x + 8, rect.y + 5))
    
    # Barra de crescimento
    barra_rect = pygame.Rect(rect.x + 8, rect.y + 22, rect.width - 16, 12)
    pygame.draw.rect(tela, (50, 50, 50), barra_rect, border_radius=4)
    
    preenchida = barra_rect.copy()
    preenchida.width = int(preenchida.width * (planta.percentual_crescimento / 100))
    pygame.draw.rect(tela, (100, 200, 100), preenchida, border_radius=4)
    
    pct_texto = fonte_normal.render(f"{planta.percentual_crescimento}%", 
                                   True, COR_TEXTO)
    tela.blit(pct_texto, (rect.right - 35, rect.y + 5))
