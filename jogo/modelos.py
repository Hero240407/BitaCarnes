import random
import time

from .config import DIRECOES
from .personagens import obter_banco_personagens
from .sociedade import (
    PAPEIS_NPC,
    PLANTAS_DISPONIVEIS,
    evoluir_tipo_assentamento,
    gerar_lore_mundo,
    gerar_nome_local,
    gerar_objetivo_inicial,
    maybe_evento_coletivo,
    resposta_npc,
)


class MemoriaRaphael:
    def __init__(self):
        self.historico_conversas: list[dict] = []
        self.eventos: list[dict] = []
        self.moralidade_raphael = 0
        self.intervencoes = 0
        self.avisos_jogador = 0

    def adicionar_conversa(self, papel: str, mensagem: str) -> None:
        self.historico_conversas.append({"papel": papel, "mensagem": mensagem, "timestamp": time.time()})

    def adicionar_evento(self, evento: str) -> None:
        self.eventos.append({"evento": evento, "timestamp": time.time()})

    def obter_contexto(self, tamanho_maximo: int = 3000) -> str:
        contexto = "=== MEMORIA DA SESSAO ===\n"
        if self.historico_conversas:
            contexto += "CONVERSAS RECENTES:\n"
            for entrada in self.historico_conversas[-20:]:
                contexto += f"  {entrada['papel']}: {entrada['mensagem']}\n"
        if self.eventos:
            contexto += "\nEVENTOS RECENTES:\n"
            for entrada in self.eventos[-30:]:
                contexto += f"  - {entrada['evento']}\n"
        contexto += f"\nMORALIDADE DE RAPHAEL: {self.moralidade_raphael}\n"
        return contexto[:tamanho_maximo]


