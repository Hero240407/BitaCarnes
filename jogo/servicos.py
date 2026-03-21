import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import pygame

from .config import (
    NOME_MODELO,
    NOME_MODELO_BASE,
    NOME_MODELO_PESADO,
    OLLAMA_URL,
    OBJETIVO_PATH,
    SAVE_DIR,
    TECLAS_PODER_CANDIDATAS,
    TECLAS_RESERVADAS,
)
from .modelos import MemoriaRaphael, Mundo, SistemaTempo


def chamar_ollama_leve(prompt: str, timeout: int = 12, temperature: float = 0.9) -> str | None:
    return chamar_ollama(prompt, NOME_MODELO_BASE, timeout=timeout, temperature=temperature)


def chamar_ollama_pesado(prompt: str, timeout: int = 30, temperature: float = 0.5) -> str | None:
    return chamar_ollama(prompt, NOME_MODELO_PESADO, timeout=timeout, temperature=temperature)


def normalizar_lore_personagem(perfil: dict) -> dict:
    perfil_normalizado = dict(perfil)
    origem_bruta = str(perfil_normalizado.get("origem", "")).strip()
    if not origem_bruta:
        return perfil_normalizado

    marcador_legado = " Legado:"
    if marcador_legado in origem_bruta:
        perfil_normalizado["origem"] = origem_bruta.split(marcador_legado, 1)[0].strip()
    else:
        perfil_normalizado["origem"] = origem_bruta

    campos = {
        "legado": r"Legado:\s*(.*?)(?=\s+Motivacao:|\s+Segredo:|$)",
        "motivacao": r"Motivacao:\s*(.*?)(?=\s+Segredo:|$)",
        "segredo": r"Segredo:\s*(.*)$",
    }
    for chave, padrao in campos.items():
        if perfil_normalizado.get(chave):
            continue
        achado = re.search(padrao, origem_bruta)
        if achado:
            perfil_normalizado[chave] = achado.group(1).strip().rstrip(".")

    return perfil_normalizado


def aplicar_lore_personagem(perfil: dict, lore: dict) -> dict:
    perfil_final = normalizar_lore_personagem(perfil)
    perfil_final["origem"] = str(lore.get("origem") or perfil_final.get("origem") or "Origem desconhecida.").strip()
    perfil_final["legado"] = str(lore.get("legado") or perfil_final.get("legado") or "Sem legado conhecido").strip()
    perfil_final["motivacao"] = str(lore.get("motivacao") or perfil_final.get("motivacao") or "Buscar um novo destino").strip()
    perfil_final["segredo"] = str(lore.get("segredo") or perfil_final.get("segredo") or "Guarda algo que ainda nao revelou").strip()
    return perfil_final


def perfil_tem_lore_enriquecida(perfil: dict) -> bool:
    perfil_normalizado = normalizar_lore_personagem(perfil)
    return bool(
        perfil_normalizado.get("origem")
        and perfil_normalizado.get("legado")
        and perfil_normalizado.get("motivacao")
        and perfil_normalizado.get("segredo")
    )


