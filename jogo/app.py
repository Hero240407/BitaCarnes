import json
import random
import time
from concurrent.futures import Future, ThreadPoolExecutor

import pygame

from .config import ALTURA_CHAT, ALTURA_HUD, TAMANHO_CELULA
from .modelos import SistemaTempo
from .opcoes import carregar_configuracoes, escolher_display_para_config, resolucao_atual
from .servicos import (
    Raphael,
    carregar_objetivos,
    carregar_save,
    criar_mundo_com_raphael,
    gerar_itens_iniciais_raphael,
    salvar_jogo,
    tecla_nome,
)
from .ui import calcular_camera, menu_inicial, renderizar_chat, renderizar_inventario, renderizar_mundo


def _tela_geracao_mundo(tela: pygame.Surface, relogio: pygame.time.Clock, futuro: Future) -> tuple:
    fonte = pygame.font.SysFont("cambria", 26, bold=True)
    fonte_txt = pygame.font.SysFont("constantia", 18)
    inicio = time.time()
    mostrar_log = True
    logs = ["[Raphael] Iniciando ritual de criacao..."]
    estagios = [
        (0.12, "Abrindo os ceus de Raphael"),
        (0.30, "Esculpindo biomas e rios"),
        (0.52, "Erguendo vilas e habitantes"),
        (0.74, "Forjando itens iniciais"),
        (0.92, "Lendo cronicas e finalizando mundo"),
    ]
    ultimo_estagio = -1

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                raise SystemExit
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_l:
                mostrar_log = not mostrar_log

        progresso = min(0.96, (time.time() - inicio) / 4.8)
        for i, (limite, texto) in enumerate(estagios):
            if progresso >= limite and i > ultimo_estagio:
                logs.append(f"[Etapa] {texto}")
                ultimo_estagio = i

        if futuro.done():
            progresso = 1.0

        tela.fill((18, 24, 38))
        painel = pygame.Rect(80, 80, tela.get_width() - 160, tela.get_height() - 160)
        pygame.draw.rect(tela, (208, 190, 150), painel, border_radius=16)
        pygame.draw.rect(tela, (146, 110, 78), painel, 4, border_radius=16)
        titulo = fonte.render("Geracao de Mundo", True, (74, 48, 36))
        tela.blit(titulo, (painel.x + 24, painel.y + 20))
        instr = fonte_txt.render("L alterna log detalhado", True, (98, 70, 52))
        tela.blit(instr, (painel.right - instr.get_width() - 24, painel.y + 28))

        barra = pygame.Rect(painel.x + 24, painel.y + 72, painel.width - 48, 32)
        pygame.draw.rect(tela, (122, 94, 70), barra, border_radius=8)
        preenchida = barra.inflate(-6, -6)
        preenchida.width = int((barra.width - 6) * progresso)
        pygame.draw.rect(tela, (86, 158, 102), preenchida, border_radius=6)
        pct = fonte_txt.render(f"{int(progresso * 100)}%", True, (244, 236, 216))
        tela.blit(pct, pct.get_rect(center=barra.center))

        estagio_txt = "Concluindo..." if progresso >= 1.0 else estagios[max(0, ultimo_estagio)][1] if ultimo_estagio >= 0 else "Preparando roteiro..."
        tela.blit(fonte_txt.render(estagio_txt, True, (74, 54, 40)), (painel.x + 24, painel.y + 116))

        area_log = pygame.Rect(painel.x + 24, painel.y + 150, painel.width - 48, painel.height - 176)
        pygame.draw.rect(tela, (236, 224, 194), area_log, border_radius=10)
        linhas_visiveis = max(5, area_log.height // 24)
        linhas = logs if mostrar_log else logs[-3:]
        for i, linha in enumerate(linhas[-linhas_visiveis:]):
            txt = fonte_txt.render(linha[:110], True, (82, 58, 42))
            tela.blit(txt, (area_log.x + 10, area_log.y + 10 + i * 22))

        pygame.display.flip()
        relogio.tick(60)

        if futuro.done():
            logs.append("[Final] Mundo estabelecido com sucesso.")
            return futuro.result()


def rodar() -> None:
    print("\n=== BITACARNES ===\n")

    objetivos = carregar_objetivos()
    acao_menu, dados_menu = menu_inicial()
    if acao_menu == "sair":
        pygame.quit()
        return

    perfil_jogador = None
    save_atual: str | None
    if acao_menu == "novo" and isinstance(dados_menu, dict):
        perfil_jogador = dados_menu.get("perfil_jogador")
        save_atual = str(dados_menu.get("save_name") or "")
    else:
        save_atual = dados_menu if isinstance(dados_menu, str) else None

    cfg = carregar_configuracoes()
    largura_tela, altura_tela = resolucao_atual(cfg)
    display_idx = escolher_display_para_config(cfg, (largura_tela, altura_tela))
    if cfg.get("fullscreen", False):
        flags = pygame.FULLSCREEN
        tamanhos = pygame.display.get_desktop_sizes()
        if 0 <= display_idx < len(tamanhos):
            largura_tela, altura_tela = tamanhos[display_idx]
    elif cfg.get("windowed_fullscreen", False):
        flags = pygame.NOFRAME
        desktop = pygame.display.get_desktop_sizes()
        if 0 <= display_idx < len(desktop):
            largura_tela, altura_tela = desktop[display_idx]
    else:
        flags = 0

    pygame.init()
    pygame.display.set_caption("BitaCarnes - Controlado pelo Jogador")
    tela = pygame.display.set_mode((largura_tela, altura_tela), flags, display=display_idx)
    fonte_hud = pygame.font.SysFont("consolas", 16)
    fonte_emoji = pygame.font.SysFont("segoe ui emoji", 20)
    relogio = pygame.time.Clock()

    if acao_menu == "carregar" and save_atual:
        try:
            mundo, memoria, _ = carregar_save(save_atual)
            raphael = Raphael(memoria, objetivos)
            tamanho_real = mundo.tamanho
            print(f"[Save carregado: {save_atual}]")
        except Exception as exc:
            print(f"Falha ao carregar save ({exc}). Iniciando novo jogo.")
            print("[Raphael esta acordando...]")
            mundo, tamanho_real, memoria, raphael = criar_mundo_com_raphael(objetivos, perfil_jogador)
            save_atual = save_atual or f"save_{int(time.time())}"
    else:
        print("[Raphael esta acordando...]")
        with ThreadPoolExecutor(max_workers=1) as criador:
            futuro_mundo = criador.submit(criar_mundo_com_raphael, objetivos, perfil_jogador)
            mundo, tamanho_real, memoria, raphael = _tela_geracao_mundo(tela, relogio, futuro_mundo)
        save_atual = save_atual or f"save_{int(time.time())}"

    print(f"[Raphael falou.]")
    print(f"[Mundo: {tamanho_real}x{tamanho_real} | Seu nome: {mundo.nome_humano} | Idade: {mundo.idade_humano}]")
    print(f"[Lore: {mundo.origem_humano}]\n")

    rodando = True
    tick = 0
    ultimo_tempo_acao = 0.0
    atraso_acao = 0.2
    inicio_partida = time.time()
    ultimo_upkeep = inicio_partida
    tempo_sistema = SistemaTempo(segundos_por_dia=24 * 60)
    ultimo_frame_tempo = time.time()
    historico_chat: list[str] = ["Raphael: Bem-vindo, mortal."]
    contador_intervencao = 0
    intervalo_observacao = 6
    teclas_poder_ativas: dict[int, str] = {}
    modo_input: str | None = None
    texto_input = ""
    pausado = False
    inventario_aberto = False
    indice_inventario_hover: int | None = None
    ultimo_update_animais = time.time()
    executor = ThreadPoolExecutor(max_workers=1)
    futuro_raphael: Future | None = None
    tipo_futuro: str | None = None

    economia_cfg = (
        objetivos.get("mundo", {}).get("economia")
        or objetivos.get("world", {}).get("economy", {})
    )
    consumo_comida_segundo = float(
        economia_cfg.get(
            "consumo_comida_segundo",
            economia_cfg.get("food_upkeep_per_second", economia_cfg.get("consumo_comida_tick", economia_cfg.get("food_upkeep_per_tick", 0.15))),
        )
    )
    dano_fome_segundo = float(
        economia_cfg.get(
            "dano_fome_segundo",
            economia_cfg.get("starvation_damage_per_second", economia_cfg.get("dano_fome_tick", economia_cfg.get("starvation_damage_per_tick", 2))),
        )
    )
    tempo_graca_fome_segundos = float(economia_cfg.get("tempo_graca_fome_segundos", 180))
    render_cfg = objetivos.get("gameplay", {}).get("render", {})
    quadrados_x = int(render_cfg.get("visible_squares_x", 28))
    quadrados_y = int(render_cfg.get("visible_squares_y", 14))

    while rodando and mundo.hp > 0:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.MOUSEMOTION and mundo.interior_ativo is None:
                camera_x, camera_y, celulas_largura, celulas_altura = calcular_camera(mundo, quadrados_x, quadrados_y)
                mouse_x, mouse_y = evento.pos
                area_mapa_altura = tela.get_height() - ALTURA_HUD - ALTURA_CHAT
                if 0 <= mouse_x < celulas_largura * TAMANHO_CELULA and 0 <= mouse_y < area_mapa_altura:
                    tile_x = camera_x + int(mouse_x // TAMANHO_CELULA)
                    tile_y = camera_y + int(mouse_y // TAMANHO_CELULA)
                    mundo.definir_direcao_olhar_por_tile(tile_x, tile_y)
            elif evento.type == pygame.KEYDOWN:
                agora = time.time()
                if evento.key == pygame.K_ESCAPE and modo_input is None:
                    pausado = not pausado
                    historico_chat.append("Sistema: jogo pausado" if pausado else "Sistema: jogo retomado")
                    continue

                if modo_input is None and evento.key == pygame.K_i:
                    inventario_aberto = not inventario_aberto
                    if inventario_aberto:
                        historico_chat.append("Sistema: inventario aberto")
                    continue

                if modo_input is not None:
                    if evento.key == pygame.K_ESCAPE:
                        modo_input = None
                        texto_input = ""
                        continue
                    if evento.key == pygame.K_RETURN:
                        texto_final = texto_input.strip()
                        if modo_input == "chat" and texto_final:
                            historico_chat.append(f"Voce: {texto_final}")
                            memoria.avisos_jogador += 1
                            if "missao" in texto_final.lower() or "quest" in texto_final.lower():
                                q = mundo.gerar_quest_raphael()
                                historico_chat.append(f"Sistema: Nova quest - {q['descricao']}")
                            if "item" in texto_final.lower() and ("criar" in texto_final.lower() or "gerar" in texto_final.lower()):
                                novos = gerar_itens_iniciais_raphael(mundo.nome_humano, quantidade=3)
                                for item in novos:
                                    item["equipado"] = False
                                    mundo.inventario_itens.append(item)
                                historico_chat.append(f"Raphael: Forjei {len(novos)} itens novos para sua jornada.")
                            if futuro_raphael is None:
                                if "poder" in texto_final.lower() or "dom" in texto_final.lower() or "habilidade" in texto_final.lower():
                                    tipo_futuro = "pedido_poder"
                                    futuro_raphael = executor.submit(
                                        raphael.avaliar_pedido_poder,
                                        mundo,
                                        texto_final,
                                        set(teclas_poder_ativas.keys()),
                                    )
                                    historico_chat.append("Raphael: Estou julgando seu pedido...")
                                else:
                                    tipo_futuro = "chat"
                                    futuro_raphael = executor.submit(raphael.responder_jogador, mundo, texto_final)
                                    historico_chat.append("Raphael: Estou ouvindo...")
                            else:
                                historico_chat.append("Raphael: Ainda estou respondendo ao seu último chamado.")
                        elif modo_input == "npc" and texto_final:
                            historico_chat.append(f"Voce -> NPC: {texto_final}")
                            if mundo.npc_foco:
                                resposta_npc = mundo.conversar_com_npc(mundo.npc_foco, texto_final)
                                historico_chat.append(resposta_npc)
                            else:
                                historico_chat.append("Sistema: Nenhum NPC em foco.")
                        elif modo_input == "salvar_como" and texto_final:
                            nome_final = salvar_jogo(
                                texto_final,
                                mundo,
                                memoria,
                                {"tick": tick, "timestamp": time.time(), "versao": 1},
                            )
                            save_atual = nome_final
                            historico_chat.append(f"Sistema: save '{nome_final}' gravado")

                        modo_input = None
                        texto_input = ""
                        continue
                    if evento.key == pygame.K_BACKSPACE:
                        texto_input = texto_input[:-1]
                    elif evento.unicode and evento.unicode.isprintable() and len(texto_input) < 120:
                        texto_input += evento.unicode
                    continue

                if pausado:
                    continue

                if inventario_aberto:
                    if evento.key in {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9}:
                        idx_item = evento.key - pygame.K_1
                        indice_inventario_hover = idx_item
                        historico_chat.append(f"Sistema: {mundo.alternar_equipamento_por_indice(idx_item)}")
                    continue

                if (agora - ultimo_tempo_acao) < atraso_acao and evento.key in {
                    pygame.K_w,
                    pygame.K_a,
                    pygame.K_s,
                    pygame.K_d,
                    pygame.K_g,
                    pygame.K_e,
                    pygame.K_b,
                    pygame.K_SPACE,
                    pygame.K_c,
                    pygame.K_t,
                    pygame.K_z,
                    pygame.K_f,
                }:
                    continue

                if evento.key == pygame.K_w:
                    mundo.mover_humano("cima")
                    mundo.expandir_mundo_quando_perto_borda()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_s:
                    mundo.mover_humano("baixo")
                    mundo.expandir_mundo_quando_perto_borda()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_a:
                    mundo.mover_humano("esquerda")
                    mundo.expandir_mundo_quando_perto_borda()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_d:
                    mundo.mover_humano("direita")
                    mundo.expandir_mundo_quando_perto_borda()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_g:
                    mundo.coletar()
                    mundo.moralidade_jogador += 2
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_e:
                    mundo.escavar()
                    memoria.adicionar_evento(f"{mundo.nome_humano} escavou por tesouro")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_b:
                    custo_madeira = int(economia_cfg.get("custo_madeira_casa", economia_cfg.get("house_wood_cost", 4)))
                    custo_comida = int(economia_cfg.get("custo_comida_casa", economia_cfg.get("house_food_cost", 2)))
                    mundo.construir_casa(custo_madeira, custo_comida)
                    mundo.moralidade_jogador += 3
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_SPACE:
                    mundo.atacar()
                    memoria.adicionar_evento(f"{mundo.nome_humano} atacou um inimigo")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_c:
                    mundo.matar_animal()
                    memoria.adicionar_evento(f"{mundo.nome_humano} matou um animal")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_t:
                    mundo.acariciar_animal()
                    memoria.adicionar_evento(f"{mundo.nome_humano} tentou acariciar um animal")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_z:
                    mundo.descansar()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_f:
                    historico_chat.append(f"Sistema: {mundo.acao_contextual()}")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_y:
                    npc_proximo = mundo.obter_npc_proximo()
                    if npc_proximo:
                        mundo.npc_foco = npc_proximo
                        modo_input = "npc"
                        texto_input = ""
                    else:
                        historico_chat.append("Sistema: Nenhum NPC perto para conversar.")
                elif evento.key == pygame.K_r:
                    modo_input = "chat"
                    texto_input = ""
                elif evento.key == pygame.K_F5:
                    nome_final = salvar_jogo(
                        save_atual,
                        mundo,
                        memoria,
                        {"tick": tick, "timestamp": time.time(), "versao": 1},
                    )
                    save_atual = nome_final
                    historico_chat.append(f"Sistema: save '{nome_final}' gravado")
                elif evento.key == pygame.K_F6:
                    modo_input = "salvar_como"
                    texto_input = save_atual

                if evento.key in teclas_poder_ativas:
                    id_poder = teclas_poder_ativas[evento.key]
                    if not mundo.ativar_poder_manual(id_poder):
                        teclas_poder_ativas.pop(evento.key, None)
                    if id_poder not in mundo.poderes:
                        teclas_poder_ativas.pop(evento.key, None)

                if evento.key in {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g, pygame.K_e, pygame.K_b, pygame.K_SPACE, pygame.K_c, pygame.K_t, pygame.K_z, pygame.K_f, pygame.K_y}:
                    memoria.adicionar_evento(f"Acao do jogador: {mundo.ultimo_evento}")

                if contador_intervencao >= intervalo_observacao:
                    fala, efeito = raphael.observar_e_talvez_interferir(mundo, mundo.ultimo_evento, tempo_sistema)
                    if fala:
                        historico_chat.append(f"Raphael: {fala}")
                    if efeito:
                        mundo.stats["intervencoes_raphael"] = mundo.stats.get("intervencoes_raphael", 0) + 1
                        historico_chat.append(f"Raphael: {efeito}")
                    contador_intervencao = 0

        agora_frame = time.time()
        delta_tempo = agora_frame - ultimo_frame_tempo
        if delta_tempo > 0:
            if not pausado:
                tempo_sistema.atualizar(delta_tempo)
            ultimo_frame_tempo = agora_frame

        if not pausado and (agora_frame - ultimo_update_animais) >= 0.9:
            mundo.atualizar_animais()
            ultimo_update_animais = agora_frame

        # Resultado assíncrono do Raphael (sem travar o jogo).
        if futuro_raphael is not None and futuro_raphael.done():
            try:
                if tipo_futuro == "chat":
                    resposta = str(futuro_raphael.result())
                    historico_chat.append(f"Raphael: {resposta}")
                elif tipo_futuro == "pedido_poder":
                    concedeu, motivo, dados_poder = futuro_raphael.result()
                    if concedeu and dados_poder:
                        mundo.conceder_poder(
                            dados_poder["id"],
                            dados_poder["nome"],
                            dados_poder["tipo"],
                            dados_poder["tecla"],
                            dados_poder["cargas"],
                            dados_poder["valor"],
                        )
                        if dados_poder["tecla"] is not None:
                            teclas_poder_ativas[dados_poder["tecla"]] = dados_poder["id"]
                            historico_chat.append(f"Raphael: Concedo {dados_poder['nome']} na tecla {tecla_nome(dados_poder['tecla'])}.")
                        else:
                            historico_chat.append(f"Raphael: Concedo {dados_poder['nome']} automaticamente.")
                    else:
                        historico_chat.append(f"Raphael: Recuso este dom. {motivo}")
            except Exception:
                historico_chat.append("Raphael: Minha visão está turva no momento.")
            finally:
                futuro_raphael = None
                tipo_futuro = None

        agora_loop = time.time()
        segundos_decorridos = int(agora_loop - ultimo_upkeep)
        if not pausado and segundos_decorridos > 0:
            for _ in range(segundos_decorridos):
                if (agora_loop - inicio_partida) >= tempo_graca_fome_segundos:
                    mundo.inventario["comida"] -= consumo_comida_segundo
                    if mundo.inventario["comida"] <= 0:
                        mundo.hp -= dano_fome_segundo
                        mundo.ultimo_evento = "passando fome"
                        if mundo.hp < 3 and memoria.moralidade_raphael > 0 and random.random() < 0.4:
                            raphael.manipular_mundo(mundo, "reviver")
                            historico_chat.append("Raphael: Eu o revivi.")

                evento_sociedade = mundo.atualizar_sociedade(tempo_sistema)
                if evento_sociedade:
                    historico_chat.append(f"Mundo: {evento_sociedade}")
            ultimo_upkeep = agora_loop

        if mundo.interior_ativo is None:
            mapa_altura = max(1, tela.get_height() - ALTURA_HUD - ALTURA_CHAT)
            render_qx = max(10, min(mundo.tamanho, tela.get_width() // TAMANHO_CELULA))
            render_qy = max(8, min(mundo.tamanho, mapa_altura // TAMANHO_CELULA))
            camera_x, camera_y, celulas_largura, celulas_altura = calcular_camera(mundo, render_qx, render_qy)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            area_mapa_altura = tela.get_height() - ALTURA_HUD - ALTURA_CHAT
            if 0 <= mouse_x < celulas_largura * TAMANHO_CELULA and 0 <= mouse_y < area_mapa_altura:
                tile_x = camera_x + int(mouse_x // TAMANHO_CELULA)
                tile_y = camera_y + int(mouse_y // TAMANHO_CELULA)
                mundo.definir_direcao_olhar_por_tile(tile_x, tile_y)

        tick += 1
        mapa_altura = max(1, tela.get_height() - ALTURA_HUD - ALTURA_CHAT)
        render_qx = max(10, min(mundo.tamanho, tela.get_width() // TAMANHO_CELULA))
        render_qy = max(8, min(mundo.tamanho, mapa_altura // TAMANHO_CELULA))
        modo_escuro = bool(cfg.get("modo_escuro", False))
        renderizar_mundo(tela, mundo, fonte_hud, fonte_emoji, "PAUSADO" if pausado else "JOGADOR", tempo_sistema, render_qx, render_qy, modo_escuro=modo_escuro)
        renderizar_chat(tela, historico_chat, fonte_hud, modo_input, texto_input, modo_escuro=modo_escuro)
        if inventario_aberto:
            renderizar_inventario(tela, mundo, indice_inventario_hover)
        if cfg.get("mostrar_fps", False):
            fps = int(relogio.get_fps())
            texto_fps = fonte_hud.render(f"FPS: {fps}", True, (242, 236, 214))
            tela.blit(texto_fps, (tela.get_width() - texto_fps.get_width() - 12, 8))
        pygame.display.flip()
        relogio.tick(60)

    print("\n[Simulacao Encerrada]")
    print(json.dumps(mundo.stats, indent=2))
    executor.shutdown(wait=False, cancel_futures=True)
    pygame.quit()
