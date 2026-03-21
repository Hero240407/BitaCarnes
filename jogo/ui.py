import pygame

from .config import (
    ALTURA_CHAT,
    ALTURA_HUD,
    ALTURA_TELA,
    COR_AGUA,
    COR_ANIMAL,
    COR_ARVORE,
    COR_ARMADILHA,
    COR_AVISO,
    COR_BG,
    COR_CASA,
    COR_CHAT_BG,
    COR_COMIDA,
    COR_CONTORNO,
    COR_GRID_CLARO,
    COR_GRID_ESC,
    COR_HUD,
    COR_HUMANO,
    COR_INIMIGO,
    COR_MALDITO,
    COR_MONTANHA,
    COR_SANTUARIO,
    COR_TESOURO,
    COR_TEXTO,
    LARGURA_TELA,
    TAMANHO_CELULA,
)
from .servicos import listar_saves


def desenhar_tile(superficie: pygame.Surface, rect: pygame.Rect, cor: tuple[int, int, int]) -> None:
    pygame.draw.rect(superficie, cor, rect, border_radius=5)


def desenhar_emoji(superficie: pygame.Surface, fonte: pygame.font.Font, texto: str, centro: tuple[int, int]) -> None:
    glifo = fonte.render(texto, True, (12, 14, 18))
    rect_glifo = glifo.get_rect(center=centro)
    superficie.blit(glifo, rect_glifo)


def desenhar_sprite_pixel(superficie: pygame.Surface, rect: pygame.Rect, tipo: str) -> None:
    """Sprites simples em pixel-art sem assets externos."""
    base = pygame.Surface((16, 16), pygame.SRCALPHA)
    paleta = {
        "player": (109, 177, 236),
        "animal": (150, 200, 100),
        "inimigo": (181, 77, 89),
        "arvore": (87, 148, 98),
        "casa": (177, 121, 84),
        "vila": (210, 170, 120),
    }
    cor = paleta.get(tipo, (220, 220, 220))
    base.fill((0, 0, 0, 0))
    pygame.draw.rect(base, cor, pygame.Rect(3, 2, 10, 12))
    pygame.draw.rect(base, (30, 30, 30), pygame.Rect(6, 6, 1, 1))
    pygame.draw.rect(base, (30, 30, 30), pygame.Rect(9, 6, 1, 1))
    pygame.draw.rect(base, (245, 245, 245), pygame.Rect(6, 10, 4, 1))
    sprite = pygame.transform.scale(base, (max(8, rect.width - 8), max(8, rect.height - 8)))
    srect = sprite.get_rect(center=rect.center)
    superficie.blit(sprite, srect)


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


