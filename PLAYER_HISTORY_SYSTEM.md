# Player Action History System

## Overview

A SQLite-based action logging system that tracks all player actions, decisions, and game state throughout gameplay. This replaces the JSON-based approach with a fast, queryable database optimized for performance and efficient history access.

## Key Features

### 1. **Fast Database Storage**
- SQLite database instead of JSON files
- Indexed queries for lightning-fast lookups
- Located at: `saves/{save_name}/player_history.db`
- Loads only the necessary data when needed

### 2. **Complete Action Tracking**
Every player action is recorded with:
- **Action Type**: `move_up`, `collect`, `attack`, `build_house`, `dig`, `kill_animal`, `pet_animal`, `rest`, `contextual_action`, `talk_npc`
- **Player State**: HP, Food, Morale
- **Location**: X, Y coordinates
- **Timestamp**: When the action occurred
- **Game Tick**: Frame reference
- **Details**: Additional context about each action

### 3. **Action Types Logged**
- **W/A/S/D**: Move up/left/down/right
- **G**: Collect resources
- **E**: Dig for treasure
- **B**: Build house
- **SPACE**: Attack enemy
- **C**: Kill animal
- **T**: Pet/interact with animal
- **Z**: Rest/sleep
- **F**: Contextual action (talking, interacting)
- **Y**: Talk to NPC

### 4. **Three Data Tables**

#### `player_actions` (Main Table)
```sql
- id: Unique action ID
- tick: Game tick when action occurred
- timestamp: Unix timestamp
- action_type: Type of action
- description: Human-readable description
- player_x, player_y: Player position
- player_hp: Current HP
- player_food: Current food
- player_morale: Current morale
- details: JSON-encoded additional info
- created_at: Insertion timestamp
```

#### `session_metadata`
- Tracks game session information
- Session start/end times
- Total actions in session
- Game version, player name, world seed

#### `daily_summary`
- Aggregates stats by in-game day
- Distance traveled per day
- Items collected, enemies defeated
- Houses built, morale changes

## Usage

### In Game

#### View Statistics
Type in chat (press R to talk to Raphael):

```
!history        - Show complete action statistics
!historico      - Portuguese version of history
!stats          - Show action statistics
!estatisticas   - Portuguese version of stats
!recent         - Show last 15 actions
!recentes       - Portuguese version of recent
```

### Programmatic Access

```python
from jogo.action_logger import ActionLogger

# Initialize logger
logger = ActionLogger("path/to/player_history.db")

# Log an action
logger.log_action(
    tick=100,
    timestamp=time.time(),
    action_type="move_up",
    description="Jogador moveu para cima",
    player_x=10,
    player_y=20,
    player_hp=85.5,
    player_food=50,
    player_morale=10
)

# Retrieve actions
all_actions = logger.get_all_actions()
recent = logger.get_recent_actions(count=50)
attacks = logger.get_actions_by_type("attack")
actions_range = logger.get_actions_in_range(start_tick=100, end_tick=200)

# Get statistics
stats = logger.get_action_statistics()
print(f"Total actions: {stats['total_actions']}")
print(f"Distance traveled: {stats['distance_traveled']}")
print(f"Min HP reached: {stats['min_hp_reached']}")

# Export to JSON
logger.export_to_json("export.json")

# Daily summary
logger.update_daily_summary(
    in_game_day=1,
    actions_count=150,
    distance_traveled=45,
    items_collected=12,
    enemies_defeated=3,
    morale_change=5
)

summary = logger.get_daily_summary(in_game_day=1)
```

## Save Structure

```
saves/
├── my_save_1/
│   ├── player_history.db          ← New action history database
│   ├── meta.json
│   ├── mundo.json
│   ├── tiles.json
│   ├── sociedade.json
│   ├── lore_quests.json
│   └── memoria_raphael.json
```

## Performance Benefits

| Feature | JSON | SQLite |
|---------|------|--------|
| Parsing Large History | Slow (O(n)) | Fast (O(log n) with index) |
| Filter by Type | Full scan | Indexed lookup |
| Recent Actions | Parse all, then slice | Direct LIMIT query |
| File Size | Large (text) | Compact (binary) |
| Concurrent Updates | Risky | Safe (transactional) |

## Automatic Operation

- Database is **automatically created** when a new game starts
- Actions are **logged in real-time** during gameplay
- Database is **saved with the game** (in save directory)
- Each save has its **own database** (independent history)
- Loading old saves will create a fresh database

## Technical Details

### Indexing Strategy
- `idx_action_type`: Fast filtering by action type
- `idx_tick`: Range queries by game tick
- `idx_timestamp`: Time-based filtering

### Threading Safety
- SQLite handles concurrent writes safely
- Single connection per game session
- Automatic transaction management

### Database Size
- Typical history: ~2-5 MB per 10,000 actions
- Far more compact than JSON serialization
- Structured queries prevent data duplication

## Future Enhancements

Possible additions:
- Player statistics dashboard in UI
- Heat maps of player movement
- Action replay/playback system
- Automated analysis (behavior patterns, play style detection)
- Achievement tracking based on action history
- Social sharing of action statistics

## Commands Summary

```
Game Chat Commands (Press R):
├── !history / !historico    → Full action statistics
├── !stats / !estatisticas   → Statistics summary
├── !recent / !recentes       → Last 15 actions
└── Other Raphael commands available as normal
```

## Debugging

To view database directly:

```bash
sqlite3 saves/my_save_1/player_history.db
sqlite> SELECT COUNT(*) FROM player_actions;
sqlite> SELECT action_type, COUNT(*) FROM player_actions GROUP BY action_type;
sqlite> SELECT * FROM player_actions LIMIT 10;
```

## Notes

- Database is created fresh for new games
- Old saves with JSON history remain unchanged
- New action logging starts immediately upon game load
- History is separate from game state (no game load slowdown)
- Multiple saves don't interfere with each other
