import json
import random
import time
from concurrent.futures import Future, ThreadPoolExecutor

import pygame

from .config import ALTURA_TELA, LARGURA_TELA
from .modelos import SistemaTempo
from .servicos import (
    Raphael,
    carregar_objetivos,
    carregar_save,
    criar_mundo_com_raphael,
    salvar_jogo,
    tecla_nome,
)
from .ui import menu_inicial, renderizar_chat, renderizar_mundo


def rodar() -> None:
    print("\n=== O REINO DE RAPHAEL ===\n")

    objetivos = carregar_objetivos()
    acao_menu, save_atual = menu_inicial()
    if acao_menu == "sair":
        pygame.quit()
        return

    if acao_menu == "carregar" and save_atual:
        try:
            mundo, memoria, _ = carregar_save(save_atual)
            raphael = Raphael(memoria, objetivos)
            tamanho_real = mundo.tamanho
            print(f"[Save carregado: {save_atual}]")
        except Exception as exc:
            print(f"Falha ao carregar save ({exc}). Iniciando novo jogo.")
            print("[Raphael esta acordando...]")
            mundo, tamanho_real, memoria, raphael = criar_mundo_com_raphael(objetivos)
            save_atual = save_atual or f"save_{int(time.time())}"
    else:
        print("[Raphael esta acordando...]")
        mundo, tamanho_real, memoria, raphael = criar_mundo_com_raphael(objetivos)
        save_atual = save_atual or f"save_{int(time.time())}"

    print(f"[Raphael falou.]")
    print(f"[Mundo: {tamanho_real}x{tamanho_real} | Seu nome: {mundo.nome_humano}]")
    print(f"[Lore: {mundo.origem_humano}]\n")

    pygame.init()
    pygame.display.set_caption("O Reino de Raphael - Controlado pelo Jogador")
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    fonte_hud = pygame.font.SysFont("consolas", 16)
    fonte_emoji = pygame.font.SysFont("segoe ui emoji", 20)

    relogio = pygame.time.Clock()
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
            elif evento.type == pygame.KEYDOWN:
                agora = time.time()
                if evento.key == pygame.K_ESCAPE and modo_input is None:
                    pausado = not pausado
                    historico_chat.append("Sistema: jogo pausado" if pausado else "Sistema: jogo retomado")
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

                if evento.key in {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g, pygame.K_e, pygame.K_b, pygame.K_SPACE, pygame.K_c, pygame.K_t, pygame.K_z}:
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
            ultimo_upkeep = agora_loop

        tick += 1
        renderizar_mundo(tela, mundo, fonte_hud, fonte_emoji, "PAUSADO" if pausado else "JOGADOR", tempo_sistema, quadrados_x, quadrados_y)
        renderizar_chat(tela, historico_chat, fonte_hud, modo_input, texto_input)
        pygame.display.flip()
        relogio.tick(60)

    print("\n[Simulacao Encerrada]")
    print(json.dumps(mundo.stats, indent=2))
    executor.shutdown(wait=False, cancel_futures=True)
    pygame.quit()
