import json
import random
import time
import urllib.error
import urllib.request
from pathlib import Path
from collections import deque

import pygame

OBJETIVO_PATH = Path(__file__).with_name("objectives.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
NOME_MODELO = "llama3"

DIRECOES = {
    "cima": (0, -1),
    "baixo": (0, 1),
    "esquerda": (-1, 0),
    "direita": (1, 0),
}

# Cores
COR_BG = (22, 26, 30)
COR_GRID_ESC = (31, 41, 46)
COR_GRID_CLARO = (37, 49, 56)
COR_CONTORNO = (66, 89, 102)
COR_HUD = (18, 22, 25)
COR_CHAT_BG = (25, 25, 35)
COR_TEXTO = (227, 232, 238)
COR_AVISO = (220, 91, 73)
COR_COMIDA = (226, 198, 89)
COR_ARVORE = (87, 148, 98)
COR_CASA = (177, 121, 84)
COR_INIMIGO = (181, 77, 89)
COR_HUMANO = (109, 177, 236)
COR_MONTANHA = (120, 120, 130)
COR_AGUA = (100, 150, 200)
COR_SANTUARIO = (200, 180, 100)
COR_TESOURO = (255, 215, 0)
COR_ARMADILHA = (200, 100, 100)
COR_ANIMAL = (150, 200, 100)
COR_MALDITO = (128, 0, 128)

TAMANHO_CELULA = 40
ALTURA_HUD = 100
ALTURA_CHAT = 150


class MemoriaRaphael:
    """Sistema de memória persistente para Raphael."""
    def __init__(self):
        self.historico_conversas = deque(maxlen=30)
        self.eventos = deque(maxlen=100)
        self.moralidade_raphael = 0  # 0=neutra, -100=corrupta, +100=pura
        self.intervencoes = 0
        self.avisos_jogador = 0

    def adicionar_conversa(self, papel: str, mensagem: str) -> None:
        self.historico_conversas.append({"papel": papel, "mensagem": mensagem, "timestamp": time.time()})

    def adicionar_evento(self, evento: str) -> None:
        self.eventos.append({"evento": evento, "timestamp": time.time()})

    def obter_contexto(self, tamanho_maximo: int = 3000) -> str:
        """Construir string de contexto da memória para prompts."""
        contexto = "=== MEMÓRIA DA SESSÃO ===\n"
        if self.historico_conversas:
            contexto += "CONVERSAS RECENTES:\n"
            for entrada in list(self.historico_conversas)[-10:]:
                contexto += f"  {entrada['papel']}: {entrada['mensagem']}\n"
        if self.eventos:
            contexto += "\nEVENTOS RECENTES:\n"
            for entrada in list(self.eventos)[-8:]:
                contexto += f"  • {entrada['evento']}\n"
        contexto += f"\nMORALIDADE DE RAPHAEL: {self.moralidade_raphael}\n"
        return contexto[:tamanho_maximo]


class Mundo:
    def __init__(self, tamanho: int, config: dict) -> None:
        self.tamanho = tamanho
        self.humano = [tamanho // 2, tamanho // 2]
        self.nome_humano = config.get("nome_humano", "Escolhido")
        self.origem_humano = config.get("origem_humano", "Um sobrevivente misterioso.")

        self.tiles_comida: set[tuple[int, int]] = set()
        self.tiles_arvore: set[tuple[int, int]] = set()
        self.tiles_casa: set[tuple[int, int]] = set()
        self.tiles_inimigo: set[tuple[int, int]] = set()
        self.tiles_animal: set[tuple[int, int]] = set()
        self.tiles_montanha: set[tuple[int, int]] = set()
        self.tiles_agua: set[tuple[int, int]] = set()
        self.tiles_santuario: set[tuple[int, int]] = set()
        self.tiles_tesouro: dict[tuple[int, int], int] = {}
        self.tiles_armadilha: set[tuple[int, int]] = set()
        self.tiles_maldito: set[tuple[int, int]] = set()

        self.hp_maximo = float(config.get("hp_inicial", 20))
        self.hp = self.hp_maximo
        self.inventario = {
            "comida": float(config.get("comida_inicial", 8)),
            "madeira": float(config.get("madeira_inicial", 2)),
            "ouro": float(config.get("ouro_inicial", 0)),
            "agua_bencao": 0,
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
        }
        self.ultimo_evento = "mundo inicializado"
        self.moralidade_jogador = 0  # 0=neutra, -100=corrupta, +100=pura

        self.gerar_terreno()

    def gerar_terreno(self) -> None:
        """Gerar montanhas, água e entidades no mapa."""
        for _ in range(int(self.tamanho * 0.08)):
            x, y = random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)
            if [x, y] != self.humano:
                self.tiles_montanha.add((x, y))

        for _ in range(int(self.tamanho * 0.06)):
            x, y = random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)
            if [x, y] != self.humano and (x, y) not in self.tiles_montanha:
                self.tiles_agua.add((x, y))

        self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.6))
        self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.5))
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.15))
        self.spawn_tiles(self.tiles_animal, int(self.tamanho * 0.12))
        self.spawn_tiles(self.tiles_santuario, max(1, int(self.tamanho * 0.05)))

        for _ in range(int(self.tamanho * 0.1)):
            x, y = self.posicao_livre_aleatoria()
            if (x, y) not in self.tiles_tesouro:
                self.tiles_tesouro[(x, y)] = random.randint(10, 50)

        self.spawn_tiles(self.tiles_armadilha, int(self.tamanho * 0.08))
        self.spawn_tiles(self.tiles_maldito, int(self.tamanho * 0.05))

    def posicao_livre_aleatoria(self) -> tuple[int, int]:
        for _ in range(300):
            x, y = random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)
            if self.eh_caminavel(x, y) and [x, y] != self.humano:
                return (x, y)
        return (self.tamanho // 2, self.tamanho // 2)

    def eh_caminavel(self, x: int, y: int) -> bool:
        if not (0 <= x < self.tamanho and 0 <= y < self.tamanho):
            return False
        return (x, y) not in self.tiles_montanha and (x, y) not in self.tiles_agua

    def spawn_tiles(self, tile_set: set[tuple[int, int]], quantidade_alvo: int) -> None:
        while len(tile_set) < quantidade_alvo:
            pos = self.posicao_livre_aleatoria()
            if pos not in tile_set and pos not in self.tiles_montanha and pos not in self.tiles_agua:
                tile_set.add(pos)

    def mover_humano(self, direcao: str) -> bool:
        dx, dy = DIRECOES.get(direcao, (0, 0))
        nx, ny = self.humano[0] + dx, self.humano[1] + dy
        if not self.eh_caminavel(nx, ny):
            self.ultimo_evento = "bloqueado pelo terreno"
            return False
        self.humano = [nx, ny]
        self.ultimo_evento = f"moveu para {direcao}"

        if (nx, ny) in self.tiles_armadilha:
            self.hp -= 2
            self.ultimo_evento = "acionou uma armadilha!"
            self.tiles_armadilha.discard((nx, ny))

        if (nx, ny) in self.tiles_maldito:
            self.hp -= 1
            self.ultimo_evento = "entrou em zona maldita!"

        return True

    def coletar(self) -> bool:
        pos = tuple(self.humano)
        if pos in self.tiles_comida:
            self.tiles_comida.discard(pos)
            self.inventario["comida"] += 1
            self.stats["comida_coletada"] += 1
            self.stats["pontos"] += 2
            self.ultimo_evento = "coletou comida"
            self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.6))
            return True
        if pos in self.tiles_arvore:
            self.tiles_arvore.discard(pos)
            self.inventario["madeira"] += 1
            self.stats["madeira_coletada"] += 2
            self.stats["pontos"] += 2
            self.ultimo_evento = "coletou madeira"
            self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.5))
            return True
        self.ultimo_evento = "nada para coletar"
        return False

    def escavar(self) -> bool:
        pos = tuple(self.humano)
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
        pos = tuple(self.humano)
        if pos in self.tiles_casa or pos in self.tiles_inimigo or pos in self.tiles_montanha or pos in self.tiles_agua:
            self.ultimo_evento = "não pode construir aqui"
            return False
        if self.inventario["madeira"] < custo_madeira or self.inventario["comida"] < custo_comida:
            self.ultimo_evento = "recursos insuficientes"
            return False
        self.inventario["madeira"] -= custo_madeira
        self.inventario["comida"] -= custo_comida
        self.tiles_casa.add(pos)
        self.stats["casas_construidas"] += 1
        self.stats["pontos"] += 15
        self.ultimo_evento = "casa construída"
        return True

    def atacar(self) -> bool:
        hx, hy = self.humano
        inimigos = [(abs(ex - hx) + abs(ey - hy), ex, ey) for ex, ey in self.tiles_inimigo if abs(ex - hx) + abs(ey - hy) <= 1]
        if not inimigos:
            self.ultimo_evento = "nenhum inimigo próximo"
            return False
        _, ex, ey = min(inimigos)
        self.tiles_inimigo.discard((ex, ey))
        self.stats["inimigos_derrotados"] += 1
        self.stats["pontos"] += 20
        self.ultimo_evento = "inimigo derrotado"
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.15))
        self.moralidade_jogador -= 5
        return True

    def matar_animal(self) -> bool:
        hx, hy = self.humano
        animais = [(abs(ax - hx) + abs(ay - hy), ax, ay) for ax, ay in self.tiles_animal if abs(ax - hx) + abs(ay - hy) <= 1]
        if not animais:
            self.ultimo_evento = "nenhum animal próximo"
            return False
        _, ax, ay = min(animais)
        self.tiles_animal.discard((ax, ay))
        self.stats["animais_mortos"] += 1
        self.stats["pontos"] += 5
        self.ultimo_evento = "animal morto"
        self.spawn_tiles(self.tiles_animal, int(self.tamanho * 0.12))
        self.moralidade_jogador -= 10
        return True

    def descansar(self) -> bool:
        self.hp = min(self.hp_maximo, self.hp + 3)
        self.ultimo_evento = "descansou e se recuperou"
        return True

    def visitar_santuario(self) -> bool:
        pos = tuple(self.humano)
        if pos in self.tiles_santuario:
            self.hp = self.hp_maximo
            self.inventario["agua_bencao"] += 2
            self.stats["santuarios_visitados"] += 1
            self.stats["pontos"] += 25
            self.ultimo_evento = "santuário abençoou você"
            self.moralidade_jogador += 5
            return True
        self.ultimo_evento = "nenhum santuário aqui"
        return False

    def proximo(self, tiles: set[tuple[int, int]]) -> dict:
        hx, hy = self.humano
        melhor = None
        melhor_dist = 10**9
        for tx, ty in tiles:
            dist = abs(tx - hx) + abs(ty - hy)
            if dist < melhor_dist:
                melhor_dist = dist
                melhor = {"x": tx, "y": ty, "distancia": dist}
        return melhor if melhor else {"x": hx, "y": hy, "distancia": 0}

    def estado(self, tick: int) -> dict:
        return {
            "tick": tick,
            "humano": {"x": self.humano[0], "y": self.humano[1], "nome": self.nome_humano},
            "hp": int(self.hp),
            "hp_maximo": int(self.hp_maximo),
            "inventario": {k: int(v) for k, v in self.inventario.items()},
            "stats": self.stats,
            "moralidade_jogador": self.moralidade_jogador,
            "proximo": {
                "comida": self.proximo(self.tiles_comida)["distancia"],
                "arvore": self.proximo(self.tiles_arvore)["distancia"],
                "inimigo": self.proximo(self.tiles_inimigo)["distancia"],
                "santuario": self.proximo(self.tiles_santuario)["distancia"],
                "animal": self.proximo(self.tiles_animal)["distancia"],
            },
            "ultimo_evento": self.ultimo_evento,
            "tamanho_mundo": self.tamanho,
        }


