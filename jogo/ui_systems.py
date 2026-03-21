"""Renderizadores de UI para sistemas integrados (Equipment, Skills, Quests, Dungeons)"""
import pygame


def renderizar_menu_equipamento(tela: pygame.Surface, mundo, equipamento=None, banco_items=None) -> None:
    """Renderiza menu de equipamento mostrando itens equipados e bônus"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    area = pygame.Rect(40, 20, tela.get_width() - 80, tela.get_height() - 60)
    
    # Background panel
    pygame.draw.rect(tela, (208, 190, 150), area, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), area, 4, border_radius=16)
    
    # Title
    titulo = "EQUIPAMENTO"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    y = area.y + 50
    
    # Bônus totais
    if mundo:
        bonus_ataque = mundo.bonus_equipamentos.get("ataque", 0)
        bonus_defesa = mundo.bonus_equipamentos.get("defesa", 0)
        
        tela.blit(fonte_titulo.render("BONUS TOTAIS", True, (146, 98, 70)), (area.x + 20, y))
        y += 30
        tela.blit(fonte_texto.render(f"Ataque: +{int(bonus_ataque)}", True, (200, 80, 80)), (area.x + 40, y))
        y += 25
        tela.blit(fonte_texto.render(f"Defesa: +{int(bonus_defesa)}", True, (80, 150, 200)), (area.x + 40, y))
        y += 30
        
        # Itens Equipados
        tela.blit(fonte_titulo.render("ITENS EQUIPADOS", True, (146, 98, 70)), (area.x + 20, y))
        y += 30
        
        if mundo.inventario_itens:
            for idx, slot in enumerate(mundo.equipamentos):
                item_idx = mundo.equipamentos[slot]
                if item_idx is not None and 0 <= item_idx < len(mundo.inventario_itens):
                    item = mundo.inventario_itens[item_idx]
                    nome_item = item.get("nome", "Item Desconhecido")
                    tela.blit(fonte_texto.render(f"[{slot}] {nome_item}", True, (112, 74, 48)), (area.x + 40, y))
                    y += 22
        
        if y <area.bottom - 40:
            tela.blit(fonte_texto.render("Use 1-9 no inventário para equipar", True, (150, 120, 80)), (area.x + 40, y))


def renderizar_menu_skills(tela: pygame.Surface, mundo, banco_habilidades=None) -> None:
    """Renderiza menu de skills/habilidades e progressão"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    area = pygame.Rect(40, 20, tela.get_width() - 80, tela.get_height() - 60)
    
    # Background panel
    pygame.draw.rect(tela, (208, 190, 150), area, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), area, 4, border_radius=16)
    
    # Title
    titulo = "HABILIDADES & PROGRESSAO"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    y = area.y + 50
    
    # Stats do personagem
    tela.blit(fonte_titulo.render("ATRIBUTOS PRINCIPAIS", True, (146, 98, 70)), (area.x + 20, y))
    y += 30
    
    if mundo:
        stats_display = [
            (f"HP:", f"{mundo.hp:.0f}/{mundo.hp_maximo:.0f}", (200, 80, 80)),
            (f"Força:", f"+{int(mundo.bonus_equipamentos.get('ataque', 0))}", (184, 100, 60)),
            (f"Defesa:", f"+{int(mundo.bonus_equipamentos.get('defesa', 0))}", (80, 150, 200)),
            (f"Moralidade:", f"{mundo.moralidade_jogador:+d}", (80, 200, 100) if mundo.moralidade_jogador >= 0 else (200, 80, 80)),
        ]
        
        for label, valor, cor in stats_display:
            tela.blit(fonte_texto.render(label, True, (112, 74, 48)), (area.x + 40, y))
            tela.blit(fonte_texto.render(valor, True, cor), (area.x + 180, y))
            y += 25
        
        y += 15
        tela.blit(fonte_titulo.render("DESTREZA", True, (146, 98, 70)), (area.x + 20, y))
        y += 28
        tela.blit(fonte_texto.render("(Sistema de skills será implementado em breve)", True, (150, 120, 80)), (area.x + 40, y))


