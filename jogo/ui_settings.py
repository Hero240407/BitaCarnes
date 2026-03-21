"""Settings Menu and Configuration UI"""
import pygame
from .ui import obter_assets, _fontes


def renderizar_menu_configuracoes(
    tela: pygame.Surface,
    configuracoes: dict,
    opcao_selecionada: int = 0,
    gerenciador_som=None,
) -> None:
    """Renderiza menu de configurações (F7) com volume, resolução, etc."""
    assets = obter_assets()
    fonte_texto, fonte_titulo, fonte_subtitulo, _ = _fontes()
    
    # Escurecer fundo
    overlay = pygame.Surface((tela.get_width(), tela.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    tela.blit(overlay, (0, 0))
    
    # Layout responsivo
    largura_menu = min(700, tela.get_width() - 40)
    altura_menu = min(550, tela.get_height() - 60)
    area = pygame.Rect(
        tela.get_width() // 2 - largura_menu // 2,
        tela.get_height() // 2 - altura_menu // 2,
        largura_menu,
        altura_menu
    )
    assets.painel(tela, area, estilo="beige")
    
    titulo = "CONFIGURAÇÕES"
    txt_titulo = fonte_subtitulo.render(titulo, True, (74, 48, 36))
    tela.blit(txt_titulo, (area.centerx - txt_titulo.get_width() // 2, area.y + 20))
    
    # Preparar opções
    volume_master = configuracoes.get("volume_master", 80)
    fullscreen = configuracoes.get("fullscreen", False)
    mostrar_fps = configuracoes.get("mostrar_fps", False)
    vibracao = configuracoes.get("vibracao_tela", True)
    dicas = configuracoes.get("dicas_contextuais", True)
    
    opcoes = [
        f"Volume Master: {volume_master}%",
        f"Modo Tela: {'Fullscreen' if fullscreen else 'Janela'}",
        f"Mostrar FPS: {'Sim' if mostrar_fps else 'Não'}",
        f"Vibração Tela: {'Ativada' if vibracao else 'Desativada'}",
        f"Dicas Contextuais: {'Ativadas' if dicas else 'Desativadas'}",
        "← Voltar",
    ]
    
    botao_altura = 45
    botao_largura = largura_menu - 60
    espaco = 6
    inicio_y = area.y + 70
    
    for i, opcao_texto in enumerate(opcoes):
        botao = pygame.Rect(
            area.centerx - botao_largura // 2,
            inicio_y + i * (botao_altura + espaco),
            botao_largura,
            botao_altura
        )
        
        ativo = (i == opcao_selecionada)
        cor_fundo = (184, 100, 60) if ativo else (146, 98, 70)
        cor_texto = (245, 233, 210) if ativo else (200, 170, 140)
        
        pygame.draw.rect(tela, cor_fundo, botao, border_radius=6)
        pygame.draw.rect(tela, (245, 233, 210) if ativo else (112, 74, 48), botao, 2, border_radius=6)
        
        texto = fonte_titulo.render(opcao_texto, True, cor_texto)
        tela.blit(texto, (botao.centerx - texto.get_width() // 2, botao.centery - texto.get_height() // 2))
        
        # Mostrar dica para volume
        if i == 0 and ativo:
            dica = "← Reduzir | Aumentar →"
            txt_dica = fonte_texto.render(dica, True, (112, 74, 48))
            tela.blit(txt_dica, (botao.right + 10, botao.centery - txt_dica.get_height() // 2))
    
    # Rodapé
    instrucoes = "↑↓ Navegar | ← → Ajustar | ENTER Alternar | ESC Cancelar"
    txt_inst = fonte_texto.render(instrucoes, True, (112, 74, 48))
    tela.blit(txt_inst, (area.centerx - txt_inst.get_width() // 2, area.bottom - 30))


def processar_input_configuracoes(
    evento: pygame.event.EventType,
    opcao_selecionada: int,
    configuracoes: dict,
    gerenciador_som=None,
) -> tuple[int, dict, bool]:
    """Processa input do menu de configurações.
    
    Retorna: (nova_opcao, configuracoes_atualizadas, fechar_menu)
    """
    fechar = False
    
    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_UP:
            opcao_selecionada = max(0, opcao_selecionada - 1)
        elif evento.key == pygame.K_DOWN:
            opcao_selecionada = min(5, opcao_selecionada + 1)
        elif evento.key == pygame.K_ESCAPE:
            fechar = True
        elif evento.key == pygame.K_RETURN:
            if opcao_selecionada == 5:  # Voltar
                fechar = True
        elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
            # Ajustar valor
            if opcao_selecionada == 0:  # Volume
                mudanca = -5 if evento.key == pygame.K_LEFT else 5
                novo_volume = max(0, min(100, configuracoes.get("volume_master", 80) + mudanca))
                configuracoes["volume_master"] = novo_volume
                if gerenciador_som:
                    gerenciador_som.definir_volume(novo_volume / 100.0)
            elif opcao_selecionada == 1:  # Fullscreen
                configuracoes["fullscreen"] = not configuracoes.get("fullscreen", False)
            elif opcao_selecionada == 2:  # FPS
                configuracoes["mostrar_fps"] = not configuracoes.get("mostrar_fps", False)
            elif opcao_selecionada == 3:  # Vibração
                configuracoes["vibracao_tela"] = not configuracoes.get("vibracao_tela", True)
            elif opcao_selecionada == 4:  # Dicas
                configuracoes["dicas_contextuais"] = not configuracoes.get("dicas_contextuais", True)
    
    return opcao_selecionada, configuracoes, fechar