def _lore_fallback(nome: str, origem_atual: str) -> dict:
    legados = [
        "descendente de cartografos do norte",
        "herdeiro de uma linhagem de guardioes",
        "filho de artesaos de vila fronteirica",
        "sobrevivente de um assentamento perdido",
        "aprendiz de uma ordem de druidas errantes",
        "ultimo herdeiro de uma casa de cavaleiros",
        "filho adotivo de mercadores do deserto rubro",
        "pupilo de um bibliotecario de runas esquecidas",
        "descendente de navegadores de mares etereos",
        "sobrevivente de uma cidadela devorada pela nevoa",
    ]
    motivacoes = [
        "provar que pode unir vilas rivais",
        "descobrir porque os santuarios ficaram silenciosos",
        "reconstruir a honra da propria familia",
        "mapear ruinas e impedir nova era de guerra",
        "encontrar o grimorio que salvou sua infancia",
        "quebrar a maldicao que ronda seu sobrenome",
        "abrir uma rota segura entre reinos em conflito",
        "erguer um novo lar para refugiados da fronteira",
        "seguir os rastros de um dragao desaparecido",
        "dominar a mana ancestral sem se corromper",
    ]
    segredos = [
        "carrega um simbolo antigo que reage a mana",
        "ouve ecos de sonhos profeticos em noites de chuva",
        "guarda um mapa incompleto de um tesouro imperial",
        "tem medo de altura por causa de uma queda antiga",
        "esconde um pacto de sangue feito na adolescencia",
        "foi marcado por uma estrela no dia do eclipse",
        "possui um pingente que sussurra em lingua morta",
        "nunca contou que foi salvo por uma criatura maldita",
        "enxerga ruinas antigas em visoes durante tempestades",
        "carrega uma chave sem fechadura conhecida",
    ]
    legado = random.choice(legados)
    motivacao = random.choice(motivacoes)
    segredo = random.choice(segredos)
    origem_base = origem_atual.strip() if origem_atual else f"{nome} surgiu de um passado nebuloso."
    return {
        "origem": origem_base,
        "legado": legado,
        "motivacao": motivacao,
        "segredo": segredo,
    }


def enriquecer_lore_personagem_base(perfil: dict) -> dict:
    nome = str(perfil.get("nome", "Escolhido"))
    idade = int(perfil.get("idade", 18))
    papel = str(perfil.get("papel_social", "protagonista"))
    origem_atual = str(perfil.get("origem", ""))

    prompt = (
        "Voce e um assistente de lore rapido para jogos RPG de fantasia ampla.\n"
        "Responda APENAS JSON valido com as chaves: origem, legado, motivacao, segredo.\n"
        "Cada campo deve ter 1 frase curta em portugues brasileiro.\n"
        "Pode usar qualquer subgenero fantasia: alta fantasia, fantasia sombria, steampunk magico, oriental mistico, fadas, dragoes, ruinas arcanas, reinos em guerra.\n"
        "Evite repeticoes e entregue ideias criativas, mantendo tom apropriado para aventura.\n"
        "Nao reutilize formulas genericas como 'nasceu sob as estrelas' ou 'sobreviveu a tempos dificeis'.\n"
        "A origem deve soar unica, como uma entre infinitas possibilidades de fantasia.\n"
        f"Nome: {nome}\n"
        f"Idade: {idade}\n"
        f"Papel: {papel}\n"
        f"Origem atual: {origem_atual}\n"
    )

    resposta = chamar_ollama_leve(prompt, timeout=12, temperature=0.95)
    if not resposta:
        return _lore_fallback(nome, origem_atual)

    try:
        bruto = json.loads(resposta)
        origem = str(bruto.get("origem", "")).strip()
        legado = str(bruto.get("legado", "")).strip()
        motivacao = str(bruto.get("motivacao", "")).strip()
        segredo = str(bruto.get("segredo", "")).strip()
        if not origem or not legado or not motivacao or not segredo:
            return _lore_fallback(nome, origem_atual)
        return {
            "origem": origem,
            "legado": legado,
            "motivacao": motivacao,
            "segredo": segredo,
        }
    except (ValueError, json.JSONDecodeError):
        return _lore_fallback(nome, origem_atual)


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
        resposta = chamar_ollama_pesado(prompt)
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
        resposta = chamar_ollama_pesado(prompt)
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
        resposta = chamar_ollama_pesado(prompt)
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


