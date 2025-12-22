"""Game environment wrappers for TorchRL."""

from .base import GameEnvironment
from .registry import register_environment, get_environment, get_registered_games
from .chess_env import ChessEnvironment
from .snake_env import SnakeEnvironment
from .tetris_env import TetrisEnvironment
from .tictactoe_env import TicTacToeEnvironment
from .spaceinvaders_env import SpaceInvadersEnvironment

__all__ = [
    # Base
    "GameEnvironment",
    # Registry
    "register_environment",
    "get_environment",
    "get_registered_games",
    # Environments
    "ChessEnvironment",
    "SnakeEnvironment",
    "TetrisEnvironment",
    "TicTacToeEnvironment",
    "SpaceInvadersEnvironment",
]
