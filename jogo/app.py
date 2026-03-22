import json
import math
import random
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

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
    SAVE_DIR,
    normalizar_nome_save,
)
from .ui import calcular_camera, menu_inicial, renderizar_chat, renderizar_inventario, renderizar_mundo, renderizar_menu_ajuda, renderizar_menu_lore, renderizar_menu_pausa
from .ui_settings import renderizar_menu_configuracoes, processar_input_configuracoes

# Hotbar Mode System
try:
    from .ui_hotbar import HotbarManager, GameMode, renderizar_overlay_modo
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar ui_hotbar.py: {e}")
    HotbarManager = None
    GameMode = None

# NPC Backstory Lazy Loading
try:
    from .npc_backstory_lazy import SistemaBackstoriesLazyLoading
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar npc_backstory_lazy.py: {e}")
    SistemaBackstoriesLazyLoading = None

# New system UI menus
try:
    from .ui_systems import (
        renderizar_menu_equipamento,
        renderizar_menu_skills,
        renderizar_menu_quests,
        renderizar_menu_dungeons,
        renderizar_menu_stats,
        renderizar_menu_farming,
        renderizar_dungeon_interior,
        renderizar_historia_npc,
    )
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar ui_systems.py: {e}")
    renderizar_menu_equipamento = None
    renderizar_menu_skills = None
    renderizar_menu_quests = None
    renderizar_menu_dungeons = None
    renderizar_menu_stats = None
    renderizar_menu_farming = None
    renderizar_dungeon_interior = None
    renderizar_historia_npc = None

# Novos sistemas Stardew Valley
from .farming import FarmManager
from .npc_relations import GerenciadorRelacoes, ComportamentoNPC
from .calendar import Calendario
from .quests import QuestManager, ObjetivoGeral
from .fishing import MiniGamePesca, HistoricoPesca
from .weather import SistemaClima
from .ui_enhanced import renderizar_hud_expandida
from .action_logger import ActionLogger

# Novos sistemas: UI, Diálogo e Mundo
from .ui_enhancements import MenuAnimado, BarraProgresso, TooltipSistema, PainelInventarioVisual, IndicadorSocial
from .npc_dialogue_ai import SistemaConversas
from .location_ambiance import GerenciadorAmbiance, SistemaTempoAmbiane, TipoBioma
from .world_interactions import GerenciadorObjetos, SistemaPovoado, SistemaProgresso

# Som e Música
from .sound_manager import GerenciadorSom, GerenciadorEfeitosSonoros, MusicaContexto, ContextoMusica

# Novos sistemas não-integrados
try:
    from .dungeon import Masmorra, SalaMasmorra, TipoBiomaMasmorra, DificuldadeMasmorra, Gerador_Masmorra
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar dungeon.py: {e}")
    Masmorra = SalaMasmorra = TipoBiomaMasmorra = DificuldadeMasmorra = Gerador_Masmorra = None

try:
    from .dungeon_sistema import GerenciadorDungeonSessao, GeneradorEntradaDungeon
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar dungeon_sistema.py: {e}")
    GerenciadorDungeonSessao = GeneradorEntradaDungeon = None

try:
    from .equipment import Item, Equipamento, BancoDados_Items
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar equipment.py: {e}")
    Item = Equipamento = BancoDados_Items = None

try:
    from .progression import Habilidade, HabilidadeAprendida, BancoDados_Habilidades
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar progression.py: {e}")
    Habilidade = HabilidadeAprendida = BancoDados_Habilidades = None

try:
    from .mobs import Mob, GerenciadorMobs
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar mobs.py: {e}")
    Mob = GerenciadorMobs = None

try:
    from .biomas import ConfiguradorBiomas
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar biomas.py: {e}")
    ConfiguradorBiomas = None

try:
    from .animations import GerenciadorAnimacoes
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar animations.py: {e}")
    GerenciadorAnimacoes = None

try:
    from .npc_backstories import GeradorHistoricosIA