def chamar_ollama(prompt: str, modelo: str, timeout: int = 30, temperature: float = 0.5) -> str | None:
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": float(temperature)},
    }
    body = json.dumps(payload).encode("utf-8")
    requisicao = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            bruto = resposta.read().decode("utf-8")
            envelope = json.loads(bruto)
            return envelope.get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _itens_fallback() -> list[dict]:
    return [
        {
            "nome": "Lamina do Novato Isekai",
            "tipo": "espada",
            "slot": "arma",
            "raridade": "incomum",
            "descricao": "Uma espada simples, porem fiel para os primeiros biomas.",
            "bonus": {"ataque": 2, "defesa": 0, "hp": 0, "sorte": 0, "coleta": 0},
        },
        {
            "nome": "Peitoral de Couro de Aventureiro",
            "tipo": "armadura",
            "slot": "armadura",
            "raridade": "comum",
            "descricao": "Protecao leve inspirada em cronicas de fantasia.",
            "bonus": {"ataque": 0, "defesa": 2, "hp": 4, "sorte": 0, "coleta": 0},
        },
        {
            "nome": "Anel da Sorte de Guilda",
            "tipo": "anel",
            "slot": "acessorio",
            "raridade": "raro",
            "descricao": "Um anel que atrai encontros favoraveis e descansos melhores.",
            "bonus": {"ataque": 0, "defesa": 0, "hp": 0, "sorte": 2, "coleta": 1},
        },
        {
            "nome": "Reliquia de Mana Dourada",
            "tipo": "reliquia",
            "slot": "reliquia",
            "raridade": "epico",
            "descricao": "Fragmento antigo que fortalece o corpo do heroi.",
            "bonus": {"ataque": 1, "defesa": 1, "hp": 6, "sorte": 1, "coleta": 0},
        },
        {
            "nome": "Po de Teleporte Curto",
            "tipo": "consumivel",
            "slot": "consumivel",
            "raridade": "incomum",
            "descricao": "Cristais de viagem usados em contos de outro mundo.",
            "bonus": {"ataque": 0, "defesa": 0, "hp": 2, "sorte": 0, "coleta": 0},
        },
        {
            "nome": "Picareta do Mineiro Arcano",
            "tipo": "ferramenta",
            "slot": "arma",
            "raridade": "incomum",
            "descricao": "Ferramenta robusta para escavar e lutar em cavernas.",
            "bonus": {"ataque": 1, "defesa": 0, "hp": 0, "sorte": 0, "coleta": 2},
        },
        {
            "nome": "Manto do Erudito Lunar",
            "tipo": "manto",
            "slot": "armadura",
            "raridade": "raro",
            "descricao": "Manto elegante de academias magicas de fantasia.",
            "bonus": {"ataque": 0, "defesa": 1, "hp": 3, "sorte": 1, "coleta": 0},
        },
        {
            "nome": "Broche da Primeira Quest",
            "tipo": "broche",
            "slot": "acessorio",
            "raridade": "comum",
            "descricao": "Marca de quem aceitou a jornada sem hesitar.",
            "bonus": {"ataque": 0, "defesa": 1, "hp": 1, "sorte": 1, "coleta": 0},
        },
    ]