class SistemaTempo:
    def __init__(self, segundos_por_dia: float = 24 * 60) -> None:
        self.segundos_por_dia = float(segundos_por_dia)
        self.segundos_totais = 0.0
        self.congelado = False

    def atualizar(self, delta_segundos: float) -> None:
        if not self.congelado:
            self.segundos_totais += max(0.0, delta_segundos)

    @property
    def dia(self) -> int:
        return int(self.segundos_totais // self.segundos_por_dia) + 1

    @property
    def hora_decimal(self) -> float:
        frac = (self.segundos_totais % self.segundos_por_dia) / self.segundos_por_dia
        return frac * 24.0

    @property
    def horario_formatado(self) -> str:
        horas = int(self.hora_decimal) % 24
        minutos = int((self.hora_decimal - int(self.hora_decimal)) * 60) % 60
        return f"{horas:02d}:{minutos:02d}"

    @property
    def fase(self) -> str:
        h = self.hora_decimal
        if 6 <= h < 12:
            return "manha"
        if 12 <= h < 18:
            return "tarde"
        if 18 <= h < 22:
            return "anoitecer"
        return "noite"

    def alternar_congelamento(self) -> str:
        self.congelado = not self.congelado
        return "tempo parado" if self.congelado else "tempo retomado"

    def avancar(self, dias: int = 0, horas: int = 0, minutos: int = 0, anos: int = 0) -> None:
        dias_total = max(0, dias) + max(0, anos) * 365
        self.segundos_totais += dias_total * self.segundos_por_dia
        self.segundos_totais += max(0, horas) * (self.segundos_por_dia / 24)
        self.segundos_totais += max(0, minutos) * (self.segundos_por_dia / (24 * 60))


class Mundo:
    def __init__(self, tamanho: int, config: dict) -> None:
        banco_personagens = obter_banco_personagens()
        perfil_jogador = dict(config.get("perfil_jogador") or banco_personagens.gerar_perfil_jogador(config.get("nome_humano")))
        self.tamanho = tamanho
        self.humano = [tamanho // 2, tamanho // 2]
        self.perfil_jogador = perfil_jogador
        self.nome_humano = perfil_jogador.get("nome", config.get("nome_humano", "Escolhido"))
        self.idade_humano = int(perfil_jogador.get("idade", random.randint(9, 30)))
        self.origem_humano = perfil_jogador.get("origem", config.get("origem_humano", "Um sobrevivente misterioso."))

        self.tiles_comida: set[tuple[int, int]] = set()
        self.tiles_arvore: set[tuple[int, int]] = set()
        self.tiles_casa: set[tuple[int, int]] = set()
        self.tiles_inimigo: set[tuple[int, int]] = set()
        self.animais: dict[tuple[int, int], dict] = {}
        self.tiles_montanha: set[tuple[int, int]] = set()
        self.tiles_agua: set[tuple[int, int]] = set()
        self.tiles_santuario: set[tuple[int, int]] = set()
        self.tiles_vila: set[tuple[int, int]] = set()
        self.tiles_igreja: set[tuple[int, int]] = set()
        self.tiles_biblioteca: set[tuple[int, int]] = set()
        self.tiles_castelo: set[tuple[int, int]] = set()
        self.tiles_tesouro: dict[tuple[int, int], int] = {}
        self.tiles_armadilha: set[tuple[int, int]] = set()
        self.tiles_maldito: set[tuple[int, int]] = set()
        
        # Caminhos e estradas
        self.tiles_caminho_pedra: set[tuple[int, int]] = set()  # Stone paths (low development)
        self.tiles_estrada_asfalto: set[tuple[int, int]] = set()  # Asphalt roads (high development)
        self.tiles_mar: set[tuple[int, int]] = set()  # Sea/ocean tiles
        
        # Estruturas de fantasia e isekai adicionadas
        self.tiles_torre_magica: set[tuple[int, int]] = set()
        self.tiles_dragao_covil: set[tuple[int, int]] = set()
        self.tiles_floresta_sagrada: set[tuple[int, int]] = set()
        self.tiles_templo_antigo: set[tuple[int, int]] = set()
        self.tiles_caverna_cristal: set[tuple[int, int]] = set()
        self.tiles_portal_isekai: set[tuple[int, int]] = set()
        self.tiles_mina_anao: set[tuple[int, int]] = set()
        self.tiles_floresta_elfo: set[tuple[int, int]] = set()
        self.tiles_vulcao_menor: set[tuple[int, int]] = set()
        self.tiles_tumulo_antigo: set[tuple[int, int]] = set()

        self.vilas: dict[str, dict] = {}
        self.npcs: dict[str, dict] = {}
        self.casa_para_id: dict[tuple[int, int], str] = {}
        self.interior_ativo: str | None = None
        self.npc_foco: str | None = None
        
        # NPC Movement System
        self.npc_rotas: dict[str, list[tuple[int, int]]] = {}  # Route for each NPC
        self.npc_rota_indice: dict[str, int] = {}  # Current position in route
        self.npc_em_casa: dict[str, bool] = {}  # Whether NPC is inside home
        self.npc_proximo_movimento: dict[str, float] = {}  # Time until next movement
        
        # NPC Behavior System (AI-driven routines)
        self.npc_comportamento: dict[str, "ComportamentoNPC"] = {}  # AI behavior for each NPC

        self.world_lore = gerar_lore_mundo(self.nome_humano)
        self.ano_base = int(self.world_lore.get("era_inicial", 1500))
        self.ano_atual = self.ano_base
        self.quests_ativas: list[dict] = [gerar_objetivo_inicial()]

        self.hp_base = float(config.get("hp_inicial", 20))
        self.hp_maximo = self.hp_base
        self.hp = self.hp_maximo
        self.inventario = {
            "comida": float(config.get("comida_inicial", 8)),
            "madeira": float(config.get("madeira_inicial", 2)),
            "ouro": float(config.get("ouro_inicial", 0)),
            "agua_bencao": 0,
            "conhecimento": 0,
        }
        self.stats = {
            "pontos": 0,
            "casas_construidas": 0,
            "inimigos_derrotados": 0,
            "animais_mortos": 0,
            "comida_coletada": 0,
            "madeira_coletada": 0,
            "tesouros_encontrados": 0,
            "santuarios_visitados": 0,
            "animais_domesticados": 0,
            "interacoes_npc": 0,
            "anos_passados": 0,
        }
        self.poderes: dict[str, dict] = {}
        self.inventario_itens: list[dict] = []
        self.equipamentos: dict[str, int | None] = {
            "arma": None,
            "armadura": None,
            "acessorio": None,
            "reliquia": None,
            "consumivel": None,
        }
        self.bonus_equipamentos: dict[str, float] = {
            "ataque": 0.0,
            "defesa": 0.0,
            "hp": 0.0,
            "sorte": 0.0,
            "coleta": 0.0,
        }
        self.pet: dict | None = None
        self.magias_aprendidas: list[str] = []
        self.mestre_id: str | None = None
        self.direcao_olhar = "baixo"
        self.animar_humano_ate = 0.0
        self.tick_animacao_humano = 0
        self.ultimo_evento = "mundo inicializado"
        self.moralidade_jogador = 0
        
        # Animacao de movimento (walking)
        self.movimento_inicio_pos: list[float] = list(self.humano)
        self.movimento_fim_pos: list[float] = list(self.humano)
        self.movimento_tempo_inicial = 0.0
        self.movimento_duracao = 0.0  # Duracao em segundos
        self.movimento_ativo = False

        self.gerar_terreno()
        self.gerar_sociedade_inicial()
        self._aplicar_spawn_inicial(config.get("spawn_inicial"))
        itens_iniciais = list(config.get("itens_iniciais", []))
        if itens_iniciais:
            self.adicionar_itens_iniciais(itens_iniciais)

    def _tile_livre_para_spawn(self, x: int, y: int) -> bool:
        if not self.eh_caminavel(x, y):
            return False
        pos = (x, y)
        if pos in self.tiles_inimigo or pos in self.animais:
            return False
        for npc in self.npcs.values():
            if tuple(npc.get("pos", (-1, -1))) == pos:
                return False
        return True

    def _eh_vizinho_de(self, x: int, y: int, tiles: set[tuple[int, int]], distancia: int = 1) -> bool:
        for dx in range(-distancia, distancia + 1):
            for dy in range(-distancia, distancia + 1):
                if (x + dx, y + dy) in tiles:
                    return True
        return False

    def _combina_tema_spawn(self, x: int, y: int, tema: str) -> bool:
        tema_limpo = (tema or "").strip().lower()
        if not tema_limpo:
            return False

        if any(chave in tema_limpo for chave in ("vila", "aldeia", "cidade", "fronteira povoada")):
            return self._eh_vizinho_de(x, y, self.tiles_vila | self.tiles_casa | self.tiles_igreja | self.tiles_biblioteca, 2)
        if any(chave in tema_limpo for chave in ("floresta", "bosque", "mata", "arvore")):
            return self._eh_vizinho_de(x, y, self.tiles_arvore, 2)
        if any(chave in tema_limpo for chave in ("santuario", "templo", "sagrado", "igreja")):
            return self._eh_vizinho_de(x, y, self.tiles_santuario | self.tiles_igreja, 2)
        if any(chave in tema_limpo for chave in ("ruina", "biblioteca", "castelo", "fortaleza")):
            return self._eh_vizinho_de(x, y, self.tiles_biblioteca | self.tiles_castelo | self.tiles_casa, 2)
        if any(chave in tema_limpo for chave in ("rio", "agua", "lago", "margem", "costa")):
            return self._eh_vizinho_de(x, y, self.tiles_agua, 1)
        if any(chave in tema_limpo for chave in ("montanha", "penhasco", "serra", "colina")):
            return self._eh_vizinho_de(x, y, self.tiles_montanha, 1)
        if any(chave in tema_limpo for chave in ("fronteira", "ermo", "selvagem", "estrada")):
            return not self._eh_vizinho_de(x, y, self.tiles_vila | self.tiles_casa, 3)
        return False

    def _posicoes_preferidas_por_tema(self, tema: str) -> list[tuple[int, int]]:
        tema_limpo = (tema or "").strip().lower()
        if not tema_limpo:
            return []

        candidatos: list[tuple[int, int]] = []
        for y in range(self.tamanho):
            for x in range(self.tamanho):
                if self._tile_livre_para_spawn(x, y) and self._combina_tema_spawn(x, y, tema_limpo):
                    candidatos.append((x, y))
        random.shuffle(candidatos)
        return candidatos[:32]

    def _aplicar_spawn_inicial(self, spawn_cfg: dict | None) -> None:
        cx, cy = self.tamanho // 2, self.tamanho // 2
        candidatos_base: list[tuple[int, int]] = []
        tema_spawn = ""
        if isinstance(spawn_cfg, dict):
            try:
                sx = max(0, min(self.tamanho - 1, int(spawn_cfg.get("x", cx))))
                sy = max(0, min(self.tamanho - 1, int(spawn_cfg.get("y", cy))))
                candidatos_base.append((sx, sy))
            except (TypeError, ValueError):
                pass
            tema_spawn = str(spawn_cfg.get("tema", ""))
            candidatos_base.extend(self._posicoes_preferidas_por_tema(tema_spawn))
        candidatos_base.append((cx, cy))

        for bx, by in candidatos_base:
            for raio in range(0, 6):
                for dx in range(-raio, raio + 1):
                    for dy in range(-raio, raio + 1):
                        tx = bx + dx
                        ty = by + dy
                        if not (0 <= tx < self.tamanho and 0 <= ty < self.tamanho):
                            continue
                        if self._tile_livre_para_spawn(tx, ty):
                            self.humano = [tx, ty]
                            return

        for _ in range(400):
            rx = random.randint(0, self.tamanho - 1)
            ry = random.randint(0, self.tamanho - 1)
            if self._tile_livre_para_spawn(rx, ry):
                self.humano = [rx, ry]
                return

    def posicao_ocupada_por_entidade(self, x: int, y: int) -> bool:
        pos = (x, y)
        if pos == tuple(self.humano):
            return True
        if pos in self.tiles_inimigo:
            return True
        if pos in self.animais:
            return True
        for npc in self.npcs.values():
            if tuple(npc.get("pos", (-1, -1))) == pos:
                return True
        return False

    def posicao_livre_aleatoria(self) -> tuple[int, int]:
        for _ in range(350):
            x, y = random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)
            if self.eh_caminavel(x, y) and not self.posicao_ocupada_por_entidade(x, y):
                return (x, y)
        return (self.tamanho // 2, self.tamanho // 2)

    def eh_caminavel(self, x: int, y: int) -> bool:
        if not (0 <= x < self.tamanho and 0 <= y < self.tamanho):
            return False
        return (x, y) not in self.tiles_montanha and (x, y) not in self.tiles_agua

    def gerar_terreno(self) -> None:
        """Generate world terrain with improved algorithms for coherent biomes."""
        tema_terra = self.world_lore.get("tema_terra", "reino_fragmentado")
        
        # Step 1: Generate village centers first (before any blocked terrain)
        # This will be done later in gerar_sociedade_inicial()
        # But we need to reserve zones for villages
        zonas_vila_reservadas: set[tuple[int, int]] = set()
        
        # Step 2: Generate coherent mountain ranges (not scattered)
        self._gerar_montanhas_coerentes(tema_terra)
        
        # Step 3: Generate water lakes and seas (7+ tiles minimum for lakes)
        self._gerar_agua_coerente(tema_terra)
        
        # Step 4: Generate stone groups (3+ tiles minimum)
        # Stones are represented as scattered elements across biomes
        # For now, we'll use the existing tiles for added visual variety
        
        # Step 5: Spawn basic resources
        self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.85))
        self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.7))
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.1))
        self.spawn_animais(max(4, int(self.tamanho * 0.2)))
        
        # Step 6: Generate sanctuaries
        santuario_qty = int(self.tamanho * 0.08) if tema_terra == "ruinas_mystticas" else int(self.tamanho * 0.04)
        self.spawn_tiles(self.tiles_santuario, max(1, santuario_qty))

        # Step 7: Generate treasures, traps, curses
        for _ in range(int(self.tamanho * 0.08)):
            x, y = self.posicao_livre_aleatoria()
            self.tiles_tesouro[(x, y)] = random.randint(10, 60)

        armadilha_qty = int(self.tamanho * 0.08) if tema_terra == "terra_mutante" else int(self.tamanho * 0.06)
        maldito_qty = int(self.tamanho * 0.06) if tema_terra == "terra_mutante" else int(self.tamanho * 0.03)
        self.spawn_tiles(self.tiles_armadilha, armadilha_qty)
        self.spawn_tiles(self.tiles_maldito, maldito_qty)
        
        # Step 8: Estruturas de fantasia e isekai
        self.spawn_tiles(self.tiles_torre_magica, max(1, int(self.tamanho * 0.04)))
        self.spawn_tiles(self.tiles_dragao_covil, max(1, int(self.tamanho * 0.02)))
        self.spawn_tiles(self.tiles_floresta_sagrada, max(1, int(self.tamanho * 0.05)))
        self.spawn_tiles(self.tiles_templo_antigo, max(1, int(self.tamanho * 0.03)))
        self.spawn_tiles(self.tiles_caverna_cristal, max(1, int(self.tamanho * 0.03)))
        self.spawn_tiles(self.tiles_portal_isekai, max(1, int(self.tamanho * 0.02)))
        self.spawn_tiles(self.tiles_mina_anao, max(1, int(self.tamanho * 0.03)))
        self.spawn_tiles(self.tiles_floresta_elfo, max(1, int(self.tamanho * 0.04)))
        self.spawn_tiles(self.tiles_vulcao_menor, max(1, int(self.tamanho * 0.02)))
        self.spawn_tiles(self.tiles_tumulo_antigo, max(1, int(self.tamanho * 0.03)))

    def _gerar_montanhas_coerentes(self, tema_terra: str) -> None:
        """Generate mountain clusters >= 3 tiles using better algorithms."""
        if tema_terra == "terra_mutante":
            num_clusters = max(2, self.tamanho // 4)
            fill_rate = 0.20
        elif tema_terra == "ruinas_mystticas":
            num_clusters = max(2, self.tamanho // 3)
            fill_rate = 0.25
        else:  # reino_fragmentado, santuarios_selvagens
            num_clusters = max(2, self.tamanho // 4)
            fill_rate = 0.20

        for _ in range(num_clusters):
            cx = random.randint(2, self.tamanho - 3)
            cy = random.randint(2, self.tamanho - 3)
            raio = random.randint(2, 4)
            
            # Generate cluster using diamond/circle shape
            group_tiles: set[tuple[int, int]] = set()
            for y in range(max(0, cy - raio), min(self.tamanho, cy + raio + 1)):
                for x in range(max(0, cx - raio), min(self.tamanho, cx + raio + 1)):
                    # Use manhattan distance for more organic shapes
                    distancia = abs(x - cx) + abs(y - cy)
                    if distancia <= raio and random.random() < fill_rate:
                        group_tiles.add((x, y))
            
            # Only add if group has at least 3 tiles (minimum mountain size)
            if len(group_tiles) >= 3:
                self.tiles_montanha.update(group_tiles)

    def _gerar_agua_coerente(self, tema_terra: str) -> None:
        """Generate water lakes and seas. Lakes should have 7+ tiles (minimum lake size)."""
        if tema_terra == "terra_mutante":
            num_clusters = max(2, self.tamanho // 3)
            base_size = 10
        elif tema_terra == "ruinas_mystticas":
            num_clusters = max(1, self.tamanho // 4)
            base_size = 8
        else:  # reino_fragmentado, santuarios_selvagens
            num_clusters = max(2, self.tamanho // 3)
            base_size = 10

        min_lake_size = 7

        # Generate coherent water clusters
        for _ in range(num_clusters):
            cx = random.randint(1, self.tamanho - 2)
            cy = random.randint(1, self.tamanho - 2)
            raio = random.randint(1, 3)
            
            group_tiles: set[tuple[int, int]] = set()
            # Generate lake - spiral outward from center to ensure min size
            for radius_check in range(raio + 1):
                for y in range(max(0, cy - radius_check), min(self.tamanho, cy + radius_check + 1)):
                    for x in range(max(0, cx - radius_check), min(self.tamanho, cx + radius_check + 1)):
                        distancia = abs(x - cx) + abs(y - cy)
                        if distancia <= radius_check and 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                            # Don't place water on mountains or existing water too close
                            if (x, y) not in self.tiles_montanha and (x, y) not in self.tiles_agua:
                                # Bias towards center
                                prob = 0.7 if distancia == 0 else (0.5 if radius_check <= 1 else 0.35)
                                if random.random() < prob:
                                    group_tiles.add((x, y))
                                # Ensure we get enough tiles for lakes
                                elif len(group_tiles) < base_size and distancia <= radius_check:
                                    group_tiles.add((x, y))
            
            # Only add if group meets minimum lake size
            if len(group_tiles) >= min_lake_size:
                self.tiles_agua.update(group_tiles)
        
        # Optionally add some sea/ocean around edges
        self._gerar_mar_bordas()

    def _gerar_mar_bordas(self) -> None:
        """Generate sea/ocean tiles around world edges."""
        if self.tamanho < 20:
            return  # Only for larger worlds
        
        # Add ocean to edges (5% chance per edge tile)
        borda_thickness = 2
        for x in range(self.tamanho):
            for y in range(self.tamanho):
                is_on_edge = x < borda_thickness or x >= self.tamanho - borda_thickness or \
                             y < borda_thickness or y >= self.tamanho - borda_thickness
                if is_on_edge and random.random() < 0.5:
                    if not self._tile_livre_para_spawn(x, y):
                        continue
                    self.tiles_mar.add((x, y))

    def _gerar_caminhos_entre_vilas(self) -> None:
        """Generate paths connecting villages after village generation."""
        if len(self.vilas) < 2:
            return  # Need at least 2 villages to connect
        
        vilas_list = list(self.vilas.values())
        
        # Connect nearby villages in a network
        conectadas: set[int] = set()
        for i in range(len(vilas_list)):
            if len(conectadas) < len(vilas_list) - 1:
                # Find nearest unconnected village
                min_dist = float('inf')
                nearest_j = -1
                vi_pos = tuple(vilas_list[i]["pos"])
                
                for j in range(len(vilas_list)):
                    if i == j or j in conectadas:
                        continue
                    vj_pos = tuple(vilas_list[j]["pos"])
                    dist = abs(vi_pos[0] - vj_pos[0]) + abs(vi_pos[1] - vj_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                        nearest_j = j
                
                if nearest_j >= 0:
                    vj_pos = tuple(vilas_list[nearest_j]["pos"])
                    # Determine path type based on village technology level
                    tech_avg = (vilas_list[i].get("tecnologia", 1) + vilas_list[nearest_j].get("tecnologia", 1)) / 2
                    usar_asfalto = tech_avg >= 2.5
                    
                    # Trace path with A* pathfinding for better routes
                    self._tracar_caminho_astar(vi_pos, vj_pos, usar_asfalto)
                    conectadas.add(nearest_j)

    def _tracar_caminho_astar(self, inicio: tuple[int, int], fim: tuple[int, int], usar_asfalto: bool = False) -> None:
        """Trace a path using simple A* to go around obstacles."""  
        from collections import deque
        
        x0, y0 = inicio
        x1, y1 = fim
        
        # Use simple BFS pathfinding to navigate around terrain
        queue: deque = deque([(x0, y0, [(x0, y0)])])
        visited: set[tuple[int, int]] = {(x0, y0)}
        path_found: list[tuple[int, int]] | None = None
        
        while queue and len(visited) < self.tamanho * self.tamanho:
            x, y, path = queue.popleft()
            
            if x == x1 and y == y1:
                path_found = path
                break
            
            # Try all 4 directions, prioritizing straight paths
            neighbors = [
                (x, y + 1),  # down
                (x, y - 1),  # up
                (x + 1, y),  # right
                (x - 1, y),  # left
            ]
            
            for nx, ny in neighbors:
                if (nx, ny) not in visited and 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                    if self.eh_caminavel(nx, ny):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [(nx, ny)]))
        
        # Add path tiles if we found a route
        if path_found:
            for x, y in path_found:
                if self.eh_caminavel(x, y):
                    if usar_asfalto:
                        self.tiles_estrada_asfalto.add((x, y))
                    else:
                        self.tiles_caminho_pedra.add((x, y))

    def _tracar_caminho(self, inicio: tuple[int, int], fim: tuple[int, int], usar_asfalto: bool = False) -> None:
        """Trace a path between two points using Bresenham algorithm (simple line)."""
        x0, y0 = inicio
        x1, y1 = fim
        
        # Bresenham line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            pos = (x, y)
            
            # Add to appropriate path set if walkable
            if self.eh_caminavel(x, y):
                if usar_asfalto:
                    self.tiles_estrada_asfalto.add(pos)
                else:
                    self.tiles_caminho_pedra.add(pos)
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _gerar_roteiros_npcs(self) -> None:
        """Generate patrol routes for NPCs on village paths and AI-driven daily routines."""
        for npc_id, npc in self.npcs.items():
            vila_id = npc.get("vila_id")
            if not vila_id or vila_id not in self.vilas:
                continue
            
            vila = self.vilas[vila_id]
            vila_pos = tuple(vila["pos"])
            casa_pos = tuple(npc.get("pos", [0, 0]))
            
            # Build route: home → village center → nearby areas → home
            rota: list[tuple[int, int]] = []
            
            # Start at home
            rota.append(casa_pos)
            
            # Go to village center if different
            if casa_pos != vila_pos:
                rota.append(vila_pos)
            
            # Add some nearby patrol positions
            vx, vy = vila_pos
            for _ in range(3):
                px = max(0, min(self.tamanho - 1, vx + random.randint(-3, 3)))
                py = max(0, min(self.tamanho - 1, vy + random.randint(-3, 3)))
                if self.eh_caminavel(px, py):
                    rota.append((px, py))
            
            # Return home
            if rota and rota[-1] != casa_pos:
                rota.append(casa_pos)
            
            # Store route for this NPC
            self.npc_rotas[npc_id] = rota if len(rota) > 1 else [casa_pos]
            self.npc_rota_indice[npc_id] = 0
            self.npc_em_casa[npc_id] = True
            self.npc_proximo_movimento[npc_id] = 0.0
            
            # Generate AI-driven daily routine for NPC
            if npc_id in self.npc_comportamento:
                comportamento = self.npc_comportamento[npc_id]
                # Generate personalized routine based on NPC personality
                try:
                    comportamento.gerar_rotina_ia(
                        hora_local_trabalho=vila_pos,
                        hora_taverna=vila_pos,  # Tavern at village center
                        hora_praca=vila_pos,    # Plaza at village center
                    )
                except Exception as e:
                    print(f"[Aviso] Falha ao gerar rotina IA para {npc.get('nome', npc_id)}: {e}")
                    # Fallback to random routine
                    comportamento.gerar_rotina_randomica()

    def atualizar_npcs_movimento(self, delta_tempo: float) -> None:
        """Update NPC movement based on time, patrol routes, and daily routines."""
        for npc_id, npc in self.npcs.items():
            # Skip if NPC is in a house interior
            if self.interior_ativo is not None and npc.get("casa_id") == self.interior_ativo:
                continue
            
            # Get NPC's current activity from AI routine (if available)
            comportamento = self.npc_comportamento.get(npc_id)
            atividade_atual = None
            if comportamento and comportamento.rotina:
                # Get current hour from game time
                hora_atual = getattr(self, 'hora_atual', 12)  # Default to noon if not available
                atividade_atual = comportamento.rotina.obter_atividade_atual(hora_atual)
            
            # Update movement timer
            if npc_id in self.npc_proximo_movimento:
                self.npc_proximo_movimento[npc_id] -= delta_tempo
            
            # Skip if not enough time has passed
            if self.npc_proximo_movimento.get(npc_id, 0) > 0:
                continue
            
            rota = self.npc_rotas.get(npc_id, [npc.get("pos", [0, 0])])
            if not rota:
                continue
            
            indice = self.npc_rota_indice.get(npc_id, 0)
            current_pos = npc.get("pos", [0, 0])
            target_pos = rota[indice]
            
            # If there's a current activity, influence movement towards it
            if atividade_atual and atividade_atual.tipo_atividade != "dormir":
                # Move towards activity location somewhat (80% chance)
                if random.random() < 0.2:
                    target_pos = atividade_atual.locacao
            
            # Check if reached current target
            if tuple(current_pos) == target_pos:
                # Move to next waypoint in route
                indice = (indice + 1) % len(rota)
                self.npc_rota_indice[npc_id] = indice
                target_pos = rota[indice]
                
                # Update "em_casa" status
                self.npc_em_casa[npc_id] = (tuple(target_pos) == tuple(npc.get("pos", [0, 0])))
            
            # Move one step towards target
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            
            if dx != 0 or dy != 0:
                # Move closer to target
                if dx > 0:
                    new_x = current_pos[0] + 1
                elif dx < 0:
                    new_x = current_pos[0] - 1
                else:
                    new_x = current_pos[0]
                
                if dy > 0:
                    new_y = current_pos[1] + 1
                elif dy < 0:
                    new_y = current_pos[1] - 1
                else:
                    new_y = current_pos[1]
                
                # Check if new position is walkable
                if self.eh_caminavel(new_x, new_y) and not self.posicao_ocupada_por_entidade(new_x, new_y):
                    npc["pos"] = [new_x, new_y]
                    self.npc_proximo_movimento[npc_id] = 1.0  # Time between moves (seconds) - reduced speed
                else:
                    # If can't move forward, try alternate direction
                    alt_positions = []
                    for (ax, ay) in [(new_x, current_pos[1]), (current_pos[0], new_y)]:
                        if self.eh_caminavel(ax, ay) and not self.posicao_ocupada_por_entidade(ax, ay):
                            alt_positions.append((ax, ay))
                    
                    if alt_positions:
                        ax, ay = random.choice(alt_positions)
                        npc["pos"] = [ax, ay]
                        self.npc_proximo_movimento[npc_id] = 1.0  # Reduced speed
                    else:
                        # Stuck, skip this update
                        self.npc_proximo_movimento[npc_id] = 0.2

    def spawn_tiles(self, tile_set: set[tuple[int, int]], quantidade_alvo: int) -> None:
        while len(tile_set) < quantidade_alvo:
            pos = self.posicao_livre_aleatoria()
            if pos not in tile_set and self.eh_caminavel(pos[0], pos[1]):
                tile_set.add(pos)

    def spawn_animais(self, quantidade_alvo: int) -> None:
        # Animais reais e fantasy/anime/isekai themed
        especies = [
            # Animais reais
            "coelho", "raposa", "lobo", "capivara", "veado", "gato", "javali", "coruja", "lince", "cervo",
            # Criaturas de fantasia e anime
            "dragaozinho", "fenix", "unicórnio", "grifo", "esfinge", "peryton", "kitsune", 
            "goblin", "slime", "espectro", "wyvern_jovem", "centauro", "naga", "harpia",
            "elfo_selvagem", "fada_luminosa", "ent_pequeno", "golem_terra", "espelho_magico",
            "valraven", "shadows_menores", "sprite_florestal", "quimera_pequena", "pegaso",
            "basilisco_jovem", "demônio_fraco", "anjo_caído", "divindade_menora", "bestia_primor"
        ]
        personalidades = [
            # Personalidades básicas
            "timido", "curioso", "agressivo", "calmo",
            # Adicionais para fantasy/isekai
            "nobre", "selvagem", "misterioso", "alegre", "melancolico", "obsessivo", "astuto", 
            "leal", "traidor", "sarcástico", "compassivo", "destruidor", "protetor", "solitário"
        ]
        while len(self.animais) < quantidade_alvo:
            pos = self.posicao_livre_aleatoria()
            if pos in self.animais:
                continue
            especie = random.choice(especies)
            personalidade = random.choice(personalidades)
            # Alguns animais fantasy tem atributos especiais
            eh_magico = especie in ["dragaozinho", "fenix", "unicórnio", "grifo", "fada_luminosa", 
                                    "anjo_caído", "divindade_menora", "pegaso", "kitsune", "elfo_selvagem"]
            eh_perigoso = especie in ["basilisco_jovem", "demônio_fraco", "quimera_pequena", "wyvern_jovem", 
                                      "naga", "goblin", "shadows_menores", "bestia_primor"]
            self.animais[pos] = {
                "especie": especie,
                "personalidade": personalidade,
                "domesticado": False,
                "foge": random.random() < (0.65 if random.random() < 0.3 else 0.45),  # Fantasy criaturas podem ou não fugir
                "energia": random.randint(2, 10 if eh_perigoso else 8),
                "eh_magico": eh_magico,
                "eh_perigoso": eh_perigoso,
            }

    def gerar_sociedade_inicial(self) -> None:
        """Generate villages with protected zones (no mountains inside villages)."""
        banco_personagens = obter_banco_personagens()
        qtd_vilas = random.randint(1, max(2, self.tamanho // 14))
        for i in range(qtd_vilas):
            vx, vy = self.posicao_livre_aleatoria()
            
            # STEP 1: Clear mountains/water from village protection zone (5x5 area)
            self._limpar_zona_vila(vx, vy, raio_protecao=2)
            
            self.tiles_vila.add((vx, vy))
            vila_id = f"v{i + 1}"
            casas: list[str] = []
            nome_vila = gerar_nome_local()
            
            # Inicializar sistema de plantacoes para a vila
            plantacoes: list[dict] = []
            qtd_plantacoes = random.randint(2, 4)
            for p in range(qtd_plantacoes):
                tipo_planta = random.choice(list(PLANTAS_DISPONIVEIS.keys()))
                plantacoes.append({
                    "id": f"{vila_id}_p{p + 1}",
                    "tipo": tipo_planta,
                    "dias_plantados": 0,
                    "dias_crescimento": PLANTAS_DISPONIVEIS[tipo_planta]["dias_crescimento"],
                    "colheita_pronta": False,
                })
            
            self.vilas[vila_id] = {
                "id": vila_id,
                "nome": nome_vila,
                "pos": [vx, vy],
                "tipo": "aldeia",
                "populacao": random.randint(18, 48),
                "tecnologia": random.randint(1, 3),
                "magia": random.randint(0, 2),
                "casas": casas,
                "tem_igreja": random.random() < 0.7,
                "tem_biblioteca": random.random() < 0.2,
                "tem_castelo": False,
                "tem_internet": False,
                "imperio": f"Imperio de {gerar_nome_local()}",
                "plantacoes": plantacoes,  # Sistema de culturas
                "alimentos_produzidos": 0.0,  # Total de alimentos ja colhidos
            }

            for h in range(random.randint(2, 5)):
                hx = max(0, min(self.tamanho - 1, vx + random.randint(-2, 2)))
                hy = max(0, min(self.tamanho - 1, vy + random.randint(-2, 2)))
                if not self.eh_caminavel(hx, hy) or self.posicao_ocupada_por_entidade(hx, hy):
                    continue
                house_id = f"{vila_id}_c{h + 1}"
                self.tiles_casa.add((hx, hy))
                self.casa_para_id[(hx, hy)] = house_id
                casas.append(house_id)

                if random.random() < 0.7:
                    npc_id = f"npc_{vila_id}_{h + 1}"
                    papel = random.choice(PAPEIS_NPC)
                    perfil_npc = banco_personagens.gerar_perfil_npc(papel=papel)
                    self.npcs[npc_id] = {
                        "id": npc_id,
                        "nome": perfil_npc["nome"],
                        "idade": int(perfil_npc.get("idade", 18)),
                        "papel": papel,
                        "vila_id": vila_id,
                        "casa_id": house_id,
                        "pos": [hx, hy],
                        "memoria": [],
                        "relacao": 0,
                        "perfil": perfil_npc,
                    }
                    
                    # Create AI behavior system for NPC (lazy import to avoid circular dependency)
                    from .npc_relations import ComportamentoNPC
                    comportamento = ComportamentoNPC(npc_id, perfil_npc)
                    self.npc_comportamento[npc_id] = comportamento

            if self.vilas[vila_id]["tem_igreja"]:
                self.tiles_igreja.add((vx, vy))
            if self.vilas[vila_id]["tem_biblioteca"]:
                bx = max(0, min(self.tamanho - 1, vx + 1))
                by = vy
                if self.eh_caminavel(bx, by):
                    self.tiles_biblioteca.add((bx, by))
        
        # STEP 2: Generate paths connecting villages
        self._gerar_caminhos_entre_vilas()
        
        # STEP 3: Generate NPC patrol routes and initialize movement
        self._gerar_roteiros_npcs()

    def _limpar_zona_vila(self, vx: int, vy: int, raio_protecao: int = 2) -> None:
        """Clear mountains and water from village protection zone."""
        for dx in range(-raio_protecao, raio_protecao + 1):
            for dy in range(-raio_protecao, raio_protecao + 1):
                x = vx + dx
                y = vy + dy
                if 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                    pos = (x, y)
                    # Remove mountains and water from village zone
                    self.tiles_montanha.discard(pos)
                    self.tiles_agua.discard(pos)
                    self.tiles_mar.discard(pos)


    def mover_humano(self, direcao: str) -> bool:
        self.direcao_olhar = direcao
        if self.interior_ativo is not None:
            self.ultimo_evento = "voce esta dentro de uma casa"
            return False

        dx, dy = DIRECOES.get(direcao, (0, 0))
        nx, ny = self.humano[0] + dx, self.humano[1] + dy
        if not self.eh_caminavel(nx, ny):
            self.ultimo_evento = "bloqueado pelo terreno"
            return False
        if self.posicao_ocupada_por_entidade(nx, ny):
            self.ultimo_evento = "espaco ocupado por outra entidade"
            return False

        # Inicia animacao de movimento para este tile
        self.movimento_inicio_pos = list(self.humano)
        self.movimento_fim_pos = [nx, ny]
        self.movimento_tempo_inicial = time.time()
        self.movimento_duracao = 0.22  # Duracao do movimento em segundos (caminhada)
        self.movimento_ativo = True
        
        self.humano = [nx, ny]
        self.tick_animacao_humano += 1
        self.animar_humano_ate = time.time() + 0.22
        self.ultimo_evento = f"moveu para {direcao}"

        if (nx, ny) in self.tiles_armadilha:
            self.receber_dano(2, "acionou uma armadilha", tipo="ataque")
            self.tiles_armadilha.discard((nx, ny))
        if (nx, ny) in self.tiles_maldito:
            self.receber_dano(1, "entrou em zona maldita", tipo="maldicao")

        return True

    def definir_direcao_olhar_por_tile(self, tile_x: int, tile_y: int) -> None:
        """
        So atualiza direcao se o mouse estiver dentro de 4 blocos de distancia.
        Caso contrario, mantem a ultima direcao (standby).
        """
        dx = tile_x - self.humano[0]
        dy = tile_y - self.humano[1]
        
        # Verifica se o mouse esta proximo o suficiente (distancia Manhattan <= 4)
        distancia = abs(dx) + abs(dy)
        if distancia > 4:
            # Mouse muito longe, mantem ultima direcao
            return
        
        if dx == 0 and dy == 0:
            return
        if abs(dx) >= abs(dy):
            self.direcao_olhar = "direita" if dx > 0 else "esquerda"
        else:
            self.direcao_olhar = "baixo" if dy > 0 else "cima"

    def obter_posicao_visual(self) -> tuple[float, float]:
        """
        Retorna a posicao visual atual do personagem durante animacao de movimento.
        Se nao esta em movimento, retorna a posicao atual (em humano).
        Interpolacao suave com easing.
        """
        if not self.movimento_ativo or self.movimento_duracao <= 0:
            return float(self.humano[0]), float(self.humano[1])
        
        agora = time.time()
        tempo_passado = agora - self.movimento_tempo_inicial
        
        if tempo_passado >= self.movimento_duracao:
            # Animacao terminou
            self.movimento_ativo = False
            return float(self.humano[0]), float(self.humano[1])
        
        # Progresso de 0 a 1
        progresso = tempo_passado / self.movimento_duracao
        
        # Easing suave (ease-out quadratico)
        progresso_easing = 1 - (1 - progresso) ** 2
        
        # Interpolacao
        vx = self.movimento_inicio_pos[0] + (self.movimento_fim_pos[0] - self.movimento_inicio_pos[0]) * progresso_easing
        vy = self.movimento_inicio_pos[1] + (self.movimento_fim_pos[1] - self.movimento_inicio_pos[1]) * progresso_easing
        
        return vx, vy

    def tile_a_frente(self) -> tuple[int, int]:
        dx, dy = DIRECOES.get(self.direcao_olhar, (0, 1))
        return (self.humano[0] + dx, self.humano[1] + dy)

    def acao_contextual(self) -> str:
        pos = self.tile_a_frente()
        if self.interior_ativo is not None:
            self.interior_ativo = None
            self.ultimo_evento = "saiu da casa"
            return self.ultimo_evento

        if pos in self.casa_para_id:
            self.interior_ativo = self.casa_para_id[pos]
            self.ultimo_evento = "entrou em uma casa da vila"
            return self.ultimo_evento

        if pos in self.tiles_biblioteca:
            self.inventario["conhecimento"] += 1
            if random.random() < 0.25:
                magia = random.choice(["runa de cura", "luz eterea", "barreira arcana", "passo de mana"])
                if magia not in self.magias_aprendidas:
                    self.magias_aprendidas.append(magia)
                    self.ultimo_evento = f"aprendeu magia: {magia}"
                    return self.ultimo_evento
            self.ultimo_evento = "estudou na biblioteca"
            return self.ultimo_evento

        if pos in self.tiles_igreja:
            self.ultimo_evento = "ouviu palavras de Raphael pela igreja"
            return self.ultimo_evento

        self.ultimo_evento = "nenhuma interacao contextual aqui"
        return self.ultimo_evento

    def obter_npc_proximo(self) -> str | None:
        hx, hy = self.tile_a_frente()
        melhor_id = None
        melhor_dist = 999
        for npc_id, npc in self.npcs.items():
            x, y = npc["pos"]
            dist = abs(x - hx) + abs(y - hy)
            if dist == 0 and dist < melhor_dist:
                melhor_id = npc_id
                melhor_dist = dist
        return melhor_id

    def conversar_com_npc(self, npc_id: str, mensagem: str) -> str:
        npc = self.npcs.get(npc_id)
        if not npc:
            return "Nao ha ninguem para conversar."

        resposta = resposta_npc(npc["nome"], npc["papel"], mensagem, npc["memoria"], self.ano_atual)
        npc["memoria"].append({"jogador": self.nome_humano, "mensagem": mensagem, "resposta": resposta, "ano": self.ano_atual})
        npc["relacao"] += 1
        self.stats["interacoes_npc"] += 1
        self.ultimo_evento = f"conversou com {npc['nome']}"
        return resposta

    def gerar_quest_raphael(self) -> dict:
        """Gera uma quest de Raphael usando AI contextualizada ao mundo e jogador."""
        # Importar aqui para evitar dependência circular
        from .quest_generation_ai import gerar_quest_dinamica_ai
        
        # Tentar criar uma memória básica se não existir
        if not hasattr(self, '_memoria_temp'):
            from .modelos import MemoriaRaphael
            self._memoria_temp = MemoriaRaphael()
        
        quest_id = f"q_raphael_{len(self.quests_ativas) + 1}"
        
        try:
            # Gerar quest contextualizada usando IA
            quest_data = gerar_quest_dinamica_ai(
                self,
                self._memoria_temp,
                dificuldade_preferida=random.randint(2, 4),
                tipo_preferido=random.choice(["descoberta", "entrega", "derrota", "coleta"])
            )
            
            # Converter dados IA em formato de quest compatível
            quest = {
                "id": quest_id,
                "titulo": quest_data.get("nome", "Pedido de Raphael"),
                "descricao": quest_data.get("descricao", "Uma jornada aguarda você."),
                "status": "ativa",
                "origem": "raphael",
                "ignorada": False,
                "tipo": quest_data.get("tipo", "descoberta"),
                "dificuldade": quest_data.get("dificuldade", 3),
                "recompensa_ouro": quest_data.get("recompensa_ouro", 200),
                "recompensa_exp": quest_data.get("recompensa_exp", 500),
                "npc_giver": quest_data.get("npc_giver", "Raphael"),
                "ai_generated": True,
                "lore_connection": quest_data.get("lore_connection", ""),
            }
            
        except Exception as e:
            # Fallback para quests básicas se IA falhar
            print(f"[Quest] Fallback usado: {e}")
            quest = {
                "id": quest_id,
                "titulo": "Pedido de Raphael",
                "descricao": random.choice([
                    "Investigue rumores de guerra entre dois imperios.",
                    "Proteja uma aldeia durante um festival religioso.",
                    "Busque conhecimento antigo em uma biblioteca esquecida.",
                    "Converse com um mestre arcano e aprenda uma magia nova.",
                ]),
                "status": "ativa",
                "origem": "raphael",
                "ignorada": False,
            }
        
        self.quests_ativas.append(quest)
        return quest

    def atualizar_animais(self) -> None:
        novos: dict[tuple[int, int], dict] = {}
        hx, hy = self.humano

        for (x, y), info in list(self.animais.items()):
            if info.get("domesticado"):
                dx = 1 if hx > x else -1 if hx < x else 0
                dy = 1 if hy > y else -1 if hy < y else 0
                nx, ny = x + dx, y + dy
                if self.eh_caminavel(nx, ny) and not self.posicao_ocupada_por_entidade(nx, ny):
                    novos[(nx, ny)] = info
                    continue

            dist = abs(hx - x) + abs(hy - y)
            mover = random.random() < 0.6
            if not mover:
                novos[(x, y)] = info
                continue

            nx, ny = x, y
            personalidade = info.get("personalidade", "calmo")
            foge = info.get("foge", False)
            if foge and dist <= 3:
                nx += -1 if hx > x else 1 if hx < x else random.choice([-1, 1])
                ny += -1 if hy > y else 1 if hy < y else random.choice([-1, 1])
            elif personalidade == "curioso" and dist <= 5:
                nx += 1 if hx > x else -1 if hx < x else 0
                ny += 1 if hy > y else -1 if hy < y else 0
            elif personalidade == "agressivo" and dist <= 2:
                nx += 1 if hx > x else -1 if hx < x else 0
                ny += 1 if hy > y else -1 if hy < y else 0
            else:
                nx += random.choice([-1, 0, 1])
                ny += random.choice([-1, 0, 1])

            if self.eh_caminavel(nx, ny) and not self.posicao_ocupada_por_entidade(nx, ny) and (nx, ny) not in novos:
                novos[(nx, ny)] = info
            else:
                novos[(x, y)] = info

        self.animais = novos

    def atualizar_sociedade(self, tempo: SistemaTempo) -> str | None:
        novo_ano = self.ano_base + (tempo.dia // 365)
        if novo_ano <= self.ano_atual:
            return None

        self.ano_atual = novo_ano
        self.stats["anos_passados"] = self.ano_atual - self.ano_base

        for vila in self.vilas.values():
            vila["populacao"] += random.randint(4, 15)
            vila["tecnologia"] += random.randint(0, 2)
            vila["magia"] += random.randint(0, 2)
            vila["tipo"] = evoluir_tipo_assentamento(vila["populacao"], vila["tecnologia"], vila["magia"])

            if vila["tipo"] in {"castelo", "cidade", "metropole"}:
                vila["tem_castelo"] = True
                cx, cy = vila["pos"]
                self.tiles_castelo.add((cx, cy))

            if vila["tecnologia"] >= 12 and self.ano_atual >= 2500:
                vila["tem_internet"] = True

            if random.random() < 0.3:
                cx, cy = vila["pos"]
                bx = max(0, min(self.tamanho - 1, cx + random.randint(-2, 2)))
                by = max(0, min(self.tamanho - 1, cy + random.randint(-2, 2)))
                if self.eh_caminavel(bx, by):
                    self.tiles_casa.add((bx, by))

        evento = maybe_evento_coletivo()
        if evento:
            self.ultimo_evento = evento
            return evento

        self.ultimo_evento = f"ano {self.ano_atual}: vilas evoluiram"
        return self.ultimo_evento
    
    def atualizar_culturas_diarias(self) -> None:
        """Atualiza o crescimento diario das culturas em todas as vilas."""
        for vila in self.vilas.values():
            if "plantacoes" not in vila:
                continue
            
            for plantacao in vila["plantacoes"]:
                if plantacao["colheita_pronta"]:
                    # Ja foi colhida, replanta a proxima cultura
                    novo_tipo = random.choice(list(PLANTAS_DISPONIVEIS.keys()))
                    plantacao["tipo"] = novo_tipo
                    plantacao["dias_plantados"] = 0
                    plantacao["dias_crescimento"] = PLANTAS_DISPONIVEIS[novo_tipo]["dias_crescimento"]
                    plantacao["colheita_pronta"] = False
                else:
                    # Incrementa dias plantados
                    plantacao["dias_plantados"] += 1
                    dias_necessarios = plantacao["dias_crescimento"]
                    
                    # Verifica se a colheita esta pronta
                    if plantacao["dias_plantados"] >= dias_necessarios:
                        plantacao["colheita_pronta"] = True
                        tipo_planta = plantacao["tipo"]
                        alimento_produzido = PLANTAS_DISPONIVEIS[tipo_planta]["food_yield"]
                        vila["alimentos_produzidos"] = vila.get("alimentos_produzidos", 0) + alimento_produzido

    def expandir_mundo_quando_perto_borda(self, margem: int = 2, bloco: int = 6) -> bool:
        hx, hy = self.humano
        lados: list[str] = []
        if hx <= margem:
            lados.append("esquerda")
        if hx >= self.tamanho - 1 - margem:
            lados.append("direita")
        if hy <= margem:
            lados.append("cima")
        if hy >= self.tamanho - 1 - margem:
            lados.append("baixo")

        if not lados:
            return False

        for lado in lados:
            self._expandir_lado(lado, bloco)

        self.ultimo_evento = f"mundo expandiu para {self.tamanho}x{self.tamanho}"
        return True

    def _expandir_lado(self, lado: str, qtd: int) -> None:
        def shift_set(base: set[tuple[int, int]], dx: int, dy: int) -> set[tuple[int, int]]:
            return {(x + dx, y + dy) for (x, y) in base}

        def shift_dict(base: dict[tuple[int, int], int], dx: int, dy: int) -> dict[tuple[int, int], int]:
            return {(x + dx, y + dy): v for (x, y), v in base.items()}

        def shift_animais(base: dict[tuple[int, int], dict], dx: int, dy: int) -> dict[tuple[int, int], dict]:
            return {(x + dx, y + dy): dict(v) for (x, y), v in base.items()}

        if lado == "esquerda":
            dx, dy = qtd, 0
            self.humano[0] += qtd
        elif lado == "cima":
            dx, dy = 0, qtd
            self.humano[1] += qtd
        else:
            dx, dy = 0, 0

        if dx or dy:
            self.tiles_comida = shift_set(self.tiles_comida, dx, dy)
            self.tiles_arvore = shift_set(self.tiles_arvore, dx, dy)
            self.tiles_casa = shift_set(self.tiles_casa, dx, dy)
            self.tiles_inimigo = shift_set(self.tiles_inimigo, dx, dy)
            self.tiles_montanha = shift_set(self.tiles_montanha, dx, dy)
            self.tiles_agua = shift_set(self.tiles_agua, dx, dy)
            self.tiles_santuario = shift_set(self.tiles_santuario, dx, dy)
            self.tiles_vila = shift_set(self.tiles_vila, dx, dy)
            self.tiles_igreja = shift_set(self.tiles_igreja, dx, dy)
            self.tiles_biblioteca = shift_set(self.tiles_biblioteca, dx, dy)
            self.tiles_castelo = shift_set(self.tiles_castelo, dx, dy)
            self.tiles_armadilha = shift_set(self.tiles_armadilha, dx, dy)
            self.tiles_maldito = shift_set(self.tiles_maldito, dx, dy)
            self.tiles_tesouro = shift_dict(self.tiles_tesouro, dx, dy)
            self.animais = shift_animais(self.animais, dx, dy)
            self.casa_para_id = {(x + dx, y + dy): cid for (x, y), cid in self.casa_para_id.items()}
            for npc in self.npcs.values():
                npc["pos"][0] += dx
                npc["pos"][1] += dy
            for vila in self.vilas.values():
                vila["pos"][0] += dx
                vila["pos"][1] += dy

        self.tamanho += qtd
        
        # Generate terrain specifically in the expanded areas for better coverage
        # Add more terrain to new expanded zones to avoid sparse areas
        self.spawn_tiles(self.tiles_agua, max(int(self.tamanho * 0.15), 5))  # Water for variety
        self.spawn_tiles(self.tiles_montanha, max(int(self.tamanho * 0.12), 4))  # Mountains
        self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.65))  # Food
        self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.8))  # Trees (dense forest)
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.08))  # Enemies
        self.spawn_animais(max(6, int(self.tamanho * 0.25)))  # Animals

    def receber_dano(self, valor: float, motivo: str, tipo: str = "geral") -> bool:
        reducao = max(0.0, min(0.65, self.bonus_equipamentos.get("defesa", 0.0) * 0.03))
        valor = max(0.5, valor * (1.0 - reducao))
        defesa = self.poderes.get("defesa_divina")
        if defesa and defesa.get("cargas", 0) > 0 and tipo == "ataque":
            defesa["cargas"] -= 1
            self.ultimo_evento = f"defesa divina bloqueou dano ({motivo})"
            if defesa["cargas"] <= 0:
                del self.poderes["defesa_divina"]
            return True

        self.hp = max(0, self.hp - valor)
        self.ultimo_evento = motivo
        return False

    def ativar_poder_manual(self, id_poder: str) -> bool:
        poder = self.poderes.get(id_poder)
        if not poder or poder.get("cargas", 0) <= 0:
            self.ultimo_evento = "poder indisponivel"
            return False

        tipo = poder.get("tipo")
        if tipo == "cura_celestial":
            cura = float(poder.get("valor", 6))
            self.hp = min(self.hp_maximo, self.hp + cura)
            self.ultimo_evento = "cura celestial ativada"
        elif tipo == "passo_etereo":
            for _ in range(12):
                x, y = self.posicao_livre_aleatoria()
                if (x, y) not in self.tiles_inimigo:
                    self.humano = [x, y]
                    break
            self.ultimo_evento = "passo etereo ativado"
        elif tipo == "colheita_milagre":
            self.inventario["comida"] += float(poder.get("valor", 3))
            self.ultimo_evento = "colheita milagrosa recebida"
        else:
            self.ultimo_evento = "poder sem efeito"

        poder["cargas"] -= 1
        if poder["cargas"] <= 0:
            del self.poderes[id_poder]
        self.stats["pontos"] += 4
        return True

    def conceder_poder(self, id_poder: str, nome: str, tipo: str, tecla: int | None, cargas: int, valor: float = 0.0) -> None:
        self.poderes[id_poder] = {
            "nome": nome,
            "tipo": tipo,
            "tecla": tecla,
            "cargas": max(1, int(cargas)),
            "valor": valor,
        }

    def coletar(self) -> bool:
        bonus_coleta = int(max(0.0, self.bonus_equipamentos.get("coleta", 0.0)))
        pos = self.tile_a_frente()
        if pos in self.tiles_comida:
            self.tiles_comida.discard(pos)
            self.inventario["comida"] += 1 + bonus_coleta
            self.stats["comida_coletada"] += 1
            self.stats["pontos"] += 2
            self.ultimo_evento = "coletou comida"
            self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.7))
            return True
        if pos in self.tiles_arvore:
            self.tiles_arvore.discard(pos)
            self.inventario["madeira"] += 1 + bonus_coleta
            self.stats["madeira_coletada"] += 2
            self.stats["pontos"] += 2
            self.ultimo_evento = "coletou madeira"
            self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.85))
            return True
        self.ultimo_evento = "nada para coletar"
        return False

    def escavar(self) -> bool:
        pos = self.tile_a_frente()
        if pos in self.tiles_tesouro:
            ouro = self.tiles_tesouro.pop(pos)
            self.inventario["ouro"] += ouro
            self.stats["tesouros_encontrados"] += 1
            self.stats["pontos"] += ouro
            self.ultimo_evento = f"encontrou {ouro}o!"
            return True
        self.ultimo_evento = "nenhum tesouro aqui"
        return False

    def construir_casa(self, custo_madeira: int, custo_comida: int) -> bool:
        pos = self.tile_a_frente()
        if pos in self.tiles_casa or pos in self.tiles_inimigo or pos in self.tiles_montanha or pos in self.tiles_agua:
            self.ultimo_evento = "nao pode construir aqui"
            return False
        if self.posicao_ocupada_por_entidade(pos[0], pos[1]):
            self.ultimo_evento = "ha uma entidade ocupando o local"
            return False
        if self.inventario["madeira"] < custo_madeira or self.inventario["comida"] < custo_comida:
            self.ultimo_evento = "recursos insuficientes"
            return False
        self.inventario["madeira"] -= custo_madeira
        self.inventario["comida"] -= custo_comida
        self.tiles_casa.add(pos)
        self.stats["casas_construidas"] += 1
        self.stats["pontos"] += 15
        self.ultimo_evento = "casa construida"
        return True

    def atacar(self) -> bool:
        alvo = self.tile_a_frente()
        if alvo not in self.tiles_inimigo:
            self.ultimo_evento = "nenhum inimigo proximo"
            return False
        ex, ey = alvo
        self.tiles_inimigo.discard((ex, ey))
        self.stats["inimigos_derrotados"] += 1
        bonus_ataque = int(max(0.0, self.bonus_equipamentos.get("ataque", 0.0)))
        self.stats["pontos"] += 20 + bonus_ataque * 2
        self.ultimo_evento = "inimigo derrotado"
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.1))
        self.moralidade_jogador -= 5
        return True

    def matar_animal(self) -> bool:
        alvo = self.tile_a_frente()
        if alvo not in self.animais:
            self.ultimo_evento = "nenhum animal proximo"
            return False
        ax, ay = alvo
        self.animais.pop((ax, ay), None)
        self.stats["animais_mortos"] += 1
        self.stats["pontos"] += 5
        self.ultimo_evento = "animal morto"
        self.spawn_animais(max(4, int(self.tamanho * 0.2)))
        self.moralidade_jogador -= 10
        return True

    def acariciar_animal(self) -> bool:
        alvo = self.tile_a_frente()
        info = self.animais.get(alvo)
        if not info:
            self.ultimo_evento = "nenhum animal para acariciar"
            return False
        chance = 0.75 if info.get("personalidade") in {"calmo", "curioso"} else 0.35
        if random.random() <= chance:
            info["domesticado"] = True
            self.pet = {"x": alvo[0], "y": alvo[1], "especie": info.get("especie", "animal")}
            self.stats["animais_domesticados"] += 1
            self.ultimo_evento = f"{info.get('especie', 'animal')} virou seu pet"
            self.moralidade_jogador += 2
            return True
        self.ultimo_evento = "o animal recuou e nao confiou em voce"
        return False

    def descansar(self) -> bool:
        cura_base = 3 + int(max(0.0, self.bonus_equipamentos.get("sorte", 0.0)))
        self.hp = min(self.hp_maximo, self.hp + cura_base)
        self.ultimo_evento = "descansou e se recuperou"
        return True

    def adicionar_itens_iniciais(self, itens: list[dict]) -> None:
        self.inventario_itens = []
        for item in itens:
            self.inventario_itens.append(
                {
                    "nome": str(item.get("nome", "Item Desconhecido")),
                    "tipo": str(item.get("tipo", "item")),
                    "slot": str(item.get("slot", "acessorio")),
                    "raridade": str(item.get("raridade", "comum")),
                    "descricao": str(item.get("descricao", "Sem descricao")),
                    "bonus": {
                        "ataque": float(item.get("bonus", {}).get("ataque", 0.0)),
                        "defesa": float(item.get("bonus", {}).get("defesa", 0.0)),
                        "hp": float(item.get("bonus", {}).get("hp", 0.0)),
                        "sorte": float(item.get("bonus", {}).get("sorte", 0.0)),
                        "coleta": float(item.get("bonus", {}).get("coleta", 0.0)),
                    },
                    "equipado": False,
                }
            )
        self.atualizar_atributos_de_equipamentos()

    def atualizar_atributos_de_equipamentos(self) -> None:
        bonus = {"ataque": 0.0, "defesa": 0.0, "hp": 0.0, "sorte": 0.0, "coleta": 0.0}
        for slot, idx in self.equipamentos.items():
            if idx is None:
                continue
            if not (0 <= idx < len(self.inventario_itens)):
                self.equipamentos[slot] = None
                continue
            item = self.inventario_itens[idx]
            for chave in bonus:
                bonus[chave] += float(item.get("bonus", {}).get(chave, 0.0))
            item["equipado"] = True

        for i, item in enumerate(self.inventario_itens):
            slot_item = str(item.get("slot", "acessorio"))
            item["equipado"] = self.equipamentos.get(slot_item) == i

        self.bonus_equipamentos = bonus
        hp_antigo = self.hp_maximo
        self.hp_maximo = max(10.0, self.hp_base + bonus["hp"])
        if self.hp_maximo < hp_antigo:
            self.hp = min(self.hp, self.hp_maximo)

    def alternar_equipamento_por_indice(self, indice: int) -> str:
        if not (0 <= indice < len(self.inventario_itens)):
            return "indice de item invalido"
        item = self.inventario_itens[indice]
        slot = str(item.get("slot", "acessorio"))
        atual = self.equipamentos.get(slot)
        if atual == indice:
            self.equipamentos[slot] = None
            self.atualizar_atributos_de_equipamentos()
            self.ultimo_evento = f"desequipou {item['nome']}"
            return self.ultimo_evento

        self.equipamentos[slot] = indice
        self.atualizar_atributos_de_equipamentos()
        self.ultimo_evento = f"equipou {item['nome']}"
        return self.ultimo_evento

    def estado(self, tick: int) -> dict:
        return {
            "tick": tick,
            "humano": {
                "x": self.humano[0],
                "y": self.humano[1],
                "nome": self.nome_humano,
                "idade": self.idade_humano,
                "origem": self.origem_humano,
            },
            "hp": int(self.hp),
            "hp_maximo": int(self.hp_maximo),
            "inventario": {k: int(v) if isinstance(v, (int, float)) else v for k, v in self.inventario.items()},
            "inventario_itens": self.inventario_itens,
            "equipamentos": self.equipamentos,
            "bonus_equipamentos": {k: round(v, 2) for k, v in self.bonus_equipamentos.items()},
            "stats": self.stats,
            "moralidade_jogador": self.moralidade_jogador,
            "ultimo_evento": self.ultimo_evento,
            "tamanho_mundo": self.tamanho,
            "quantidade_animais": len(self.animais),
            "quantidade_vilas": len(self.vilas),
            "ano_atual": self.ano_atual,
            "lore": self.world_lore,
            "quest_ativa": self.quests_ativas[0]["descricao"] if self.quests_ativas else "Sem quest",
            "direcao_olhar": self.direcao_olhar,
        }
