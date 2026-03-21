from __future__ import annotations

from pathlib import Path

import pygame

RAIZ_SPRITES = Path(__file__).resolve().parent.parent / "sprites"


class GerenciadorAssets:
    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface] = {}
        self._ui_root = RAIZ_SPRITES / "kenney_ui-pack-rpg-expansion" / "PNG"

    def imagem(self, nome: str) -> pygame.Surface:
        chave = str(self._ui_root / nome)
        if chave not in self._cache:
            self._cache[chave] = pygame.image.load(chave).convert_alpha()
        return self._cache[chave]

    def painel(self, destino: pygame.Surface, rect: pygame.Rect, estilo: str = "beige", inset: bool = False, alpha: int = 255) -> None:
        prefixo = "panelInset" if inset else "panel"
        sprite = self.imagem(f"{prefixo}_{estilo}.png")
        superficie = pygame.transform.scale(sprite, (rect.width, rect.height))
        if alpha != 255:
            superficie = superficie.copy()
            superficie.set_alpha(alpha)
        destino.blit(superficie, rect)

    def botao(self, destino: pygame.Surface, rect: pygame.Rect, fonte: pygame.font.Font, texto: str, ativo: bool = False) -> None:
        nome = "buttonLong_brown_pressed.png" if ativo else "buttonLong_brown.png"
        sprite = pygame.transform.scale(self.imagem(nome), (rect.width, rect.height))
        destino.blit(sprite, rect)
        sombra = fonte.render(texto, True, (64, 40, 28))
        rotulo = fonte.render(texto, True, (246, 234, 206))
        sombra_rect = sombra.get_rect(center=(rect.centerx + 1, rect.centery + 2))
        rotulo_rect = rotulo.get_rect(center=(rect.centerx, rect.centery + 1))
        destino.blit(sombra, sombra_rect)
        destino.blit(rotulo, rotulo_rect)

    def icone(self, nome: str, tamanho: tuple[int, int]) -> pygame.Surface:
        return pygame.transform.scale(self.imagem(nome), tamanho)


_GERENCIADOR: GerenciadorAssets | None = None


def obter_assets() -> GerenciadorAssets:
    global _GERENCIADOR
    if _GERENCIADOR is None:
        _GERENCIADOR = GerenciadorAssets()
    return _GERENCIADOR