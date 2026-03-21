# F1 Help Menu - Complete Update

## What's Now in the Help Tab (Press F1)

The help menu has been completely updated to include all game features, new commands, and how to play. When you press **F1** during gameplay, you'll see a comprehensive guide.

---

## Help Menu Sections

### 1. **MOVIMENTO E ACOES** (Movement and Actions)

Basic movement controls:
```
[W/Seta Cima]    Mover para cima          [D/Seta Dir]      Mover para direita
[A/Seta Esq]     Mover para esquerda      [S/Seta Baixo]    Mover para baixo
```

Interactive actions:
```
[G]              Coletar recurso           [B]               Construir casa
[E]              Escavar tesouro           [SPACE]           Atacar inimigo
[C]              Matar animal              [Z]               Descansar
[T]              Acariciar animal          [F]               Acao contextual
```

### 2. **MENU E NPCs** (Menu and NPC Interaction)

```
[Y]              Conversar com NPC         [F1]              Abrir ajuda
[I]              Abrir inventario          [F2]              Ver lore
[R]              Falar com Raphael         [F5]              Salvar jogo
[ESC]            Menu de pausa             [F6]              Salvar como novo
[1-9]            Usar poderes
```

### 3. **COMANDOS DE CHAT** (Chat Commands - Press R)

NEW! All the AI-powered quest and history features:

```
!quest / !missao        → Gera uma quest contextualizada ao seu personagem
!profecia               → Gera quest sobre a profecia do mundo
!conflito               → Gera quest envolvendo o conflito principal
!history / !historico   → Mostra suas estatisticas de acoes
!stats                  → Resumo estatistico do gameplay
!recent / !recentes     → Mostra suas ultimas 15 acoes com posicao
```

### 4. **DICAS** (Tips)

Helpful tips about the game:
- **DICA:** Use chat commands (R) para gerar quests personalizadas ao seu mundo e personagem!
- **DICA:** Seus quests sao contextualizados a sua origem, legado, motivacao e segredo.
- **DICA:** Pressione F2 para ver a lore detalhada do mundo e seu destino.

---

## How to Access the Help Menu

**In-Game:** Press **F1** at any time (except during input)

**What Happens:**
1. Game pauses
2. Comprehensive help panel appears
3. Shows all controls, commands, and tips
4. Press **ESC** to close and resume

---

## What's New in This Update

### New Keyboard Controls (Now Documented)
- **G** - Collect resources
- **E** - Dig for treasure
- **B** - Build house
- **SPACE** - Attack enemies
- **C** - Kill animal
- **T** - Pet/interact with animals
- **Z** - Rest/sleep

### New Chat Commands (Now Documented)
- **!quest** - Get AI-generated contextual quests
- **!profecia** - Quests about world prophecy
- **!conflito** - Quests about world conflicts
- **!history** - View your action statistics
- **!stats** - Statistical summary
- **!recent** - See your last 15 actions

### New Section: Chat Commands
Added dedicated section explaining all the new AI quest generation commands with descriptions of what each does.

### New Section: Tips
Added helpful reminders about:
- How to use chat commands for quests
- How quests are personalized to your character
- How to view detailed world lore

---

## Help Menu Layout

The help menu is organized into clear sections:

1. **Title:** "AJUDA - Controles, Comandos e Como Jogar"
   - Updated to reflect all features

2. **Layout:**
   - Movement & Actions (organized in columns)
   - Menu & NPC Keys (organized in columns)  
   - Chat Commands (full-width descriptions)
   - Tips & Reminders

3. **Colors:**
   - Keys: Orange ([W], [G], etc.)
   - Descriptions: Brown
   - Section Titles: Darker brown
   - Tips: Brown text with larger font

4. **Footer:**
   - "ESC para fechar | Sua jornada sera guiada pelo conhecimento"

---

## Examples of What Players Will See

### Movement Section Example
```
[W/Seta Cima]    Mover para cima        [D/Seta Dir]     Mover para direita
[A/Seta Esq]     Mover para esquerda    [S/Seta Baixo]   Mover para baixo
```

### Chat Commands Section Example
```
!quest / !missao        Gera uma quest contextualizada ao seu personagem
!profecia               Gera quest sobre a profecia do mundo
!conflito               Gera quest envolvendo o conflito principal
!history / !historico   Mostra suas estatisticas de acoes
!stats                  Resumo estatistico do gameplay
!recent / !recentes     Mostra suas ultimas 15 acoes com posicao
```

### Tips Example
```
DICA: Use chat commands (R) para gerar quests personalizadas ao seu mundo e personagem!
DICA: Seus quests sao contextualizados a sua origem, legado, motivacao e segredo.
DICA: Pressione F2 para ver a lore detalhada do mundo e seu destino.
```

---

## File Location & Implementation

**File Modified:** `jogo/ui.py`  
**Function:** `renderizar_menu_ajuda(tela: pygame.Surface)`  
**Line:** ~179

The function now:
1. Creates organized sections for different control types
2. Uses 2-column layout for better space usage
3. Includes full-width chat commands section
4. Adds helpful tips at the bottom
5. Properly sizes all text with existing fonts

---

## No Errors

✓ All code verified - no syntax errors
✓ Uses existing fonts from the game
✓ Layout automatically adjusts to screen resolution
✓ Compatible with existing help menu system

---

## Summary

Your F1 help menu is now **complete and comprehensive**. Players can press F1 at any time to see:

✅ All movement controls (W/A/S/D + arrow keys)
✅ All action keys (G, E, B, SPACE, C, T, Z, F, Y)
✅ All menu keys (I, R, F1, F2, F5, F6, ESC)
✅ All chat commands (!quest, !profecia, !conflito, !history, !stats, !recent)
✅ Helpful tips about the system
✅ Clear organization and descriptions

**Players no longer need external documentation** — everything is available in-game through the help menu! 🎮
