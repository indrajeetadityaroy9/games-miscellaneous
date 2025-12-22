"""Generic RL agent factory classes."""

from pathlib import Path
from typing import TypeVar, Generic, Optional, Callable

from ..base import RLAgent, AgentResponse, AgentType
from ..config import RLConfig
from ..errors import RLModelError
from ..environments.base import GameEnvironment
from ..model_loader import ModelLoader
from ..inference import RLInference

StateT = TypeVar("StateT")
ActionT = TypeVar("ActionT")


class BaseRLAgent(RLAgent[StateT, ActionT], Generic[StateT, ActionT]):
    """Base RL agent with common implementation.

    Handles model loading, inference, and action selection.
    Game-specific behavior is delegated to the environment.
    """

    def __init__(
        self,
        config: RLConfig,
        env: GameEnvironment[StateT, ActionT],
        name: str,
        fallback_fn: Optional[Callable[[StateT], Optional[ActionT]]] = None,
    ) -> None:
        self.config = config
        self.env = env
        self._name = name
        self._fallback_fn = fallback_fn
        self._model = None
        self._inference: Optional[RLInference] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def agent_type(self) -> AgentType:
        return AgentType.RL

    def load_model(self, path: Path) -> None:
        """Load trained model from file."""
        self._model = ModelLoader.load_model(path, self.config.device)
        self._inference = RLInference(self._model, self.config)

    def is_model_loaded(self) -> bool:
        return self._model is not None

    def get_action(self, state: StateT) -> AgentResponse[ActionT]:
        """Get action from RL model."""
        if self._inference is None:
            raise RLModelError("No model loaded")

        obs = self.env.state_to_observation(state)
        mask = self.env.get_legal_action_mask(state)

        action_idx = self._inference.get_action(obs, mask)
        action = self.env.action_to_game_action(action_idx, state)

        return AgentResponse(action=action)

    def get_fallback_action(self, state: StateT) -> Optional[ActionT]:
        """Get fallback action using provided fallback function or random."""
        if self._fallback_fn is not None:
            return self._fallback_fn(state)
        # Default: sample random legal action
        action_idx = self.env.sample_action(state)
        return self.env.action_to_game_action(action_idx, state)


class BaseRandomAgent(RLAgent[StateT, ActionT], Generic[StateT, ActionT]):
    """Base random agent with common implementation.

    Selects random legal actions using the environment's action mask.
    """

    def __init__(
        self,
        config: RLConfig,
        env: GameEnvironment[StateT, ActionT],
        name: str,
    ) -> None:
        self.config = config
        self.env = env
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def agent_type(self) -> AgentType:
        return AgentType.RANDOM

    def load_model(self, path: Path) -> None:
        """Random agent doesn't need a model."""
        pass

    def is_model_loaded(self) -> bool:
        return True  # Always ready

    def get_action(self, state: StateT) -> AgentResponse[ActionT]:
        """Get random legal action."""
        action_idx = self.env.sample_action(state)
        action = self.env.action_to_game_action(action_idx, state)
        return AgentResponse(action=action)

    def get_fallback_action(self, state: StateT) -> Optional[ActionT]:
        """Fallback is same as primary action for random agent."""
        return self.get_action(state).action
