"""Data models for Terminal Tetris game."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Position:
    """Immutable grid position."""
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)


@dataclass(frozen=True)
class Tetromino:
    """A tetromino piece with its shape matrix and color."""
    shape: tuple[tuple[int, ...], ...]  # 2D shape matrix (rows of cells)
    color: int  # 1-7 corresponding to piece type


@dataclass(frozen=True)
class BoardConfig:
    """Board configuration constants."""
    width: int = 10
    height: int = 18


@dataclass
class GameState:
    """Complete game state container."""
    board: list[list[int]]  # height x width grid, 0=empty, 1-7=colors
    current_piece: Optional[Tetromino]
    position: Position
    score: int = 0
    high_score: int = 0
    level: int = 1
    lines_cleared: int = 0
    combo: int = 0
    last_clear_was_tetris: bool = False
    is_game_over: bool = False
    is_paused: bool = False
    clearing_rows: tuple[int, ...] = ()

    def copy(self) -> "GameState":
        """Create a shallow copy with a deep copy of the board."""
        return GameState(
            board=[row[:] for row in self.board],
            current_piece=self.current_piece,
            position=self.position,
            score=self.score,
            high_score=self.high_score,
            level=self.level,
            lines_cleared=self.lines_cleared,
            combo=self.combo,
            last_clear_was_tetris=self.last_clear_was_tetris,
            is_game_over=self.is_game_over,
            is_paused=self.is_paused,
            clearing_rows=self.clearing_rows,
        )