def gerar_itens_iniciais_raphael(nome_humano: str, quantidade: int = 8) -> list[dict]:
    quantidade = max(6, min(12, int(quantidade)))
    prompt = (
        "Voce e Raphael criando itens iniciais para um jogo sandbox em estilo terraria e fantasia.\n"
        "Inspire-se em isekais, animes de fantasia e livros de fantasia classica.\n"
        "Responda APENAS JSON valido com uma lista em 'itens'.\n"
        "Cada item precisa: nome, tipo, slot(arma|armadura|acessorio|reliquia|consumivel), raridade, descricao, bonus.\n"
        "bonus precisa conter numeros: ataque, defesa, hp, sorte, coleta.\n"
        f"Crie exatamente {quantidade} itens para o heroi {nome_humano}."
    )
    resposta = chamar_ollama_leve(prompt, timeout=16, temperature=0.8)
    if not resposta:
        base = _itens_fallback()
        random.shuffle(base)
        return base[:quantidade]
    try:
        bruto = json.loads(resposta)
        itens = bruto.get("itens", bruto if isinstance(bruto, list) else [])
        saida = []
        for item in itens[:quantidade]:
            slot = str(item.get("slot", "acessorio"))
            if slot not in {"arma", "armadura", "acessorio", "reliquia", "consumivel"}:
                slot = "acessorio"
            bonus = item.get("bonus", {})
            saida.append(
                {
                    "nome": str(item.get("nome", "Item Arcano"))[:60],
                    "tipo": str(item.get("tipo", "item"))[:30],
                    "slot": slot,
                    "raridade": str(item.get("raridade", "comum"))[:20],
                    "descricao": str(item.get("descricao", "Sem descricao"))[:180],
                    "bonus": {
                        "ataque": float(bonus.get("ataque", 0)),
                        "defesa": float(bonus.get("defesa", 0)),
                        "hp": float(bonus.get("hp", 0)),
                        "sorte": float(bonus.get("sorte", 0)),
                        "coleta": float(bonus.get("coleta", 0)),
                    },
                }
            )
        if not saida:
            base = _itens_fallback()
            random.shuffle(base)
            return base[:quantidade]
        return saida
    except (ValueError, json.JSONDecodeError):
        base = _itens_fallback()
        random.shuffle(base)
        return base[:quantidade]


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
    nomes = set()
    for p in SAVE_DIR.glob("*.json"):
        nomes.add(p.stem)
    for d in SAVE_DIR.iterdir():
        if d.is_dir() and (d / "meta.json").exists():
            nomes.add(d.name)
    return sorted(list(nomes), key=str.lower)


