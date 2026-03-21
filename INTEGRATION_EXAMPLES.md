# 💻 INTEGRATION_EXAMPLES.md - Exemplos de Integração

## Como Integrar os Novos Sistemas com Suas Ações

Este arquivo mostra exemplos práticos de como os novos sistemas Stardew Valley se conectam com as ações do jogador.

---

## 🌾 Integração de Agricultura

### Quando o Jogador Coleta com `G`

```python
# Em app.py ou servicos.py:
elif evento.key == pygame.K_g:
    mundo.coletar()
    
    # NOVO: Também atualiza farm se em área de cultivo
    if farm_manager.obter_celula(mundo.humano[0], mundo.humano[1]).planta_atual:
        sucesso, info = farm_manager.colher(
            mundo.humano[0], 
            mundo.humano[1],
            PLANTAS_DISPONIVEIS
        )
        if sucesso:
            mundo.comida += info['quantidade']
            farm_manager.dinheiro += info['valor']
            historico_chat.append(f"Colheu {info['tipo']}: +{info['quantidade']} comida")
```

### Quando o Jogador Descansa com `Z`

```python
# Descansar também avança o dia
elif evento.key == pygame.K_z:
    mundo.descansar()
    
    # Avanço do calendário
    eventos_calendario = calendario.avancar_dia()
    clima_tipo, msg_clima = clima_sistema.avancar_dia(calendario.estacao.value)
    
    farm_manager.avancar_dia()
    relacao_gerenciador.avancar_dia()
    quest_manager.avancar_dia()
    
    historico_chat.append(msg_clima)
```

---

## 💬 Integração de NPCs

### Quando o Jogador Fala com `Y`

```python
elif evento.key == pygame.K_y:
    # Encontra NPC próximo
    npc_proximo = mundo.obter_npc_proximo()
    
    if npc_proximo:
        npc_id = npc_proximo['id']
        
        # Registrar se não existe
        if npc_id not in relacao_gerenciador.relacoes:
            relacao_gerenciador.registrar_npc(npc_id, npc_proximo['nome'])
        
        # Conversar e aumentar corações
        sucesso, msg = relacao_gerenciador.conversar_npc(npc_id, "casual")
        
        # Gerar diálogo por IA
        if sucesso:
            dialogo_ia = raphael.gerar_dialogo_npc(
                npc_proximo['perfil'],
                relacao_gerenciador.obter_relacao(npc_id).sentimento
            )
            historico_chat.append(f"{npc_proximo['nome']}: {dialogo_ia}")
```

### Quando Dá Presente

```python
# Sistema de presentes
def dar_presente_npc(npc_id, tipo_presente, afinidade):
    sucesso, msg = relacao_gerenciador.dar_presente(npc_id, tipo_presente, afinidade)
    
    if sucesso:
        # Aumenta felicidade do NPC
        relacao = relacao_gerenciador.obter_relacao(npc_id)
        
        if afinidade >= 2:
            historico_chat.append(f"✨ {relacao.npc_nome} adorou!")
        elif afinidade >= 1:
            historico_chat.append(f"😊 {relacao.npc_nome} gostou.")
        else:
            historico_chat.append(f"😐 {relacao.npc_nome} achou ok.")
        
        # Registrar no histórico
        memoria.adicionar_evento(f"Deu presente a {relacao.npc_nome}")
```

---

## 📅 Integração de Calendário

### Eventos de Festival

```python
# Diariamente:
eventos_calendario = calendario.avancar_dia()

if eventos_calendario['festival']:
    festival = eventos_calendario['festival']
    
    historico_chat.append(f"🎉 {festival.nome} - {festival.descricao}")
    
    # NPCs vão para o festival
    # Chance de aumentar relacionamentos
    for npc_id in relacao_gerenciador.relacoes:
        if random.random() < 0.7:  # 70% aparecem no festival
            relacao = relacao_gerenciador.obter_relacao(npc_id)
            relacao.adicionar_coracao(1)
            historico_chat.append(f"Viu {relacao.npc_nome} no festival!")
    
    # Prêmios do festival
    mundo.dinheiro += festival.premios.get('ouro', 0)
    memoria.adicionar_evento(f"Participou do {festival.nome}")
```

