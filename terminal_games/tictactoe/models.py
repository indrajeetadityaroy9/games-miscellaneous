"""Data models for Tic-Tac-Toe game."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class Player(Enum):
    """Player markers."""
    X = "X"  # AI
    O = "O"  # Human


# A cell can be empty (represented by its index 0-8) or contain a Player
CellValue = Union[int, Player]
Board = tuple[CellValue, ...]


@dataclass(frozen=True)
class GameState:
    """Complete game state."""
    board: Board = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    cursor_position: int = 4  # Start at center cell
    is_game_over: bool = False
    winner: Optional[str] = None  # "You Win!", "You Lose!", "Tie Game!"
    winning_cells: tuple[int, ...] = ()  # Indices of winning combo