def salvar_jogo(nome_save: str, mundo: Mundo, memoria: MemoriaRaphael, meta: dict) -> str:
    SAVE_DIR.mkdir(exist_ok=True)
    nome = normalizar_nome_save(nome_save)
    pasta = SAVE_DIR / nome
    pasta.mkdir(parents=True, exist_ok=True)

    (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "mundo.json").write_text(
        json.dumps(
            {
                "tamanho": mundo.tamanho,
                "humano": mundo.humano,
                "nome_humano": mundo.nome_humano,
                "idade_humano": mundo.idade_humano,
                "origem_humano": mundo.origem_humano,
                "perfil_jogador": mundo.perfil_jogador,
                "hp": mundo.hp,
                "hp_base": mundo.hp_base,
                "hp_maximo": mundo.hp_maximo,
                "inventario": mundo.inventario,
                "inventario_itens": mundo.inventario_itens,
                "equipamentos": mundo.equipamentos,
                "stats": mundo.stats,
                "moralidade_jogador": mundo.moralidade_jogador,
                "poderes": mundo.poderes,
                "pet": mundo.pet,
                "magias_aprendidas": mundo.magias_aprendidas,
                "ano_base": mundo.ano_base,
                "ano_atual": mundo.ano_atual,
                "interior_ativo": mundo.interior_ativo,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (pasta / "tiles.json").write_text(
        json.dumps(
            {
                "comida": list(mundo.tiles_comida),
                "arvore": list(mundo.tiles_arvore),
                "casa": list(mundo.tiles_casa),
                "inimigo": list(mundo.tiles_inimigo),
                "animais": [{"x": x, "y": y, "dados": info} for (x, y), info in mundo.animais.items()],
                "montanha": list(mundo.tiles_montanha),
                "agua": list(mundo.tiles_agua),
                "santuario": list(mundo.tiles_santuario),
                "vila": list(mundo.tiles_vila),
                "igreja": list(mundo.tiles_igreja),
                "biblioteca": list(mundo.tiles_biblioteca),
                "castelo": list(mundo.tiles_castelo),
                "armadilha": list(mundo.tiles_armadilha),
                "maldito": list(mundo.tiles_maldito),
                "tesouro": [{"x": x, "y": y, "ouro": ouro} for (x, y), ouro in mundo.tiles_tesouro.items()],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (pasta / "sociedade.json").write_text(
        json.dumps(
            {
                "vilas": mundo.vilas,
                "npcs": mundo.npcs,
                "casa_para_id": [{"x": x, "y": y, "id": cid} for (x, y), cid in mundo.casa_para_id.items()],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (pasta / "lore_quests.json").write_text(
        json.dumps(
            {
                "world_lore": mundo.world_lore,
                "quests_ativas": mundo.quests_ativas,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (pasta / "memoria_raphael.json").write_text(
        json.dumps(
            {
                "conversas": list(memoria.historico_conversas),
                "eventos": list(memoria.eventos),
                "moralidade_raphael": memoria.moralidade_raphael,
                "intervencoes": memoria.intervencoes,
                "avisos_jogador": memoria.avisos_jogador,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return nome


def carregar_save(nome_save: str) -> tuple[Mundo, MemoriaRaphael, dict]:

    nome_norm = normalizar_nome_save(nome_save)
    pasta = SAVE_DIR / nome_norm
    arquivo_legado = SAVE_DIR / f"{nome_norm}.json"

    print(f"[carregar_save] Procurando save: {nome_save} (normalizado: {nome_norm})")

    if pasta.exists() and pasta.is_dir() and (pasta / "mundo.json").exists():
        print(f"[carregar_save] Save moderno encontrado em {pasta}")
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8")) if (pasta / "meta.json").exists() else {}
        m = json.loads((pasta / "mundo.json").read_text(encoding="utf-8"))
        tiles = json.loads((pasta / "tiles.json").read_text(encoding="utf-8"))
        sociedade = json.loads((pasta / "sociedade.json").read_text(encoding="utf-8")) if (pasta / "sociedade.json").exists() else {}
        lore_quests = json.loads((pasta / "lore_quests.json").read_text(encoding="utf-8")) if (pasta / "lore_quests.json").exists() else {}
        mem = json.loads((pasta / "memoria_raphael.json").read_text(encoding="utf-8")) if (pasta / "memoria_raphael.json").exists() else {}
    elif arquivo_legado.exists():
        print(f"[carregar_save] Save legado encontrado em {arquivo_legado}")
        dados = json.loads(arquivo_legado.read_text(encoding="utf-8"))
        meta = dados.get("meta", {})
        m = dados["mundo"]
        tiles = m["tiles"]
        sociedade = {}
        lore_quests = {}
        mem = dados.get("memoria", {})
    else:
        print(f"[carregar_save] Save nao encontrado: {nome_save}")
        raise FileNotFoundError(f"Save nao encontrado: {nome_save}")

    mundo = Mundo(int(m["tamanho"]), {
        "nome_humano": m["nome_humano"],
        "perfil_jogador": m.get("perfil_jogador"),
        "origem_humano": m["origem_humano"],
        "hp_inicial": m.get("hp_base", m["hp_maximo"]),
        "comida_inicial": m["inventario"]["comida"],
        "madeira_inicial": m["inventario"]["madeira"],
        "ouro_inicial": m["inventario"].get("ouro", 0),
    })
    print(f"[carregar_save] Mundo carregado: {mundo.tamanho}x{mundo.tamanho}")
    print(f"[carregar_save] Personagem: {mundo.nome_humano} | Idade: {mundo.idade_humano}")
    print(f"[carregar_save] Origem: {mundo.origem_humano}")
    if hasattr(mundo, 'perfil_jogador') and mundo.perfil_jogador:
        print(f"[carregar_save] Perfil do personagem: {json.dumps(mundo.perfil_jogador, ensure_ascii=False, indent=2)}")
    if hasattr(mundo, 'world_lore') and mundo.world_lore:
        print(f"[carregar_save] World Lore: {json.dumps(mundo.world_lore, ensure_ascii=False, indent=2)}")

    mundo.humano = list(m["humano"])
    mundo.idade_humano = int(m.get("idade_humano", mundo.idade_humano))
    if m.get("perfil_jogador"):
        mundo.perfil_jogador = dict(m["perfil_jogador"])
    mundo.hp = float(m["hp"])
    mundo.hp_base = float(m.get("hp_base", mundo.hp_base))
    mundo.hp_maximo = float(m["hp_maximo"])
    mundo.inventario = dict(m["inventario"])
    mundo.inventario_itens = list(m.get("inventario_itens", []))
    mundo.equipamentos = dict(m.get("equipamentos", mundo.equipamentos))
    mundo.stats = dict(m["stats"])
    mundo.moralidade_jogador = int(m.get("moralidade_jogador", 0))
    mundo.poderes = dict(m.get("poderes", {}))
    mundo.pet = m.get("pet")
    mundo.magias_aprendidas = list(m.get("magias_aprendidas", []))
    mundo.ano_base = int(m.get("ano_base", mundo.ano_base))
    mundo.ano_atual = int(m.get("ano_atual", mundo.ano_atual))
    mundo.interior_ativo = m.get("interior_ativo")
    mundo.atualizar_atributos_de_equipamentos()

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
    mundo.tiles_igreja = set(tuple(x) for x in tiles.get("igreja", []))
    mundo.tiles_biblioteca = set(tuple(x) for x in tiles.get("biblioteca", []))
    mundo.tiles_castelo = set(tuple(x) for x in tiles.get("castelo", []))
    mundo.tiles_armadilha = set(tuple(x) for x in tiles["armadilha"])
    mundo.tiles_maldito = set(tuple(x) for x in tiles["maldito"])
    mundo.tiles_tesouro = {(int(t["x"]), int(t["y"])): int(t["ouro"]) for t in tiles["tesouro"]}

    mundo.vilas = dict(sociedade.get("vilas", {}))
    mundo.npcs = dict(sociedade.get("npcs", {}))
    for npc in mundo.npcs.values():
        npc.setdefault("idade", 18)
        npc.setdefault("perfil", {"nome": npc.get("nome", "NPC"), "idade": npc.get("idade", 18)})
    casa_para_id = sociedade.get("casa_para_id", [])
    mundo.casa_para_id = {(int(x["x"]), int(x["y"])): x["id"] for x in casa_para_id}
    mundo.world_lore = dict(lore_quests.get("world_lore", mundo.world_lore))
    mundo.quests_ativas = list(lore_quests.get("quests_ativas", mundo.quests_ativas))

    memoria = MemoriaRaphael()
    memoria.historico_conversas = list(mem.get("conversas", []))
    memoria.eventos = list(mem.get("eventos", []))
    memoria.moralidade_raphael = int(mem.get("moralidade_raphael", 0))
    memoria.intervencoes = int(mem.get("intervencoes", 0))
    memoria.avisos_jogador = int(mem.get("avisos_jogador", 0))

    return mundo, memoria, meta


def criar_mundo_com_raphael(objetivos: dict, perfil_jogador: dict | None = None) -> tuple[Mundo, int, MemoriaRaphael, Raphael]:
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
        '{"tamanho_grid": inteiro, "nome_humano": string, "origem": string, "hp": inteiro, "comida": inteiro, "madeira": inteiro, "spawn": {"x": inteiro, "y": inteiro, "tema": string}}'
    )

    print("[criar_mundo_com_raphael] Gerando mundo com prompt:")
    print(prompt)
    resposta = chamar_ollama_pesado(prompt, timeout=30, temperature=0.6)
    nome_base = (perfil_jogador or {}).get("nome", "Escolhido")
    if not resposta:
        print("[criar_mundo_com_raphael] Nenhuma resposta do modelo, usando fallback padrao.")
        config_mundo = {
            "tamanho_grid": 20,
            "nome_humano": nome_base,
            "origem_humano": "Nascido sob a luz das estrelas.",
            "hp_inicial": 20,
            "comida_inicial": 8,
            "madeira_inicial": 2,
            "ouro_inicial": 0,
            "spawn_inicial": None,
            "perfil_jogador": perfil_jogador,
        }
    else:
        try:
            analisado = json.loads(resposta)
            print(f"[criar_mundo_com_raphael] Resposta do modelo: {json.dumps(analisado, ensure_ascii=False, indent=2)}")
            tamanho_grid = min(40, max(16, int(analisado.get("tamanho_grid", 20))))
            spawn = analisado.get("spawn") if isinstance(analisado.get("spawn"), dict) else {}
            sx = int(spawn.get("x", tamanho_grid // 2))
            sy = int(spawn.get("y", tamanho_grid // 2))
            config_mundo = {
                "tamanho_grid": tamanho_grid,
                "nome_humano": (perfil_jogador or {}).get("nome", analisado.get("nome_humano", nome_base)),
                "origem_humano": analisado.get("origem", "Um sobrevivente misterioso."),
                "hp_inicial": max(15, int(analisado.get("hp", 20))),
                "comida_inicial": max(5, int(analisado.get("comida", 8))),
                "madeira_inicial": max(1, int(analisado.get("madeira", 2))),
                "ouro_inicial": 0,
                "spawn_inicial": {
                    "x": max(0, min(tamanho_grid - 1, sx)),
                    "y": max(0, min(tamanho_grid - 1, sy)),
                    "tema": str(spawn.get("tema", "fronteira"))[:40],
                },
                "perfil_jogador": perfil_jogador,
            }
        except Exception as e:
            print(f"[criar_mundo_com_raphael] Erro ao analisar resposta do modelo: {e}")
            config_mundo = {
                "tamanho_grid": 20,
                "nome_humano": nome_base,
                "origem_humano": "Nascido sob a luz das estrelas.",
                "hp_inicial": 20,
                "comida_inicial": 8,
                "madeira_inicial": 2,
                "ouro_inicial": 0,
                "spawn_inicial": None,
                "perfil_jogador": perfil_jogador,
            }

    if perfil_jogador and not perfil_tem_lore_enriquecida(perfil_jogador):
        print("[criar_mundo_com_raphael] Enriquecendo lore do personagem...")
        lore_extra = enriquecer_lore_personagem_base(perfil_jogador)
        perfil_jogador = aplicar_lore_personagem(perfil_jogador, lore_extra)
        config_mundo["origem_humano"] = perfil_jogador.get("origem", config_mundo["origem_humano"])
    elif perfil_jogador:
        perfil_jogador = normalizar_lore_personagem(perfil_jogador)
        config_mundo["origem_humano"] = perfil_jogador.get("origem", config_mundo["origem_humano"])

    config_mundo["itens_iniciais"] = gerar_itens_iniciais_raphael(config_mundo["nome_humano"], quantidade=8)

    print(f"[criar_mundo_com_raphael] Mundo: {config_mundo['tamanho_grid']}x{config_mundo['tamanho_grid']}")
    print(f"[criar_mundo_com_raphael] Personagem: {config_mundo['nome_humano']}")
    print(f"[criar_mundo_com_raphael] Origem: {config_mundo['origem_humano']}")
    if perfil_jogador:
        print(f"[criar_mundo_com_raphael] Perfil do personagem: {json.dumps(perfil_jogador, ensure_ascii=False, indent=2)}")

    mundo = Mundo(config_mundo["tamanho_grid"], config_mundo)
    raphael = Raphael(memoria, objetivos)
    memoria.adicionar_evento(f"Mundo criado: {config_mundo['tamanho_grid']}x{config_mundo['tamanho_grid']}")
    memoria.adicionar_evento(f"Personagem: {config_mundo['nome_humano']}")
    return mundo, config_mundo["tamanho_grid"], memoria, raphael
