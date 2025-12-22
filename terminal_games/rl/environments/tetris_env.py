"""Tetris environment for TorchRL."""

from typing import Tuple
from enum import IntEnum

import numpy as np

from .base import GameEnvironment
from .registry import register_environment
from ...tetris.models import GameState, BoardConfig


class TetrisAction(IntEnum):
    """Discrete Tetris actions."""
    NOOP = 0
    LEFT = 1
    RIGHT = 2
    ROTATE = 3
    SOFT_DROP = 4
    HARD_DROP = 5


@register_environment("tetris")
class TetrisEnvironment(GameEnvironment[GameState, TetrisAction]):
    """
    Tetris environment for TorchRL.

    Observation: (2, height, width) tensor
        - Channel 0: Locked pieces on board
        - Channel 1: Current falling piece position

    Action space: 6 discrete actions
    """

    def __init__(self, config: BoardConfig = BoardConfig()) -> None:
        self.config = config
        self._observation_shape = (2, config.height, config.width)

    @property
    def observation_shape(self) -> Tuple[int, ...]:
        return self._observation_shape

    @property
    def action_space_size(self) -> int:
        return 6

    def state_to_observation(self, state: GameState) -> np.ndarray:
        """Convert tetris game state to tensor."""
        obs = np.zeros(self._observation_shape, dtype=np.float32)

        # Channel 0: locked pieces on board
        for y, row in enumerate(state.board):
            for x, cell in enumerate(row):
                if cell != 0:
                    obs[0, y, x] = 1.0

        # Channel 1: current falling piece
        if state.current_piece is not None:
            for row_idx, row in enumerate(state.current_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell != 0:
                        y = state.position.y + row_idx
                        x = state.position.x + col_idx
                        if 0 <= y < self.config.height and 0 <= x < self.config.width:
                            obs[1, y, x] = 1.0

        return obs

    def action_to_game_action(self, action_idx: int, state: GameState) -> TetrisAction:
        """Convert action index to TetrisAction."""
        return TetrisAction(action_idx)

    def get_legal_action_mask(self, state: GameState) -> np.ndarray:
        """
        Get mask of legal actions.

        All actions are always legal in Tetris (collision is handled by game logic).
        """
        return np.ones(6, dtype=np.float32)