def renderizar_mundo(
    tela: pygame.Surface,
    mundo,
    fonte_hud: pygame.font.Font,
    fonte_emoji: pygame.font.Font,
    modo: str,
    tempo,
    quadrados_x: int,
    quadrados_y: int,
) -> None:
    tela.fill(COR_BG)

    celulas_largura = max(10, quadrados_x)
    celulas_altura = max(8, quadrados_y)
    metade_l = celulas_largura // 2
    metade_a = celulas_altura // 2

    camera_x = max(0, min(mundo.tamanho - celulas_largura, mundo.humano[0] - metade_l))
    camera_y = max(0, min(mundo.tamanho - celulas_altura, mundo.humano[1] - metade_a))

    for y in range(camera_y, min(mundo.tamanho, camera_y + celulas_altura)):
        for x in range(camera_x, min(mundo.tamanho, camera_x + celulas_largura)):
            tela_x = (x - camera_x) * TAMANHO_CELULA
            tela_y = (y - camera_y) * TAMANHO_CELULA
            rect = pygame.Rect(tela_x, tela_y, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)
            base = COR_GRID_ESC if (x + y) % 2 == 0 else COR_GRID_CLARO
            pygame.draw.rect(tela, base, rect)
            pygame.draw.rect(tela, COR_CONTORNO, rect, 1)

            pos = (x, y)
            if pos in mundo.tiles_montanha:
                desenhar_tile(tela, rect.inflate(-8, -8), COR_MONTANHA)
                desenhar_emoji(tela, fonte_emoji, "⛰️", rect.center)
            elif pos in mundo.tiles_agua:
                desenhar_tile(tela, rect.inflate(-8, -8), COR_AGUA)
                desenhar_emoji(tela, fonte_emoji, "💧", rect.center)
            elif pos in mundo.tiles_maldito:
                desenhar_tile(tela, rect.inflate(-10, -10), COR_MALDITO)
                desenhar_emoji(tela, fonte_emoji, "🌑", rect.center)
            elif pos in mundo.tiles_santuario:
                desenhar_tile(tela, rect.inflate(-10, -10), COR_SANTUARIO)
                desenhar_emoji(tela, fonte_emoji, "⛪", rect.center)
            elif pos in mundo.tiles_casa:
                desenhar_tile(tela, rect.inflate(-10, -10), COR_CASA)
                desenhar_sprite_pixel(tela, rect, "casa")
            elif pos in mundo.tiles_vila:
                desenhar_tile(tela, rect.inflate(-9, -9), (120, 95, 70))
                desenhar_sprite_pixel(tela, rect, "vila")
            elif pos in mundo.tiles_inimigo:
                desenhar_tile(tela, rect.inflate(-12, -12), COR_INIMIGO)
                desenhar_sprite_pixel(tela, rect, "inimigo")
            elif pos in mundo.animais:
                desenhar_tile(tela, rect.inflate(-12, -12), COR_ANIMAL)
                especie = mundo.animais[pos].get("especie", "animal")
                emoji = "🐺" if especie == "lobo" else "🦊" if especie == "raposa" else "🐇" if especie == "coelho" else "🐱" if especie == "gato" else "🦌"
                desenhar_emoji(tela, fonte_emoji, emoji, rect.center)
            elif pos in mundo.tiles_comida:
                desenhar_tile(tela, rect.inflate(-14, -14), COR_COMIDA)
                desenhar_emoji(tela, fonte_emoji, "🍎", rect.center)
            elif pos in mundo.tiles_arvore:
                desenhar_tile(tela, rect.inflate(-12, -12), COR_ARVORE)
                desenhar_emoji(tela, fonte_emoji, "🌲", rect.center)
            elif pos in mundo.tiles_armadilha:
                desenhar_tile(tela, rect.inflate(-14, -14), COR_ARMADILHA)
                desenhar_emoji(tela, fonte_emoji, "🪤", rect.center)
            elif pos in mundo.tiles_tesouro:
                desenhar_tile(tela, rect.inflate(-14, -14), COR_TESOURO)
                desenhar_emoji(tela, fonte_emoji, "💎", rect.center)

    hx, hy = mundo.humano
    rect_humano = pygame.Rect((hx - camera_x) * TAMANHO_CELULA, (hy - camera_y) * TAMANHO_CELULA, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)
    desenhar_tile(tela, rect_humano.inflate(-6, -6), COR_HUMANO)
    desenhar_sprite_pixel(tela, rect_humano, "player")

    if tempo.fase in {"noite", "anoitecer"}:
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA - ALTURA_HUD - ALTURA_CHAT), pygame.SRCALPHA)
        overlay.fill((10, 16, 40, 110 if tempo.fase == "noite" else 60))
        tela.blit(overlay, (0, 0))

    hud_y = ALTURA_TELA - ALTURA_HUD - ALTURA_CHAT
    pygame.draw.rect(tela, COR_HUD, pygame.Rect(0, hud_y, LARGURA_TELA, ALTURA_HUD))
    pet_txt = f" | Pet: {mundo.pet.get('especie', 'sim')}" if mundo.pet else ""
    linha1 = f"{mundo.nome_humano} | HP {int(mundo.hp)}/{int(mundo.hp_maximo)} | Comida {int(mundo.inventario['comida'])} Madeira {int(mundo.inventario['madeira'])}{pet_txt}"
    linha2 = f"Pontos {mundo.stats['pontos']} | Dia {tempo.dia} {tempo.horario_formatado} ({tempo.fase}) | Modo: {modo} | Animais: {len(mundo.animais)}"
    linha3 = f"Evento: {mundo.ultimo_evento} | Intervencoes de Raphael: {mundo.stats.get('intervencoes_raphael', 0)}"

    for idx, linha in enumerate([linha1, linha2, linha3]):
        tela.blit(fonte_hud.render(linha, True, COR_TEXTO), (8, hud_y + 8 + idx * 28))