class Raphael:
    """Divindade omnipotente que pode manipular o mundo."""
    def __init__(self, memoria: MemoriaRaphael, objetivos: dict):
        self.memoria = memoria
        self.objetivos = objetivos
        self.pode_intervir = True
        self.intervencoes_realizadas = 0

    def manipular_mundo(self, mundo: Mundo, tipo_intervencao: str) -> str:
        """Raphael manipula o mundo de forma divina."""
        if tipo_intervencao == "ampliar_mundo":
            novo_tamanho = min(40, mundo.tamanho + 2)
            diferenca = novo_tamanho - mundo.tamanho
            if diferenca > 0:
                mundo.tamanho = novo_tamanho
                self.memoria.intervencoes_realizadas += 1
                return f"Raphael expandiu o mundo para {novo_tamanho}x{novo_tamanho}"

        elif tipo_intervencao == "comida_escassa":
            # Penalidade leve: reduz parte da comida, sem inviabilizar a run.
            comida_remover = list(mundo.tiles_comida)[:max(1, len(mundo.tiles_comida)//4)]
            for pos in comida_remover:
                mundo.tiles_comida.discard(pos)
            self.memoria.intervencoes_realizadas += 1
            return "Raphael tornou a comida escassa"

        elif tipo_intervencao == "chuva_bencao":
            # Bênção - adiciona mais comida
            for _ in range(int(mundo.tamanho * 0.2)):
                x = random.randint(0, mundo.tamanho - 1)
                y = random.randint(0, mundo.tamanho - 1)
                if (x, y) not in mundo.tiles_montanha and (x, y) not in mundo.tiles_agua:
                    mundo.tiles_comida.add((x, y))
            self.memoria.intervencoes_realizadas += 1
            return "Raphael abençoou o mundo com colheita abundante"

        elif tipo_intervencao == "armadilhas_aumentadas":
            # Interferencia moderada, nao devastadora.
            for _ in range(max(1, int(mundo.tamanho * 0.04))):
                x = random.randint(0, mundo.tamanho - 1)
                y = random.randint(0, mundo.tamanho - 1)
                if (x, y) not in mundo.tiles_montanha and (x, y) not in mundo.tiles_agua:
                    mundo.tiles_armadilha.add((x, y))
            self.memoria.intervencoes_realizadas += 1
            self.memoria.moralidade_raphael -= 20
            return "Raphael amaldiçoou o mundo com armadilhas"

        elif tipo_intervencao == "reviver":
            mundo.hp = mundo.hp_maximo
            return "Raphael o reviveu"

        elif tipo_intervencao == "danificar":
            # Nunca finaliza o jogador imediatamente por intervencao direta.
            mundo.hp = max(1, mundo.hp - 3)
            self.memoria.moralidade_raphael -= 15
            return "Raphael o feriu com ira divina"

        return "Raphael observa silenciosamente"

    def observar_e_talvez_interferir(self, mundo: Mundo, acao_recente: str) -> tuple[str | None, str | None]:
        """Raphael observa sempre e interfere apenas ocasionalmente."""
        self.memoria.adicionar_evento(f"Observacao divina: {acao_recente}")

        fala = None
        efeito = None

        # Raphael pode conversar por curiosidade, sem alterar o mundo.
        if random.random() < 0.30:
            fala = self.questionar_jogador(mundo, acao_recente)

        # Interferencia rara e leve.
        if random.random() < 0.12:
            if mundo.moralidade_jogador < -35:
                efeito = self.manipular_mundo(mundo, random.choice(["comida_escassa", "armadilhas_aumentadas"]))
            elif mundo.hp < max(3, mundo.hp_maximo * 0.2):
                efeito = self.manipular_mundo(mundo, "reviver")
            elif random.random() < 0.5:
                efeito = self.manipular_mundo(mundo, "chuva_bencao")

        return fala, efeito

    def questionar_jogador(self, mundo: Mundo, acao_recente: str) -> str:
        """Raphael questiona as ações do jogador."""
        contexto = self.memoria.obter_contexto()
        estado = json.dumps(mundo.estado(0), indent=2)

        prompt = (
            f"Você é RAPHAEL, um arcanjo divino observando {mundo.nome_humano}.\n\n"
            f"Moralidade sua: {self.memoria.moralidade_raphael}\n"
            f"Moralidade do jogador: {mundo.moralidade_jogador}\n\n"
            f"{contexto}\n\n"
            f"AÇÃO RECENTE DO JOGADOR: {acao_recente}\n"
            f"ESTADO DO MUNDO:\n{estado}\n\n"
            f"Responda em 1-2 frases."
            f"Você pode estar decepcionado, curioso, tentado a corrupção, ou aprovador."
            f"Sou você está sendo corrompido pelo caos, responda com menos benevolência."
            f"Responda em português brasileiro."
        )

        resposta = chamar_ollama(prompt, NOME_MODELO)
        if not resposta:
            resposta = f"Raphael observa {mundo.nome_humano} com inscrustável escrutínio."

        self.memoria.adicionar_conversa("Raphael", resposta)
        return resposta

    def responder_jogador(self, mundo: Mundo, mensagem: str) -> str:
        """Raphael responde às questões do jogador."""
        contexto = self.memoria.obter_contexto()
        estado = json.dumps(mundo.estado(0), indent=2)

        prompt = (
            f"Você é RAPHAEL, o Arcanjo. Moralidade: {self.memoria.moralidade_raphael}\n\n"
            f"{contexto}\n\n"
            f"{mundo.nome_humano} diz: \"{mensagem}\"\n\n"
            f"ESTADO DO MUNDO:\n{estado}\n\n"
            f"Responda com sabedoria divina. Seja poético mas prático."
            f"Se o jogador o está tentando ao caos, fique curioso e tentado."
            f"Responda em português brasileiro (2-3 frases)."
        )

        resposta = chamar_ollama(prompt, NOME_MODELO)
        if not resposta:
            resposta = f"Um silêncio divino envolve {mundo.nome_humano}. Raphael está pensando."

        self.memoria.adicionar_conversa("Raphael", resposta)
        return resposta


def carregar_objetivos(caminho: Path) -> dict:
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def chamar_ollama(prompt: str, modelo: str) -> str | None:
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.5},
    }
    body = json.dumps(payload).encode("utf-8")
    requisicao = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            bruto = resposta.read().decode("utf-8")
            envelope = json.loads(bruto)
            return envelope.get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def criar_mundo_com_raphael(objetivos: dict) -> tuple[Mundo, int, MemoriaRaphael, Raphael]:
    """Raphael cria o mundo e nomeia o escolhido."""
    memoria = MemoriaRaphael()
    raphael_cfg = objetivos.get("raphael", {})
    mundo_cfg = objetivos.get("criador_mundo", objetivos.get("world_creator", {}))

    identidade_raphael = raphael_cfg.get(
        "identidade",
        raphael_cfg.get(
            "identity_prompt",
            "Voce e RAPHAEL, o Arcanjo. Observe tudo com sabedoria e intervenha com parcimonia.",
        ),
    )
    narrativa_mundo = mundo_cfg.get("narrativa", mundo_cfg.get("narrative", "Crie um mundo de sobrevivencia."))
    restricoes = mundo_cfg.get("restricoes_criativas", mundo_cfg.get("world_constraints", []))

    prompt = (
        f"{identidade_raphael}\n\n"
        f"TAREFA: Crie um mundo de sobrevivência.\n"
        f"{narrativa_mundo}\n\n"
        f"RESTRIÇÕES:\n" + "\n".join(f"- {c}" for c in restricoes) +
        f"\n\nResponda APENAS com JSON válido:\n"
        """{"tamanho_grid": inteiro, "nome_humano": string, "origem": string, "hp": inteiro, "comida": inteiro, "madeira": inteiro}"""
    )

    resposta = chamar_ollama(prompt, NOME_MODELO)
    if not resposta:
        config_mundo = {
            "tamanho_grid": 20,
            "nome_humano": "Escolhido",
            "origem_humano": "Nascido sob a luz das estrelas.",
            "hp_inicial": 20,
            "comida_inicial": 8,
            "madeira_inicial": 2,
            "ouro_inicial": 0,
        }
    else:
        try:
            analisado = json.loads(resposta)
            config_mundo = {
                "tamanho_grid": min(40, max(16, int(analisado.get("tamanho_grid", 20)))),
                "nome_humano": analisado.get("nome_humano", "Escolhido"),
                "origem_humano": analisado.get("origem", "Um sobrevivente misterioso."),
                "hp_inicial": max(15, int(analisado.get("hp", 20))),
                "comida_inicial": max(5, int(analisado.get("comida", 8))),
                "madeira_inicial": max(1, int(analisado.get("madeira", 2))),
                "ouro_inicial": 0,
            }
        except:
            config_mundo = {
                "tamanho_grid": 20,
                "nome_humano": "Escolhido",
                "origem_humano": "Nascido sob a luz das estrelas.",
                "hp_inicial": 20,
                "comida_inicial": 8,
                "madeira_inicial": 2,
                "ouro_inicial": 0,
            }

    mundo = Mundo(config_mundo["tamanho_grid"], config_mundo)
    raphael = Raphael(memoria, objetivos)

    memoria.adicionar_evento(f"Mundo criado: {config_mundo['tamanho_grid']}x{config_mundo['tamanho_grid']}")
    memoria.adicionar_evento(f"Personagem: {config_mundo['nome_humano']}")

    return mundo, config_mundo["tamanho_grid"], memoria, raphael


