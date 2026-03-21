# Runtime Errors and Attribute Mismatches - Comprehensive Report

## Critical Issues Found

### 1. **sound_manager.py - Line 387: Incorrect Attribute Name**
- **Issue**: Accessing `mundo.hp_max` which does not exist
- **Correct Name**: `mundo.hp_maximo`
- **File**: `jogo/sound_manager.py`
- **Line**: 387
- **Code**: 
  ```python
  if mundo.hp < mundo.hp_max * 0.3:
  ```
- **Fix**: Change to:
  ```python
  if mundo.hp < mundo.hp_maximo * 0.3:
  ```
- **Impact**: Runtime AttributeError if music context determination triggers this condition

---

### 2. **app.py - Lines 820, 827, 838: Non-existent Attribute `tempo_sistema.hora`**
- **Issue**: Attempting to access `tempo_sistema.hora` which does not exist
- **Correct Name**: `tempo_sistema.hora_decimal`
- **File**: `jogo/app.py`
- **Lines**: 
  - Line 820: `'hora': int(tempo_sistema.hora % 24),`
  - Line 827: `hora=int(tempo_sistema.hora % 24)`
  - Line 838: `hora_decimal = tempo_sistema.hora`
- **Class Definition**: `SistemaTempo` in `jogo/modelos.py` has these properties but NOT `.hora`:
  - `hora_decimal` (property) - returns float representing hour of day (0-24)
  - `dia` (property)
  - `fase` (property)
  - `horario_formatado` (property)
- **Fix**: Replace all `tempo_sistema.hora` with `tempo_sistema.hora_decimal`
- **Impact**: Runtime AttributeError when NPC dialogue or fishing mechanics trigger

---

### 3. **app.py - Line 1039: Non-existent Enum Value**
- **Issue**: Using `BiomaMob.PLANICIE` which does not exist
- **Correct Name**: `BiomaMob.PRADARIA`
- **File**: `jogo/app.py`
- **Line**: 1039
- **Code**:
  ```python
  gerenciador_mobs.spawan_mob_random(BiomaMob.PLANICIE, x, y)
  ```
- **Available BiomaMob Values** (from `jogo/mobs.py`):
  - FLORESTA
  - PRADARIA (not PLANICIE)
  - MONTANHA
  - SUBTERRANEO
  - ALAGADO
  - CEMITERIO
  - VULCAO
- **Fix**: Change to:
  ```python
  gerenciador_mobs.spawan_mob_random(BiomaMob.PRADARIA, x, y)
  ```
- **Impact**: Runtime AttributeError when mob spawning is triggered during gameplay

---

### 4. **FILES_INTEGRATION_NOTES.md - Line 80: Documentation Error**
- **Issue**: Documentation example shows wrong attribute name
- **File**: `md/FILES_INTEGRATION_NOTES.md`
- **Line**: 80
- **Code**: 
  ```python
  barra_hp.atualizar(mundo.hp / max(1, mundo.hp_max))
  ```
- **Correct**: Should be:
  ```python
  barra_hp.atualizar(mundo.hp / max(1, mundo.hp_maximo))
  ```
- **Impact**: Code copied from this documentation will fail
- **Note**: This appears to be copy-pasted elsewhere in app.py (line 1163 is correct with `hp_maximo`)

---

## Summary Table

| File | Line(s) | Issue Type | Current | Correct | Severity |
|------|---------|-----------|---------|---------|----------|
| `jogo/sound_manager.py` | 387 | Attribute Name | `mundo.hp_max` | `mundo.hp_maximo` | HIGH |
| `jogo/app.py` | 820, 827, 838 | Attribute Name | `tempo_sistema.hora` | `tempo_sistema.hora_decimal` | HIGH |
| `jogo/app.py` | 1039 | Enum Value | `BiomaMob.PLANICIE` | `BiomaMob.PRADARIA` | HIGH |
| `md/FILES_INTEGRATION_NOTES.md` | 80 | Documentation | `mundo.hp_max` | `mundo.hp_maximo` | MEDIUM |

---

## Verification

### Clase Definitions Reviewed:
- ✓ `Mundo` class in `jogo/modelos.py` - Confirmed: uses `hp_maximo`, not `hp_max`
- ✓ `SistemaTempo` class in `jogo/modelos.py` - Confirmed: has `hora_decimal`, not `hora`
- ✓ `BiomaMob` enum in `jogo/mobs.py` - Confirmed: has PRADARIA, not PLANICIE
- ✓ `Calendario` class in `jogo/calendar.py` - Has `estacao_nome` property ✓
- ✓ `SistemaClima` class in `jogo/weather.py` - Has `clima_atual` attribute ✓
- ✓ World interaction methods verified - All exist properly

---

## Notes on Other Potential Issues

### False Positives (Methods/Attributes That DO Exist):
- `mundo.acao_contextual()` - ✓ Exists in modelos.py:611
- `mundo.obter_npc_proximo()` - ✓ Exists in modelos.py:641
- `mundo.conversar_com_npc()` - ✓ Exists in modelos.py:653
- `mundo.gerar_quest_raphael()` - ✓ Exists in modelos.py:665
- `mundo.atualizar_sociedade()` - ✓ Exists in modelos.py:765
- `mundo.expandir_mundo_quando_perto_borda()` - ✓ Exists in modelos.py:828
- `gerenciador_objetos.obter_objetos_proximo()` - ✓ Exists in world_interactions.py:157
- `gerenciador_ambiance.atualizar_ambiance()` - ✓ Exists in location_ambiance.py:179
- `sistema_backstories.foi_revelada_backstory()` - ✓ Exists in npc_backstory_lazy.py:343
- `sistema_backstories.revelar_backstory_npc()` - ✓ Exists in npc_backstory_lazy.py:316
- `sistema_progresso.registrar_descoberta()` - ✓ Exists in world_interactions.py:303
- `sistema_povoado.gerar_evento()` - ✓ Exists in world_interactions.py:220
- `gerenciador_mobs.spawan_mob_random()` - ✓ Exists in mobs.py:290 (Note: typo in name "spawan" but it's consistent)
- `calendario.estacao_nome` - ✓ Is a property in calendar.py:103
- `clima_sistema.clima_atual` - ✓ Exists as attribute in weather.py

---

## Recommendations

1. **Immediate Actions**: Fix the three high-severity issues in app.py and sound_manager.py
2. **Documentation Update**: Correct the example code in FILES_INTEGRATION_NOTES.md
3. **Testing**: Run game through these code paths to verify fixes:
   - Sound system when HP < 30% max
   - NPC dialogue and fishing mechanics
   - Mob spawning during gameplay
4. **Code Review**: Consider using type hints and linting to catch these issues earlier