def renderizar_menu_quests(tela: pygame.Surface, mundo, quest_manager=None) -> None:
    """Renderiza menu de quests/missões"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    area = pygame.Rect(40, 20, tela.get_width() - 80, tela.get_height() - 60)
    
    # Background panel
    pygame.draw.rect(tela, (208, 190, 150), area, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), area, 4, border_radius=16)
    
    # Title
    titulo = "MISSOES E QUESTS"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    y = area.y + 50
    
    if mundo:
        # Quests ativas
        quests_ativas = getattr(mundo, 'quests_ativas', [])
        
        if quests_ativas:
            tela.blit(fonte_titulo.render("MISSOES ATIVAS", True, (146, 98, 70)), (area.x + 20, y))
            y += 30
            
            for i, quest in enumerate(quests_ativas[:5]):
                desc = quest.get('descricao', 'Missão sem descrição')
                # Quebra texto se for muito longo
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                tela.blit(fonte_texto.render(desc, True, (112, 74, 48)), (area.x + 40, y))
                y += 22
        else:
            tela.blit(fonte_titulo.render("NENHUMA MISSAO ATIVA", True, (146, 98, 70)), (area.x + 20, y))
            y += 30
            tela.blit(fonte_texto.render("Use !quest, !profecia ou !conflito para gerar missões", True, (150, 120, 80)), (area.x + 40, y))


def renderizar_menu_dungeons(tela: pygame.Surface, mundo, tamanho_real=100) -> None:
    """Renderiza menu de dungeons disponíveis"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    area = pygame.Rect(40, 20, tela.get_width() - 80, tela.get_height() - 60)
    
    # Background panel
    pygame.draw.rect(tela, (208, 190, 150), area, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), area, 4, border_radius=16)
    
    # Title
    titulo = "DUNGEONS & MAZMORRAS"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    y = area.y + 50
    
    tela.blit(fonte_titulo.render("MASMORRAS DISPONIVEIS", True, (146, 98, 70)), (area.x + 20, y))
    y += 30
    
    dungeons_info = [
        ("Caverna de Pedra", "Facil", "Próxima ao rio principal"),
        ("Cripta Antiga", "Normal", "Sob as ruinas da vila"),
        ("Torre Maldita", "Dificil", "No topo da montanha"),
        ("Templo Esquecido", "Dificil", "Perdido na floresta escura"),
    ]
    
    for nome, dif, loc in dungeons_info:
        tela.blit(fonte_texto.render(f"⚔️  {nome}", True, (112, 74, 48)), (area.x + 40, y))
        y += 22
        tela.blit(fonte_texto.render(f"  Dificuldade: {dif} | {loc}", True, (150, 120, 80)), (area.x + 60, y))
        y += 22
    
    y += 15
    tela.blit(fonte_texto.render("Sistema de entrada em dungeons será implementado", True, (150, 120, 80)), (area.x + 40, y))