except ImportError as e:
    print(f"[Aviso] Não foi possível carregar npc_backstories.py: {e}")
    GeradorHistoricosIA = None


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
        print(f"[Sistema] Tentando carregar save: {save_atual}")
        try:
            from .ui import renderizar_tela_carregamento
            
            # Loading stages
            etapas = [
                "Carregando arquivos do save...",
                "Construindo mundo...",
                "Carregando inventário...",
                "Carregando NPCs e habitantes...",
                "Carregando sistemas de jogo...",
                "Finalizando..."
            ]
            
            # Show loading screen with stages
            for i, etapa in enumerate(etapas):
                renderizar_tela_carregamento(tela, relogio, save_atual, etapas, i, 0.5)
            
            mundo, memoria, _ = carregar_save(save_atual)
            raphael = Raphael(memoria, objetivos)
            tamanho_real = mundo.tamanho
            
            # Final loading stage
            renderizar_tela_carregamento(tela, relogio, save_atual, etapas, len(etapas) - 1, 1.0)
            time.sleep(0.3)
            
            print(f"[Save carregado com sucesso: {save_atual}]")
            print(f"[Mundo] Tamanho: {tamanho_real}x{tamanho_real}")
            print(f"[Personagem] Nome: {mundo.nome_humano} | Idade: {mundo.idade_humano}")
            print(f"[Lore] Origem: {mundo.origem_humano}")
            print(f"[Quests Ativas] {len(getattr(mundo, 'quests_ativas', []))}")
        except Exception as exc:
            print(f"[Erro] Falha ao carregar save ({exc}). Iniciando novo jogo.")
            print("[Raphael] Ritual de criacao iniciado...")
            mundo, tamanho_real, memoria, raphael = criar_mundo_com_raphael(objetivos, perfil_jogador)
            save_atual = save_atual or f"save_{int(time.time())}"
            print(f"[Novo Mundo] Tamanho: {tamanho_real}x{tamanho_real}")
            print(f"[Personagem] Nome: {mundo.nome_humano} | Idade: {mundo.idade_humano}")
            print(f"[Lore] Origem: {mundo.origem_humano}")
            print(f"[Quests Ativas] {len(getattr(mundo, 'quests_ativas', []))}")
    else:
        print("[Raphael] Ritual de criacao iniciado...")
        with ThreadPoolExecutor(max_workers=1) as criador:
            futuro_mundo = criador.submit(criar_mundo_com_raphael, objetivos, perfil_jogador)
            mundo, tamanho_real, memoria, raphael = _tela_geracao_mundo(tela, relogio, futuro_mundo)
        save_atual = save_atual or f"save_{int(time.time())}"
        print(f"[Novo Mundo] Tamanho: {tamanho_real}x{tamanho_real}")
        print(f"[Personagem] Nome: {mundo.nome_humano} | Idade: {mundo.idade_humano}")
        print(f"[Lore] Origem: {mundo.origem_humano}")
        print(f"[Quests Ativas] {len(getattr(mundo, 'quests_ativas', []))}")
        if hasattr(mundo, 'perfil_jogador') and mundo.perfil_jogador:
            print(f"[Detalhes do Personagem] {json.dumps(mundo.perfil_jogador, ensure_ascii=False, indent=2)}")
        if hasattr(mundo, 'world_lore') and mundo.world_lore:
            print(f"[World Lore] {json.dumps(mundo.world_lore, ensure_ascii=False, indent=2)}")

    print(f"[Raphael] Mundo pronto para jogar!")

    # Sistemas Stardew Valley
    farm_manager = FarmManager(tamanho_farm=20)
    # Add initial seeds
    farm_manager.adicionar_sementes("milho", 10)
    farm_manager.adicionar_sementes("tomate", 10)
    farm_manager.adicionar_sementes("abobora", 8)
    farm_manager.adicionar_sementes("melancia", 5)
    relacao_gerenciador = GerenciadorRelacoes()
    calendario = Calendario(ano_inicial=1)
    quest_manager = QuestManager()
    objetivo_geral = ObjetivoGeral()
    pesca_manager = MiniGamePesca()
    historico_pesca = HistoricoPesca()
    clima_sistema = SistemaClima()

    # Sistema de registro de ações do jogador
    save_dir = SAVE_DIR / normalizar_nome_save(save_atual) if save_atual else SAVE_DIR / "temp_save"
    save_dir.mkdir(parents=True, exist_ok=True)
    action_logger = ActionLogger(save_dir / "player_history.db")
    print(f"[Sistema] Action Logger inicializado: {save_dir / 'player_history.db'}")

    # === Novos Sistemas: UI, Ambiance, Diálogo, Mundo ===
    # UI Enhancements
    barra_hp = BarraProgresso(largura=150, cor_cheia=(200, 80, 80), cor_vazia=(100, 100, 100))
    barra_comida = BarraProgresso(largura=150, cor_cheia=(200, 150, 80), cor_vazia=(100, 100, 100))
    barra_morale = BarraProgresso(largura=150, cor_cheia=(80, 200, 100), cor_vazia=(100, 100, 100))
    tooltip_sistema = TooltipSistema()
    print("[Sistema] UI Enhancements carregado")

    # Location Ambiance System
    gerenciador_ambiance = GerenciadorAmbiance()
    sistema_tempo_ambiance = SistemaTempoAmbiane()
    print("[Sistema] Location Ambiance System carregado")

    # NPC Dialogue AI System
    sistema_conversas = SistemaConversas()
    print("[Sistema] NPC Dialogue AI System carregado")

    # Hotbar Mode System
    if HotbarManager:
        hotbar = HotbarManager()
        print("[Sistema] Hotbar Mode System carregado")
    else:
        hotbar = None

    # NPC Backstory Lazy Loading System
    if SistemaBackstoriesLazyLoading:
        sistema_backstories = SistemaBackstoriesLazyLoading()
        # Initialize basic backstories for all NPCs
        for npc_nome in relacao_gerenciador.relacoes.keys():
            if npc_nome != mundo.nome_humano:  # Don't create backstory for player
                sistema_backstories.criar_npc_backstory(
                    nome=npc_nome,
                    papel_social="Cidadão",
                    idade=random.randint(15, 70),
                    origem=random.choice(list(["aldeão", "cidade", "floresta", "castelo", "masmorra"]))
                )
        print(f"[Sistema] NPC Backstory Lazy Loading System carregado - {len(sistema_backstories.backstories_basicas)} NPCs")
    else:
        sistema_backstories = None

    # World Interactions System
    gerenciador_objetos = GerenciadorObjetos()
    gerenciador_objetos.gerar_objetos_procedural(tamanho_mundo=tamanho_real, densidade=0.02)
    sistema_povoado = SistemaPovoado()
    sistema_progresso = SistemaProgresso()
    print(f"[Sistema] World Interactions System carregado com {len(gerenciador_objetos.objetos_mundo)} objetos")

    # Sound/Music System
    gerenciador_som = GerenciadorSom()
    gerenciador_efeitos = GerenciadorEfeitosSonoros()
    # Apply volume from config
    volume_config = cfg.get("volume_master", 80) / 100.0
    if hasattr(gerenciador_som, 'definir_volume'):
        gerenciador_som.definir_volume(volume_config)
    print("[Sistema] Sound Manager carregado")

    # === Novos Sistemas Integrados ===
    
    # Equipment System
    if BancoDados_Items:
        banco_items = BancoDados_Items()
        equipamento_jogador = Equipamento() if Equipamento else None
        print("[Sistema] Equipment System carregado")
    
    # Progression/Skills System
    if BancoDados_Habilidades:
        banco_habilidades = BancoDados_Habilidades()
        from .progression import SistemaProgression
        sistema_progressao_jogador = SistemaProgression()
        # Learn some starter skills
        sistema_progressao_jogador.aprender_habilidade(101)  # Golpe Crítico
        print(f"[Sistema] Skills/Progression System carregado - Nível {sistema_progressao_jogador.nivel} | HP Max: {sistema_progressao_jogador.vida_max}")
    else:
        banco_habilidades = None
        sistema_progressao_jogador = None
    
    # Mobs System
    if GerenciadorMobs:
        gerenciador_mobs = GerenciadorMobs()
        # Spawn initial mobs in the world
        from .mobs import BiomaMob
        for _ in range(3):  # Spawn 3 initial mobs
            x = random.randint(mundo.humano[0] - 50, mundo.humano[0] + 50)
            y = random.randint(mundo.humano[1] - 50, mundo.humano[1] + 50)
            gerenciador_mobs.spawan_mob_random(BiomaMob.PRADARIA, x, y)
        print(f"[Sistema] Mob Manager inicializado com {len(gerenciador_mobs.mobs)} mobs")
    else:
        gerenciador_mobs = None
    
    # Dungeons System
    if Masmorra and GerenciadorDungeonSessao:
        gerenciador_dungeons = {}  # Armazenar geradores/entradas
        gerenciador_sessao_dungeon = GerenciadorDungeonSessao()
        gerador_dungeon = Gerador_Masmorra()
        
        # Gerar entradas de dungeon no mundo
        if GeneradorEntradaDungeon:
            entradas_dungeon = GeneradorEntradaDungeon.gerar_multiplas_entradas(tamanho_real, quantidade=4)
            # Adicionar às interações do mundo
            for entrada in entradas_dungeon:
                gerenciador_dungeons[entrada['id']] = entrada
        
        print(f"[Sistema] Dungeon System carregado com {len(gerenciador_dungeons)} entradas")
    else:
        gerenciador_dungeons = None
        gerenciador_sessao_dungeon = None
        gerador_dungeon = None
    
    # Biomas System
    if ConfiguradorBiomas:
        configurador_biomas = ConfiguradorBiomas()
        print("[Sistema] Biomas System carregado")
    else:
        configurador_biomas = None
    
    # Animations System
    if GerenciadorAnimacoes:
        gerenciador_animacoes = GerenciadorAnimacoes()
        print("[Sistema] Animation System carregado")
    else:
        gerenciador_animacoes = None
    
    # NPC Backstories
    if GeradorHistoricosIA:
        gerador_historicos = GeradorHistoricosIA()
        print("[Sistema] NPC Backstory Generator carregado")
    else:
        gerador_historicos = None

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
    menu_aberto: str | None = None
    opcao_pausa_selecionada = 0
    opcao_config_selecionada = 0
    ultimo_tempo_menu_nav = 0.0
    inventario_aberto = False
    indice_inventario_hover: int | None = None
    em_dungeon = False  # Rastrear se o jogador está em dungeon
    ultimo_update_animais = time.time()
    ultimo_dia_culturas = tempo_sistema.dia  # Rastrear dia anterior para atualizacoes de culturas
    ultimo_dia_calendario = calendario.dia_mes  # Rastrear para eventos de novo dia
    ultimo_spawn_mobs = time.time()  # Rastrear para spawning de mobs
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

    # Começar música do jogo
    gerenciador_som.tocar_musica(MusicaContexto.EXPLORAR, fade_in=False)

    # Auto-save on game start
    print(f"[Auto-save] Salvando mundo inicial: {save_atual}")
    salvar_jogo(save_atual, mundo, memoria, {
        "tick": tick,
        "timestamp": time.time(),
        "versao": 1,
        "personagem": mundo.nome_humano,
        "idade": mundo.idade_humano,
        "origem": mundo.origem_humano
    })

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
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Handle pause menu mouse clicks
                if menu_aberto == "pausa":
                    mouse_pos = evento.pos
                    # Calculate button positions (matching renderizar_menu_pausa)
                    tela_width = tela.get_width()
                    tela_height = tela.get_height()
                    area_x = tela_width // 2 - 220
                    area_y = tela_height // 2 - 200
                    
                    botao_altura = 50
                    botao_largura = 340
                    espaco = 8
                    inicio_y = area_y + 80
                    
                    for i in range(6):
                        botao = pygame.Rect(
                            area_x + (440 - botao_largura) // 2,
                            inicio_y + i * (botao_altura + espaco),
                            botao_largura,
                            botao_altura
                        )
                        if botao.collidepoint(mouse_pos):
                            opcao_pausa_selecionada = i
                            # Execute the selected option
                            if i == 0:  # Retomar Jogo
                                menu_aberto = None
                                pausado = False
                            elif i == 1:  # Salvar e Continuar
                                nome_final = salvar_jogo(save_atual, mundo, memoria, {"tick": tick, "timestamp": time.time(), "versao": 1})
                                save_atual = nome_final
                                historico_chat.append(f"Sistema: save '{nome_final}' gravado")
                                menu_aberto = None
                                pausado = False
                            elif i == 2:  # Salvar Como Novo Save
                                modo_input = "salvar_como"
                                texto_input = ""
                                menu_aberto = None
                            elif i == 3:  # Mudar Configuracoes
                                menu_aberto = "configuracoes"
                                pausado = True
                                opcao_config_selecionada = 0
                            elif i == 4:  # Voltar ao Menu
                                modo_input = None
                                rodando = False
                            elif i == 5:  # Sair do Jogo
                                rodando = False
                            break
            elif evento.type == pygame.KEYDOWN:
                agora = time.time()
                
                # Menus keyboard handling
                if menu_aberto == "pausa":
                    if evento.key == pygame.K_ESCAPE:
                        menu_aberto = None
                        pausado = False
                        continue
                    
                    # Mouse click handling for pause menu
                    elif evento.key == pygame.K_UP and agora - ultimo_tempo_menu_nav > 0.15:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 6
                        ultimo_tempo_menu_nav = agora
                        continue
                    elif evento.key == pygame.K_DOWN and agora - ultimo_tempo_menu_nav > 0.15:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 6
                        ultimo_tempo_menu_nav = agora
                        continue
                    elif evento.key == pygame.K_RETURN:
                        if opcao_pausa_selecionada == 0:  # Retomar Jogo
                            menu_aberto = None
                            pausado = False
                        elif opcao_pausa_selecionada == 1:  # Salvar e Continuar
                            nome_final = salvar_jogo(save_atual, mundo, memoria, {"tick": tick, "timestamp": time.time(), "versao": 1})
                            save_atual = nome_final
                            historico_chat.append(f"Sistema: save '{nome_final}' gravado")
                            menu_aberto = None
                            pausado = False
                        elif opcao_pausa_selecionada == 2:  # Salvar Como Novo Save
                            modo_input = "salvar_como"
                            texto_input = ""
                            menu_aberto = None
                        elif opcao_pausa_selecionada == 3:  # Mudar Configuracoes
                            menu_aberto = "configuracoes"
                            pausado = True
                            opcao_config_selecionada = 0
                        elif opcao_pausa_selecionada == 4:  # Voltar ao Menu
                            modo_input = None
                            rodando = False
                        elif opcao_pausa_selecionada == 5:  # Sair do Jogo
                            rodando = False
                        continue
                elif menu_aberto == "configuracoes":
                    if evento.key == pygame.K_UP:
                        opcao_config_selecionada = max(0, opcao_config_selecionada - 1)
                    elif evento.key == pygame.K_DOWN:
                        opcao_config_selecionada = min(5, opcao_config_selecionada + 1)
                    elif evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT:
                        opcao_config_selecionada, cfg, fechar = processar_input_configuracoes(
                            evento, opcao_config_selecionada, cfg, gerenciador_som
                        )
                        if fechar:
                            menu_aberto = None
                            pausado = False
                    elif evento.key == pygame.K_RETURN:
                        opcao_config_selecionada, cfg, fechar = processar_input_configuracoes(
                            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN), opcao_config_selecionada, cfg, gerenciador_som
                        )
                        if fechar:
                            menu_aberto = None
                            pausado = False
                    elif evento.key == pygame.K_ESCAPE:
                        menu_aberto = None
                        pausado = False
                    continue
                elif menu_aberto in {"ajuda", "lore", "skills", "quests", "dungeons", "stats", "equipamento", "farming", "backstory"}:
                    if evento.key == pygame.K_ESCAPE:
                        menu_aberto = None
                        pausado = False
                        continue
                
                # TAB - Switch Game Modes (Hotbar)
                if evento.key == pygame.K_TAB and modo_input is None:
                    if hotbar:
                        hotbar.ciclar_modo_frente()
                        historico_chat.append(f"🎮 Modo: {hotbar.modo_atual.value}")
                    continue
                
                # SHIFT+TAB - Previous Mode
                if evento.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT and modo_input is None:
                    if hotbar:
                        hotbar.ciclar_modo_atras()
                        historico_chat.append(f"🎮 Modo: {hotbar.modo_atual.value}")
                    continue
                
                # F1 - Help menu
                if evento.key == pygame.K_F1 and modo_input is None:
                    menu_aberto = "ajuda"
                    pausado = True
                    continue
                
                # F2 - Lore menu
                if evento.key == pygame.K_F2 and modo_input is None:
                    menu_aberto = "lore"
                    pausado = True
                    continue
                
                # K - Skills/Stats menu
                if evento.key == pygame.K_k and modo_input is None:
                    menu_aberto = "skills"
                    pausado = True
                    continue
                
                # Q - Quests menu
                if evento.key == pygame.K_q and modo_input is None:
                    menu_aberto = "quests"
                    pausado = True
                    continue
                
                # O - Dungeons menu
                if evento.key == pygame.K_o and modo_input is None:
                    menu_aberto = "dungeons"
                    pausado = True
                    continue
                
                # L - Stats menu
                if evento.key == pygame.K_l and modo_input is None:
                    menu_aberto = "stats"
                    pausado = True
                    continue
                
                # E (when not digging) - Equipment menu
                if evento.key == pygame.K_e and modo_input is None and not inventario_aberto:
                    menu_aberto = "equipamento"
                    pausado = True
                    continue
                
                # V - Farming menu
                if evento.key == pygame.K_v and modo_input is None:
                    menu_aberto = "farming"
                    pausado = True
                    continue
                
                if evento.key == pygame.K_ESCAPE and modo_input is None and menu_aberto is None:
                    menu_aberto = "pausa"
                    pausado = True
                    opcao_pausa_selecionada = 0
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
                            
                            # Check for special commands
                            if texto_final.lower() in ["!history", "!historico", "!stats", "!estatisticas"]:
                                from .history_utils import format_action_statistics
                                stats_text = format_action_statistics(action_logger)
                                historico_chat.append(stats_text)
                            elif texto_final.lower() in ["!recent", "!recentes"]:
                                from .history_utils import get_action_summary
                                summary_text = get_action_summary(action_logger, action_count=15)
                                historico_chat.append(summary_text)
                            elif texto_final.lower() in ["!quest", "!missao", "!questao"]:
                                # Generate AI-powered contextual quest
                                q = mundo.gerar_quest_raphael()
                                titulo = q.get("titulo", "Quest de Raphael")
                                desc = q.get("descricao", "Uma jornada aguarda")
                                recompensa = q.get("recompensa_ouro", 100)
                                historico_chat.append(f"Raphael: {titulo}")
                                historico_chat.append(f"Sistema: {desc}")
                                historico_chat.append(f"Recompensa: {recompensa} ouro")
                            elif texto_final.lower() in ["!profecia", "!prophecy"]:
                                # Generate prophecy-driven quest
                                from .quest_generation_ai import gerar_quest_prophecy
                                quest_prof = gerar_quest_prophecy(mundo, memoria)
                                if quest_prof:
                                    historico_chat.append(f"Raphael: Sobre a profecia...")
                                    historico_chat.append(f"Sistema: {quest_prof.get('descricao', 'Um passo em direção ao destino')}")
                                    historico_chat.append(f"Dificuldade: {'⭐' * quest_prof.get('dificuldade', 3)}")
                                else:
                                    historico_chat.append("Raphael: Ainda não consigo ler a profecia claramente.")
                            elif texto_final.lower() in ["!conflito", "!conflict"]:
                                # Generate conflict-driven quest
                                from .quest_generation_ai import gerar_quest_conflito_principal
                                quest_conf = gerar_quest_conflito_principal(mundo, memoria)
                                if quest_conf:
                                    historico_chat.append(f"Raphael: O conflito reclama sua atenção...")
                                    historico_chat.append(f"Sistema: {quest_conf.get('descricao', 'Você é envolvido no conflito')}")
                                    historico_chat.append(f"Dificuldade: {'⭐' * quest_conf.get('dificuldade', 4)}")
                                else:
                                    historico_chat.append("Raphael: O conflito permanece obscuro.")
                            elif "item" in texto_final.lower() and ("criar" in texto_final.lower() or "gerar" in texto_final.lower()):
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
                                
                                # Reveal NPC backstory on first interaction
                                if sistema_backstories and not sistema_backstories.foi_revelada_backstory(mundo.npc_foco):
                                    backstory_detalhada = sistema_backstories.revelar_backstory_npc(mundo.npc_foco)
                                    if backstory_detalhada:
                                        historico_chat.append(f"📖 Você aprendeu mais sobre {mundo.npc_foco}!")
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
                    pygame.K_j,
                    pygame.K_m,
                    pygame.K_h,
                    pygame.K_n,
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
                    # Attack with equipment and progression bonuses
                    dano_base = 5
                    bônus_equipamento = 0
                    bônus_progressao = 0
                    arma_equipada = ""
                    
                    # Apply equipment bonuses
                    if equipamento_jogador:
                        bônus_equipamento = equipamento_jogador.bônus_ataque
                        if equipamento_jogador.arma:
                            arma_equipada = f" com {equipamento_jogador.arma.nome}"
                    
                    # Apply progression system bonuses
                    if sistema_progressao_jogador:
                        bônus_progressao = sistema_progressao_jogador.ataque_total - 5
                    
                    dano_total = dano_base + bônus_equipamento + bônus_progressao
                    mundo.atacar()
                    historico_chat.append(f"⚔️  Golpe da espada{arma_equipada}! Dano: {dano_total}")
                    
                    # Check for nearby mobs and damage them
                    if gerenciador_mobs:
                        try:
                            mobs_proximos = [m for m in gerenciador_mobs.mobs if 
                                           abs(m.x - mundo.humano[0]) <= 2 and 
                                           abs(m.y - mundo.humano[1]) <= 2]
                            
                            for mob in mobs_proximos:
                                dano_real = mob.receber_dano(dano_total)
                                historico_chat.append(f"  →  {mob.nome} tomou {dano_real} dano! HP: {mob.percentual_vida}%")
                                
                                # Check if mob is dead and give loot
                                if not mob.esta_vivo:
                                    historico_chat.append(f"💀 {mob.nome} foi derrotado!")
                                    # Add gold reward
                                    ouro_drop = mob.ouro_drop
                                    mundo.inventario['ouro'] = mundo.inventario.get('ouro', 0) + ouro_drop
                                    historico_chat.append(f"  💰 +{ouro_drop} ouro")
                                    
                                    # Roll for loot drops
                                    # Get mob definition for drop table
                                    from .mobs import MOBS_DATABASE
                                    definicao_mob = MOBS_DATABASE.get(mob.nome.lower())
                                    if definicao_mob and definicao_mob.itens_drop_possíveis:
                                        for item_drop in definicao_mob.itens_drop_possíveis:
                                            if random.random() < item_drop.get("chance", 0.1):
                                                nome_item = item_drop.get("nome", "item desconhecido")
                                                # Create a generic item and add to inventory
                                                item_novo = {
                                                    "nome": nome_item,
                                                    "tipo": "material",
                                                    "quantidade": 1,
                                                    "valor": 10 + random.randint(0, 20)
                                                }
                                                if 'itens' not in mundo.inventario_itens:
                                                    mundo.inventario_itens = []
                                                mundo.inventario_itens.append(item_novo)
                                                historico_chat.append(f"  📦 Obteve: {nome_item}")
                                    
                                    # Gain XP
                                    exp_dado = mob.exp_drop
                                    if sistema_progressao_jogador:
                                        levouup = sistema_progressao_jogador.ganhar_experiencia(exp_dado)
                                        historico_chat.append(f"  ⭐ +{exp_dado} XP")
                                        if levouup:
                                            historico_chat.append(f"💪 LEVEL UP! Nível agora é {sistema_progressao_jogador.nivel}!")
                                            historico_chat.append(f"   HP Max: {sistema_progressao_jogador.vida_max} | Pontos de skill: +{sistema_progressao_jogador.pontos_skill_disponiveis}")
                                    mundo.moralidade_jogador += 1
                        except Exception as e:
                            pass  # Silently handle mob combat errors
                    
                    memoria.adicionar_evento(f"{mundo.nome_humano} atacou um inimigo com dano {dano_total}")
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
                    # Interagir com objetos do mundo primeiro, depois ação contextual
                    objetos_proximos = gerenciador_objetos.obter_objetos_proximo(mundo.humano[0], mundo.humano[1], raio=1)
                    if objetos_proximos:
                        obj = objetos_proximos[0]
                        resultado = gerenciador_objetos.interagir_objeto(obj.id)
                        if resultado['sucesso']:
                            historico_chat.append(f"🏛️ {resultado['nome']}: {resultado['descricao']}")
                            historico_chat.append(f"💰 Ganho: {resultado['recompensa']}")
                            sistema_progresso.registrar_descoberta(resultado['nome'])
                            # Apply rewards
                            if 'ouro' in resultado['recompensa']:
                                mundo.inventario['ouro'] = mundo.inventario.get('ouro', 0) + resultado['recompensa']['ouro']
                            if 'conhecimento' in resultado['recompensa']:
                                mundo.moralidade_jogador += resultado['recompensa']['conhecimento']
                        else:
                            historico_chat.append(f"Sistema: {resultado['mensagem']}")
                    else:
                        # Se não houver objeto, fazer ação contextual
                        historico_chat.append(f"Sistema: {mundo.acao_contextual()}")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_y:
                    npc_id = mundo.obter_npc_proximo()
                    if npc_id:
                        npc_proximo = mundo.npcs.get(npc_id, {})
                        mundo.npc_foco = npc_id
                        # Generate AI-powered contextual dialogue
                        npc_nome = npc_proximo.get('nome', 'Desconhecido')
                        npc_info = {
                            'personalidade': npc_proximo.get('personalidade', 'Amigável'),
                            'profissao': npc_proximo.get('profissao', 'Habitante'),
                            'relacionamento_historico': 'Conhecido',
                        }
                        mundo_contexto = {
                            'estacao': calendario.estacao_nome,
                            'clima': getattr(clima_sistema.clima_atual, 'value', 'Ensolarado'),
                            'hora': int(tempo_sistema.hora_decimal % 24),
                        }
                        dialogo_ia = sistema_conversas.iniciar_conversa(
                            npc_nome=npc_nome,
                            jogador_info={'nome': mundo.nome_humano, 'profissao': 'Aventureiro'},
                            npc_info=npc_info,
                            mundo_contexto=mundo_contexto,
                            hora=int(tempo_sistema.hora_decimal % 24)
                        )
                        historico_chat.append(f"{npc_nome}: {dialogo_ia}")
                        modo_input = "npc"
                        texto_input = ""
                    else:
                        historico_chat.append("Sistema: Nenhum NPC perto para conversar.")
                elif evento.key == pygame.K_p:
                    # Fishing minigame (P for Pesca)
                    # Determine location based on nearby water or default to "rio"
                    local_pesca = "rio"  # Default, could be enhanced to detect water tiles
                    hora_decimal = tempo_sistema.hora_decimal
                    estacao = calendario.estacao_nome
                    
                    if pesca_manager.iniciar_pesca(local_pesca, hora_decimal, estacao):
                        sucesso, msg_pesca = pesca_manager.tentar_pescagem(duracao_minutos=1)
                        historico_chat.append(f"🎣 {msg_pesca}")
                        
                        if sucesso:
                            # Registrar captura no histórico
                            historico_pesca.registrar_captura(
                                pesca_manager.peixe_capturado_nome,
                                pesca_manager.ganho_ouro
                            )
                            # Adicionar ouro ao inventário
                            mundo.inventario['ouro'] = mundo.inventario.get('ouro', 0) + pesca_manager.ganho_ouro
                            # Log action
                            memoria.adicionar_evento(f"{mundo.nome_humano} pescou um {pesca_manager.peixe_capturado_nome}")
                            action_logger.log_action(
                                tick=tick,
                                timestamp=time.time(),
                                action_type='fish',
                                description=f"Pescou {pesca_manager.peixe_capturado_nome} ganho {pesca_manager.ganho_ouro} ouro",
                                player_x=mundo.humano[0],
                                player_y=mundo.humano[1],
                                player_hp=mundo.hp,
                                player_food=mundo.inventario.get("comida", 0),
                                player_morale=mundo.moralidade_jogador,
                                details={
                                    'peixe': pesca_manager.peixe_capturado_nome,
                                    'ouro_ganho': pesca_manager.ganho_ouro,
                                }
                            )
                    else:
                        historico_chat.append("🎣 Nenhum peixe está ativo neste local/hora/estação.")
                    
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_x:
                    # X - Sair do dungeon
                    if em_dungeon and gerenciador_sessao_dungeon:
                        sucesso, recompensas = gerenciador_sessao_dungeon.sair_dungeon()
                        em_dungeon = False
                        if sucesso:
                            historico_chat.append("⚔️  Você saiu do dungeon!")
                            historico_chat.append(f"💰 Ouro obtido: {recompensas['ouro']}")
                            historico_chat.append(f"⚔️  Inimigos derrotados: {recompensas['inimigos_derrotados']}")
                            mundo.inventario['ouro'] = mundo.inventario.get('ouro', 0) + recompensas['ouro']
                    else:
                        pass  # X pode ser usado para outras ações fora de dungeon
                elif evento.key == pygame.K_j:
                    # J - Arar (Plow) - Farming mode only
                    modo_atual = hotbar.modo_atual.value if hotbar else None
                    if modo_atual == "FAZENDA":
                        celula = farm_manager.obter_celula(mundo.humano[0], mundo.humano[1])
                        if farm_manager.aradir_terreno(mundo.humano[0], mundo.humano[1]):
                            historico_chat.append("🌾 Você arou o terreno!")
                            mundo.moralidade_jogador += 1
                            contador_intervencao += 1
                            ultimo_tempo_acao = agora
                        else:
                            historico_chat.append("🌾 Terreno já foi arado ou não pode ser arado.")
                    else:
                        historico_chat.append("🌾 Use Modo FAZENDA (TAB) para arar.")
                elif evento.key == pygame.K_m:
                    # M - Plantar (Plant) - Farming mode only
                    modo_atual = hotbar.modo_atual.value if hotbar else None
                    if modo_atual == "FAZENDA":
                        sementes = farm_manager.obter_sementes_disponiveis()
                        if sementes:
                            # Plant default tipo (primeiro disponível)
                            tipo_primeira = list(sementes.keys())[0]
                            if farm_manager.plantar_semente(mundo.humano[0], mundo.humano[1], tipo_primeira, 5, tempo_sistema.dia, calendario.estacao_nome):
                                historico_chat.append(f"🌱 Você plantou {tipo_primeira}!")
                                mundo.moralidade_jogador += 1
                                contador_intervencao += 1
                                ultimo_tempo_acao = agora
                            else:
                                historico_chat.append("🌱 Não foi possível plantar aqui.")
                        else:
                            historico_chat.append("🌱 Você não tem sementes. Use !item criar para obter sementes.")
                    else:
                        historico_chat.append("🌱 Use Modo FAZENDA (TAB) para plantar.")
                elif evento.key == pygame.K_h:
                    # H - Contexto dependente: Colher (Harvest) em FAZENDA ou Dungeon em outros modos
                    modo_atual = hotbar.modo_atual.value if hotbar else None
                    if modo_atual == "FAZENDA":
                        # Harvest mode
                        celula = farm_manager.obter_celula(mundo.humano[0], mundo.humano[1])
                        sucesso, recompensas = farm_manager.colher(mundo.humano[0], mundo.humano[1], {"padrão": {"food_yield": 1.0}})
                        if sucesso:
                            historico_chat.append(f"🌾 Você colheu {recompensas['tipo']}! Ganho: {recompensas['valor']} ouro")
                            mundo.inventario['ouro'] = mundo.inventario.get('ouro', 0) + recompensas['valor']
                            mundo.moralidade_jogador += 2
                            contador_intervencao += 1
                            ultimo_tempo_acao = agora
                        else:
                            historico_chat.append("🌾 Nada para colher aqui.")
                    else:
                        # Dungeon mode
                        if em_dungeon:
                            pass  # Dentro do dungeon, H não faz nada
                        else:
                            # Procurar por entradas de dungeon próximas
                            if gerenciador_dungeons and gerador_dungeon:
                                dungeon_proximo = None
                                distancia_min = 2  # 2 tiles de distância
                                
                                for entrada_id, entrada in list(gerenciador_dungeons.items()):
                                    dist = abs(entrada['x'] - mundo.humano[0]) + abs(entrada['y'] - mundo.humano[1])
                                    if dist <= distancia_min:
                                        dungeon_proximo = entrada
                                        break
                                
                                if dungeon_proximo:
                                    # Gerar dungeon
                                    from .dungeon import TipoBiomaMasmorra
                                    profundidade = dungeon_proximo.get('profundidade_sugerida', 1)
                                    # Mapear tipo de entrada para bioma
                                    tipo_to_bioma = {
                                        'caverna': TipoBiomaMasmorra.CAVERNA_PEDRA,
                                        'cripta': TipoBiomaMasmorra.CRIPTA_ANTIGA,
                                        'torre': TipoBiomaMasmorra.TORRE_MALDITA,
                                        'templo': TipoBiomaMasmorra.TEMPLO_ESQUECIDO,
                                        'mina': TipoBiomaMasmorra.MINA_PROFUNDA,
                                        'floresta': TipoBiomaMasmorra.FLORESTAS_SOMBRIAS,
                                        'vulcao': TipoBiomaMasmorra.VULCAO,
                                    }
                                    bioma = tipo_to_bioma.get(dungeon_proximo.get('tipo', 'caverna'), TipoBiomaMasmorra.CAVERNA_PEDRA)
                                    
                                    try:
                                        masmorra = gerador_dungeon.gerar(profundidade, bioma)
                                        gerenciador_sessao_dungeon.entrar_dungeon(masmorra, dungeon_proximo['id'])
                                        em_dungeon = True
                                        historico_chat.append(f"⚔️  Você entrou em {dungeon_proximo['nome']}!")
                                        historico_chat.append(f"Profundidade: {profundidade} | Dificuldade: {masmorra.dificuldade.value}")
                                    except Exception as e:
                                        historico_chat.append(f"Erro ao entrar no dungeon: {e}")
                                else:
                                    historico_chat.append("Sistema: Nenhum dungeon próximo. Use H perto de uma entrada.")
                elif evento.key == pygame.K_n:
                    # N - Contexto dependente: Regar (Water) em FAZENDA ou Dungeon navigation
                    modo_atual = hotbar.modo_atual.value if hotbar else None
                    if modo_atual == "FAZENDA":
                        # Water mode
                        if farm_manager.regar_terreno(mundo.humano[0], mundo.humano[1]):
                            historico_chat.append("💧 Você regou o terreno!")
                            mundo.moralidade_jogador += 1
                            contador_intervencao += 1
                            ultimo_tempo_acao = agora
                        else:
                            historico_chat.append("💧 Terreno já foi regado ou não pode ser regado.")
                    else:
                        # Dungeon navigation
                        if em_dungeon and gerenciador_sessao_dungeon:
                            # Simples: ir para primeira sala conectada
                            sala = gerenciador_sessao_dungeon.sessao_ativa.dungeon_obj.sala_atual
                            if sala.conectada_a:
                                proxima_sala = sala.conectada_a[0]
                                if gerenciador_sessao_dungeon.avancar_sala(proxima_sala):
                                    historico_chat.append(f"Você avançou para a sala {proxima_sala}")
                                    historico_chat.append(gerenciador_sessao_dungeon.obter_descricao_sala())
                                else:
                                    historico_chat.append("Não foi possível avançar para essa sala")
                elif evento.key == pygame.K_r:
                    modo_input = "chat"
                    texto_input = ""
                elif evento.key == pygame.K_b:
                    # B - View NPC Backstory
                    if mundo.npc_foco and sistema_backstories:
                        menu_aberto = "backstory"
                        pausado = True
                    continue
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
                elif evento.key == pygame.K_F7 and modo_input is None:
                    # Abrir menu de configurações
                    menu_aberto = "configuracoes"
                    pausado = True
                    opcao_config_selecionada = 0

                if evento.key in teclas_poder_ativas:
                    id_poder = teclas_poder_ativas[evento.key]
                    if not mundo.ativar_poder_manual(id_poder):
                        teclas_poder_ativas.pop(evento.key, None)
                    if id_poder not in mundo.poderes:
                        teclas_poder_ativas.pop(evento.key, None)

                if evento.key in {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g, pygame.K_e, pygame.K_b, pygame.K_SPACE, pygame.K_c, pygame.K_t, pygame.K_z, pygame.K_f, pygame.K_y, pygame.K_p, pygame.K_j, pygame.K_m, pygame.K_n, pygame.K_h}:
                    memoria.adicionar_evento(f"Acao do jogador: {mundo.ultimo_evento}")
                    
                    # Log to action database
                    action_type_map = {
                        pygame.K_w: 'move_up',
                        pygame.K_s: 'move_down',
                        pygame.K_a: 'move_left',
                        pygame.K_d: 'move_right',
                        pygame.K_g: 'collect',
                        pygame.K_e: 'dig',
                        pygame.K_b: 'build_house',
                        pygame.K_SPACE: 'attack',
                        pygame.K_c: 'kill_animal',
                        pygame.K_t: 'pet_animal',
                        pygame.K_z: 'rest',
                        pygame.K_f: 'contextual_action',
                        pygame.K_y: 'talk_npc',
                        pygame.K_p: 'fish',
                        pygame.K_j: 'farm_plow',
                        pygame.K_m: 'farm_plant',
                        pygame.K_n: 'farm_water',
                        pygame.K_h: 'farm_harvest',
                    }
                    action_type = action_type_map.get(evento.key, 'unknown_action')
                    
                    action_logger.log_action(
                        tick=tick,
                        timestamp=time.time(),
                        action_type=action_type,
                        description=mundo.ultimo_evento,
                        player_x=mundo.humano[0],
                        player_y=mundo.humano[1],
                        player_hp=mundo.hp,
                        player_food=mundo.inventario.get("comida", 0),
                        player_morale=mundo.moralidade_jogador,
                        details={
                            'evento': mundo.ultimo_evento,
                        }
                    )

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
        
        # Spawning de mobs periodicamente
        if not pausado and gerenciador_mobs and (agora_frame - ultimo_spawn_mobs) >= 5.0:
            # Spawnar novo mob a distância aleatória do jogador
            try:
                from .mobs import BiomaMob
                
                # Determine biome based on player position for mob diversity
                def obter_bioma_em_posicao(x: int, y: int) -> BiomaMob:
                    """Determina bioma em uma posição usando hash seeded"""
                    seed = (x // 50) ^ (y // 50)
                    random_local = random.Random(seed)
                    biomas = list(BiomaMob)
                    return random_local.choice(biomas)
                
                distancia = random.randint(30, 70)
                angulo = random.uniform(0, 6.28)
                x = int(mundo.humano[0] + distancia * math.cos(angulo))
                y = int(mundo.humano[1] + distancia * math.sin(angulo))
                # Limitar ao tamanho do mundo
                x = max(0, min(x, mundo.tamanho - 1))
                y = max(0, min(y, mundo.tamanho - 1))
                
                # Get biome-appropriate mob
                bioma_local = obter_bioma_em_posicao(x, y)
                gerenciador_mobs.spawan_mob_random(bioma_local, x, y)
                ultimo_spawn_mobs = agora_frame
            except Exception as e:
                print(f"[Aviso] Erro ao spawnar mob: {e}")
        
        # Atualizar culturas diariamente
        if not pausado and tempo_sistema.dia > ultimo_dia_culturas:
            mundo.atualizar_culturas_diarias()
            ultimo_dia_culturas = tempo_sistema.dia
            
            # === Atualizações dos novos sistemas Stardew Valley ===
            # Avançar calendário
            eventos_calendario = calendario.avancar_dia()
            if eventos_calendario["novo_ano"]:
                historico_chat.append(f"🎆 {eventos_calendario['mensagem']}")
            if eventos_calendario["festival"]:
                historico_chat.append(eventos_calendario['mensagem'])
            
            # Avançar clima
            clima_tipo, msg_clima = clima_sistema.avancar_dia(calendario.estacao.value)
            historico_chat.append(f"Clima: {msg_clima}")
            
            # Atualizar farm
            farm_manager.avancar_dia()
            
            # Atualizar relacionamentos
            relacao_gerenciador.avancar_dia()
            
            # Atualizar quests
            quest_manager.avancar_dia()
            
            # Atualizar Mobs (spawning, movement)
            if gerenciador_mobs:
                gerenciador_mobs.avancar_dia()
            
            # Atualizar Dungeons (if any active)
            if gerenciador_dungeons:
                for dungeon_id in list(gerenciador_dungeons.keys()):
                    dungeon = gerenciador_dungeons[dungeon_id]
                    if hasattr(dungeon, 'avancar_dia'):
                        dungeon.avancar_dia()
            
            # Registrar no histórico
            memoria.adicionar_evento(f"Dia {calendario.dia_mes} de {calendario.estacao_nome}, Ano {calendario.ano}")
            
            # === Atualizações dos novos sistemas Stardew Enhanced ===
            # Atualizar cooldowns de objetos do mundo
            gerenciador_objetos.atualizar_cooldowns()
            
            # Limpar cache de diálogos antigos (novo dia = novos diálogos)
            sistema_tempo_ambiance.hora_atual = 6  # Day starts
            sistema_conversas.gerenciador.limpar_cache_hora(new_hora=6)


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
            # Reserve space at the bottom for hotbar + info bars, and at the right for chat
            altura_reservada_inferior = ALTURA_CHAT + 140  # chat + hotbar + info bars
            mapa_altura = max(1, tela.get_height() - ALTURA_HUD - altura_reservada_inferior)
            render_qx = max(10, min(mundo.tamanho, tela.get_width() // TAMANHO_CELULA))
            render_qy = max(8, min(mundo.tamanho, mapa_altura // TAMANHO_CELULA))
            camera_x, camera_y, celulas_largura, celulas_altura = calcular_camera(mundo, render_qx, render_qy)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            area_mapa_altura = tela.get_height() - ALTURA_HUD - altura_reservada_inferior
            if 0 <= mouse_x < celulas_largura * TAMANHO_CELULA and 0 <= mouse_y < area_mapa_altura:
                tile_x = camera_x + int(mouse_x // TAMANHO_CELULA)
                tile_y = camera_y + int(mouse_y // TAMANHO_CELULA)
                mundo.definir_direcao_olhar_por_tile(tile_x, tile_y)

        # === Atualizações por frame dos Novos Sistemas ===
        if not pausado:
            # Update current hour for NPC routines
            mundo.hora_atual = int(tempo_sistema.hora_decimal % 24)
            
            # Atualizar movimento de NPCs
            mundo.atualizar_npcs_movimento(relogio.get_time() / 1000.0)
            
            # Atualizar ambiance baseado em posição atual
            gerenciador_ambiance.atualizar_ambiance(mundo.humano[0], mundo.humano[1], {})
            
            # Atualizar time system para efeitos ambientes
            sistema_tempo_ambiance.hora_atual = int(tempo_sistema.hora_decimal % 24)
            sistema_tempo_ambiance.clima_atual = getattr(clima_sistema.clima_atual, 'value', 'Ensolarado')
            
            # Atualizar barras de progresso
            barra_hp.atualizar(mundo.hp / max(1, mundo.hp_maximo))
            barra_comida.atualizar(max(0, mundo.inventario.get("comida", 0)) / max(1, mundo.inventario.get("comida", 100)))
            barra_morale.atualizar((mundo.moralidade_jogador + 10) / 20)  # -10 to +10 mapped to 0-1
            
            # Atualizar música baseado no contexto do jogo
            contexto_musica = ContextoMusica.determinar_contexto(mundo, tempo_sistema, mundo.ultimo_evento, pausado=pausado)
            gerenciador_som.atualizar_musica(contexto_musica)
            
            # Gerar eventos do mundo aleatoriamente
            evento_mundo = sistema_povoado.gerar_evento(mundo.humano[0], mundo.humano[1])
            if evento_mundo and random.random() < 0.01:  # 1% chance per frame
                historico_chat.append(f"[Evento] {evento_mundo['nome']}: {evento_mundo['reacao']}")
                if "xp" not in historico_chat[-1] and "Encontro" not in historico_chat[-1]:
                    sistema_progresso.registrar_evento(evento_mundo['id'])

        tick += 1
        mapa_altura = max(1, tela.get_height() - ALTURA_HUD - ALTURA_CHAT)
        render_qx = max(10, min(mundo.tamanho, tela.get_width() // TAMANHO_CELULA))
        render_qy = max(8, min(mundo.tamanho, mapa_altura // TAMANHO_CELULA))
        modo_escuro = bool(cfg.get("modo_escuro", False))
        
        # === CRITICAL FIX: Clear entire screen before rendering ===
        # This fixes the ghosting/transparency trails bug by ensuring all previous frames are erased
        # Must be done with the FULL window dimensions, not just the map area
        tela.fill((20, 20, 30))
        
        # Renderizar mundo ou dungeon
        if em_dungeon and renderizar_dungeon_interior:
            renderizar_dungeon_interior(tela, gerenciador_sessao_dungeon)
        else:
            renderizar_mundo(tela, mundo, fonte_hud, fonte_emoji, "PAUSADO" if pausado else "JOGADOR", tempo_sistema, render_qx, render_qy, modo_escuro=modo_escuro)
        
        # Draw chat background to ensure no overlap and clear separation
        chat_bg_rect = pygame.Rect(0, tela.get_height() - ALTURA_CHAT, tela.get_width(), ALTURA_CHAT)
        pygame.draw.rect(tela, (25, 25, 35), chat_bg_rect)
        renderizar_chat(tela, historico_chat, fonte_hud, modo_input, texto_input, modo_escuro=modo_escuro)
        if inventario_aberto:
            renderizar_inventario(tela, mundo, indice_inventario_hover)
        
        # === Renderizar UI Enhancements ===
        if not pausado and not inventario_aberto and not em_dungeon:
            # Renderizar barras de progresso no HUD (não em dungeon)
            fonte_pequena = pygame.font.SysFont("constantia", 12)
            
            # Reposition health-related bars to bottom left, just above the chat and below the hotbar
            bar_x = 32  # Padding from left
            bar_y_base = tela.get_height() - ALTURA_CHAT - 90  # Just above chat area
            spacing = 28
            barra_hp.desenhar(tela, x=bar_x, y=bar_y_base, rotulo="HP")
            barra_comida.desenhar(tela, x=bar_x, y=bar_y_base + spacing, rotulo="Fome")
            barra_morale.desenhar(tela, x=bar_x, y=bar_y_base + 2 * spacing, rotulo="Moral")
            
            # Location ambiance info - repositioned to avoid overlap
            ambiance_atual = gerenciador_ambiance.ambiance_atual or {}
            if hasattr(ambiance_atual, 'descricao'):
                loc_text = f"📍 {ambiance_atual.descricao[:40]}..."
                txt = fonte_pequena.render(loc_text, True, (200, 200, 150))
                tela.blit(txt, (tela.get_width() - 300, tela.get_height() - 125))
            
            # Nearby objects indicator
            proximos = gerenciador_objetos.obter_objetos_proximo(mundo.humano[0], mundo.humano[1], raio=3)
            if proximos:
                obj_text = f"🏛️ {proximos[0].nome} ({abs(proximos[0].x - mundo.humano[0]) + abs(proximos[0].y - mundo.humano[1])} tiles)"
                txt = fonte_pequena.render(obj_text, True, (200, 180, 100))
                tela.blit(txt, (tela.get_width() - 300, tela.get_height() - 140))
        
        # Renderizar menus
        if menu_aberto == "ajuda":
            renderizar_menu_ajuda(tela)
        elif menu_aberto == "lore":
            renderizar_menu_lore(tela, mundo, memoria)
        elif menu_aberto == "pausa":
            renderizar_menu_pausa(tela, mundo, opcao_pausa_selecionada, tempo_sistema, historico_chat, mouse_pos=pygame.mouse.get_pos())
        elif menu_aberto == "configuracoes":
            renderizar_menu_configuracoes(tela, cfg, opcao_config_selecionada, gerenciador_som)
        elif menu_aberto == "equipamento" and renderizar_menu_equipamento:
            renderizar_menu_equipamento(tela, mundo, equipamento_jogador if 'equipamento_jogador' in locals() else None, banco_items if 'banco_items' in locals() else None)
        elif menu_aberto == "skills" and renderizar_menu_skills:
            renderizar_menu_skills(tela, mundo, banco_habilidades if 'banco_habilidades' in locals() else None)
        elif menu_aberto == "quests" and renderizar_menu_quests:
            renderizar_menu_quests(tela, mundo, quest_manager)
        elif menu_aberto == "dungeons" and renderizar_menu_dungeons:
            renderizar_menu_dungeons(tela, mundo, tamanho_real)
        elif menu_aberto == "stats" and renderizar_menu_stats:
            renderizar_menu_stats(tela, mundo, memoria)
        elif menu_aberto == "farming" and renderizar_menu_farming:
            renderizar_menu_farming(tela, farm_manager if 'farm_manager' in locals() else None, calendario)
        elif menu_aberto == "backstory" and renderizar_historia_npc and sistema_backstories:
            # Display NPC backstory menu
            npc_nome = mundo.npc_foco if mundo.npc_foco else None
            if npc_nome:
                backstory = sistema_backstories.obter_backstory_detalhada(npc_nome)
                familia = sistema_backstories.obter_familia_npc(npc_nome)
                if backstory:
                    renderizar_historia_npc(tela, backstory, familia)
        
        # Render Hotbar (now as horizontal bar at bottom left)
        if hotbar and not menu_aberto:
            # Place hotbar just above the player info bars and above the chat
            hotbar_y = tela.get_height() - ALTURA_CHAT - 140  # 140px above chat, adjust as needed
            hotbar.renderizar_hotbar(tela, y_position=hotbar_y)
        
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
