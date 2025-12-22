"""Snake environment for TorchRL."""

from typing import Tuple
from enum import IntEnum

import numpy as np

from .base import GameEnvironment
from .registry import register_environment
from ...snake.models import (
    GameState,
    Direction,
    BoardConfig,
    OPPOSITE_DIRECTIONS,
)


class SnakeAction(IntEnum):
    """Discrete snake actions."""
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


# Map action indices to Direction enum
ACTION_TO_DIRECTION = {
    SnakeAction.UP: Direction.UP,
    SnakeAction.DOWN: Direction.DOWN,
    SnakeAction.LEFT: Direction.LEFT,
    SnakeAction.RIGHT: Direction.RIGHT,
}


@register_environment("snake")
class SnakeEnvironment(GameEnvironment[GameState, Direction]):
    """
    Snake environment for TorchRL.

    Observation: (4, rows, cols) tensor
        - Channel 0: Snake head position
        - Channel 1: Snake body positions
        - Channel 2: Apple position
        - Channel 3: Current direction encoding

    Action space: 4 discrete actions (UP, DOWN, LEFT, RIGHT)
    """

    def __init__(self, config: BoardConfig = BoardConfig()) -> None:
        self.config = config
        self._observation_shape = (4, config.rows, config.columns)

    @property
    def observation_shape(self) -> Tuple[int, ...]:
        return self._observation_shape

    @property
    def action_space_size(self) -> int:
        return 4

    def state_to_observation(self, state: GameState) -> np.ndarray:
        """Convert snake game state to tensor."""
        obs = np.zeros(self._observation_shape, dtype=np.float32)

        # Channel 0: snake head
        head = state.snake.head
        if 0 <= head.y < self.config.rows and 0 <= head.x < self.config.columns:
            obs[0, head.y, head.x] = 1.0

        # Channel 1: snake body (excluding head)
        for cell in state.snake.cells[1:]:
            if 0 <= cell.y < self.config.rows and 0 <= cell.x < self.config.columns:
                obs[1, cell.y, cell.x] = 1.0

        # Channel 2: apple
        apple = state.apple
        if 0 <= apple.y < self.config.rows and 0 <= apple.x < self.config.columns:
            obs[2, apple.y, apple.x] = 1.0

        # Channel 3: direction encoding (encode as gradient in movement direction)
        current_dir = state.snake.direction
        if current_dir == Direction.UP:
            obs[3, :, :] = np.linspace(1, 0, self.config.rows).reshape(-1, 1)
        elif current_dir == Direction.DOWN:
            obs[3, :, :] = np.linspace(0, 1, self.config.rows).reshape(-1, 1)
        elif current_dir == Direction.LEFT:
            obs[3, :, :] = np.linspace(1, 0, self.config.columns).reshape(1, -1)
        elif current_dir == Direction.RIGHT:
            obs[3, :, :] = np.linspace(0, 1, self.config.columns).reshape(1, -1)

        return obs

    def action_to_game_action(self, action_idx: int, state: GameState) -> Direction:
        """Convert action index to Direction."""
        return ACTION_TO_DIRECTION[SnakeAction(action_idx)]

    def get_legal_action_mask(self, state: GameState) -> np.ndarray:
        """
        Get mask of legal actions.

        Snake cannot turn 180 degrees (reverse direction).
        """
        mask = np.ones(4, dtype=np.float32)

        # Get current direction and its opposite
        current_dir = state.snake.direction
        opposite_dir = OPPOSITE_DIRECTIONS[current_dir]

        # Find the action index of the opposite direction
        for action, direction in ACTION_TO_DIRECTION.items():
            if direction == opposite_dir:
                mask[action] = 0.0
                break

        return mask
