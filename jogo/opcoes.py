from __future__ import annotations

import json
from pathlib import Path

import pygame

CONFIG_PATH = Path(__file__).resolve().parent.parent / "saves" / "configuracoes.json"
RESOLUCOES = [
    (1280, 880),
    (1366, 900),
    (1600, 900),
    (1920, 1080),
]

DEFAULT_CONFIG = {
    "resolucao": [1280, 880],
    "monitor_index": 0,
    "fullscreen": False,
    "windowed_fullscreen": False,
    "modo_escuro": False,
    "mostrar_fps": False,
    "volume_master": 80,
    "vibracao_tela": True,
    "dicas_contextuais": True,
}


def carregar_configuracoes() -> dict:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        salvar_configuracoes(dict(DEFAULT_CONFIG))
        return dict(DEFAULT_CONFIG)
    try:
        bruto = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cfg = dict(DEFAULT_CONFIG)
        cfg.update(bruto)
        res = cfg.get("resolucao", [1280, 880])
        if isinstance(res, (list, tuple)) and len(res) == 2:
            cfg["resolucao"] = [int(res[0]), int(res[1])]
        else:
            cfg["resolucao"] = [1280, 880]
        tamanhos = pygame.display.get_desktop_sizes()
        monitor = int(cfg.get("monitor_index", 0))
        if tamanhos:
            monitor = max(0, min(monitor, len(tamanhos) - 1))
        else:
            monitor = 0
        cfg["monitor_index"] = monitor
        cfg["fullscreen"] = bool(cfg.get("fullscreen", False))
        cfg["windowed_fullscreen"] = bool(cfg.get("windowed_fullscreen", False))
        cfg["modo_escuro"] = bool(cfg.get("modo_escuro", False))
        cfg["mostrar_fps"] = bool(cfg.get("mostrar_fps", False))
        cfg["vibracao_tela"] = bool(cfg.get("vibracao_tela", True))
        cfg["dicas_contextuais"] = bool(cfg.get("dicas_contextuais", True))
        cfg["volume_master"] = max(0, min(100, int(cfg.get("volume_master", 80))))
        return cfg
    except (ValueError, TypeError):
        salvar_configuracoes(dict(DEFAULT_CONFIG))
        return dict(DEFAULT_CONFIG)


def salvar_configuracoes(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def resolucao_atual(config: dict) -> tuple[int, int]:
    res = config.get("resolucao", [1280, 880])
    return int(res[0]), int(res[1])


def escolher_display_para_resolucao(resolucao: tuple[int, int]) -> int:
    tamanhos = pygame.display.get_desktop_sizes()
    if not tamanhos:
        return 0

    rw, rh = resolucao
    candidatos: list[tuple[int, int, int]] = []
    for idx, (dw, dh) in enumerate(tamanhos):
        if dw >= rw and dh >= rh:
            sobra = (dw - rw) + (dh - rh)
            area = dw * dh
            candidatos.append((sobra, area, idx))

    if candidatos:
        candidatos.sort(key=lambda x: (x[0], x[1]))
        return candidatos[0][2]

    # Se nenhuma tela comporta a resolucao pedida, escolhe a de area mais proxima.
    alvo_area = rw * rh
    melhor_idx = 0
    melhor_diff = None
    for idx, (dw, dh) in enumerate(tamanhos):
        diff = abs((dw * dh) - alvo_area)
        if melhor_diff is None or diff < melhor_diff:
            melhor_diff = diff
            melhor_idx = idx
    return melhor_idx


def escolher_display_para_config(config: dict, resolucao: tuple[int, int]) -> int:
    tamanhos = pygame.display.get_desktop_sizes()
    if not tamanhos:
        return 0
    monitor = int(config.get("monitor_index", 0))
    if 0 <= monitor < len(tamanhos):
        return monitor
    return escolher_display_para_resolucao(resolucao)