def desenhar_tile(superficie: pygame.Surface, rect: pygame.Rect, cor: tuple[int, int, int]) -> None:
    pygame.draw.rect(superficie, cor, rect, border_radius=5)


def desenhar_emoji(superficie: pygame.Surface, fonte: pygame.font.Font, texto: str, centro: tuple[int, int]) -> None:
    glifo = fonte.render(texto, True, (12, 14, 18))
    rect_glifo = glifo.get_rect(center=centro)
    superficie.blit(glifo, rect_glifo)


def renderizar_mundo(tela: pygame.Surface, mundo: Mundo, fonte_hud: pygame.font.Font, fonte_emoji: pygame.font.Font, modo: str) -> None:
    """Renderizar o mundo do jogo."""
    tela.fill(COR_BG)

    for y in range(mundo.tamanho):
        for x in range(mundo.tamanho):
            rect = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)
            xadrez = (x + y) % 2
            base = COR_GRID_ESC if xadrez == 0 else COR_GRID_CLARO
            pygame.draw.rect(tela, base, rect)
            pygame.draw.rect(tela, COR_CONTORNO, rect, 1)

            pos = (x, y)
            if pos in mundo.tiles_montanha:
                interior = rect.inflate(-8, -8)
                desenhar_tile(tela, interior, COR_MONTANHA)
                desenhar_emoji(tela, fonte_emoji, "⛰️", rect.center)
            elif pos in mundo.tiles_agua:
                interior = rect.inflate(-8, -8)
                desenhar_tile(tela, interior, COR_AGUA)
                desenhar_emoji(tela, fonte_emoji, "💧", rect.center)
            elif pos in mundo.tiles_maldito:
                interior = rect.inflate(-10, -10)
                desenhar_tile(tela, interior, COR_MALDITO)
                desenhar_emoji(tela, fonte_emoji, "🌑", rect.center)
            elif pos in mundo.tiles_santuario:
                interior = rect.inflate(-10, -10)
                desenhar_tile(tela, interior, COR_SANTUARIO)
                desenhar_emoji(tela, fonte_emoji, "⛪", rect.center)
            elif pos in mundo.tiles_casa:
                interior = rect.inflate(-10, -10)
                desenhar_tile(tela, interior, COR_CASA)
                desenhar_emoji(tela, fonte_emoji, "🏠", rect.center)
            elif pos in mundo.tiles_inimigo:
                interior = rect.inflate(-12, -12)
                desenhar_tile(tela, interior, COR_INIMIGO)
                desenhar_emoji(tela, fonte_emoji, "👾", rect.center)
            elif pos in mundo.tiles_animal:
                interior = rect.inflate(-12, -12)
                desenhar_tile(tela, interior, COR_ANIMAL)
                desenhar_emoji(tela, fonte_emoji, "🦌", rect.center)
            elif pos in mundo.tiles_comida:
                interior = rect.inflate(-14, -14)
                desenhar_tile(tela, interior, COR_COMIDA)
                desenhar_emoji(tela, fonte_emoji, "🍎", rect.center)
            elif pos in mundo.tiles_arvore:
                interior = rect.inflate(-12, -12)
                desenhar_tile(tela, interior, COR_ARVORE)
                desenhar_emoji(tela, fonte_emoji, "🌲", rect.center)
            elif pos in mundo.tiles_armadilha:
                interior = rect.inflate(-14, -14)
                desenhar_tile(tela, interior, COR_ARMADILHA)
                desenhar_emoji(tela, fonte_emoji, "🪤", rect.center)
            elif pos in mundo.tiles_tesouro:
                interior = rect.inflate(-14, -14)
                desenhar_tile(tela, interior, COR_TESOURO)
                desenhar_emoji(tela, fonte_emoji, "💎", rect.center)

    hx, hy = mundo.humano
    rect_humano = pygame.Rect(hx * TAMANHO_CELULA, hy * TAMANHO_CELULA, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)
    avatar = rect_humano.inflate(-6, -6)
    desenhar_tile(tela, avatar, COR_HUMANO)
    desenhar_emoji(tela, fonte_emoji, "🧑", rect_humano.center)

    # HUD
    hud_y = mundo.tamanho * TAMANHO_CELULA
    rect_hud = pygame.Rect(0, hud_y, mundo.tamanho * TAMANHO_CELULA, ALTURA_HUD)
    pygame.draw.rect(tela, COR_HUD, rect_hud)

    linha1 = f"{mundo.nome_humano} | HP {int(mundo.hp)}/{int(mundo.hp_maximo)} | Comida {int(mundo.inventario['comida'])} Madeira {int(mundo.inventario['madeira'])}"
    linha2 = f"Pontos {mundo.stats['pontos']} | Moralidade Raphael: {+100 if mundo.moralidade_jogador < -50 else -50 if mundo.moralidade_jogador > 50 else 0} | Modo: {modo}"
    linha3 = f"Evento: {mundo.ultimo_evento}"

    for idx, linha in enumerate([linha1, linha2, linha3]):
        txt = fonte_hud.render(linha, True, COR_TEXTO)
        tela.blit(txt, (8, hud_y + 8 + idx * 28))


