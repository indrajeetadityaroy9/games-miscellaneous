"""RL agent registry for game selection."""

from enum import Enum
from typing import Optional, Callable, Any

from .base import RLAgent, AgentType
from .config import RLConfig
from .environments.registry import get_environment, ENV_REGISTRY
from .agents.factory import BaseRLAgent, BaseRandomAgent
from .agents.fallbacks import ChessMinimaxAgent, TicTacToeMinimaxAgent


class GameType(Enum):
    """Enumeration of supported games."""

    CHESS = "chess"
    SNAKE = "snake"
    TETRIS = "tetris"
    TICTACTOE = "tictactoe"
    SPACEINVADERS = "spaceinvaders"


# Game-specific fallback functions for RL agents
def _chess_fallback(board: Any) -> Optional[Any]:
    """Chess fallback using minimax."""
    from ..chess.chess_ai import get_best_move
    return get_best_move(board, depth=2)


def _tictactoe_fallback(state: Any) -> Optional[int]:
    """Tic-Tac-Toe fallback using minimax."""
    from ..tictactoe.game_logic import get_best_move
    return get_best_move(state.board)


# Fallback function mapping
_FALLBACK_FUNCTIONS: dict[GameType, Callable] = {
    GameType.CHESS: _chess_fallback,
    GameType.TICTACTOE: _tictactoe_fallback,
}

# Games that have minimax agents
_MINIMAX_GAMES: set[GameType] = {GameType.CHESS, GameType.TICTACTOE}


def _get_game_display_name(game: GameType) -> str:
    """Get human-readable display name for a game."""
    names = {
        GameType.CHESS: "Chess",
        GameType.SNAKE: "Snake",
        GameType.TETRIS: "Tetris",
        GameType.TICTACTOE: "Tic-Tac-Toe",
        GameType.SPACEINVADERS: "Space Invaders",
    }
    return names.get(game, game.value.title())


def create_rl_agent(game: GameType, config: RLConfig) -> RLAgent:
    """Create an RL agent for the specified game."""
    env = get_environment(game.value)
    fallback_fn = _FALLBACK_FUNCTIONS.get(game)
    name = f"{_get_game_display_name(game)} RL Agent"
    return BaseRLAgent(config, env, name, fallback_fn)


def create_random_agent(game: GameType, config: RLConfig) -> RLAgent:
    """Create a random agent for the specified game."""
    env = get_environment(game.value)
    name = f"{_get_game_display_name(game)} Random Agent"
    return BaseRandomAgent(config, env, name)


def create_minimax_agent(game: GameType, config: RLConfig) -> Optional[RLAgent]:
    """Create a minimax agent for the specified game (if available)."""
    if game == GameType.CHESS:
        return ChessMinimaxAgent(config)
    elif game == GameType.TICTACTOE:
        return TicTacToeMinimaxAgent(config)
    return None


class RLRegistry:
    """Registry for RL agent factories.

    Uses factory pattern to create agents dynamically.
    """

    @classmethod
    def get_agent(
        cls,
        game: GameType,
        config: RLConfig,
        prefer_rl: bool = True,
    ) -> RLAgent:
        """
        Create an RL agent for the specified game.

        Args:
            game: Which game to get agent for
            config: RL configuration
            prefer_rl: If True, prefer RL model; if False, prefer minimax/random
        """
        if game.value not in ENV_REGISTRY:
            raise ValueError(f"No environment registered for {game}")

        # Try RL agent if preferred
        if prefer_rl:
            model_path = config.get_model_path(game.value)
            if model_path is not None:
                agent = create_rl_agent(game, config)
                agent.load_model(model_path)
                return agent

        # Fallback chain: minimax -> random
        if config.fallback_to_minimax and game in _MINIMAX_GAMES:
            minimax_agent = create_minimax_agent(game, config)
            if minimax_agent is not None:
                return minimax_agent

        # Final fallback: random agent
        return create_random_agent(game, config)

    @classmethod
    def get_available_types(cls, game: GameType) -> list[AgentType]:
        """Get list of available agent types for a game."""
        if game.value not in ENV_REGISTRY:
            return []

        types = [AgentType.RL, AgentType.RANDOM]
        if game in _MINIMAX_GAMES:
            types.append(AgentType.MINIMAX)
        return types

    @classmethod
    def is_registered(cls, game: GameType, agent_type: AgentType) -> bool:
        """Check if a specific agent type is registered for a game."""
        if game.value not in ENV_REGISTRY:
            return False

        if agent_type == AgentType.MINIMAX:
            return game in _MINIMAX_GAMES
        return True  # RL and RANDOM are always available