### Plantas Plantáveis Variam

```python
def obter_plantas_disponibles_agora():
    estacao_atual = calendario.estacao.value
    plantas = calendario.obter_plantas_plantaveis()
    
    return [
        PLANTAS_DISPONIVEIS[p] for p in plantas 
        if p in PLANTAS_DISPONIVEIS
    ]

# Quando jogador planta:
plantas_ok = obter_plantas_disponibles_agora()
if tipo_planta not in [p['nome'] for p in plantas_ok]:
    historico_chat.append(f"Não pode plantar {tipo_planta} nesta estação!")
    return False
```

---

## 🎯 Integração de Quests

### Dinâmica de Quest Automática

```python
# Quando jogador coleta item:
if mundo.obter_item():
    # Verificar quests ativas
    for quest_id in quest_manager.quests_ativas:
        quest = quest_manager.obter_quest(quest_id)
        
        if quest.tipo == TipoQuest.COLETA and quest.objetivo_quantidade > 0:
            quest.avancar_progresso(1)
            
            if quest.status == StatusQuest.COMPLETA:
                sucesso, recompensa = quest_manager.completar_quest(quest_id)
                if sucesso:
                    mundo.dinheiro += recompensa.ouro
                    mundo.exp += recompensa.exp
                    historico_chat.append(f"✅ Quest completa: {quest.nome}!")
```

### Gerar Quest Aleatória

```python
# A cada novo dia, pode oferecer quest aleatória
if random.random() < 0.3:  # 30% de chance diária
    nova_quest = quest_manager.gerar_quest_randomica()
    quest_manager.registrar_quest(nova_quest)
    historico_chat.append(f"Nova missão disponível: {nova_quest.nome}")
```

---

## 🎣 Integração de Pesca

### Quando Jogador Vai Pescar

```python
# Criar hotkey para pesca (ex: P)
elif evento.key == pygame.K_p:
    posicao = mundo.humano
    
    # Verificar se próximo de água
    if mundo.obter_tipo_celula(posicao) == "agua":
        # Iniciar minigame
        if pesca_manager.iniciar_pesca("rio", tempo_sistema.hora_decimal, calendario.estacao.value):
            sucesso, msg = pesca_manager.tentar_pescagem(5)
            
            if sucesso:
                historico_chat.append(f"🎣 {msg}")
                mundo.dinheiro += pesca_manager.ganho_ouro
                mundo.exp += pesca_manager.ganho_exp
                
                # Registrar captura
                historico_pesca.registrar_captura(
                    pesca_manager.peixe_capturado_nome,
                    pesca_manager.ganho_ouro
                )
            else:
                historico_chat.append(f"🎣 {msg}")
        else:
            historico_chat.append("Nada está mordendo no momento...")
    else:
        historico_chat.append("Precisa estar próximo da água para pescar!")
```

---

## 🌤️ Integração de Clima

### Clima Afeta Ações

```python
# Quando tenta colher em clima ruim
def tentar_colher():
    efeitos_clima = clima_sistema.afeta_agricultura()
    
    if not efeitos_clima["pode_colher"]:
        historico_chat.append("Clima muito ruim para colher hoje!")
        return False
    
    # Normal
    mundo.coletar()
    return True

# Quando tenta pescar
def tentar_pescar():
    efeitos_clima = clima_sistema.afeta_pesca()
    
    taxa_acelerada = efeitos_clima["taxa_acelerada"]
    raros_aumentado = efeitos_clima["peixes_raros_aumentado"]
    
    # Aplicar efeitos...
    tempo_pesca = 5 / taxa_acelerada
    
    if raros_aumentado:
        historico_chat.append("Ótimo dia para pescar raros!")
```

### Clima Afeta NPCs

```python
# Atualizar comportamento de NPCs
efeitos_npc = clima_sistema.afeta_npcs()

if efeitos_npc["npcs_dentro_casa"]:
    # NPCs em casa durante tempestade
    for npc_id, npc in mundo.npcs.items():
        npc.dentro_casa = True
        
if efeitos_npc["mood_ajuste"] != 0:
    # Ajustar humor de todos
    for npc_id in relacao_gerenciador.relacoes:
        rel = relacao_gerenciador.obter_relacao(npc_id)
        rel.adicionar_coracao(efeitos_npc["mood_ajuste"] * 0.5)
```

