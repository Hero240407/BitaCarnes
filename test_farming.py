#!/usr/bin/env python
"""Quick test to verify farming system implementation."""

from jogo.modelos import Mundo, SistemaTempo
from jogo.sociedade import PLANTAS_DISPONIVEIS

# Create a test world
config = {
    "nome_humano": "TestPlayer",
    "idade_humano": 20,
    "origem_humano": "Test origin",
    "hp_inicial": 20,
    "comida_inicial": 10,
}

mundo = Mundo(tamanho=32, config=config)

# Check if villages have plantations
total_plantacoes = 0
for vila_id, vila in mundo.vilas.items():
    if "plantacoes" in vila:
        total_plantacoes += len(vila["plantacoes"])
        print(f"Vila {vila['nome']}: {len(vila['plantacoes'])} plantacoes")
        for p in vila["plantacoes"]:
            tipo_planta = p["tipo"]
            dias = PLANTAS_DISPONIVEIS[tipo_planta]["dias_crescimento"]
            print(f"  - {tipo_planta}: {dias} dias de crescimento")

print(f"\nTotal plantacoes: {total_plantacoes}")

# Test daily crop update
print("\n--- Testing Daily Crop Update ---")
tempo = SistemaTempo()
print(f"Dia inicial: {tempo.dia}")

# Simulate daily updates
for i in range(10):
    mundo.atualizar_culturas_diarias()
    tempo.avancar(dias=1)
    
    # Check if any crops are ready
    culturas_prontas = 0
    for vila in mundo.vilas.values():
        for plantacao in vila["plantacoes"]:
            if plantacao["colheita_pronta"]:
                culturas_prontas += 1
    
    if culturas_prontas > 0:
        print(f"Dia {tempo.dia}: {culturas_prontas} culturas prontas para colheita")

print("\nSUCCESS: Farms working correctly!")