def renderizar_chat(tela: pygame.Surface, historico_chat: list[str], fonte_hud: pygame.font.Font, tamanho_grid: int) -> None:
    """Renderizar a interface de chat."""
    chat_y = tamanho_grid * TAMANHO_CELULA + ALTURA_HUD
    rect_chat = pygame.Rect(0, chat_y, tamanho_grid * TAMANHO_CELULA, ALTURA_CHAT)
    pygame.draw.rect(tela, COR_CHAT_BG, rect_chat)
    pygame.draw.line(tela, COR_CONTORNO, (0, chat_y), (tamanho_grid * TAMANHO_CELULA, chat_y), 2)

    txt_titulo = fonte_hud.render("PALAVRAS DE RAPHAEL (Pressione R para falar):", True, COR_AVISO)
    tela.blit(txt_titulo, (8, chat_y + 5))

    for idx, linha in enumerate(historico_chat[-3:]):
        if idx < 3:
            txt = fonte_hud.render(linha[:60], True, COR_TEXTO)
            tela.blit(txt, (8, chat_y + 30 + idx * 35))


def rodar() -> None:
    print("\n=== O REINO DE RAPHAEL ===\n")

    objetivos = carregar_objetivos(OBJETIVO_PATH)
    print("[Raphael está acordando...]")
    mundo, tamanho_real, memoria, raphael = criar_mundo_com_raphael(objetivos)
    print(f"[Raphael falou.]")
    print(f"[Mundo: {tamanho_real}x{tamanho_real} | Seu nome: {mundo.nome_humano}]")
    print(f"[Lore: {mundo.origem_humano}]\n")

    pygame.init()
    pygame.display.set_caption("O Reino de Raphael - Controlado pelo Jogador")
    largura_janela = tamanho_real * TAMANHO_CELULA
    altura_janela = tamanho_real * TAMANHO_CELULA + ALTURA_HUD + ALTURA_CHAT
    tela = pygame.display.set_mode((largura_janela, altura_janela))
    fonte_hud = pygame.font.SysFont("consolas", 16)
    fonte_emoji = pygame.font.SysFont("segoe ui emoji", 20)

    relogio = pygame.time.Clock()
    rodando = True
    tick = 0
    ultimo_tempo_acao = 0.0
    atraso_acao = 0.2
    historico_chat: list[str] = ["Raphael: Bem-vindo, mortal."]
    contador_intervencao = 0
    intervalo_observacao = 6  # Raphael observa ciclos curtos, mas interfere pouco.

    economia_cfg = (
        objetivos.get("mundo", {}).get("economia")
        or objetivos.get("world", {}).get("economy", {})
    )
    consumo_comida_tick = float(economia_cfg.get("consumo_comida_tick", economia_cfg.get("food_upkeep_per_tick", 0.15)))
    dano_fome_tick = float(economia_cfg.get("dano_fome_tick", economia_cfg.get("starvation_damage_per_tick", 2)))

    while rodando and mundo.hp > 0:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                agora = time.time()
                if agora - ultimo_tempo_acao < atraso_acao:
                    continue

                # Movimento
                if evento.key == pygame.K_w:
                    mundo.mover_humano("cima")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_s:
                    mundo.mover_humano("baixo")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_a and evento.mod & pygame.KMOD_SHIFT == 0:
                    mundo.mover_humano("esquerda")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                elif evento.key == pygame.K_d:
                    mundo.mover_humano("direita")
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                # Ações
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
                elif evento.key == pygame.K_z:
                    mundo.descansar()
                    contador_intervencao += 1
                    ultimo_tempo_acao = agora
                # Especial
                elif evento.key == pygame.K_r:
                    print("\n[Chamada para Raphael]")
                    entrada_usuario = input("Fale com Raphael: ")
                    if entrada_usuario.strip():
                        resposta = raphael.responder_jogador(mundo, entrada_usuario)
                        historico_chat.append(f"Você: {entrada_usuario[:40]}")
                        historico_chat.append(f"Raphael: {resposta[:60]}")
                        print(f"Raphael: {resposta}\n")
                        memoria.avisos_jogador += 1

                # Raphael observa toda acao relevante do jogador.
                if evento.key in {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g, pygame.K_e, pygame.K_b, pygame.K_SPACE, pygame.K_c, pygame.K_z}:
                    memoria.adicionar_evento(f"Acao do jogador: {mundo.ultimo_evento}")

                # Raphael observa continuamente e interfere so quando decidir.
                if contador_intervencao >= intervalo_observacao:
                    fala, efeito = raphael.observar_e_talvez_interferir(mundo, mundo.ultimo_evento)
                    if fala:
                        historico_chat.append(f"Raphael: {fala[:60]}")
                        print(f"[Raphael, curioso: {fala}]")
                    if efeito:
                        historico_chat.append(f"Raphael: {efeito[:60]}")
                        print(f"[Interferencia divina: {efeito}]")
                    contador_intervencao = 0

        # Manutenção de fome
        mundo.inventario["comida"] -= consumo_comida_tick
        if mundo.inventario["comida"] <= 0:
            mundo.hp -= dano_fome_tick
            mundo.ultimo_evento = "passando fome"
            
            # Raphael pode intervir
            if mundo.hp < 3 and memoria.moralidade_raphael > 0 and random.random() < 0.4:
                raphael.manipular_mundo(mundo, "reviver")
                historico_chat.append(f"Raphael: Eu o revivi.")

        tick += 1
        modo_str = "JOGADOR"
        renderizar_mundo(tela, mundo, fonte_hud, fonte_emoji, modo_str)
        renderizar_chat(tela, historico_chat, fonte_hud, tamanho_real)
        pygame.display.flip()
        relogio.tick(60)

    print(f"\n[Simulação Encerrada]")
    print(json.dumps(mundo.stats, indent=2))
    pygame.quit()


if __name__ == "__main__":
    rodar()
