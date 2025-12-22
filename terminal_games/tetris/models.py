"""Data models for Terminal Tetris game."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class GameState:
    """Complete game state container."""
    board: tuple[tuple[int, ...], ...]  # height x width grid, 0=empty, 1-7=colors
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
