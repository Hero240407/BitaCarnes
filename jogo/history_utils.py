"""
Utilities for displaying and analyzing player action history.
"""

from .action_logger import ActionLogger


def format_action_statistics(logger: ActionLogger) -> str:
    """
    Formats action statistics into a readable string.
    
    Args:
        logger: ActionLogger instance
        
    Returns:
        Formatted string with statistics
    """
    stats = logger.get_action_statistics()
    
    lines = [
        "=== HISTORICO DE ACOES DO JOGADOR ===",
        f"Total de Ações: {stats['total_actions']}",
        f"Distância Viajada: {stats['distance_traveled']} tiles",
        f"HP Mínimo Atingido: {stats['min_hp_reached']:.1f}%",
        f"Moralidade Máxima: {stats['max_morale']}",
        f"Moralidade Mínima: {stats['min_morale']}",
        "",
        "=== AÇÕES POR TIPO ===",
    ]
    
    actions_by_type = stats.get('actions_by_type', {})
    for action_type, count in sorted(actions_by_type.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['total_actions'] * 100) if stats['total_actions'] > 0 else 0
        lines.append(f"{action_type}: {count} ({percentage:.1f}%)")
    
    return "\n".join(lines)


def get_action_summary(logger: ActionLogger, action_count: int = 10) -> str:
    """
    Gets a summary of recent actions.
    
    Args:
        logger: ActionLogger instance
        action_count: Number of recent actions to include
        
    Returns:
        Formatted string with recent actions
    """
    recent = logger.get_recent_actions(count=action_count)
    
    lines = [
        f"=== ÚLTIMAS {action_count} AÇÕES ===",
    ]
    
    for action in recent:
        lines.append(
            f"[{action.get('action_type')}] {action.get('description')} "
            f"@ ({action.get('player_x')}, {action.get('player_y')}) "
            f"HP:{action.get('player_hp'):.1f}% F:{action.get('player_food')}"
        )
    
    return "\n".join(lines)
