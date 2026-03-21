import random
import time

from .config import DIRECOES


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
        self.tamanho = tamanho
        self.humano = [tamanho // 2, tamanho // 2]
        self.nome_humano = config.get("nome_humano", "Escolhido")
        self.origem_humano = config.get("origem_humano", "Um sobrevivente misterioso.")

        self.tiles_comida: set[tuple[int, int]] = set()
        self.tiles_arvore: set[tuple[int, int]] = set()
        self.tiles_casa: set[tuple[int, int]] = set()
        self.tiles_inimigo: set[tuple[int, int]] = set()
        self.animais: dict[tuple[int, int], dict] = {}
        self.tiles_montanha: set[tuple[int, int]] = set()
        self.tiles_agua: set[tuple[int, int]] = set()
        self.tiles_santuario: set[tuple[int, int]] = set()
        self.tiles_vila: set[tuple[int, int]] = set()
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
            "animais_domesticados": 0,
        }
        self.poderes: dict[str, dict] = {}
        self.pet: dict | None = None
        self.ultimo_evento = "mundo inicializado"
        self.moralidade_jogador = 0

        self.gerar_terreno()

    def gerar_terreno(self) -> None:
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
        self.spawn_animais(max(2, int(self.tamanho * 0.14)))
        self.spawn_tiles(self.tiles_santuario, max(1, int(self.tamanho * 0.05)))
        self.spawn_tiles(self.tiles_vila, max(1, int(self.tamanho * 0.03)))

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

    def spawn_animais(self, quantidade_alvo: int) -> None:
        especies = ["coelho", "raposa", "lobo", "capivara", "veado", "gato"]
        personalidades = ["timido", "curioso", "agressivo", "calmo"]
        while len(self.animais) < quantidade_alvo:
            pos = self.posicao_livre_aleatoria()
            if pos in self.animais:
                continue
            self.animais[pos] = {
                "especie": random.choice(especies),
                "personalidade": random.choice(personalidades),
                "domesticado": False,
                "foge": random.random() < 0.55,
                "energia": random.randint(2, 8),
            }

    def mover_humano(self, direcao: str) -> bool:
        dx, dy = DIRECOES.get(direcao, (0, 0))
        nx, ny = self.humano[0] + dx, self.humano[1] + dy
        if not self.eh_caminavel(nx, ny):
            self.ultimo_evento = "bloqueado pelo terreno"
            return False
        self.humano = [nx, ny]
        self.ultimo_evento = f"moveu para {direcao}"

        if (nx, ny) in self.tiles_armadilha:
            self.receber_dano(2, "acionou uma armadilha", tipo="ataque")
            self.tiles_armadilha.discard((nx, ny))

        if (nx, ny) in self.tiles_maldito:
            self.receber_dano(1, "entrou em zona maldita", tipo="maldicao")

        if (nx, ny) in self.tiles_vila:
            self.ultimo_evento = "entrou em uma vila"

        return True

    def expandir_mundo_quando_perto_borda(self, margem: int = 2, bloco: int = 6) -> bool:
        """Expande o mundo dinamicamente em qualquer direção quando o jogador chega perto da borda."""
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
            if self.pet is not None:
                self.pet["x"] += qtd
        elif lado == "cima":
            dx, dy = 0, qtd
            self.humano[1] += qtd
            if self.pet is not None:
                self.pet["y"] += qtd
        elif lado == "direita":
            dx, dy = 0, 0
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
            self.tiles_armadilha = shift_set(self.tiles_armadilha, dx, dy)
            self.tiles_maldito = shift_set(self.tiles_maldito, dx, dy)
            self.tiles_tesouro = shift_dict(self.tiles_tesouro, dx, dy)
            self.animais = shift_animais(self.animais, dx, dy)

        self.tamanho += qtd
        self.spawn_tiles(self.tiles_comida, int(self.tamanho * 0.6))
        self.spawn_tiles(self.tiles_arvore, int(self.tamanho * 0.5))
        self.spawn_tiles(self.tiles_inimigo, int(self.tamanho * 0.15))
        self.spawn_tiles(self.tiles_santuario, max(1, int(self.tamanho * 0.05)))
        self.spawn_tiles(self.tiles_vila, max(1, int(self.tamanho * 0.03)))
        self.spawn_tiles(self.tiles_armadilha, int(self.tamanho * 0.08))
        self.spawn_tiles(self.tiles_maldito, int(self.tamanho * 0.05))
        self.spawn_animais(max(2, int(self.tamanho * 0.14)))

    def atualizar_animais(self) -> None:
        """IA simples de animais com personalidade e fuga."""
        novos: dict[tuple[int, int], dict] = {}
        hx, hy = self.humano

        for (x, y), info in list(self.animais.items()):
            if info.get("domesticado"):
                # Animal domesticado segue de forma suave.
                dx = 1 if hx > x else -1 if hx < x else 0
                dy = 1 if hy > y else -1 if hy < y else 0
                nx, ny = x + dx, y + dy
                if self.eh_caminavel(nx, ny):
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
                # agressivo não foge, aproxima.
                nx += 1 if hx > x else -1 if hx < x else 0
                ny += 1 if hy > y else -1 if hy < y else 0
            else:
                nx += random.choice([-1, 0, 1])
                ny += random.choice([-1, 0, 1])

            if self.eh_caminavel(nx, ny) and (nx, ny) not in novos:
                novos[(nx, ny)] = info
            else:
                novos[(x, y)] = info

        self.animais = novos

    def acariciar_animal(self) -> bool:
        hx, hy = self.humano
        alvos = [((x, y), info) for (x, y), info in self.animais.items() if abs(x - hx) + abs(y - hy) <= 1]
        if not alvos:
            self.ultimo_evento = "nenhum animal para acariciar"
            return False

        (pos, info) = random.choice(alvos)
        chance = 0.75 if info.get("personalidade") in {"calmo", "curioso"} else 0.35
        if random.random() <= chance:
            info["domesticado"] = True
            self.pet = {"x": pos[0], "y": pos[1], "especie": info.get("especie", "animal")}
            self.stats["animais_domesticados"] += 1
            self.ultimo_evento = f"{info.get('especie', 'animal')} virou seu pet"
            self.moralidade_jogador += 2
            return True

        self.ultimo_evento = "o animal recuou e nao confiou em voce"
        return False

    def receber_dano(self, valor: float, motivo: str, tipo: str = "geral") -> bool:
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
            self.ultimo_evento = "nao pode construir aqui"
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
        hx, hy = self.humano
        inimigos = [(abs(ex - hx) + abs(ey - hy), ex, ey) for ex, ey in self.tiles_inimigo if abs(ex - hx) + abs(ey - hy) <= 1]
        if not inimigos:
            self.ultimo_evento = "nenhum inimigo proximo"
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
        animais = [(abs(ax - hx) + abs(ay - hy), ax, ay) for ax, ay in self.animais if abs(ax - hx) + abs(ay - hy) <= 1]
        if not animais:
            self.ultimo_evento = "nenhum animal proximo"
            return False
        _, ax, ay = min(animais)
        self.animais.pop((ax, ay), None)
        self.stats["animais_mortos"] += 1
        self.stats["pontos"] += 5
        self.ultimo_evento = "animal morto"
        self.spawn_animais(max(2, int(self.tamanho * 0.14)))
        self.moralidade_jogador -= 10
        return True

    def descansar(self) -> bool:
        self.hp = min(self.hp_maximo, self.hp + 3)
        self.ultimo_evento = "descansou e se recuperou"
        return True

    def estado(self, tick: int) -> dict:
        return {
            "tick": tick,
            "humano": {"x": self.humano[0], "y": self.humano[1], "nome": self.nome_humano},
            "hp": int(self.hp),
            "hp_maximo": int(self.hp_maximo),
            "inventario": {k: int(v) for k, v in self.inventario.items()},
            "stats": self.stats,
            "moralidade_jogador": self.moralidade_jogador,
            "ultimo_evento": self.ultimo_evento,
            "tamanho_mundo": self.tamanho,
            "quantidade_animais": len(self.animais),
            "quantidade_vilas": len(self.tiles_vila),
        }
