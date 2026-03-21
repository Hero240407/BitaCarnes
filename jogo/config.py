from pathlib import Path

import pygame

OBJETIVO_PATH = Path(__file__).resolve().parent.parent / "objectives.json"
SAVE_DIR = Path(__file__).resolve().parent.parent / "saves"
OLLAMA_URL = "http://localhost:11434/api/generate"
NOME_MODELO = "llama3"
NOME_MODELO_PESADO = "llama3"
NOME_MODELO_BASE = "qwen2.5:1.5b-base"
NOME_MODELO_EMBED = "nomic-embed-text"

DIRECOES = {
    "cima": (0, -1),
    "baixo": (0, 1),
    "esquerda": (-1, 0),
    "direita": (1, 0),
}

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
ALTURA_CHAT = 220
LARGURA_TELA = 1280
ALTURA_TELA = 880

TECLAS_RESERVADAS = {
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
    pygame.K_i,
    pygame.K_z,
    pygame.K_f,
    pygame.K_y,
    pygame.K_r,
    pygame.K_F5,
    pygame.K_ESCAPE,
    pygame.K_RETURN,
    pygame.K_UP,
    pygame.K_DOWN,
}

TECLAS_PODER_CANDIDATAS = [
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
    pygame.K_6,
    pygame.K_7,
    pygame.K_8,
    pygame.K_9,
    pygame.K_0,
    pygame.K_F3,
    pygame.K_F4,
    pygame.K_F6,
    pygame.K_F7,
    pygame.K_F8,
    pygame.K_F9,
    pygame.K_F10,
    pygame.K_F11,
    pygame.K_F12,
]

# Letras disponiveis para poderes quando inventario esta baixo (0-1 itens)
# Exclui letras reservadas: w, a, s, d, g, e, b, c, t, i, z, f, y, r
TECLAS_PODER_LETRAS = [
    pygame.K_h,
    pygame.K_j,
    pygame.K_k,
    pygame.K_l,
    pygame.K_m,
    pygame.K_n,
    pygame.K_o,
    pygame.K_p,
    pygame.K_q,
    pygame.K_u,
    pygame.K_v,
    pygame.K_x,
]
