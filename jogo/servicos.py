import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import pygame

from .config import NOME_MODELO, OLLAMA_URL, OBJETIVO_PATH, SAVE_DIR, TECLAS_PODER_CANDIDATAS, TECLAS_RESERVADAS
from .modelos import MemoriaRaphael, Mundo, SistemaTempo


class Raphael:
    def __init__(self, memoria: MemoriaRaphael, objetivos: dict):
        self.memoria = memoria
        self.objetivos = objetivos
        self.pode_intervir = True

    def manipular_mundo(self, mundo: Mundo, tipo_intervencao: str, tempo: SistemaTempo | None = None) -> str:
        if tipo_intervencao == "ampliar_mundo":
            novo_tamanho = min(40, mundo.tamanho + 2)
            if novo_tamanho > mundo.tamanho:
                mundo.tamanho = novo_tamanho
                self.memoria.intervencoes += 1
                return f"Raphael expandiu o mundo para {novo_tamanho}x{novo_tamanho}"

        if tipo_intervencao == "comida_escassa":
            comida_remover = list(mundo.tiles_comida)[:max(1, len(mundo.tiles_comida)//4)]
            for pos in comida_remover:
                mundo.tiles_comida.discard(pos)
            self.memoria.intervencoes += 1
            return "Raphael tornou a comida escassa"

        if tipo_intervencao == "chuva_bencao":
            for _ in range(int(mundo.tamanho * 0.2)):
                x = random.randint(0, mundo.tamanho - 1)
                y = random.randint(0, mundo.tamanho - 1)
                if (x, y) not in mundo.tiles_montanha and (x, y) not in mundo.tiles_agua:
                    mundo.tiles_comida.add((x, y))
            self.memoria.intervencoes += 1
            return "Raphael abencoou o mundo com colheita abundante"

        if tipo_intervencao == "armadilhas_aumentadas":
            for _ in range(max(1, int(mundo.tamanho * 0.04))):
                x = random.randint(0, mundo.tamanho - 1)
                y = random.randint(0, mundo.tamanho - 1)
                if (x, y) not in mundo.tiles_montanha and (x, y) not in mundo.tiles_agua:
                    mundo.tiles_armadilha.add((x, y))
            self.memoria.intervencoes += 1
            self.memoria.moralidade_raphael -= 20
            return "Raphael amaldicoou o mundo com armadilhas"

        if tipo_intervencao == "reviver":
            mundo.hp = mundo.hp_maximo
            return "Raphael o reviveu"

        if tipo_intervencao == "parar_ou_retomar_tempo" and tempo is not None:
            self.memoria.intervencoes += 1
            return f"Raphael {tempo.alternar_congelamento()}"

        if tipo_intervencao == "avancar_tempo" and tempo is not None:
            self.memoria.intervencoes += 1
            escolha = random.choice([(0, 6, 0, 0), (2, 0, 0, 0), (0, 0, 0, 1)])
            tempo.avancar(dias=escolha[0], horas=escolha[1], minutos=escolha[2], anos=escolha[3])
            if escolha[3] > 0:
                return "Raphael avancou 1 ano no fluxo temporal"
            if escolha[0] > 0:
                return f"Raphael avancou {escolha[0]} dias"
            return f"Raphael avancou {escolha[1]} horas"

        return "Raphael observa silenciosamente"

    def observar_e_talvez_interferir(self, mundo: Mundo, acao_recente: str, tempo: SistemaTempo | None = None) -> tuple[str | None, str | None]:
        self.memoria.adicionar_evento(f"Observacao divina: {acao_recente}")
        fala = None
        efeito = None

        # Fala automática sem chamada remota para não travar o loop.
        if random.random() < 0.30:
            tons = [
                "Observo seus passos com curiosidade.",
                "Seu caminho revela suas intenções.",
                "Cada decisão sua altera o destino do mundo.",
                "Vejo hesitação, mas também potencial.",
            ]
            fala = f"{random.choice(tons)} Ação recente: {acao_recente}."
            self.memoria.adicionar_conversa("Raphael", fala)

        if random.random() < 0.12:
            if mundo.moralidade_jogador < -35:
                efeito = self.manipular_mundo(mundo, random.choice(["comida_escassa", "armadilhas_aumentadas"]), tempo)
            elif mundo.hp < max(3, mundo.hp_maximo * 0.2):
                efeito = self.manipular_mundo(mundo, "reviver", tempo)
            elif tempo is not None and random.random() < 0.30:
                efeito = self.manipular_mundo(mundo, random.choice(["parar_ou_retomar_tempo", "avancar_tempo"]), tempo)
            elif random.random() < 0.5:
                efeito = self.manipular_mundo(mundo, "chuva_bencao", tempo)

        return fala, efeito

    def questionar_jogador(self, mundo: Mundo, acao_recente: str) -> str:
        contexto = self.memoria.obter_contexto()
        estado = json.dumps(mundo.estado(0), indent=2)
        prompt = (
            f"Voce e RAPHAEL observando {mundo.nome_humano}.\n"
            f"Moralidade sua: {self.memoria.moralidade_raphael} | do jogador: {mundo.moralidade_jogador}\n\n"
            f"{contexto}\n\n"
            f"ACAO RECENTE: {acao_recente}\nESTADO:\n{estado}\n\n"
            "Responda em 1-2 frases em portugues brasileiro."
        )
        resposta = chamar_ollama(prompt, NOME_MODELO)
        if not resposta:
            resposta = f"Raphael observa {mundo.nome_humano} em silencio."
        self.memoria.adicionar_conversa("Raphael", resposta)
        return resposta

    def responder_jogador(self, mundo: Mundo, mensagem: str) -> str:
        contexto = self.memoria.obter_contexto()
        estado = json.dumps(mundo.estado(0), indent=2)
        prompt = (
            f"Voce e RAPHAEL, o Arcanjo. Moralidade: {self.memoria.moralidade_raphael}\n\n"
            f"{contexto}\n\n"
            f"{mundo.nome_humano} diz: '{mensagem}'\n\n"
            f"ESTADO:\n{estado}\n\n"
            "Responda em portugues brasileiro, 2-3 frases, com sabedoria pratica."
        )
        resposta = chamar_ollama(prompt, NOME_MODELO)
        if not resposta:
            resposta = f"Um silencio divino envolve {mundo.nome_humano}."
        self.memoria.adicionar_conversa("Raphael", resposta)
        return resposta

    def avaliar_pedido_poder(self, mundo: Mundo, pedido: str, teclas_usadas: set[int]) -> tuple[bool, str, dict | None]:
        contexto = self.memoria.obter_contexto()
        estado = json.dumps(mundo.estado(0), indent=2)
        prompt = (
            "Voce e RAPHAEL. Decida se concede ou recusa um poder.\n"
            "Responda JSON: conceder(bool), motivo(str), tipo_poder(str), nome_poder(str), cargas(int), valor(float).\n"
            "Tipos validos: defesa_divina, cura_celestial, passo_etereo, colheita_milagre.\n\n"
            f"{contexto}\n\nESTADO: {estado}\nPEDIDO: {pedido}\n"
        )
        resposta = chamar_ollama(prompt, NOME_MODELO)
        if not resposta:
            return False, "Hoje nao concederei este dom.", None

        try:
            dado = json.loads(resposta)
            conceder = bool(dado.get("conceder", False))
            motivo = str(dado.get("motivo", "Sem julgamento."))
            if not conceder:
                return False, motivo, None

            tipo = str(dado.get("tipo_poder", "defesa_divina"))
            if tipo not in {"defesa_divina", "cura_celestial", "passo_etereo", "colheita_milagre"}:
                tipo = "defesa_divina"

            nome_poder = str(dado.get("nome_poder", "Dom Divino"))
            cargas = max(1, int(dado.get("cargas", 1)))
            valor = float(dado.get("valor", 0))

            tecla = None
            if tipo != "defesa_divina":
                tecla = proxima_tecla_poder(teclas_usadas)
                if tecla is None:
                    return False, "Nao ha teclas livres para novos dons.", None

            return True, motivo, {
                "id": tipo,
                "nome": nome_poder,
                "tipo": tipo,
                "tecla": tecla,
                "cargas": cargas,
                "valor": valor,
            }
        except (ValueError, json.JSONDecodeError):
            return False, "Nao compreendi seu pedido neste momento.", None


def carregar_objetivos(caminho: Path = OBJETIVO_PATH) -> dict:
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


def tecla_nome(tecla: int) -> str:
    return pygame.key.name(tecla).upper()


def proxima_tecla_poder(teclas_usadas: set[int]) -> int | None:
    for tecla in TECLAS_PODER_CANDIDATAS:
        if tecla not in TECLAS_RESERVADAS and tecla not in teclas_usadas:
            return tecla
    return None


def normalizar_nome_save(nome: str) -> str:
    nome_limpo = re.sub(r"[^a-zA-Z0-9_\- ]", "", nome).strip()
    return nome_limpo[:60] if nome_limpo else "save_sem_nome"


def listar_saves() -> list[str]:
    SAVE_DIR.mkdir(exist_ok=True)
    return sorted([p.stem for p in SAVE_DIR.glob("*.json")], key=str.lower)


def salvar_jogo(nome_save: str, mundo: Mundo, memoria: MemoriaRaphael, meta: dict) -> str:
    SAVE_DIR.mkdir(exist_ok=True)
    nome = normalizar_nome_save(nome_save)
    caminho = SAVE_DIR / f"{nome}.json"

    dados = {
        "meta": meta,
        "mundo": {
            "tamanho": mundo.tamanho,
            "humano": mundo.humano,
            "nome_humano": mundo.nome_humano,
            "origem_humano": mundo.origem_humano,
            "hp": mundo.hp,
            "hp_maximo": mundo.hp_maximo,
            "inventario": mundo.inventario,
            "stats": mundo.stats,
            "moralidade_jogador": mundo.moralidade_jogador,
            "poderes": mundo.poderes,
            "pet": mundo.pet,
            "tiles": {
                "comida": list(mundo.tiles_comida),
                "arvore": list(mundo.tiles_arvore),
                "casa": list(mundo.tiles_casa),
                "inimigo": list(mundo.tiles_inimigo),
                "animais": [
                    {
                        "x": x,
                        "y": y,
                        "dados": info,
                    }
                    for (x, y), info in mundo.animais.items()
                ],
                "montanha": list(mundo.tiles_montanha),
                "agua": list(mundo.tiles_agua),
                "santuario": list(mundo.tiles_santuario),
                "vila": list(mundo.tiles_vila),
                "armadilha": list(mundo.tiles_armadilha),
                "maldito": list(mundo.tiles_maldito),
                "tesouro": [{"x": x, "y": y, "ouro": ouro} for (x, y), ouro in mundo.tiles_tesouro.items()],
            },
        },
        "memoria": {
            "conversas": list(memoria.historico_conversas),
            "eventos": list(memoria.eventos),
            "moralidade_raphael": memoria.moralidade_raphael,
            "intervencoes": memoria.intervencoes,
            "avisos_jogador": memoria.avisos_jogador,
        },
    }
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return nome


def carregar_save(nome_save: str) -> tuple[Mundo, MemoriaRaphael, dict]:
    caminho = SAVE_DIR / f"{normalizar_nome_save(nome_save)}.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))

    m = dados["mundo"]
    mundo = Mundo(int(m["tamanho"]), {
        "nome_humano": m["nome_humano"],
        "origem_humano": m["origem_humano"],
        "hp_inicial": m["hp_maximo"],
        "comida_inicial": m["inventario"]["comida"],
        "madeira_inicial": m["inventario"]["madeira"],
        "ouro_inicial": m["inventario"].get("ouro", 0),
    })

    mundo.humano = list(m["humano"])
    mundo.hp = float(m["hp"])
    mundo.hp_maximo = float(m["hp_maximo"])
    mundo.inventario = dict(m["inventario"])
    mundo.stats = dict(m["stats"])
    mundo.moralidade_jogador = int(m.get("moralidade_jogador", 0))
    mundo.poderes = dict(m.get("poderes", {}))
    mundo.pet = m.get("pet")

    tiles = m["tiles"]
    mundo.tiles_comida = set(tuple(x) for x in tiles["comida"])
    mundo.tiles_arvore = set(tuple(x) for x in tiles["arvore"])
    mundo.tiles_casa = set(tuple(x) for x in tiles["casa"])
    mundo.tiles_inimigo = set(tuple(x) for x in tiles["inimigo"])
    mundo.animais = {}
    if "animais" in tiles:
        for a in tiles["animais"]:
            mundo.animais[(int(a["x"]), int(a["y"]))] = dict(a.get("dados", {}))
    else:
        # Compatibilidade com saves antigos.
        for pos in tiles.get("animal", []):
            mundo.animais[tuple(pos)] = {
                "especie": "veado",
                "personalidade": "calmo",
                "domesticado": False,
                "foge": True,
                "energia": 4,
            }
    mundo.tiles_montanha = set(tuple(x) for x in tiles["montanha"])
    mundo.tiles_agua = set(tuple(x) for x in tiles["agua"])
    mundo.tiles_santuario = set(tuple(x) for x in tiles["santuario"])
    mundo.tiles_vila = set(tuple(x) for x in tiles.get("vila", []))
    mundo.tiles_armadilha = set(tuple(x) for x in tiles["armadilha"])
    mundo.tiles_maldito = set(tuple(x) for x in tiles["maldito"])
    mundo.tiles_tesouro = {(int(t["x"]), int(t["y"])): int(t["ouro"]) for t in tiles["tesouro"]}

    memoria = MemoriaRaphael()
    mem = dados.get("memoria", {})
    memoria.historico_conversas = list(mem.get("conversas", []))
    memoria.eventos = list(mem.get("eventos", []))
    memoria.moralidade_raphael = int(mem.get("moralidade_raphael", 0))
    memoria.intervencoes = int(mem.get("intervencoes", 0))
    memoria.avisos_jogador = int(mem.get("avisos_jogador", 0))

    return mundo, memoria, dados.get("meta", {})


def criar_mundo_com_raphael(objetivos: dict) -> tuple[Mundo, int, MemoriaRaphael, Raphael]:
    memoria = MemoriaRaphael()
    raphael_cfg = objetivos.get("raphael", {})
    mundo_cfg = objetivos.get("criador_mundo", objetivos.get("world_creator", {}))

    identidade_raphael = raphael_cfg.get(
        "identidade",
        raphael_cfg.get("identity_prompt", "Voce e RAPHAEL, o Arcanjo."),
    )
    narrativa_mundo = mundo_cfg.get("narrativa", mundo_cfg.get("narrative", "Crie um mundo de sobrevivencia."))
    restricoes = mundo_cfg.get("restricoes_criativas", mundo_cfg.get("world_constraints", []))

    prompt = (
        f"{identidade_raphael}\n\n"
        f"TAREFA: Crie um mundo de sobrevivencia.\n"
        f"{narrativa_mundo}\n\n"
        f"RESTRICOES:\n" + "\n".join(f"- {c}" for c in restricoes) +
        "\n\nResponda APENAS JSON valido:\n"
        '{"tamanho_grid": inteiro, "nome_humano": string, "origem": string, "hp": inteiro, "comida": inteiro, "madeira": inteiro}'
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
        except Exception:
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
