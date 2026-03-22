from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import math
import time
from typing import Optional

import pygame

from .assets import obter_assets
from .config import ALTURA_CHAT, ALTURA_HUD, COR_AVISO, COR_TEXTO, TAMANHO_CELULA
from .opcoes import RESOLUCOES, carregar_configuracoes, escolher_display_para_config, resolucao_atual, salvar_configuracoes
from .personagens import obter_banco_personagens
from .servicos import aplicar_lore_personagem, enriquecer_lore_personagem_base, listar_saves, normalizar_lore_personagem, perfil_tem_lore_enriquecida, obter_info_save, deletar_save, renomear_save

# Sprite system imports
try:
    from .sprite_renderer import TerrainRenderer, HouseVisualizer
    from .sprite_system import get_sprite_manager
    SPRITE_RENDERING_AVAILABLE = True
except ImportError:
    SPRITE_RENDERING_AVAILABLE = False
    TerrainRenderer = None
    HouseVisualizer = None


def calcular_camera(mundo, quadrados_x: int, quadrados_y: int) -> tuple[int, int, int, int]:
    celulas_largura = max(10, quadrados_x)
    celulas_altura = max(8, quadrados_y)
    metade_l = celulas_largura // 2
    metade_a = celulas_altura // 2
    camera_x = max(0, min(mundo.tamanho - celulas_largura, mundo.humano[0] - metade_l))
    camera_y = max(0, min(mundo.tamanho - celulas_altura, mundo.humano[1] - metade_a))
    return camera_x, camera_y, celulas_largura, celulas_altura


def quebrar_texto(fonte: pygame.font.Font, texto: str, largura_max: int) -> list[str]:
    palavras = texto.split()
    if not palavras:
        return [""]
    linhas: list[str] = []
    atual = palavras[0]
    for palavra in palavras[1:]:
        teste = f"{atual} {palavra}"
        if fonte.size(teste)[0] <= largura_max:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    linhas.append(atual)
    return linhas


def _fontes() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    return (
        pygame.font.SysFont("constantia", 17),
        pygame.font.SysFont("constantia", 21, bold=True),
        pygame.font.SysFont("cambria", 28, bold=True),
        pygame.font.SysFont("cambria", 42, bold=True),
    )


def _desenhar_fundo_mistico(tela: pygame.Surface, tick_base: int = 0) -> None:
    altura = tela.get_height()
    largura = tela.get_width()
    for y in range(altura):
        mistura = y / max(1, altura - 1)
        cor = (
            int(18 + 32 * mistura),
            int(24 + 28 * mistura),
            int(32 + 40 * mistura),
        )
        pygame.draw.line(tela, cor, (0, y), (largura, y))

    for indice in range(16):
        x = int((indice * 91 + tick_base * 3) % (largura + 80)) - 40
        raio = 120 + (indice % 5) * 18
        cor = (36 + indice * 4, 52 + indice * 2, 68 + indice * 3, 35)
        brilho = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(brilho, cor, (raio, raio), raio)
        tela.blit(brilho, (x, 18 + (indice * 37) % max(120, altura - 220)))