def renderizar_chat(tela: pygame.Surface, historico_chat: list[str], fonte_hud: pygame.font.Font, modo_input: str | None, texto_input: str) -> None:
    chat_y = ALTURA_TELA - ALTURA_CHAT
    pygame.draw.rect(tela, COR_CHAT_BG, pygame.Rect(0, chat_y, LARGURA_TELA, ALTURA_CHAT))
    pygame.draw.line(tela, COR_CONTORNO, (0, chat_y), (LARGURA_TELA, chat_y), 2)

    titulo = "PALAVRAS DE RAPHAEL (R: falar/pedir poder no chat | T: acariciar | ESC: pausar | F5/F6 salvar)"
    tela.blit(fonte_hud.render(titulo, True, COR_AVISO), (8, chat_y + 5))

    linhas: list[str] = []
    for msg in historico_chat[-18:]:
        linhas.extend(quebrar_texto(fonte_hud, msg, LARGURA_TELA - 16))

    max_linhas = max(1, (ALTURA_CHAT - 72) // 24)
    for idx, linha in enumerate(linhas[-max_linhas:]):
        tela.blit(fonte_hud.render(linha, True, COR_TEXTO), (8, chat_y + 34 + idx * 24))

    if modo_input is not None:
        tipo = "CHAT" if modo_input == "chat" else "SAVE"
        pygame.draw.rect(tela, (12, 14, 20), pygame.Rect(6, ALTURA_TELA - 38, LARGURA_TELA - 12, 30), border_radius=6)
        tela.blit(fonte_hud.render("Digite e pressione ENTER (ESC cancela)", True, (170, 170, 190)), (10, ALTURA_TELA - 62))
        tela.blit(fonte_hud.render(f"[{tipo}] {(texto_input + '_')[:140]}", True, (245, 245, 245)), (12, ALTURA_TELA - 34))


def menu_inicial() -> tuple[str, str | None]:
    pygame.init()
    tela = pygame.display.set_mode((700, 420))
    pygame.display.set_caption("O Reino de Raphael - Menu")
    fonte = pygame.font.SysFont("consolas", 28)
    fonte2 = pygame.font.SysFont("consolas", 20)
    relogio = pygame.time.Clock()

    opcoes = ["Novo Jogo", "Carregar Save", "Sair"]
    idx = 0
    estado = "menu"
    texto_nome = ""
    saves = listar_saves()
    idx_save = 0

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair", None
            if evento.type == pygame.KEYDOWN:
                if estado == "menu":
                    if evento.key in {pygame.K_UP, pygame.K_w}:
                        idx = (idx - 1) % len(opcoes)
                    elif evento.key in {pygame.K_DOWN, pygame.K_s}:
                        idx = (idx + 1) % len(opcoes)
                    elif evento.key == pygame.K_RETURN:
                        esc = opcoes[idx]
                        if esc == "Novo Jogo":
                            estado = "novo_nome"
                            texto_nome = ""
                        elif esc == "Carregar Save":
                            saves = listar_saves()
                            if saves:
                                idx_save = 0
                                estado = "carregar"
                        else:
                            return "sair", None
                elif estado == "novo_nome":
                    if evento.key == pygame.K_ESCAPE:
                        estado = "menu"
                    elif evento.key == pygame.K_RETURN:
                        return "novo", (texto_nome.strip() or f"save_{int(pygame.time.get_ticks())}")
                    elif evento.key == pygame.K_BACKSPACE:
                        texto_nome = texto_nome[:-1]
                    elif evento.unicode and evento.unicode.isprintable() and len(texto_nome) < 50:
                        texto_nome += evento.unicode
                elif estado == "carregar":
                    if evento.key == pygame.K_ESCAPE:
                        estado = "menu"
                    elif evento.key in {pygame.K_UP, pygame.K_w} and saves:
                        idx_save = (idx_save - 1) % len(saves)
                    elif evento.key in {pygame.K_DOWN, pygame.K_s} and saves:
                        idx_save = (idx_save + 1) % len(saves)
                    elif evento.key == pygame.K_RETURN and saves:
                        return "carregar", saves[idx_save]

        tela.fill((17, 20, 24))
        tela.blit(fonte.render("O REINO DE RAPHAEL", True, (230, 220, 200)), (170, 40))
        tela.blit(fonte2.render("Setas/W-S para navegar, ENTER confirmar, ESC voltar", True, (180, 180, 180)), (120, 90))

        if estado == "menu":
            for i, opcao in enumerate(opcoes):
                cor = (255, 210, 120) if i == idx else (220, 220, 220)
                tela.blit(fonte.render(opcao, True, cor), (240, 170 + i * 60))
        elif estado == "novo_nome":
            tela.blit(fonte.render("Nome do save:", True, (230, 230, 230)), (220, 180))
            tela.blit(fonte.render((texto_nome + "_")[:32], True, (255, 210, 120)), (220, 240))
        elif estado == "carregar":
            tela.blit(fonte2.render("Escolha um save para carregar:", True, (230, 230, 230)), (220, 140))
            for i, nome in enumerate(saves[:10]):
                cor = (255, 210, 120) if i == idx_save else (220, 220, 220)
                tela.blit(fonte2.render(nome, True, cor), (220, 180 + i * 26))

        pygame.display.flip()
        relogio.tick(60)