---

## 🎨 Integração de UI

### Mostrar Painéis Aprimorados

```python
# No final da renderização, antes do pygame.display.flip()
modo_info_expandida = True  # Toggle com tecla (ex: TAB)

if modo_info_expandida:
    rect_hud = pygame.Rect(
        tela.get_width() - 400,
        ALTURA_CHAT,
        400,
        tela.get_height() - ALTURA_CHAT - ALTURA_HUD
    )
    
    renderizar_hud_expandida(
        tela,
        calendario,
        clima_sistema,
        farm_manager,
        relacao_gerenciador,
        quest_manager,
        rect_hud
    )
```

---

## 🔄 Fluxo Completo de Um Dia

```python
def avancar_dia_completo():
    """Simula um dia completo com todos os sistemas"""
    
    print(f"\n=== {calendario.data_formatada} ===")
    
    # 1. Calendário
    eventos = calendario.avancar_dia()
    print(f"📅 {calendario.estacao_nome} - Dia {calendario.dia_mes}")
    
    # 2. Clima
    clima_tipo, msg = clima_sistema.avancar_dia(calendario.estacao.value)
    print(f"🌤️ {msg}")
    
    # 3. Agricultura
    farm_manager.avancar_dia()
    print(f"🌾 Plantas crescem um dia")
    
    # 4. Relacionamentos
    relacao_gerenciador.avancar_dia()
    print(f"💝 Relacionamentos verificados")
    
    # 5. Quests
    quest_manager.avancar_dia()
    print(f"📋 Quests verificadas")
    
    # 6. Festival?
    if eventos['festival']:
        print(f"🎉 FESTIVAL: {eventos['festival'].nome}!")
    
    # 7. Eventos críticos
    if random.random() < 0.05:  # 5% de evento especial
        evento_especial = gerar_evento_randomico()
        print(f"⚡ Evento especial: {evento_especial}")
    
    print(f"\n💰 Dinheiro: {farm_manager.dinheiro}")
    print(f"❤️ Melhores relacionamentos: {obter_top_relacionamentos(3)}")
    print(f"📋 Quests ativas: {len(quest_manager.obter_quests_ativas())}")
```

---

## 🛠️ Checklist de Integração

- [ ] Importar todos os módulos em `app.py`
- [ ] Inicializar sistemas com `farm_manager = FarmManager()`
- [ ] Atualizar sistemas diariamente
- [ ] Conectar ações do jogador aos sistemas
- [ ] Mostrar feedback no chat/UI
- [ ] Salvar estado dos sistemas em save files
- [ ] Estressar teste com Raphael gerando conteúdo
- [ ] Balancear dificuldade (níveis de XP, preços, etc)

---

## 📊 Dados para Persistência

Certifique-se de salvar/carregar:

```python
save_data = {
    # Farm
    'farm': {
        'dinheiro': farm_manager.dinheiro,
        'nivel': farm_manager.nivel_agricultura,
        'exp': farm_manager.exp_agricultura,
        'celulas': farm_manager.celulas_cultivo,
        'sementes': farm_manager.sementes_inventario,
    },
    
    # Relacionamentos
    'relacoes': {
        npc_id: {
            'coracao': rel.coracao,
            'casado': relacao_gerenciador.casado_com == npc_id,
            'filhos': len(relacao_gerenciador.filhos),
        }
        for npc_id, rel in relacao_gerenciador.relacoes.items()
    },
    
    # Calendário
    'calendario': {
        'ano': calendario.ano,
        'estacao': calendario.estacao.value,
        'dia': calendario.dia_mes,
    },
    
    # Quests
    'quests': {
        qid: {
            'status': q.status.value,
            'progresso': q.quantidade_completa,
        }
        for qid, q in quest_manager.quests.items()
    },
    
    # Pesca
    'pesca': {
        'historico': historico_pesca.peixes_capturados,
        'ganho_total': historico_pesca.total_ouro_ganho,
    }
}
```

---

**Aproveite sua integração! 🚀**
