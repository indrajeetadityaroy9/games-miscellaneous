"""Tic-Tac-Toe environment for TorchRL."""

from typing import Tuple

import numpy as np

from .base import GameEnvironment
from .registry import register_environment
from ...tictactoe.models import GameState, Player


@register_environment("tictactoe")
class TicTacToeEnvironment(GameEnvironment[GameState, int]):
    """
    Tic-Tac-Toe environment for TorchRL.

    Observation: (3, 3, 3) tensor
        - Channel 0: X positions
        - Channel 1: O positions
        - Channel 2: Empty positions

    Action space: 9 discrete actions (board positions 0-8)
    """

    OBSERVATION_SHAPE = (3, 3, 3)

    def __init__(self) -> None:
        pass

    @property
    def observation_shape(self) -> Tuple[int, ...]:
        return self.OBSERVATION_SHAPE

    @property
    def action_space_size(self) -> int:
        return 9

    def state_to_observation(self, state: GameState) -> np.ndarray:
        """Convert tic-tac-toe game state to tensor."""
        obs = np.zeros(self.OBSERVATION_SHAPE, dtype=np.float32)

        for i, cell in enumerate(state.board):
            row, col = divmod(i, 3)
            if cell == Player.X:
                obs[0, row, col] = 1.0  # X positions
            elif cell == Player.O:
                obs[1, row, col] = 1.0  # O positions
            else:
                # Empty cell (cell is the index number)
                obs[2, row, col] = 1.0  # Empty positions

        return obs

    def action_to_game_action(self, action_idx: int, state: GameState) -> int:
        """Convert action index to board position."""
        return action_idx

    def get_legal_action_mask(self, state: GameState) -> np.ndarray:
        """
        Get mask of legal actions.

        Only empty cells are legal moves.
        """
        mask = np.zeros(9, dtype=np.float32)
        for i, cell in enumerate(state.board):
            # Empty cells contain their index (int), occupied cells contain Player enum
            if isinstance(cell, int):
                mask[i] = 1.0
        return mask