def _desenhar_textura_grama(tela: pygame.Surface, rect: pygame.Rect, escuro: tuple[int, int, int], claro: tuple[int, int, int]) -> None:
    pygame.draw.rect(tela, escuro, rect)
    for i in range(0, rect.width, 6):
        altura = 4 + ((rect.x + rect.y + i) // 7) % 6
        x = rect.x + i + 2
        pygame.draw.line(tela, claro, (x, rect.bottom - 2), (x + 1, rect.bottom - altura), 2)


def _desenhar_agua(tela: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(tela, (54, 112, 168), rect)
    for i in range(0, rect.width, 7):
        pygame.draw.arc(tela, (134, 214, 236), pygame.Rect(rect.x + i, rect.y + 6, 10, 8), math.pi, math.tau, 1)
        pygame.draw.arc(tela, (175, 235, 249), pygame.Rect(rect.x + i - 2, rect.y + 17, 12, 8), math.pi, math.tau, 1)


def _desenhar_montanha(tela: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(tela, (96, 88, 96), rect)
    pontos = [
        (rect.x + 2, rect.bottom - 2),
        (rect.centerx - 4, rect.y + 12),
        (rect.centerx + 5, rect.y + 6),
        (rect.right - 2, rect.bottom - 2),
    ]
    pygame.draw.polygon(tela, (148, 144, 154), pontos)
    pygame.draw.polygon(tela, (220, 220, 224), [pontos[1], (rect.centerx, rect.y + 4), pontos[2]])


def _desenhar_arvore(tela: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(tela, (128, 90, 52), pygame.Rect(rect.centerx - 3, rect.centery + 2, 6, 12))
    pygame.draw.circle(tela, (40, 122, 72), (rect.centerx, rect.centery - 1), 11)
    pygame.draw.circle(tela, (66, 165, 98), (rect.centerx - 6, rect.centery - 2), 7)
    pygame.draw.circle(tela, (66, 165, 98), (rect.centerx + 7, rect.centery - 5), 6)


def _desenhar_recurso(tela: pygame.Surface, rect: pygame.Rect, cor: tuple[int, int, int], brilho: tuple[int, int, int]) -> None:
    miolo = rect.inflate(-18, -18)
    pygame.draw.ellipse(tela, cor, miolo)
    pygame.draw.ellipse(tela, brilho, miolo.inflate(-6, -8))


def _desenhar_casa(tela: pygame.Surface, rect: pygame.Rect, castelo: bool = False, templo: bool = False) -> None:
    corpo = pygame.Rect(rect.x + 8, rect.y + 14, rect.width - 16, rect.height - 16)
    if castelo:
        pygame.draw.rect(tela, (140, 146, 156), corpo)
        pygame.draw.rect(tela, (172, 178, 190), corpo, 2)
        pygame.draw.rect(tela, (116, 122, 134), pygame.Rect(rect.x + 6, rect.y + 6, 10, 14))
        pygame.draw.rect(tela, (116, 122, 134), pygame.Rect(rect.right - 16, rect.y + 6, 10, 14))
    else:
        pygame.draw.polygon(
            tela,
            (136, 68, 52) if not templo else (184, 148, 78),
            [(rect.x + 5, rect.y + 18), (rect.centerx, rect.y + 4), (rect.right - 5, rect.y + 18)],
        )
        pygame.draw.rect(tela, (190, 156, 112) if not templo else (218, 204, 162), corpo)
    porta = pygame.Rect(corpo.centerx - 4, corpo.bottom - 10, 8, 10)
    pygame.draw.rect(tela, (92, 58, 38), porta)
    pygame.draw.rect(tela, (124, 180, 210), pygame.Rect(corpo.x + 5, corpo.y + 6, 7, 6))
    if templo:
        pygame.draw.line(tela, (236, 232, 214), (rect.centerx, rect.y + 6), (rect.centerx, rect.y + 20), 2)
        pygame.draw.line(tela, (236, 232, 214), (rect.centerx - 4, rect.y + 10), (rect.centerx + 4, rect.y + 10), 2)


def _desenhar_inimigo(tela: pygame.Surface, rect: pygame.Rect) -> None:
    corpo = rect.inflate(-18, -12)
    pygame.draw.ellipse(tela, (96, 18, 34), corpo)
    pygame.draw.rect(tela, (160, 38, 54), pygame.Rect(corpo.x + 4, corpo.y + 6, corpo.width - 8, corpo.height - 8))
    pygame.draw.circle(tela, (244, 224, 186), (corpo.centerx, corpo.y + 7), 4)
    pygame.draw.circle(tela, (255, 220, 64), (corpo.centerx - 2, corpo.y + 7), 1)
    pygame.draw.circle(tela, (255, 220, 64), (corpo.centerx + 2, corpo.y + 7), 1)


def _desenhar_animal(tela: pygame.Surface, rect: pygame.Rect, especie: str) -> None:
    base = (186, 150, 104)
    if especie in {"lobo", "raposa", "lince"}:
        base = (160, 96, 72)
    elif especie in {"coruja"}:
        base = (130, 118, 96)
    corpo = pygame.Rect(rect.x + 10, rect.y + 18, rect.width - 18, rect.height - 20)
    pygame.draw.ellipse(tela, base, corpo)
    pygame.draw.circle(tela, tuple(min(255, c + 28) for c in base), (corpo.right - 4, corpo.y + 7), 5)
    pygame.draw.circle(tela, (30, 24, 22), (corpo.right - 5, corpo.y + 7), 1)


# Sprite rendering helper function
def _renderizar_terreno_com_sprites(tela: pygame.Surface, rect: pygame.Rect, 
                                    bioma: str, x: int, y: int,
                                    terrain_renderer: TerrainRenderer) -> bool:
    """Tenta renderizar terreno com sprites. Retorna True se bem-sucedido."""
    if not SPRITE_RENDERING_AVAILABLE or terrain_renderer is None:
        return False
    
    try:
        # Map bioma names to sprite types
        bioma_map = {
            "agua": "agua",
            "montanha": "montanha",
            "arvore": "floresta",
            "maldito": "cave",
            "tesouro": "grass",
            "comida": "grass",
            None: "grass",
        }
        
        sprite_bioma = bioma_map.get(bioma, bioma or "grass")
        terrain_renderer.render_terrain(tela, rect, sprite_bioma, x, y)
        return True
    except Exception:
        return False


def _renderizar_celula_fazenda_com_sprites(tela: pygame.Surface, rect: pygame.Rect,
                                          celula,
                                          terrain_renderer: TerrainRenderer) -> bool:
    """Renderiza célula de fazenda com sprites. Retorna True se bem-sucedido."""
    if not SPRITE_RENDERING_AVAILABLE or terrain_renderer is None:
        return False
    
    try:
        plant_type = celula.planta_atual.tipo_planta if celula.planta_atual else None
        growth_stage = celula.planta_atual.estágio_sprite if celula.planta_atual else 0
        
        terrain_renderer.render_farm_cell(
            tela, rect, 
            celula.sprite_solo,
            plant_type,
            growth_stage
        )
        return True
    except Exception:
        return False


def _renderizar_sprite_personagem(
    tela: pygame.Surface,
    rect: pygame.Rect,
    perfil: dict,
    direcao: str,
    tick: int,
    animar: bool = False,
) -> None:
    banco = obter_banco_personagens()
    sprite = banco.compor_sprite(perfil, direcao=direcao, tick=tick, escala=2, animar=animar)
    bbox = sprite.get_bounding_rect()
    if bbox.width > 0 and bbox.height > 0:
        sprite = sprite.subsurface(bbox).copy()
    alvo_w = max(8, rect.width - 6)
    alvo_h = max(8, rect.height - 4)
    escala = min(alvo_w / max(1, sprite.get_width()), alvo_h / max(1, sprite.get_height()))
    novo_w = max(8, int(sprite.get_width() * escala))
    novo_h = max(8, int(sprite.get_height() * escala))
    sprite = pygame.transform.scale(sprite, (novo_w, novo_h))
    destino = sprite.get_rect(midbottom=(rect.centerx, rect.bottom - 2))
    tela.blit(sprite, destino)


def renderizar_menu_ajuda(tela: pygame.Surface) -> None:
    """Renderiza menu de ajuda (F1) responsivo para diferentes tamanhos de monitor."""
    assets = obter_assets()
    fonte_texto, fonte_titulo, fonte_subtitulo, _ = _fontes()
    
    # Layout responsivo
    margem = int(tela.get_width() * 0.03)  # 3% das bordas
    largura = tela.get_width() - (margem * 2)
    altura = tela.get_height() - (margem * 2)
    area = pygame.Rect(margem, margem, largura, altura)
    
    assets.painel(tela, area, estilo="beige")
    
    titulo = "AJUDA - Controles e Guia Rápido"
    txt_titulo = fonte_subtitulo.render(titulo, True, (74, 48, 36))
    tela.blit(txt_titulo, (area.centerx - txt_titulo.get_width() // 2, area.y + 15))
    
    x_col1 = area.x + margem
    x_col2 = area.x + area.width // 2 + margem // 2
    y = area.y + 50
    linha_altura = 18
    
    # Seção 1: Movimento
    tela.blit(fonte_titulo.render("MOVIMENTO", True, (146, 98, 70)), (x_col1, y))
    y += 22
    movimentos = [("W", "Cima"), ("A", "Esq"), ("S", "Baixo"), ("D", "Dir")]
    for i, (tecla, desc) in enumerate(movimentos):
        col_x = x_col1 if i < 2 else x_col2
        col_y = y + (i % 2) * linha_altura
        tela.blit(fonte_titulo.render(f"[{tecla}]", True, (184, 100, 60)), (col_x, col_y))
        tela.blit(fonte_texto.render(desc, True, (112, 74, 48)), (col_x + 45, col_y))
    
    y += 50
    
    # Seção 2: Ações Gerais
    tela.blit(fonte_titulo.render("ACOES", True, (146, 98, 70)), (x_col1, y))
    y += 22
    acoes = [("G", "Coletar"), ("E", "Escavar"), ("SPACE", "Atacar"), ("Z", "Descansar"),
             ("T", "Animal"), ("F", "Contextual"), ("B", "Backstory"), ("Y", "Conversar")]
    for i, (tecla, desc) in enumerate(acoes):
        col_x = x_col1 if i < 4 else x_col2
        col_y = y + (i % 4) * linha_altura
        tela.blit(fonte_titulo.render(f"[{tecla}]", True, (184, 100, 60)), (col_x, col_y))
        tela.blit(fonte_texto.render(desc, True, (112, 74, 48)), (col_x + 70, col_y))
    
    y += 85
    
    # Seção 3: Menus
    tela.blit(fonte_titulo.render("MENUS", True, (146, 98, 70)), (x_col1, y))
    y += 22
    menus = [("I", "Inventário"), ("R", "Chat"), ("F1", "Ajuda"), ("F5", "Salvar"),
             ("F7", "Configurações"), ("ESC", "Pausa"), ("F2", "Lore"), ("H", "Dungeon")]
    for i, (tecla, desc) in enumerate(menus):
        col_x = x_col1 if i < 4 else x_col2
        col_y = y + (i % 4) * linha_altura
        tela.blit(fonte_titulo.render(f"[{tecla}]", True, (184, 100, 60)), (col_x, col_y))
        tela.blit(fonte_texto.render(desc, True, (112, 74, 48)), (col_x + 65, col_y))
    
    y += 85
    
    # Seção 4: Dicas rápidas
    tela.blit(fonte_titulo.render("DICAS", True, (146, 98, 70)), (x_col1, y))
    y += 22
    dicas = [
        "• TAB = Próximo modo | SHIFT+TAB = Modo anterior",
        "• P = Pescar | H = Dungeon | T = Trabalho",
        "• Y = Conversar | B = Backstory | F1 = Ajuda",
        "• R = Chat com IA | F5/F6 = Salvar jogo",
    ]
    for dica in dicas:
        if y < area.bottom - 40:
            tela.blit(fonte_texto.render(dica, True, (112, 74, 48)), (x_col1, y))
            y += 18
    
    # Rodapé
    instrucoes = "ESC para fechar | F7 para Configurações"
    txt_inst = fonte_texto.render(instrucoes, True, (146, 98, 70))
    tela.blit(txt_inst, (area.centerx - txt_inst.get_width() // 2, area.bottom - 25))


def renderizar_menu_lore(tela: pygame.Surface, mundo, raphael_memoria) -> None:
    """Renderiza menu de lore (F2) mostrando mundo e lore do personagem."""
    assets = obter_assets()
    fonte_texto, fonte_titulo, fonte_subtitulo, _ = _fontes()
    
    area = pygame.Rect(60, 40, tela.get_width() - 120, tela.get_height() - 100)
    assets.painel(tela, area, estilo="beige")
    
    titulo = "O MUNDO E SEU DESTINO"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    col1 = pygame.Rect(area.x + 20, area.y + 60, area.width // 2 - 30, area.height - 120)
    col2 = pygame.Rect(area.centerx + 10, area.y + 60, area.width // 2 - 30, area.height - 120)
    
    assets.painel(tela, col1, estilo="brown", inset=True, alpha=230)
    assets.painel(tela, col2, estilo="brown", inset=True, alpha=230)
    
    # Coluna 1: Lore do Mundo
    tela.blit(fonte_titulo.render("LORE DO MUNDO", True, (245, 233, 210)), (col1.x + 10, col1.y + 8))
    
    world_lore = mundo.world_lore if hasattr(mundo, 'world_lore') else {}
    eixo = world_lore.get("eixo_historico", "O mundo passa por transformacoes desconhecidas.")
    era = world_lore.get("era_inicial", 1500)
    conflito = world_lore.get("conflito_principal", "Conflito desconhecido")
    lugar = world_lore.get("lugar_mstico", {}).get("descricao", "Um lugar esquecido")
    
    lore_linhas = quebrar_texto(fonte_texto, f"Era: {era} | {eixo}", col1.width - 20)
    lore_linhas.append("")
    lore_linhas.extend(quebrar_texto(fonte_texto, f"Conflito: {conflito}", col1.width - 20))
    lore_linhas.append("")
    lore_linhas.extend(quebrar_texto(fonte_texto, f"Lugar Mistico: {lugar}", col1.width - 20))
    
    for i, linha in enumerate(lore_linhas[:7]):
        tela.blit(fonte_texto.render(linha, True, (228, 205, 182)), (col1.x + 10, col1.y + 40 + i * 22))
    
    # Coluna 2: Lore do Personagem
    tela.blit(fonte_titulo.render(f"{mundo.nome_humano}", True, (245, 233, 210)), (col2.x + 10, col2.y + 8))
    
    perfil = mundo.perfil_jogador if hasattr(mundo, 'perfil_jogador') else {}
    profecia = world_lore.get("profecia", "Destino desconhecido")
    legenda = world_lore.get("legenda", "Uma lenda antiga")
    
    info_linhas = [
        f"Idade: {mundo.idade_humano} anos",
        f"",
        f"Profecia: {profecia[:50]}...",
        f"",
        f"Legenda: {legenda[:50]}...",
        f"",
        f"Legado: {perfil.get('legado', 'Desconhecido')[:40]}...",
    ]
    
    for i, linha in enumerate(info_linhas):
        if linha:
            tela.blit(fonte_texto.render(linha, True, (228, 205, 182)), (col2.x + 10, col2.y + 40 + i * 22))
    
    instrucoes = "ESC para fechar | Seu destino ja esta escrito nas cronicas"
    tela.blit(fonte_texto.render(instrucoes, True, (146, 98, 70)), (area.x + 20, area.bottom - 40))


def renderizar_menu_pausa(
    tela: pygame.Surface,
    mundo,
    opcao_selecionada: int = 0,
    tempo_sistema=None,
    historico_chat=None,
    mouse_pos: tuple[int, int] | None = None,
) -> None:
    """Renderiza menu de pausa (ESC) com opcoes."""
    assets = obter_assets()
    fonte_texto, fonte_titulo, fonte_subtitulo, _ = _fontes()
    
    if mouse_pos is None:
        mouse_pos = pygame.mouse.get_pos()
    
    # Escurecer fundo
    overlay = pygame.Surface((tela.get_width(), tela.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    tela.blit(overlay, (0, 0))
    
    area = pygame.Rect(
        tela.get_width() // 2 - 220,
        tela.get_height() // 2 - 200,
        440,
        400
    )
    assets.painel(tela, area, estilo="beige")
    
    titulo = "PAUSADO"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.centerx - fonte_subtitulo.size(titulo)[0] // 2, area.y + 20))
    
    opcoes = [
        "Retomar Jogo",
        "Salvar e Continuar",
        "Salvar Como Novo Save",
        "Mudar Configuracoes",
        "Voltar ao Menu",
        "Sair do Jogo",
    ]
    
    botao_altura = 50
    botao_largura = 340
    espaco = 8
    total_altura = len(opcoes) * botao_altura + (len(opcoes) - 1) * espaco
    inicio_y = area.y + 80
    
    for i, opcao_texto in enumerate(opcoes):
        botao = pygame.Rect(
            area.centerx - botao_largura // 2,
            inicio_y + i * (botao_altura + espaco),
            botao_largura,
            botao_altura
        )
        
        # Check if mouse is hovering or option is selected
        is_hovered = botao.collidepoint(mouse_pos)
        ativo = (i == opcao_selecionada or is_hovered)
        cor_fundo = (184, 100, 60) if ativo else (146, 98, 70)
        cor_texto = (245, 233, 210) if ativo else (200, 170, 140)
        
        pygame.draw.rect(tela, cor_fundo, botao, border_radius=8)
        pygame.draw.rect(tela, (245, 233, 210) if ativo else (112, 74, 48), botao, 3, border_radius=8)
        
        texto = fonte_titulo.render(opcao_texto, True, cor_texto)
        tela.blit(texto, (botao.centerx - texto.get_width() // 2, botao.centery - texto.get_height() // 2))
    
    instrucoes = "Use Setas para navegar | ENTER para selecionar | ESC para cancelar | MOUSE para clicar"
    tela.blit(fonte_texto.render(instrucoes, True, (112, 74, 48)), (area.x + 16, area.bottom - 32))


def renderizar_mundo(
    tela: pygame.Surface,
    mundo,
    fonte_hud: pygame.font.Font,
    fonte_emoji: pygame.font.Font,
    modo: str,
    tempo,
    quadrados_x: int,
    quadrados_y: int,
    modo_escuro: bool = False,
    terrain_renderer: Optional[TerrainRenderer] = None,
    use_sprites: bool = True,
) -> None:
    """Renderiza o mundo com suporte opcional a sprites."""
    del fonte_hud, fonte_emoji
    assets = obter_assets()
    fonte_texto, fonte_titulo, _, _ = _fontes()
    tick_visual = int(tempo.segundos_totais * 8)
    largura_tela, altura_tela = tela.get_size()
    _desenhar_fundo_mistico(tela, tick_visual)
    
    # Initialize terrain renderer if using sprites
    if use_sprites and SPRITE_RENDERING_AVAILABLE and terrain_renderer is None:
        terrain_renderer = TerrainRenderer()

    if modo_escuro:
        sombreado = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
        sombreado.fill((6, 10, 18, 110))
        tela.blit(sombreado, (0, 0))

    if mundo.interior_ativo is not None:
        area = pygame.Rect(90, 54, largura_tela - 180, altura_tela - ALTURA_CHAT - ALTURA_HUD - 72)
        assets.painel(tela, area, estilo="brown" if modo_escuro else "beige")
        interior = area.inflate(-36, -36)
        pygame.draw.rect(tela, (184, 132, 82), interior)
        for x in range(interior.x, interior.right, 18):
            pygame.draw.line(tela, (165, 118, 72), (x, interior.y), (x, interior.bottom), 2)
        titulo = f"Casa da vila: {mundo.interior_ativo}"
        subtitulo = "F para sair | O interior agora usa painel e sprites de RPG"
        tela.blit(fonte_titulo.render(titulo, True, (88, 58, 40)), (area.x + 28, area.y + 18))
        tela.blit(fonte_texto.render(subtitulo, True, (112, 74, 48)), (area.x + 28, area.y + 50))

        moradores = [n for n in mundo.npcs.values() if n.get("casa_id") == mundo.interior_ativo]
        for indice, npc in enumerate(moradores[:6]):
            bx = interior.x + 36 + (indice % 3) * 210
            by = interior.y + 66 + (indice // 3) * 138
            slot = pygame.Rect(bx, by, 160, 106)
            assets.painel(tela, slot, estilo="brown", inset=True, alpha=232)
            retrato = pygame.Rect(slot.x + 10, slot.y + 12, 54, 72)
            _renderizar_sprite_personagem(tela, retrato, npc.get("perfil", {}), "baixo", tick_visual, animar=False)
            tela.blit(fonte_titulo.render(npc["nome"], True, (244, 232, 212)), (slot.x + 70, slot.y + 14))
            tela.blit(fonte_texto.render(f"{npc['papel']} | {npc.get('idade', 18)} anos", True, (228, 205, 182)), (slot.x + 70, slot.y + 42))
            tela.blit(fonte_texto.render(f"Relacao: {npc.get('relacao', 0)}", True, (228, 205, 182)), (slot.x + 70, slot.y + 62))

        hud_y = altura_tela - ALTURA_HUD - ALTURA_CHAT
        hud = pygame.Rect(12, hud_y + 8, largura_tela - 24, ALTURA_HUD - 14)
        assets.painel(tela, hud, estilo="brown")
        linha1 = f"{mundo.nome_humano}, {mundo.idade_humano} anos | HP {int(mundo.hp)}/{int(mundo.hp_maximo)} | Ouro {int(mundo.inventario['ouro'])}"
        linha2 = f"Conhecimento {int(mundo.inventario.get('conhecimento', 0))} | Ano {mundo.ano_atual} | Quests {len(mundo.quests_ativas)}"
        linha3 = f"Evento: {mundo.ultimo_evento}"
        for indice, linha in enumerate((linha1, linha2, linha3)):
            tela.blit(fonte_texto.render(linha, True, (245, 233, 210)), (hud.x + 18, hud.y + 10 + indice * 24))
        return

    camera_x, camera_y, celulas_largura, celulas_altura = calcular_camera(mundo, quadrados_x, quadrados_y)
    area_mapa = pygame.Rect(0, 0, celulas_largura * TAMANHO_CELULA, celulas_altura * TAMANHO_CELULA)
    pygame.draw.rect(tela, (20, 28, 34), area_mapa)

    for y in range(camera_y, min(mundo.tamanho, camera_y + celulas_altura)):
        for x in range(camera_x, min(mundo.tamanho, camera_x + celulas_largura)):
            tela_x = (x - camera_x) * TAMANHO_CELULA
            tela_y = (y - camera_y) * TAMANHO_CELULA
            rect = pygame.Rect(tela_x, tela_y, TAMANHO_CELULA, TAMANHO_CELULA)
            pos = (x, y)

            if pos in mundo.tiles_agua:
                _desenhar_agua(tela, rect)
            elif pos in mundo.tiles_montanha:
                _desenhar_montanha(tela, rect)
            elif pos in mundo.tiles_maldito:
                _desenhar_textura_grama(tela, rect, (58, 34, 72), (118, 90, 136))
            elif pos in mundo.tiles_armadilha:
                _desenhar_textura_grama(tela, rect, (108, 76, 48), (156, 120, 72))
                pygame.draw.line(tela, (230, 216, 196), (rect.x + 9, rect.y + 30), (rect.centerx, rect.y + 10), 2)
                pygame.draw.line(tela, (230, 216, 196), (rect.right - 9, rect.y + 30), (rect.centerx, rect.y + 10), 2)
            else:
                base_escuro = (52, 76, 60) if (x + y) % 2 == 0 else (60, 84, 68)
                base_claro = (108, 166, 112) if (x + y) % 2 == 0 else (116, 174, 118)
                if pos in mundo.tiles_vila:
                    base_escuro = (108, 84, 62)
                    base_claro = (154, 118, 86)
                _desenhar_textura_grama(tela, rect, base_escuro, base_claro)

            pygame.draw.rect(tela, (18, 28, 24), rect, 1)

            if pos in mundo.tiles_santuario or pos in mundo.tiles_igreja:
                _desenhar_casa(tela, rect.inflate(-2, -2), templo=True)
            elif pos in mundo.tiles_castelo:
                _desenhar_casa(tela, rect.inflate(-2, -2), castelo=True)
            elif pos in mundo.tiles_casa or pos in mundo.tiles_biblioteca:
                _desenhar_casa(tela, rect.inflate(-2, -2))
            elif pos in mundo.tiles_arvore:
                _desenhar_arvore(tela, rect)
            elif pos in mundo.tiles_tesouro:
                _desenhar_recurso(tela, rect, (208, 154, 42), (248, 222, 108))
            elif pos in mundo.tiles_comida:
                _desenhar_recurso(tela, rect, (176, 58, 52), (242, 208, 132))
            elif pos in mundo.tiles_inimigo:
                _desenhar_inimigo(tela, rect)
            elif pos in mundo.animais:
                _desenhar_animal(tela, rect, mundo.animais[pos].get("especie", "animal"))

            for npc in mundo.npcs.values():
                if tuple(npc.get("pos", (-999, -999))) == pos:
                    # Don't render NPCs that are indoors (in their homes)
                    npc_id = npc.get("id")
                    if not mundo.npc_em_casa.get(npc_id, False):
                        _renderizar_sprite_personagem(tela, rect, npc.get("perfil", {}), "baixo", tick_visual, animar=False)

    hx, hy = mundo.humano
    
    # Obtem a posicao visual interpolada durante animacao de movimento
    if hasattr(mundo, 'obter_posicao_visual'):
        vx, vy = mundo.obter_posicao_visual()
    else:
        vx, vy = float(hx), float(hy)
    
    # Renderiza o personagem na posicao interpolada
    rect_humano = pygame.Rect((vx - camera_x) * TAMANHO_CELULA, (vy - camera_y) * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    sombra = pygame.Surface((rect_humano.width, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 70), sombra.get_rect())
    tela.blit(sombra, (rect_humano.x, rect_humano.bottom - 8))
    animar_humano = bool(getattr(mundo, "animar_humano_ate", 0.0) > time.time())
    tick_humano = tick_visual if animar_humano else int(getattr(mundo, "tick_animacao_humano", 0)) * 14
    _renderizar_sprite_personagem(tela, rect_humano, mundo.perfil_jogador, mundo.direcao_olhar, tick_humano, animar=animar_humano)

    fx, fy = mundo.tile_a_frente()
    if camera_x <= fx < camera_x + celulas_largura and camera_y <= fy < camera_y + celulas_altura:
        rect_frente = pygame.Rect((fx - camera_x) * TAMANHO_CELULA, (fy - camera_y) * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        pygame.draw.rect(tela, (247, 218, 112), rect_frente.inflate(-8, -8), 2, border_radius=6)
        pygame.draw.line(tela, (247, 218, 112), rect_humano.center, rect_frente.center, 2)

    if tempo.fase in {"noite", "anoitecer"}:
        overlay = pygame.Surface((area_mapa.width, area_mapa.height), pygame.SRCALPHA)
        overlay.fill((14, 18, 34, 95 if tempo.fase == "noite" else 52))
        tela.blit(overlay, (0, 0))

    hud_y = altura_tela - ALTURA_HUD - ALTURA_CHAT
    hud = pygame.Rect(12, hud_y + 8, largura_tela - 24, ALTURA_HUD - 14)
    assets.painel(tela, hud, estilo="brown")
    retrato_rect = pygame.Rect(hud.x + 12, hud.y + 8, 66, 74)
    assets.painel(tela, retrato_rect, estilo="beige", inset=True, alpha=230)
    _renderizar_sprite_personagem(tela, retrato_rect, mundo.perfil_jogador, "baixo", 0)

    pet_txt = f" | Pet: {mundo.pet.get('especie', 'sim')}" if mundo.pet else ""
    linha1 = f"{mundo.nome_humano}, {mundo.idade_humano} anos{pet_txt} | HP {int(mundo.hp)}/{int(mundo.hp_maximo)} | Comida {int(mundo.inventario['comida'])} | Madeira {int(mundo.inventario['madeira'])}"
    linha2 = f"Pontos {mundo.stats['pontos']} | Dia {tempo.dia} {tempo.horario_formatado} ({tempo.fase}) | Ano {mundo.ano_atual} | Vilas {len(mundo.vilas)} | Modo {modo}"
    objetivo = mundo.quests_ativas[0]["descricao"] if mundo.quests_ativas else "Sem objetivo"
    linha3 = f"Objetivo: {objetivo} | Evento: {mundo.ultimo_evento}"
    linhas_hud: list[str] = []
    for texto in (linha1, linha2, linha3):
        linhas_hud.extend(quebrar_texto(fonte_texto, texto, hud.width - 110))
    for indice, linha in enumerate(linhas_hud[:3]):
        tela.blit(fonte_texto.render(linha, True, (246, 235, 214)), (hud.x + 90, hud.y + 9 + indice * 23))


def renderizar_chat(
    tela: pygame.Surface,
    historico_chat: list[str],
    fonte_hud: pygame.font.Font,
    modo_input: str | None,
    texto_input: str,
    modo_escuro: bool = False,
) -> None:
    assets = obter_assets()
    largura_tela, altura_tela = tela.get_size()
    
    # Chat panel on the right side - leave space for left sidebar
    sidebar_padding = 250  # Space for left sidebar
    chat_width = 280
    chat_x = largura_tela - chat_width - 8  # Right side with small padding
    chat_y = 12
    chat_height = altura_tela - 120 - 10  # Reduced height to avoid overlap with health bars
    
    area = pygame.Rect(chat_x, chat_y, chat_width - 12, chat_height)
    assets.painel(tela, area, estilo="brown" if modo_escuro else "beige")
    assets.painel(tela, area.inflate(-16, -48), estilo="brown", inset=True, alpha=224)

    titulo = "CRONICA DO REINO"
    tela.blit(fonte_hud.render(titulo, True, COR_AVISO), (area.x + 14, area.y + 10))

    linhas: list[str] = []
    for msg in historico_chat[-12:]:
        linhas.extend(quebrar_texto(fonte_hud, msg, area.width - 30))

    max_linhas = max(1, (area.height - 88) // 22)
    for indice, linha in enumerate(linhas[-max_linhas:]):
        tela.blit(fonte_hud.render(linha, True, COR_TEXTO), (area.x + 16, area.y + 42 + indice * 22))

    if modo_input is not None:
        campo = pygame.Rect(area.x + 12, area.bottom - 38, area.width - 24, 26)
        assets.painel(tela, campo, estilo="beige", inset=True, alpha=236)
        if modo_input == "chat":
            tipo = "RAPHAEL"
        elif modo_input == "npc":
            tipo = "NPC"
        else:
            tipo = "SAVE"
        tela.blit(fonte_hud.render("ENTER: confirma", True, (178, 162, 134)), (campo.x, campo.y - 22))
        tela.blit(fonte_hud.render(f"[{tipo}] {(texto_input + '_')[:40]}", True, (72, 52, 42)), (campo.x + 8, campo.y + 4))


def renderizar_inventario(tela: pygame.Surface, mundo, indice_hover: int | None = None) -> None:
    assets = obter_assets()
    fonte_texto, fonte_titulo, fonte_subtitulo, _ = _fontes()
    area = pygame.Rect(120, 80, tela.get_width() - 240, tela.get_height() - 200)
    assets.painel(tela, area, estilo="beige")
    titulo = "Inventario de Aventura"
    tela.blit(fonte_subtitulo.render(titulo, True, (82, 54, 40)), (area.x + 22, area.y + 16))
    tela.blit(fonte_texto.render("I fecha | teclas 1-9 equipam/desequipam", True, (102, 74, 56)), (area.x + 24, area.y + 56))

    grade = pygame.Rect(area.x + 20, area.y + 88, int(area.width * 0.54), area.height - 120)
    detalhes = pygame.Rect(grade.right + 14, grade.y, area.right - grade.right - 34, grade.height)
    assets.painel(tela, grade, estilo="brown", inset=True, alpha=230)
    assets.painel(tela, detalhes, estilo="beige", inset=True, alpha=240)

    for idx, item in enumerate(mundo.inventario_itens[:12]):
        linha = pygame.Rect(grade.x + 10, grade.y + 10 + idx * 34, grade.width - 20, 28)
        ativo = bool(item.get("equipado", False))
        assets.botao(tela, linha, fonte_texto, f"{idx + 1}. {item.get('nome', 'Item')}", ativo=ativo)
        if indice_hover == idx or ativo:
            raridade = item.get("raridade", "comum")
            tela.blit(fonte_texto.render(f"{raridade}", True, (248, 224, 142)), (linha.right - 84, linha.y + 5))

    bonus = mundo.bonus_equipamentos
    slot_linhas = [
        f"Arma: {mundo.inventario_itens[mundo.equipamentos['arma']]['nome'] if mundo.equipamentos.get('arma') is not None and mundo.equipamentos.get('arma') < len(mundo.inventario_itens) else '-'}",
        f"Armadura: {mundo.inventario_itens[mundo.equipamentos['armadura']]['nome'] if mundo.equipamentos.get('armadura') is not None and mundo.equipamentos.get('armadura') < len(mundo.inventario_itens) else '-'}",
        f"Acessorio: {mundo.inventario_itens[mundo.equipamentos['acessorio']]['nome'] if mundo.equipamentos.get('acessorio') is not None and mundo.equipamentos.get('acessorio') < len(mundo.inventario_itens) else '-'}",
        f"Reliquia: {mundo.inventario_itens[mundo.equipamentos['reliquia']]['nome'] if mundo.equipamentos.get('reliquia') is not None and mundo.equipamentos.get('reliquia') < len(mundo.inventario_itens) else '-'}",
    ]
    for i, linha in enumerate(slot_linhas):
        for j, parte in enumerate(quebrar_texto(fonte_texto, linha, detalhes.width - 20)[:2]):
            tela.blit(fonte_texto.render(parte, True, (88, 60, 44)), (detalhes.x + 10, detalhes.y + 12 + i * 44 + j * 18))

    bonus_txt = [
        f"Ataque +{int(bonus.get('ataque', 0))}",
        f"Defesa +{int(bonus.get('defesa', 0))}",
        f"HP +{int(bonus.get('hp', 0))}",
        f"Sorte +{int(bonus.get('sorte', 0))}",
        f"Coleta +{int(bonus.get('coleta', 0))}",
    ]
    for i, linha in enumerate(bonus_txt):
        tela.blit(fonte_titulo.render(linha, True, (112, 78, 58)), (detalhes.x + 10, detalhes.y + 206 + i * 30))


def menu_inicial() -> tuple[str, dict | str | None]:
    pygame.init()
    pygame.display.set_caption("BitaCarnes - Menu")
    assets = obter_assets()
    banco = obter_banco_personagens()
    fonte_texto, fonte_titulo, fonte_subtitulo, fonte_logo = _fontes()
    relogio = pygame.time.Clock()

    config = carregar_configuracoes()

    def aplicar_modo_menu() -> pygame.Surface:
        largura_tela, altura_tela = resolucao_atual(config)
        display_idx = escolher_display_para_config(config, (largura_tela, altura_tela))
        if config.get("fullscreen", False):
            flags = pygame.FULLSCREEN
            tamanhos = pygame.display.get_desktop_sizes()
            if 0 <= display_idx < len(tamanhos):
                largura_tela, altura_tela = tamanhos[display_idx]
        elif config.get("windowed_fullscreen", False):
            flags = pygame.NOFRAME
            tamanhos = pygame.display.get_desktop_sizes()
            if 0 <= display_idx < len(tamanhos):
                largura_tela, altura_tela = tamanhos[display_idx]
        else:
            flags = 0
        return pygame.display.set_mode((largura_tela, altura_tela), flags, display=display_idx)

    tela = aplicar_modo_menu()
    opcoes = ["Novo Jogo", "Carregar Save", "Configuracoes", "Sair"]
    idx = 0
    estado = "menu"
    texto_nome = ""
    saves = listar_saves()
    idx_save = 0
    idx_cfg = 0
    executor_preview = ThreadPoolExecutor(max_workers=1)
    preview_lore_future: Future | None = None
    preview_lore_base: dict | None = None
    preview_lore_token = 0

    def iniciar_preview_lore() -> dict:
        nonlocal preview_lore_future, preview_lore_base, preview_lore_token
        perfil = normalizar_lore_personagem(banco.gerar_perfil_jogador())
        preview_lore_token += 1
        if preview_lore_future is not None and not preview_lore_future.done():
            preview_lore_future.cancel()
        preview_lore_base = dict(perfil)
        preview_lore_future = executor_preview.submit(enriquecer_lore_personagem_base, dict(perfil))
        return perfil

    preview = iniciar_preview_lore()
    tick_animacao = 0
    
    # Store button rects for mouse click detection
    rects_botoes_menu: list[tuple[pygame.Rect, str]] = []
    rects_botoes_saves: list[tuple[pygame.Rect, int]] = []  # Save buttons indexed by save index
    rects_botoes_config: list[tuple[pygame.Rect, str]] = []  # Config buttons indexed by field name
    rect_botao_delete: pygame.Rect | None = None
    rect_botao_rename: pygame.Rect | None = None
    
    # Get mouse position for hover effects
    mouse_pos_atual = (0, 0)
    campos_cfg = ["resolucao"]
    if len(pygame.display.get_desktop_sizes()) > 1:
        campos_cfg.append("monitor_index")
    campos_cfg.extend([
        "fullscreen",
        "windowed_fullscreen",
        "modo_escuro",
        "mostrar_fps",
        "volume_master",
        "vibracao_tela",
        "dicas_contextuais",
    ])

    def avancar_cfg(campo: str, direcao: int) -> None:
        if campo == "resolucao":
            atual = tuple(config.get("resolucao", [1280, 880]))
            pos = RESOLUCOES.index(atual) if atual in RESOLUCOES else 0
            pos = (pos + direcao) % len(RESOLUCOES)
            config["resolucao"] = [RESOLUCOES[pos][0], RESOLUCOES[pos][1]]
        elif campo == "monitor_index":
            total = len(pygame.display.get_desktop_sizes())
            if total > 1:
                atual = int(config.get("monitor_index", 0))
                config["monitor_index"] = (atual + direcao) % total
        elif campo == "volume_master":
            config["volume_master"] = max(0, min(100, int(config.get("volume_master", 80)) + direcao * 5))
        elif campo == "fullscreen":
            config["fullscreen"] = not bool(config.get("fullscreen", False))
            if config["fullscreen"]:
                config["windowed_fullscreen"] = False
        elif campo == "windowed_fullscreen":
            config["windowed_fullscreen"] = not bool(config.get("windowed_fullscreen", False))
            if config["windowed_fullscreen"]:
                config["fullscreen"] = False
        else:
            config[campo] = not bool(config.get(campo, False))

    def aplicar_cfg_instante(campo: str) -> None:
        nonlocal tela
        salvar_configuracoes(config)
        if campo in {"resolucao", "monitor_index", "fullscreen", "windowed_fullscreen", "modo_escuro"}:
            tela = aplicar_modo_menu()

    try:
        while True:
            if preview_lore_future is not None and preview_lore_future.done():
                try:
                    lore_preview = preview_lore_future.result()
                    if preview_lore_base is not None:
                        preview = aplicar_lore_personagem(preview_lore_base, lore_preview)
                except Exception:
                    pass
                finally:
                    preview_lore_future = None
                    preview_lore_base = None

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "sair", None
                
                # Track mouse position for hover effects
                if evento.type == pygame.MOUSEMOTION:
                    mouse_pos_atual = evento.pos
                
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    mouse_pos = evento.pos
                    
                    if estado == "menu":
                        for rect_botao, opcao in rects_botoes_menu:
                            if rect_botao.collidepoint(mouse_pos):
                                if opcao == "Novo Jogo":
                                    estado = "novo_nome"
                                    texto_nome = ""
                                    preview = iniciar_preview_lore()
                                elif opcao == "Carregar Save":
                                    saves = listar_saves()
                                    if saves:
                                        idx_save = 0
                                        estado = "carregar"
                                elif opcao == "Configuracoes":
                                    estado = "config"
                                elif opcao == "Sair":
                                    return "sair", None
                    
                    elif estado == "carregar":
                        # Check save buttons
                        for rect_botao, save_idx in rects_botoes_saves:
                            if rect_botao.collidepoint(mouse_pos):
                                if save_idx == "reload":
                                    # Reload saves
                                    saves = listar_saves()
                                    if saves:
                                        idx_save = max(0, min(idx_save, len(saves) - 1))
                                else:
                                    idx_save = save_idx
                                    return "carregar", saves[idx_save]
                        
                        # Check delete button
                        if rect_botao_delete and rect_botao_delete.collidepoint(mouse_pos):
                            nome_delete = saves[idx_save]
                            if deletar_save(nome_delete):
                                saves = listar_saves()
                                if saves:
                                    idx_save = min(idx_save, len(saves) - 1)
                                else:
                                    estado = "menu"
                        
                        # Check rename button
                        if rect_botao_rename and rect_botao_rename.collidepoint(mouse_pos):
                            estado = "renomear"
                            texto_nome = saves[idx_save]
                    
                    elif estado == "config":
                        # Check config buttons
                        for rect_botao, campo in rects_botoes_config:
                            if rect_botao.collidepoint(mouse_pos):
                                avancar_cfg(campo, 1)  # Click advances the option
                                aplicar_cfg_instante(campo)  # This saves the config
                
                if evento.type == pygame.KEYDOWN:
                    if estado == "menu":
                        if evento.key in {pygame.K_UP, pygame.K_w}:
                            idx = (idx - 1) % len(opcoes)
                        elif evento.key in {pygame.K_DOWN, pygame.K_s}:
                            idx = (idx + 1) % len(opcoes)
                        elif evento.key == pygame.K_RETURN:
                            escolha = opcoes[idx]
                            if escolha == "Novo Jogo":
                                estado = "novo_nome"
                                texto_nome = ""
                                preview = iniciar_preview_lore()
                            elif escolha == "Carregar Save":
                                saves = listar_saves()
                                if saves:
                                    idx_save = 0
                                    estado = "carregar"
                            elif escolha == "Configuracoes":
                                estado = "config"
                            else:
                                return "sair", None
                    elif estado == "novo_nome":
                        if evento.key == pygame.K_ESCAPE:
                            estado = "menu"
                        elif evento.key == pygame.K_SPACE:
                            preview = iniciar_preview_lore()
                        elif evento.key == pygame.K_RETURN:
                            return "novo", {
                                "save_name": texto_nome.strip() or f"cronica_{int(pygame.time.get_ticks())}",
                                "perfil_jogador": normalizar_lore_personagem(preview),
                            }
                        elif evento.key == pygame.K_BACKSPACE:
                            texto_nome = texto_nome[:-1]
                        elif evento.unicode and evento.unicode.isprintable() and len(texto_nome) < 50:
                            texto_nome += evento.unicode
                    elif estado == "carregar":
                        if evento.key == pygame.K_ESCAPE:
                            estado = "menu"
                        elif evento.key == pygame.K_r and not saves:
                            # Reload saves when no saves found
                            saves = listar_saves()
                            if saves:
                                idx_save = max(0, min(idx_save, len(saves) - 1))
                        elif evento.key == pygame.K_RETURN and not saves:
                            # Reload saves when no saves found (also on RETURN)
                            saves = listar_saves()
                            if saves:
                                idx_save = max(0, min(idx_save, len(saves) - 1))
                        elif evento.key in {pygame.K_UP, pygame.K_w} and saves:
                            idx_save = (idx_save - 1) % len(saves)
                        elif evento.key in {pygame.K_DOWN, pygame.K_s} and saves:
                            idx_save = (idx_save + 1) % len(saves)
                        elif evento.key == pygame.K_RETURN and saves:
                            return "carregar", saves[idx_save]
                        elif evento.key in {pygame.K_d} and saves:
                            # Delete save
                            nome_delete = saves[idx_save]
                            if deletar_save(nome_delete):
                                saves = listar_saves()
                                if saves:
                                    idx_save = min(idx_save, len(saves) - 1)
                                else:
                                    estado = "menu"
                        elif evento.key in {pygame.K_r} and saves:
                            # Rename save
                            estado = "renomear"
                            texto_nome = saves[idx_save]
                    elif estado == "config":
                        if evento.key == pygame.K_ESCAPE:
                            salvar_configuracoes(config)
                            estado = "menu"
                        elif evento.key in {pygame.K_UP, pygame.K_w}:
                            idx_cfg = (idx_cfg - 1) % len(campos_cfg)
                        elif evento.key in {pygame.K_DOWN, pygame.K_s}:
                            idx_cfg = (idx_cfg + 1) % len(campos_cfg)
                        elif evento.key in {pygame.K_LEFT, pygame.K_a}:
                            campo = campos_cfg[idx_cfg]
                            avancar_cfg(campo, -1)
                            aplicar_cfg_instante(campo)
                        elif evento.key in {pygame.K_RIGHT, pygame.K_d}:
                            campo = campos_cfg[idx_cfg]
                            avancar_cfg(campo, 1)
                            aplicar_cfg_instante(campo)
                        elif evento.key == pygame.K_RETURN:
                            salvar_configuracoes(config)
                            estado = "menu"
                    elif estado == "renomear":
                        if evento.key == pygame.K_ESCAPE:
                            estado = "carregar"
                        elif evento.key == pygame.K_RETURN:
                            novo_nome = texto_nome.strip()
                            nome_antigo = saves[idx_save]
                            if novo_nome and novo_nome != nome_antigo:
                                if renomear_save(nome_antigo, novo_nome):
                                    saves = listar_saves()
                                    idx_save = saves.index(novo_nome) if novo_nome in saves else 0
                            estado = "carregar"
                        elif evento.key == pygame.K_BACKSPACE:
                            texto_nome = texto_nome[:-1]
                        elif evento.unicode and evento.unicode.isprintable() and len(texto_nome) < 50:
                            texto_nome += evento.unicode

            tick_animacao += 1
            _desenhar_fundo_mistico(tela, tick_animacao)

            largura_menu, altura_menu = tela.get_size()
            margem_ui = 16
            altura_base = 564
            altura_cfg = 640 if estado == "config" else altura_base
            quadro_largura = min(816, max(740, largura_menu - margem_ui * 2))
            quadro_altura = min(max(altura_base, altura_cfg), max(500, altura_menu - margem_ui * 2))
            quadro_x = max(0, (largura_menu - quadro_largura) // 2)
            quadro_y = max(0, (altura_menu - quadro_altura) // 2)
            quadro = pygame.Rect(quadro_x, quadro_y, quadro_largura, quadro_altura)
            assets.painel(tela, quadro, estilo="beige")
            topo = pygame.Rect(quadro.x + 20, quadro.y + 18, quadro.width - 40, 90)
            assets.painel(tela, topo, estilo="brown")
            tela.blit(fonte_logo.render("BITACARNES", True, (246, 235, 214)), (topo.x + 26, topo.y + 14))
            subtitulo = "um destino aleatorio, um mundo hostil, uma cronica de fantasia"
            for i, linha in enumerate(quebrar_texto(fonte_texto, subtitulo, topo.width - 50)[:2]):
                tela.blit(fonte_texto.render(linha, True, (230, 214, 190)), (topo.x + 28, topo.y + 52 + i * 20))

            painel_y = quadro.y + 132
            painel_altura = max(240, quadro.bottom - painel_y - 130)  # Reduced more to make room for help+buttons panel
            painel_esquerdo = pygame.Rect(quadro.x + 26, painel_y, 290, painel_altura)
            painel_direito = pygame.Rect(quadro.x + 334, painel_y, quadro.right - (quadro.x + 334) - 26, painel_altura)
            assets.painel(tela, painel_esquerdo, estilo="brown", inset=True, alpha=234)
            assets.painel(tela, painel_direito, estilo="beige", inset=True, alpha=234)
            
            # Create help panel at the bottom with space for buttons
            help_panel_y = painel_esquerdo.bottom + 12
            help_panel = pygame.Rect(quadro.x + 26, help_panel_y, quadro.width - 52, quadro.bottom - help_panel_y - 12)
            assets.painel(tela, help_panel, estilo="brown", inset=True, alpha=220)
            
            # Render help text and action buttons in the bottom panel
            help_x = help_panel.x + 16
            help_y = help_panel.y + 10
            buttons_y = help_y + 45  # Space for help text (2 lines * 22 + padding)
            
            # Generate help text based on current state
            ajuda_linhas = []
            action_buttons = []  # Will store button rects and actions
            
            if estado == "menu":
                ajuda_linhas = [
                    "Setas/W-S: navegar | ENTER: confirmar | ESC: sair",
                    "SPACE: renderizar heroi aleatorio | MOUSE: clicar",
                ]
            elif estado == "novo_nome":
                ajuda_linhas = [
                    "SPACE: novo heroi | ENTER: iniciar campanha | ESC: volta",
                    "TYPE: nome do personagem (max 28 caracteres)",
                ]
            elif estado == "carregar":
                if saves:
                    ajuda_linhas = [
                        "Setas/W-S: navegar | D: deletar | R: renomear | MOUSE: clicar",
                        "ENTER: carregar save | ESC: volta ao menu",
                    ]
                else:
                    ajuda_linhas = [
                        "R ou ENTER: recarregar | ESC: volta ao menu",
                    ]
            elif estado == "renomear":
                ajuda_linhas = [
                    "TYPE: novo nome | ENTER: confirmar | ESC: cancelar",
                    "BACKSPACE: apagar caractere | MAX 40 caracteres",
                ]
            else:  # config
                ajuda_linhas = [
                    "Setas/W-S: navegar | LEFT/RIGHT para mudar | MOUSE: clicar",
                    "ENTER: salvar e voltar | ESC: voltar sem salvar",
                ]
            
            # Render help text
            for i, linha in enumerate(ajuda_linhas):
                fonte_ajuda = pygame.font.SysFont("constantia", 14)
                texto_ajuda = fonte_ajuda.render(linha, True, (240, 225, 200))
                tela.blit(texto_ajuda, (help_x, help_y + i * 22))
            
            # Render action buttons in help panel if in carregar state with saves
            if estado == "carregar" and saves:
                # Delete and Rename buttons in the help panel
                btn_width = (help_panel.width - 48) // 2 - 4
                btn_height = 32
                rect_botao_delete = pygame.Rect(help_panel.x + 16, buttons_y, btn_width, btn_height)
                rect_botao_rename = pygame.Rect(help_panel.x + 16 + btn_width + 8, buttons_y, btn_width, btn_height)
                
                delete_hovered = rect_botao_delete.collidepoint(mouse_pos_atual)
                rename_hovered = rect_botao_rename.collidepoint(mouse_pos_atual)
                
                assets.botao(tela, rect_botao_delete, fonte_texto, "Deletar (D)", ativo=delete_hovered)
                assets.botao(tela, rect_botao_rename, fonte_texto, "Renomear (R)", ativo=rename_hovered)

            if estado == "menu":
                tela.blit(fonte_subtitulo.render("Escolha seu caminho", True, (245, 232, 206)), (painel_esquerdo.x + 20, painel_esquerdo.y + 24))
                botao_y_base = painel_esquerdo.y + 72
                botao_altura = 46
                botao_passo = 64
                rects_botoes_menu = []
                for i, opcao in enumerate(opcoes):
                    rect_botao = pygame.Rect(painel_esquerdo.x + 20, botao_y_base + i * botao_passo, 246, botao_altura)
                    is_hovered = rect_botao.collidepoint(mouse_pos_atual)
                    assets.botao(tela, rect_botao, fonte_titulo, opcao, ativo=(i == idx or is_hovered))
                    rects_botoes_menu.append((rect_botao, opcao))
                    if i == idx:
                        cursor = assets.icone("cursorSword_gold.png", (28, 28))
                        tela.blit(cursor, (rect_botao.x - 16, rect_botao.y + 10))

                titulo_preview = "Estilo Atual"
            elif estado == "novo_nome":
                titulo_preview = "Heroi Gerado"
                tela.blit(fonte_subtitulo.render("Nova cronica", True, (245, 232, 206)), (painel_esquerdo.x + 20, painel_esquerdo.y + 22))
                campo = pygame.Rect(painel_esquerdo.x + 18, painel_esquerdo.y + 72, painel_esquerdo.width - 36, 58)
                assets.painel(tela, campo, estilo="beige", inset=True, alpha=240)
                tela.blit(fonte_texto.render("Nome do save", True, (245, 232, 206)), (campo.x + 8, campo.y - 22))
                valor = fonte_titulo.render((texto_nome + "_")[:28], True, (88, 58, 40))
                tela.blit(valor, (campo.x + 14, campo.y + 18))
            elif estado == "carregar":
                titulo_preview = "Saves"
                tela.blit(fonte_subtitulo.render("Escolha uma cronica salva", True, (245, 232, 206)), (painel_esquerdo.x + 20, painel_esquerdo.y + 22))
                rects_botoes_saves = []
                for i, nome in enumerate(saves[:8]):
                    rect_botao = pygame.Rect(painel_esquerdo.x + 18, painel_esquerdo.y + 72 + i * 40, 248, 34)
                    is_hovered = rect_botao.collidepoint(mouse_pos_atual)
                    assets.botao(tela, rect_botao, fonte_texto, nome, ativo=(i == idx_save or is_hovered))
                    rects_botoes_saves.append((rect_botao, i))
            else:
                titulo_preview = "Configuracoes"
                tela.blit(fonte_subtitulo.render("Ajustes do jogo", True, (245, 232, 206)), (painel_esquerdo.x + 20, painel_esquerdo.y + 22))
                desktop_sizes = pygame.display.get_desktop_sizes()
                total_monitores = max(1, len(desktop_sizes))
                monitor_atual = int(config.get("monitor_index", 0)) % total_monitores
                tamanho_monitor = desktop_sizes[monitor_atual] if desktop_sizes else (0, 0)
                valores = {
                    "resolucao": f"{config['resolucao'][0]}x{config['resolucao'][1]}",
                    "monitor_index": f"{monitor_atual + 1}/{total_monitores} ({tamanho_monitor[0]}x{tamanho_monitor[1]})",
                    "fullscreen": "ON" if config.get("fullscreen") else "OFF",
                    "windowed_fullscreen": "ON" if config.get("windowed_fullscreen") else "OFF",
                    "modo_escuro": "ON" if config.get("modo_escuro") else "OFF",
                    "mostrar_fps": "ON" if config.get("mostrar_fps") else "OFF",
                    "volume_master": f"{config.get('volume_master', 80)}%",
                    "vibracao_tela": "ON" if config.get("vibracao_tela") else "OFF",
                    "dicas_contextuais": "ON" if config.get("dicas_contextuais") else "OFF",
                }
                nomes = {
                    "resolucao": "Resolucao",
                    "monitor_index": "Monitor",
                    "fullscreen": "Tela cheia exclusiva",
                    "windowed_fullscreen": "Tela cheia em janela",
                    "modo_escuro": "UI modo escuro",
                    "mostrar_fps": "Mostrar FPS",
                    "volume_master": "Volume geral",
                    "vibracao_tela": "Vibracao de tela",
                    "dicas_contextuais": "Dicas contextuais",
                }
                lista_topo = painel_esquerdo.y + 72
                lista_rodape = painel_esquerdo.bottom - 42
                lista_altura = max(120, lista_rodape - lista_topo)
                altura_botao = 38
                passo = 44
                if len(campos_cfg) * passo > lista_altura:
                    altura_botao = 34
                    passo = 38
                if len(campos_cfg) * passo > lista_altura:
                    altura_botao = 30
                    passo = 34
                fonte_cfg = fonte_texto if altura_botao >= 34 else pygame.font.SysFont("constantia", 15)
                max_visiveis = max(1, lista_altura // passo)
                inicio = max(0, min(idx_cfg - max_visiveis + 1, len(campos_cfg) - max_visiveis))
                fim = min(len(campos_cfg), inicio + max_visiveis)
                campos_visiveis = campos_cfg[inicio:fim]

                rects_botoes_config = []
                for linha_idx, campo in enumerate(campos_visiveis):
                    idx_absoluto = inicio + linha_idx
                    rect_botao = pygame.Rect(painel_esquerdo.x + 18, lista_topo + linha_idx * passo, 248, altura_botao)
                    is_hovered = rect_botao.collidepoint(mouse_pos_atual)
                    
                    # Special rendering for volume slider
                    if campo == "volume_master":
                        # Draw button background
                        cor_botao = (184, 100, 60) if idx_absoluto == idx_cfg else (122, 94, 70)
                        cor_texto = (245, 233, 210) if idx_absoluto == idx_cfg else (200, 170, 140)
                        pygame.draw.rect(tela, cor_botao, rect_botao, border_radius=6)
                        pygame.draw.rect(tela, (245, 233, 210) if is_hovered or idx_absoluto == idx_cfg else (112, 74, 48), rect_botao, 2, border_radius=6)
                        
                        # Draw slider area
                        slider_rect = pygame.Rect(rect_botao.x + 8, rect_botao.y + 4, rect_botao.width - 16, rect_botao.height - 8)
                        pygame.draw.rect(tela, (98, 74, 58), slider_rect, border_radius=4)
                        
                        # Draw filled portion
                        volume = config.get("volume_master", 80)
                        fill_width = int((slider_rect.width - 4) * (volume / 100.0))
                        fill_rect = pygame.Rect(slider_rect.x + 2, slider_rect.y + 2, fill_width, slider_rect.height - 4)
                        pygame.draw.rect(tela, (86, 158, 102), fill_rect, border_radius=3)
                        
                        # Draw label + percentage
                        label = f"{nomes[campo]}: {valores[campo]}"
                        texto = fonte_cfg.render(label, True, cor_texto)
                        tela.blit(texto, (rect_botao.centerx - texto.get_width() // 2, rect_botao.centery - texto.get_height() // 2))
                    else:
                        assets.botao(tela, rect_botao, fonte_cfg, f"{nomes[campo]}: {valores[campo]}", ativo=(idx_absoluto == idx_cfg or is_hovered))
                    
                    rects_botoes_config.append((rect_botao, campo))

            tela.blit(fonte_subtitulo.render(titulo_preview, True, (84, 62, 46)), (painel_direito.x + 20, painel_direito.y + 18))

            if estado == "carregar" and saves:
                # Show world info for selected save
                info_save = obter_info_save(saves[idx_save])
                
                # World info panel
                info_y = painel_direito.y + 70
                info_bloco = pygame.Rect(painel_direito.x + 20, info_y, painel_direito.width - 40, 160)
                assets.painel(tela, info_bloco, estilo="beige", inset=True, alpha=240)
                
                linhas_info = [
                    f"Nome: {info_save['nome']}",
                    f"Personagem: {info_save['personagem']}",
                    f"Idade: {info_save['idade']} anos",
                    f"Tamanho mundo: {info_save['tamanho_mundo']}x{info_save['tamanho_mundo']}",
                ]
                for i, linha in enumerate(linhas_info):
                    tela.blit(fonte_texto.render(linha, True, (86, 60, 44)), (info_bloco.x + 12, info_bloco.y + 12 + i * 28))
                
                # Show origin
                origem = info_save['origem']
                linhas_origem = quebrar_texto(fonte_texto, f"Origem: {origem}", info_bloco.width - 24)
                origem_y = info_bloco.bottom + 16
                origem_bloco = pygame.Rect(painel_direito.x + 20, origem_y, painel_direito.width - 40, max(60, painel_direito.bottom - origem_y - 80))
                assets.painel(tela, origem_bloco, estilo="beige", inset=True, alpha=238)
                for i, linha in enumerate(linhas_origem[:max(2, (origem_bloco.height - 18) // 22)]):
                    tela.blit(fonte_texto.render(linha, True, (86, 60, 44)), (origem_bloco.x + 12, origem_bloco.y + 12 + i * 22))
            
            elif estado == "carregar" and not saves:
                # No saves found
                mensagem_bloco = pygame.Rect(painel_direito.x + 40, painel_direito.y + 80, painel_direito.width - 80, 200)
                assets.painel(tela, mensagem_bloco, estilo="beige", inset=True, alpha=240)
                
                msg_principal = fonte_subtitulo.render("Nenhum save encontrado", True, (86, 60, 44))
                tela.blit(msg_principal, msg_principal.get_rect(center=(painel_direito.centerx, mensagem_bloco.y + 40)))
                
                msg_desc = fonte_texto.render("Crie um novo jogo para começar", True, (102, 74, 56))
                tela.blit(msg_desc, msg_desc.get_rect(center=(painel_direito.centerx, mensagem_bloco.y + 80)))
                
                # Reload button
                rect_reload = pygame.Rect(painel_direito.x + 60, mensagem_bloco.y + 130, painel_direito.width - 120, 50)
                reload_hovered = rect_reload.collidepoint(mouse_pos_atual)
                assets.botao(tela, rect_reload, fonte_texto, "Recarregar (R)", ativo=reload_hovered)
                rects_botoes_saves = [(rect_reload, "reload")]
            
            elif estado == "renomear":
                # Rename interface
                tela.blit(fonte_subtitulo.render("Renomear Save", True, (245, 232, 206)), (painel_direito.x + 20, painel_direito.y + 30))
                
                campo = pygame.Rect(painel_direito.x + 20, painel_direito.y + 80, painel_direito.width - 40, 58)
                assets.painel(tela, campo, estilo="beige", inset=True, alpha=240)
                tela.blit(fonte_texto.render("Novo nome", True, (86, 60, 44)), (campo.x + 8, campo.y - 22))
                valor = fonte_titulo.render((texto_nome + "_")[:40], True, (88, 58, 40))
                tela.blit(valor, (campo.x + 14, campo.y + 18))
            
            else:
                # Show character preview
                retrato_slot = pygame.Rect(painel_direito.x + 28, painel_direito.y + 60, 122, 160)
                assets.painel(tela, retrato_slot, estilo="brown")
                retrato_interno = retrato_slot.inflate(-18, -18)
                assets.painel(tela, retrato_interno, estilo="beige", inset=True, alpha=240)
                retrato = banco.retrato(preview, retrato_interno.width - 8, retrato_interno.height - 8, "baixo")
                tela.blit(retrato, retrato.get_rect(center=retrato_interno.center))

                preview = normalizar_lore_personagem(preview)
                nome = preview.get("nome", "Heroi")
                idade = preview.get("idade", 18)
                origem = preview.get("origem", "Origem desconhecida.")
                legado = preview.get("legado", "Sem legado conhecido")
                motivacao = preview.get("motivacao", "Buscar um novo destino")
                papel = preview.get("papel_social", "andarilho")
                if preview_lore_future is not None:
                    origem = "Gerando origem unica..."
                    legado = "Tecendo um legado..."
                    motivacao = "Descobrindo um destino..."
                linhas_nome = quebrar_texto(fonte_titulo, nome, painel_direito.width - 194)[:2]
                for i, linha in enumerate(linhas_nome):
                    tela.blit(fonte_titulo.render(linha, True, (92, 58, 40)), (painel_direito.x + 176, painel_direito.y + 70 + i * 28))
                tela.blit(fonte_texto.render(f"{idade} anos | {papel}", True, (114, 78, 58)), (painel_direito.x + 176, painel_direito.y + 70 + len(linhas_nome) * 28))

                rodape = ""
                rodape_linhas = quebrar_texto(fonte_texto, rodape, painel_direito.width - 42)[:2]
                rodape_y = painel_direito.bottom - 48
                bloco_historia = pygame.Rect(
                    painel_direito.x + 22,
                    painel_direito.y + 246,
                    painel_direito.width - 44,
                    max(120, rodape_y - (painel_direito.y + 246) - 14),
                )
                assets.painel(tela, bloco_historia, estilo="beige", inset=True, alpha=238)

                texto_lore = [
                    f"Origem: {origem}",
                    f"Legado: {legado}",
                    f"Motivacao: {motivacao}",
                ]
                linhas_origem: list[str] = []
                for trecho in texto_lore:
                    linhas_origem.extend(quebrar_texto(fonte_texto, trecho, bloco_historia.width - 18))
                max_linhas_lore = max(3, (bloco_historia.height - 18) // 22)
                for i, linha in enumerate(linhas_origem[:max_linhas_lore]):
                    tela.blit(fonte_texto.render(linha, True, (86, 60, 44)), (bloco_historia.x + 10, bloco_historia.y + 12 + i * 22))

                for i, linha in enumerate(rodape_linhas):
                    tela.blit(fonte_texto.render(linha, True, (102, 74, 56)), (painel_direito.x + 20, rodape_y + i * 18))

            pygame.display.flip()
            relogio.tick(60)
    finally:
        executor_preview.shutdown(wait=False, cancel_futures=True)


def renderizar_tela_carregamento(
    tela: pygame.Surface,
    relogio: pygame.time.Clock,
    nome_save: str,
    etapas: list[str],
    indice_etapa: int = 0,
    progresso_etapa: float = 0.0
) -> None:
    """
    Renders a loading screen for save files.
    
    Args:
        tela: The pygame surface to render to
        relogio: The pygame clock for frame rate control
        nome_save: Name of the save being loaded
        etapas: List of loading stages (e.g., ["Carregando dados...", "Carregando mundo..."])
        indice_etapa: Current stage index (0-based)
        progresso_etapa: Progress within current stage (0.0-1.0)
    """
    fonte = pygame.font.SysFont("cambria", 28, bold=True)
    fonte_txt = pygame.font.SysFont("constantia", 16)
    fonte_pequena = pygame.font.SysFont("constantia", 14)
    
    # Fill background
    tela.fill((18, 24, 38))
    
    # Main panel
    painel = pygame.Rect(80, 80, tela.get_width() - 160, tela.get_height() - 160)
    pygame.draw.rect(tela, (208, 190, 150), painel, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), painel, 4, border_radius=16)
    
    # Title
    titulo = fonte.render("Carregando Jogo", True, (74, 48, 36))
    tela.blit(titulo, (painel.x + 24, painel.y + 20))
    
    # Save name
    nome_render = fonte_txt.render(f"Save: {nome_save}", True, (98, 70, 52))
    tela.blit(nome_render, (painel.x + 24, painel.y + 56))
    
    # Progress bar
    barra = pygame.Rect(painel.x + 24, painel.y + 100, painel.width - 48, 32)
    pygame.draw.rect(tela, (122, 94, 70), barra, border_radius=8)
    
    # Calculate overall progress
    progresso_total = (indice_etapa + progresso_etapa) / max(1, len(etapas))
    preenchida = barra.inflate(-6, -6)
    preenchida.width = int((barra.width - 6) * progresso_total)
    pygame.draw.rect(tela, (86, 158, 102), preenchida, border_radius=6)
    
    # Percentage text
    pct = fonte_txt.render(f"{int(progresso_total * 100)}%", True, (244, 236, 216))
    tela.blit(pct, pct.get_rect(center=barra.center))
    
    # Current stage
    etapa_txt = etapas[indice_etapa] if indice_etapa < len(etapas) else "Finalizando..."
    tela.blit(fonte_txt.render(etapa_txt, True, (74, 54, 40)), (painel.x + 24, painel.y + 146))
    
    # Loading indicator (animated dots)
    num_pontos = 3
    pontos_atuais = (int(time.time() * 3) % (num_pontos + 1))
    indicador = "*" * pontos_atuais + "-" * (num_pontos - pontos_atuais)
    tela.blit(fonte_pequena.render(indicador, True, (146, 110, 78)), (painel.right - 80, painel.y + 146))
    
    # Loading steps
    area_etapas = pygame.Rect(painel.x + 24, painel.y + 190, painel.width - 48, painel.height - 220)
    pygame.draw.rect(tela, (236, 224, 194), area_etapas, border_radius=10)
    
    for i, etapa in enumerate(etapas[-5:]):  # Show last 5 steps
        y_pos = area_etapas.y + 12 + (i % 5) * 28
        if y_pos + 20 > area_etapas.bottom - 12:
            break
        cor = (86, 158, 102) if i < indice_etapa else (122, 110, 98)
        marca = "[X]" if i < indice_etapa else "[>]" if i == indice_etapa else "[ ]"
        tela.blit(fonte_pequena.render(f"{marca} {etapa[:54]}", True, cor), (area_etapas.x + 12, y_pos))
    
    pygame.display.flip()
    relogio.tick(60)