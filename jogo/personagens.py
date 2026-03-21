from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random

import pygame

RAIZ_SPRITES = Path(__file__).resolve().parent.parent / "sprites" / "mana-seed-farmer" / "farmer base sheets"
TAMANHO_CELULA_BASE = 64

PASTAS_CAMADAS = {
    "corpo": "01body",
    "pes": "03fot1",
    "pernas": "04lwr1",
    "camisa": "05shrt",
    "cabelo": "13hair",
    "cabeca": "14head",
}

CELULAS_DIRECAO = {
    "baixo": (0, 1, 2),
    "esquerda": (16, 17, 18),
    "direita": (32, 33, 34),
    "cima": (48, 49, 50),
}

NOMES_INICIO = [
    "Ari", "Lia", "Mika", "Toma", "Noa", "Cora", "Eron", "Sora", "Iris", "Bento", "Kael", "Nina",
]
NOMES_FIM = [
    "el", "a", "en", "or", "is", "an", "iel", "on", "ira", "eus", "in", "orah",
]
SOBRENOMES = [
    "do Vale", "da Ponte", "dos Pinhos", "de Brasa", "da Aurora", "da Colina", "das Fontes", "de Cedro",
]
ORIGENS = [
    "cresceu entre plantações e ruinas antigas.",
    "aprendeu cedo a viver entre vilas e estradas perigosas.",
    "veio de uma familia humilde marcada por velhas profecias.",
    "foi criado perto de bosques sagrados e rios de mana.",
    "sobreviveu a anos difíceis nas bordas do reino.",
]
PAPEL_SOCIAL = [
    "andarilho", "aprendiz", "guardiao", "curandeiro", "ferreiro", "caçador", "mercadora", "cronista",
]

PALETAS_ROUPA = [
    (182, 96, 58),
    (91, 113, 146),
    (76, 140, 91),
    (152, 92, 132),
    (208, 166, 92),
    (122, 92, 74),
]
PALETAS_CABELO = [
    (68, 40, 28),
    (109, 72, 34),
    (181, 138, 74),
    (52, 55, 74),
    (146, 80, 70),
]
PALETAS_CABECA = [
    (118, 74, 42),
    (89, 68, 36),
    (70, 58, 45),
    (145, 96, 54),
]


@dataclass(slots=True)
class CatalogoCamadas:
    corpo: list[str]
    pes: list[str]
    pernas: list[str]
    camisa: list[str]
    cabelo: list[str]
    cabeca: list[str]