def renderizar_menu_stats(tela: pygame.Surface, mundo, memoria=None) -> None:
    """Renderiza menu de estatísticas gerais"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    area = pygame.Rect(40, 20, tela.get_width() - 80, tela.get_height() - 60)
    
    # Background panel
    pygame.draw.rect(tela, (208, 190, 150), area, border_radius=16)
    pygame.draw.rect(tela, (146, 110, 78), area, 4, border_radius=16)
    
    # Title
    titulo = "ESTATISTICAS"
    tela.blit(fonte_subtitulo.render(titulo, True, (74, 48, 36)), (area.x + 20, area.y + 12))
    
    y = area.y + 50
    
    if mundo:
        tela.blit(fonte_titulo.render("PERSONAGEM", True, (146, 98, 70)), (area.x + 20, y))
        y += 30
        
        stats = [
            (f"Nome:", mundo.nome_humano),
            (f"Idade:", f"{mundo.idade_humano} anos"),
            (f"Origem:", mundo.origem_humano[:30]),
            (f"HP:", f"{mundo.hp:.0f}/{mundo.hp_maximo:.0f}"),
            (f"Comida:", f"{mundo.inventario.get('comida', 0)} unidades"),
            (f"Madeira:", f"{mundo.inventario.get('madeira', 0)}"),
            (f"Ouro:", f"{mundo.inventario.get('ouro', 0)}"),
            (f"Moralidade:", f"{mundo.moralidade_jogador:+d}"),
        ]
        
        for label, valor in stats:
            tela.blit(fonte_texto.render(label, True, (112, 74, 48)), (area.x + 40, y))
            tela.blit(fonte_texto.render(str(valor), True, (112, 74, 48)), (area.x + 180, y))
            y += 22
        
        y += 15
        tela.blit(fonte_titulo.render("MUNDO", True, (146, 98, 70)), (area.x + 20, y))
        y += 30
        
        world_stats = [
            (f"Tempo:", f"Dia {int(getattr(mundo, 'ano_atual', 1))}"),
            (f"Tamanho do Mundo:", f"{mundo.tamanho}x{mundo.tamanho}"),
            (f"Vilas:", f"{len(mundo.vilas)}"),
            (f"Animais:", f"{len(mundo.animais)}"),
        ]
        
        for label, valor in world_stats:
            tela.blit(fonte_texto.render(label, True, (112, 74, 48)), (area.x + 40, y))
            tela.blit(fonte_texto.render(str(valor), True, (112, 74, 48)), (area.x + 180, y))
            y += 22


def renderizar_dungeon_interior(tela: pygame.Surface, gerenciador_sessao=None) -> None:
    """Renderiza a visualização do interior de um dungeon"""
    fonte_texto = pygame.font.SysFont("constantia", 17)
    fonte_titulo = pygame.font.SysFont("constantia", 21, bold=True)
    fonte_subtitulo = pygame.font.SysFont("cambria", 28, bold=True)
    
    if not gerenciador_sessao or not gerenciador_sessao.sessao_ativa:
        tela.fill((30, 20, 10))  # Dark background
        texto = fonte_titulo.render("Sem Dungeon Ativo", True, (200, 150, 100))
        tela.blit(texto, (tela.get_width() // 2 - texto.get_width() // 2, tela.get_height() // 2))
        return
    
    sessao = gerenciador_sessao.sessao_ativa
    dungeon = sessao.dungeon_obj
    sala = dungeon.sala_atual if dungeon else None
    
    # Dark dungeon background
    tela.fill((30, 20, 10))
    
    # Top info bar
    info_area = pygame.Rect(10, 10, tela.get_width() - 20, 60)
    pygame.draw.rect(tela, (60, 40, 20), info_area, border_radius=8)
    pygame.draw.rect(tela, (150, 100, 60), info_area, 2, border_radius=8)
    
    tela.blit(fonte_titulo.render(f"⚔️  {sala.nome if sala else 'Desconhecido'}", True, (200, 150, 100)), (info_area.x + 15, info_area.y + 8))
    
    progresso = f"Progresso: {sessao.inimigos_derrotados} inimigos | {sessao.ouro_obtido} ouro"
    tela.blit(fonte_texto.render(progresso, True, (180, 140, 100)), (info_area.x + 15, info_area.y + 35))
    
    # Main content area
    y = 85
    
    if sala:
        # Room description
        tela.blit(fonte_titulo.render(f"Tipo: {sala.tipo.value}", True, (200, 100, 100)), (20, y))
        y += 30
        
        # Enemies
        if sala.inimigos:
            tela.blit(fonte_titulo.render(f"⚔️  Inimigos ({len(sala.inimigos)})", True, (220, 80, 80)), (20, y))
            y += 25
            
            for i, inimigo in enumerate(sala.inimigos):
                if inimigo.esta_vivo:
                    status = f"  [{i+1}] {inimigo.tipo} - HP: {inimigo.vida_atual}/{inimigo.vida_max}"
                    tela.blit(fonte_texto.render(status, True, (180, 100, 100)), (40, y))
                    y += 20
            y += 10
        
        # Treasure
        if sala.bauzinhos:
            tela.blit(fonte_titulo.render(f"💰 Tesouro ({len(sala.bauzinhos)})", True, (200, 180, 80)), (20, y))
            y += 25
            
            for i, bauzin in enumerate(sala.bauzinhos):
                status = f"  [{i+1}] Baú ({bauzin.raridade}) - {bauzin.ouro} ouro"
                cor = (200, 180, 100) if not bauzin.foi_aberto else (120, 110, 80)
                tela.blit(fonte_texto.render(status, True, cor), (40, y))
                y += 20
            y += 10
        
        # Connected rooms
        if sala.conectada_a:
            tela.blit(fonte_titulo.render("Saídas Disponíveis", True, (100, 180, 200)), (20, y))
            y += 25
            
            for sala_id in sala.conectada_a[:5]:
                tela.blit(fonte_texto.render(f"  → Sala {sala_id}", True, (150, 200, 220)), (40, y))
                y += 20
    
    # Instructions at bottom
    y = tela.get_height() - 80
    pygame.draw.rect(tela, (60, 40, 20), pygame.Rect(10, y, tela.get_width() - 20, 70), border_radius=8)
    
    instructions = [
        "NUMEROS: Atacar inimigo / Abrir baú",
        "SETAS/LETRA: Mover para sala",
        "X = Sair dungeon",
        "ESC = Menu"
    ]
    
    for i, instrucao in enumerate(instructions):
        tela.blit(fonte_texto.render(instrucao, True, (150, 120, 100)), (20, y + 10 + i * 18))


def renderizar_menu_farming(tela: pygame.Surface, farm_manager=None, calendario=None):
    """Renderiza o menu de fazenda com status e ações disponíveis."""
    if not farm_manager or not calendario:
        font = pygame.font.Font(None, 36)
        tela.blit(font.render("Farm Manager não inicializado!", True, (200, 50, 50)), (100, 200))
        return
    
    # Background
    pygame.draw.rect(tela, (40, 60, 30), pygame.Rect(0, 0, tela.get_width(), tela.get_height()))
    pygame.draw.rect(tela, (60, 90, 50), pygame.Rect(20, 20, tela.get_width() - 40, tela.get_height() - 40), border_radius=12)
    
    # Fonts
    fonte_titulo = pygame.font.Font(None, 44)
    fonte_subtitulo = pygame.font.Font(None, 32)
    fonte_texto = pygame.font.Font(None, 24)
    
    y = 40
    
    # Title
    tela.blit(fonte_titulo.render("FAZENDA", True, (200, 255, 100)), (40, y))
    y += 50
    
    # Farm Status
    tela.blit(fonte_subtitulo.render("Status da Fazenda", True, (150, 200, 100)), (40, y))
    y += 35
    
    estacao = calendario.obter_estacao() if calendario else "Primavera"
    dia_mes = calendario.dia_atual % 30 + 1 if calendario else 1
    
    status_info = [
        f"Estação: {estacao}",
        f"Dia: {dia_mes}/30",
        f"Terrenos Prontos: {len(getattr(farm_manager, 'terrenos_arados', []))}",
        f"Plantas em Crescimento: {len(getattr(farm_manager, 'plantas_crescendo', []))}",
    ]
    
    for info in status_info:
        tela.blit(fonte_texto.render(info, True, (200, 220, 150)), (60, y))
        y += 28
    
    y += 10
    
    # Available Actions
    tela.blit(fonte_subtitulo.render("Ações Disponíveis", True, (150, 200, 100)), (40, y))
    y += 35
    
    acoes = [
        "J = Arar Terreno",
        "M = Plantar Semente",
        "N = Regar Plantas",
        "H = Colher Culturas",
    ]
    
    for acao in acoes:
        tela.blit(fonte_texto.render(acao, True, (200, 220, 150)), (60, y))
        y += 28
    
    y += 15
    
    # Plantable Crops
    tela.blit(fonte_subtitulo.render("Culturas Disponíveis", True, (150, 200, 100)), (40, y))
    y += 35
    
    culturas_info = [
        ("Trigo", "8 dias"),
        ("Milho", "10 dias"),
        ("Batata", "6 dias"),
        ("Cenoura", "7 dias"),
        ("Tomate", "12 dias"),
    ]
    
    for cultura, tempo in culturas_info:
        tela.blit(fonte_texto.render(f"  {cultura}: {tempo} para crescimento", True, (180, 200, 120)), (60, y))
        y += 24
    
    # Bottom instructions
    y = tela.get_height() - 60
    pygame.draw.rect(tela, (30, 50, 20), pygame.Rect(20, y, tela.get_width() - 40, 50), border_radius=8)
    
    instrucoes = [
        "ESC = Voltar | SETAS = Navegar",
    ]
    
    for instrucao in instrucoes:
        tela.blit(fonte_texto.render(instrucao, True, (150, 200, 100)), (40, y + 12))


def renderizar_historia_npc(tela: pygame.Surface, backstory=None, familia=None) -> None:
    """Renderiza o histórico detalhado de um NPC"""
    if not backstory:
        font = pygame.font.Font(None, 36)
        tela.blit(font.render("Sem informação de backstory!", True, (200, 50, 50)), (100, 200))
        return
    
    # Background
    pygame.draw.rect(tela, (30, 20, 15), pygame.Rect(0, 0, tela.get_width(), tela.get_height()))
    
    # Fonts
    fonte_titulo = pygame.font.Font(None, 44)
    fonte_subtitulo = pygame.font.Font(None, 32)
    fonte_texto = pygame.font.Font(None, 20)
    
    y = 40
    
    # Title - NPC Name
    tela.blit(fonte_titulo.render(f"📖 {backstory.nome_npc}", True, (255, 200, 100)), (40, y))
    y += 50
    
    # Basic info
    tela.blit(fonte_subtitulo.render("Sobre", True, (200, 150, 100)), (40, y))
    y += 30
    
    info_basica = [
        f"Idade: {backstory.idade_natal} anos",
        f"Quem é: {backstory.quem_e}",
    ]
    
    for info in info_basica:
        tela.blit(fonte_texto.render(info, True, (200, 200, 150)), (60, y))
        y += 24
    
    y += 10
    
    # History
    if backstory.como_cresceu:
        tela.blit(fonte_subtitulo.render("Infância", True, (200, 150, 100)), (40, y))
        y += 25
        tela.blit(fonte_texto.render(backstory.como_cresceu, True, (180, 180, 140)), (60, y))
        y += 30
    
    # Marked event
    if backstory.evento_marcante:
        tela.blit(fonte_subtitulo.render("Evento Marcante", True, (200, 150, 100)), (40, y))
        y += 25
        tela.blit(fonte_texto.render(backstory.evento_marcante, True, (220, 120, 120)), (60, y))
        y += 30
    
    # Dream/Secret
    if backstory.sonho_segredo:
        tela.blit(fonte_subtitulo.render("Sonho Secreto", True, (200, 150, 100)), (40, y))
        y += 25
        tela.blit(fonte_texto.render(backstory.sonho_segredo, True, (150, 180, 220)), (60, y))
        y += 30
    
    # Family
    if familia and len(familia) > 0:
        tela.blit(fonte_subtitulo.render("Família", True, (200, 150, 100)), (40, y))
        y += 25
        for familiar in familia[:5]:  # Show first 5 family members
            status_str = f"({familiar.status})" if familiar.status != "vivo" else ""
            tela.blit(
                fonte_texto.render(f"  {familiar.tipo_relacao.value}: {familiar.nome} {status_str}", True, (180, 200, 150)),
                (60, y)
            )
            y += 22
    
    # Traits
    y += 10
    tela.blit(fonte_subtitulo.render("Personalidade", True, (200, 150, 100)), (40, y))
    y += 25
    
    if backstory.virtudes:
        tela.blit(fonte_texto.render("Virtudes: " + ", ".join(backstory.virtudes), True, (100, 200, 100)), (60, y))
        y += 22
    
    if backstory.vícios:
        tela.blit(fonte_texto.render("Vícios: " + ", ".join(backstory.vícios), True, (200, 100, 100)), (60, y))
        y += 22
    
    # Bottom instruction
    y = tela.get_height() - 60
    pygame.draw.rect(tela, (40, 30, 20), pygame.Rect(20, y, tela.get_width() - 40, 50), border_radius=8)
    tela.blit(
        fonte_texto.render("ESC = Fechar | SETAS = Navegar", True, (150, 150, 100)),
        (40, y + 15)
    )

