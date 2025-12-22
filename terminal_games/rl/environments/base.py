"""Base class for game environments compatible with TorchRL."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Tuple

import numpy as np

StateT = TypeVar("StateT")
ActionT = TypeVar("ActionT")


class GameEnvironment(ABC, Generic[StateT, ActionT]):
    """
    Base class for game environments.

    Provides the interface needed for:
    - Converting game state to tensor observations
    - Converting action indices to game actions
    - Computing legal action masks
    """

    @property
    @abstractmethod
    def observation_shape(self) -> Tuple[int, ...]:
        """Shape of observation tensor."""
        pass

    @property
    @abstractmethod
    def action_space_size(self) -> int:
        """Number of possible discrete actions."""
        pass

    @abstractmethod
    def state_to_observation(self, state: StateT) -> np.ndarray:
        """
        Convert game state to observation tensor.

        Returns:
            numpy array of shape self.observation_shape
        """
        pass

    @abstractmethod
    def action_to_game_action(self, action_idx: int, state: StateT) -> ActionT:
        """
        Convert action index to game-specific action.

        Args:
            action_idx: Index into action space (0 to action_space_size-1)
            state: Current game state (for context-dependent conversion)

        Returns:
            Game-specific action type
        """
        pass

    @abstractmethod
    def get_legal_action_mask(self, state: StateT) -> np.ndarray:
        """
        Get binary mask of legal actions.

        Returns:
            numpy array of shape (action_space_size,) with 1.0 for legal, 0.0 for illegal
        """
        pass

    def sample_action(self, state: StateT) -> int:
        """
        Sample a random legal action.

        Returns:
            Action index
        """
        mask = self.get_legal_action_mask(state)
        legal_actions = np.where(mask > 0)[0]
        if len(legal_actions) == 0:
            return 0  # No legal actions, return default
        return int(np.random.choice(legal_actions))
