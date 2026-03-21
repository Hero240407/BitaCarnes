"""
Sistema de registro de ações do jogador usando SQLite.
Mantém histórico completo de ações do jogador de forma eficiente.
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class ActionLogger:
    """Logger de ações do jogador usando banco de dados SQLite."""
    
    def __init__(self, db_path: Path | str):
        """
        Inicializa o logger de ações.
        
        Args:
            db_path: Caminho para o arquivo .db
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Inicializa o banco de dados com as tabelas necessárias."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela principal de ações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    action_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    player_x INTEGER,
                    player_y INTEGER,
                    player_hp REAL,
                    player_food INTEGER,
                    player_morale INTEGER,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Índices para queries rápidas
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_type ON player_actions(action_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tick ON player_actions(tick)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON player_actions(timestamp)')
            
            # Tabela de sessão/metadados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start REAL NOT NULL,
                    session_end REAL,
                    total_actions INTEGER DEFAULT 0,
                    game_version TEXT,
                    player_name TEXT,
                    world_seed INTEGER
                )
            ''')
            
            # Tabela de resumo diário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    in_game_day INTEGER NOT NULL,
                    actions_count INTEGER DEFAULT 0,
                    distance_traveled INTEGER DEFAULT 0,
                    food_consumed INTEGER DEFAULT 0,
                    enemies_defeated INTEGER DEFAULT 0,
                    items_collected INTEGER DEFAULT 0,
                    houses_built INTEGER DEFAULT 0,
                    morale_change INTEGER DEFAULT 0,
                    UNIQUE(in_game_day)
                )
            ''')
            
            conn.commit()
    
    def log_action(
        self,
        tick: int,
        timestamp: float,
        action_type: str,
        description: str,
        player_x: Optional[int] = None,
        player_y: Optional[int] = None,
        player_hp: Optional[float] = None,
        player_food: Optional[int] = None,
        player_morale: Optional[int] = None,
        details: Optional[str | Dict[str, Any]] = None,
    ) -> None:
        """
        Registra uma ação do jogador.
        
        Args:
            tick: Número do tick do jogo
            timestamp: Timestamp da ação
            action_type: Tipo de ação (move, attack, collect, etc.)
            description: Descrição legível da ação
            player_x: Posição X do jogador
            player_y: Posição Y do jogador
            player_hp: HP atual do jogador
            player_food: Comida atual do jogador
            player_morale: Moralidade atual do jogador
            details: Detalhes adicionais (dict ou string)
        """
        if isinstance(details, dict):
            import json
            details = json.dumps(details, ensure_ascii=False)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO player_actions 
                (tick, timestamp, action_type, description, player_x, player_y, 
                 player_hp, player_food, player_morale, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tick, timestamp, action_type, description, player_x, player_y,
                player_hp, player_food, player_morale, details
            ))
            conn.commit()
    
    def get_all_actions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna todas as ações registradas.
        
        Args:
            limit: Número máximo de ações a retornar (None para todas)
            
        Returns:
            Lista de dicionários com as ações
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM player_actions ORDER BY tick ASC'
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_actions_by_type(self, action_type: str) -> List[Dict[str, Any]]:
        """
        Retorna ações de um tipo específico.
        
        Args:
            action_type: Tipo de ação a filtrar
            
        Returns:
            Lista de ações do tipo especificado
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM player_actions WHERE action_type = ? ORDER BY tick ASC',
                (action_type,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_actions_in_range(self, start_tick: int, end_tick: int) -> List[Dict[str, Any]]:
        """
        Retorna ações dentro de um intervalo de ticks.
        
        Args:
            start_tick: Tick inicial
            end_tick: Tick final
            
        Returns:
            Lista de ações no intervalo
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM player_actions WHERE tick BETWEEN ? AND ? ORDER BY tick ASC',
                (start_tick, end_tick)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_actions(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna as ações mais recentes.
        
        Args:
            count: Número de ações a retornar
            
        Returns:
            Lista das últimas N ações
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM player_actions ORDER BY tick DESC LIMIT ?',
                (count,)
            )
            return list(reversed([dict(row) for row in cursor.fetchall()]))
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais das ações.
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de ações
            cursor.execute('SELECT COUNT(*) as count FROM player_actions')
            total_actions = cursor.fetchone()[0]
            
            # Ações por tipo
            cursor.execute('''
                SELECT action_type, COUNT(*) as count 
                FROM player_actions 
                GROUP BY action_type 
                ORDER BY count DESC
            ''')
            actions_by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Distância viajada (aproximada)
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM player_actions 
                WHERE action_type IN ('move_up', 'move_down', 'move_left', 'move_right')
            ''')
            distance = cursor.fetchone()[0]
            
            # HP mínimo registrado
            cursor.execute('SELECT MIN(player_hp) FROM player_actions WHERE player_hp IS NOT NULL')
            min_hp = cursor.fetchone()[0]
            
            # Moralidade máxima e mínima
            cursor.execute('SELECT MAX(player_morale), MIN(player_morale) FROM player_actions WHERE player_morale IS NOT NULL')
            max_morale, min_morale = cursor.fetchone()
            
            return {
                'total_actions': total_actions,
                'actions_by_type': actions_by_type,
                'distance_traveled': distance,
                'min_hp_reached': min_hp,
                'max_morale': max_morale,
                'min_morale': min_morale,
            }
    
    def export_to_json(self, filepath: Path | str) -> None:
        """
        Exporta todas as ações para um arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo JSON de saída
        """
        import json
        
        all_actions = self.get_all_actions()
        stats = self.get_action_statistics()
        
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_actions': len(all_actions),
                'statistics': stats,
            },
            'actions': all_actions,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
    
    def clear_actions(self) -> None:
        """Limpa todas as ações registradas (use com cuidado!)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM player_actions')
            conn.commit()
    
    def get_total_action_count(self) -> int:
        """Retorna o número total de ações registradas."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM player_actions')
            return cursor.fetchone()[0]
    
    def update_daily_summary(
        self,
        in_game_day: int,
        actions_count: int,
        distance_traveled: int = 0,
        food_consumed: int = 0,
        enemies_defeated: int = 0,
        items_collected: int = 0,
        houses_built: int = 0,
        morale_change: int = 0,
    ) -> None:
        """
        Atualiza o resumo diário.
        
        Args:
            in_game_day: Dia do jogo
            actions_count: Número de ações neste dia
            distance_traveled: Distância viajada
            food_consumed: Comida consumida
            enemies_defeated: Inimigos derrotados
            items_collected: Itens coletados
            houses_built: Casas construídas
            morale_change: Mudança na moralidade
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO daily_summary
                (in_game_day, actions_count, distance_traveled, food_consumed,
                 enemies_defeated, items_collected, houses_built, morale_change)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                in_game_day, actions_count, distance_traveled, food_consumed,
                enemies_defeated, items_collected, houses_built, morale_change
            ))
            conn.commit()
    
    def get_daily_summary(self, in_game_day: int) -> Optional[Dict[str, Any]]:
        """
        Retorna o resumo de um dia específico.
        
        Args:
            in_game_day: Dia do jogo
            
        Returns:
            Dicionário com o resumo do dia ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_summary WHERE in_game_day = ?',
                (in_game_day,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados (geralmente não é necessário)."""
        # SQLite conexão é gerenciada automaticamente
        pass