class BancoPersonagens:
    def __init__(self) -> None:
        self._catalogo = self._carregar_catalogo()
        self._cache_sheets: dict[str, pygame.Surface] = {}

    def gerar_perfil_jogador(self, nome_forcado: str | None = None) -> dict:
        nome = nome_forcado.strip() if nome_forcado else self._gerar_nome()
        return self._gerar_perfil_base(nome=nome, idade=random.randint(9, 30), papel="protagonista")

    def gerar_perfil_npc(self, papel: str | None = None) -> dict:
        return self._gerar_perfil_base(
            nome=self._gerar_nome(),
            idade=random.randint(12, 78),
            papel=papel or random.choice(PAPEL_SOCIAL),
        )

    def retrato(self, perfil: dict, largura: int, altura: int, direcao: str = "baixo") -> pygame.Surface:
        base = self.compor_sprite(perfil, direcao=direcao, tick=0, escala=1)
        bbox = base.get_bounding_rect()
        if bbox.width > 0 and bbox.height > 0:
            base = base.subsurface(bbox).copy()
        alvo_w, alvo_h = max(16, largura), max(16, altura)
        escala = min(alvo_w / max(1, base.get_width()), alvo_h / max(1, base.get_height()))
        novo_w = max(16, int(base.get_width() * escala))
        novo_h = max(16, int(base.get_height() * escala))
        retrato = pygame.Surface((alvo_w, alvo_h), pygame.SRCALPHA)
        sprite = pygame.transform.scale(base, (novo_w, novo_h))
        retrato.blit(sprite, sprite.get_rect(midbottom=(alvo_w // 2, alvo_h - 2)))
        return retrato

    def compor_sprite(self, perfil: dict, direcao: str, tick: int, escala: int = 2, animar: bool = True) -> pygame.Surface:
        indices = CELULAS_DIRECAO.get(direcao, CELULAS_DIRECAO["baixo"])
        indice = indices[(tick // 14) % len(indices)] if animar else indices[1]
        canvas = pygame.Surface((TAMANHO_CELULA_BASE, TAMANHO_CELULA_BASE), pygame.SRCALPHA)

        for camada in ("corpo", "pernas", "camisa", "pes", "cabelo", "cabeca"):
            caminho = perfil.get(camada)
            if not caminho:
                continue
            frame = self._extrair_frame(caminho, indice)
            if camada in {"pernas", "camisa", "pes"}:
                frame = self._aplicar_tinta(frame, tuple(perfil.get("cor_roupa", PALETAS_ROUPA[0])))
            elif camada == "cabelo":
                frame = self._aplicar_tinta(frame, tuple(perfil.get("cor_cabelo", PALETAS_CABELO[0])))
            elif camada == "cabeca":
                frame = self._aplicar_tinta(frame, tuple(perfil.get("cor_cabeca", PALETAS_CABECA[0])))
            canvas.blit(frame, (0, 0))

        if escala <= 1:
            return canvas
        return pygame.transform.scale(canvas, (canvas.get_width() * escala, canvas.get_height() * escala))

    def _gerar_perfil_base(self, nome: str, idade: int, papel: str) -> dict:
        origem = f"{nome} {random.choice(ORIGENS)}"
        return {
            "nome": nome,
            "idade": idade,
            "papel_social": papel,
            "origem": origem,
            "corpo": random.choice(self._catalogo.corpo) if self._catalogo.corpo else "",
            "pes": random.choice(self._catalogo.pes) if self._catalogo.pes else "",
            "pernas": random.choice(self._catalogo.pernas) if self._catalogo.pernas else "",
            "camisa": random.choice(self._catalogo.camisa) if self._catalogo.camisa else "",
            "cabelo": random.choice(self._catalogo.cabelo) if self._catalogo.cabelo else "",
            "cabeca": random.choice(self._catalogo.cabeca) if self._catalogo.cabeca else "",
            "cor_roupa": list(random.choice(PALETAS_ROUPA)),
            "cor_cabelo": list(random.choice(PALETAS_CABELO)),
            "cor_cabeca": list(random.choice(PALETAS_CABECA)),
        }

    def _carregar_catalogo(self) -> CatalogoCamadas:
        def listar(pasta: str) -> list[str]:
            caminho = RAIZ_SPRITES / pasta
            if not caminho.exists():
                return []
            return [str(arquivo) for arquivo in sorted(caminho.glob("*.png"))]

        return CatalogoCamadas(
            corpo=listar(PASTAS_CAMADAS["corpo"]),
            pes=listar(PASTAS_CAMADAS["pes"]),
            pernas=listar(PASTAS_CAMADAS["pernas"]),
            camisa=listar(PASTAS_CAMADAS["camisa"]),
            cabelo=listar(PASTAS_CAMADAS["cabelo"]),
            cabeca=listar(PASTAS_CAMADAS["cabeca"]),
        )

    def _gerar_nome(self) -> str:
        nome = f"{random.choice(NOMES_INICIO)}{random.choice(NOMES_FIM)}"
        if random.random() < 0.7:
            return f"{nome} {random.choice(SOBRENOMES)}"
        return nome

    def _carregar_sheet(self, caminho: str) -> pygame.Surface:
        if caminho not in self._cache_sheets:
            self._cache_sheets[caminho] = pygame.image.load(caminho).convert_alpha()
        return self._cache_sheets[caminho]

    def _extrair_frame(self, caminho: str, indice: int) -> pygame.Surface:
        sheet = self._carregar_sheet(caminho)
        colunas = max(1, sheet.get_width() // TAMANHO_CELULA_BASE)
        x = (indice % colunas) * TAMANHO_CELULA_BASE
        y = (indice // colunas) * TAMANHO_CELULA_BASE
        rect = pygame.Rect(x, y, TAMANHO_CELULA_BASE, TAMANHO_CELULA_BASE)
        return sheet.subsurface(rect).copy()

    def _aplicar_tinta(self, superficie: pygame.Surface, cor: tuple[int, int, int]) -> pygame.Surface:
        copia = superficie.copy()
        mascara = pygame.Surface(copia.get_size(), pygame.SRCALPHA)
        mascara.fill((*cor, 255))
        copia.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return copia


_BANCO_PERSONAGENS: BancoPersonagens | None = None


def obter_banco_personagens() -> BancoPersonagens:
    global _BANCO_PERSONAGENS
    if _BANCO_PERSONAGENS is None:
        _BANCO_PERSONAGENS = BancoPersonagens()
    return _BANCO_PERSONAGENS