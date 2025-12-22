"""Data models for Terminal Snake game."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class Direction(Enum):
    """Movement direction enum."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True, slots=True)
class Position:
    """Immutable grid position."""
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))


@dataclass(frozen=True)
class Snake:
    """Snake state with head position, velocity, and body segments."""
    head: Position
    velocity: Position  # (-1, 0), (1, 0), (0, -1), or (0, 1)
    cells: tuple[Position, ...]  # Immutable tuple for hashability
    max_cells: int = 6

    @property
    def direction(self) -> Direction:
        """Current movement direction derived from velocity."""
        if self.velocity.x < 0:
            return Direction.LEFT
        elif self.velocity.x > 0:
            return Direction.RIGHT
        elif self.velocity.y < 0:
            return Direction.UP
        return Direction.DOWN


@dataclass(frozen=True)
class BoardConfig:
    """Board configuration constants."""
    columns: int = 23
    rows: int = 20


@dataclass(frozen=True)
class GameState:
    """Complete game state container."""
    snake: Snake
    apple: Position
    score: int = 0
    high_score: int = 0
    is_game_over: bool = False
    is_paused: bool = False

    @property
    def level(self) -> int:
        """Calculate level from score (1-8)."""
        return min(8, (self.score // 8) + 1)


# Direction vectors as constants
DIRECTION_VECTORS: dict[Direction, Position] = {
    Direction.UP: Position(0, -1),
    Direction.DOWN: Position(0, 1),
    Direction.LEFT: Position(-1, 0),
    Direction.RIGHT: Position(1, 0),
}

# Opposite directions for 180-degree turn prevention
OPPOSITE_DIRECTIONS: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}
