"""Space Invaders environment for TorchRL."""

from typing import Tuple
from enum import IntEnum

import numpy as np

from .base import GameEnvironment
from .registry import register_environment
from ...spaceinvaders.models import (
    GameState,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    PLAYER_Y,
)


class SpaceInvadersAction(IntEnum):
    """Discrete Space Invaders actions."""
    NOOP = 0
    LEFT = 1
    RIGHT = 2
    SHOOT = 3
    LEFT_SHOOT = 4
    RIGHT_SHOOT = 5


@register_environment("spaceinvaders")
class SpaceInvadersEnvironment(GameEnvironment[GameState, SpaceInvadersAction]):
    """
    Space Invaders environment for TorchRL.

    Observation: (4, height, width) tensor
        - Channel 0: Player position
        - Channel 1: Enemy positions
        - Channel 2: Player bullet positions
        - Channel 3: Enemy bullet positions

    Action space: 6 discrete actions
    """

    def __init__(self) -> None:
        self._observation_shape = (4, BOARD_HEIGHT, BOARD_WIDTH)

    @property
    def observation_shape(self) -> Tuple[int, ...]:
        return self._observation_shape

    @property
    def action_space_size(self) -> int:
        return 6

    def state_to_observation(self, state: GameState) -> np.ndarray:
        """Convert space invaders game state to tensor."""
        obs = np.zeros(self._observation_shape, dtype=np.float32)

        # Channel 0: player position
        player_x = state.player.x
        player_width = state.player.width
        for x in range(player_x, min(player_x + player_width, BOARD_WIDTH)):
            if 0 <= x < BOARD_WIDTH:
                # Player occupies 2 rows
                if PLAYER_Y < BOARD_HEIGHT:
                    obs[0, PLAYER_Y, x] = 1.0
                if PLAYER_Y + 1 < BOARD_HEIGHT:
                    obs[0, PLAYER_Y + 1, x] = 1.0

        # Channel 1: enemy positions
        for enemy in state.enemies:
            if enemy.active:
                for dy in range(enemy.height):
                    for dx in range(enemy.width):
                        ey = enemy.y + dy
                        ex = enemy.x + dx
                        if 0 <= ey < BOARD_HEIGHT and 0 <= ex < BOARD_WIDTH:
                            obs[1, ey, ex] = 1.0

        # Channel 2: player bullets
        for bullet in state.player_bullets:
            if bullet.active:
                if 0 <= bullet.y < BOARD_HEIGHT and 0 <= bullet.x < BOARD_WIDTH:
                    obs[2, bullet.y, bullet.x] = 1.0

        # Channel 3: enemy bullets
        for bullet in state.enemy_bullets:
            if bullet.active:
                if 0 <= bullet.y < BOARD_HEIGHT and 0 <= bullet.x < BOARD_WIDTH:
                    obs[3, bullet.y, bullet.x] = 1.0

        return obs

    def action_to_game_action(
        self, action_idx: int, state: GameState
    ) -> SpaceInvadersAction:
        """Convert action index to SpaceInvadersAction."""
        return SpaceInvadersAction(action_idx)

    def get_legal_action_mask(self, state: GameState) -> np.ndarray:
        """
        Get mask of legal actions.

        Shoot actions are masked if cooldown is active.
        """
        mask = np.ones(6, dtype=np.float32)

        if not state.can_shoot:
            # Mask shoot actions when on cooldown
            mask[SpaceInvadersAction.SHOOT] = 0.0
            mask[SpaceInvadersAction.LEFT_SHOOT] = 0.0
            mask[SpaceInvadersAction.RIGHT_SHOOT] = 0.0

        return mask
