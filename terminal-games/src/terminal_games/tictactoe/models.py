"""Data models for Tic-Tac-Toe game."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


class Player(Enum):
    """Player markers."""
    X = "X"  # AI
    O = "O"  # Human


# A cell can be empty (represented by its index 0-8) or contain a Player
CellValue = Union[int, Player]
Board = list[CellValue]


@dataclass
class GameState:
    """Complete game state."""

    board: Board = field(default_factory=lambda: list(range(9)))
    cursor_position: int = 4  # Start at center cell
    is_game_over: bool = False
    winner: Optional[str] = None  # "You Win!", "You Lose!", "Tie Game!"
    winning_cells: tuple[int, ...] = ()  # Indices of winning combo

    def copy(self) -> "GameState":
        """Create a shallow copy of the game state."""
        return GameState(
            board=self.board[:],
            cursor_position=self.cursor_position,
            is_game_over=self.is_game_over,
            winner=self.winner,
            winning_cells=self.winning_cells,
        )
