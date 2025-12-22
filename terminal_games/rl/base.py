"""Abstract base classes for RL agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar, Optional
from pathlib import Path

# Type variables for game state and action
StateT = TypeVar("StateT")
ActionT = TypeVar("ActionT")


class AgentType(Enum):
    """Available agent types."""

    RL = auto()  # Trained RL model
    MINIMAX = auto()  # Fallback minimax (Chess, Tic-Tac-Toe)
    RANDOM = auto()  # Random baseline


@dataclass
class AgentResponse(Generic[ActionT]):
    """Standardized agent response."""

    action: ActionT
    confidence: Optional[float] = None
    fallback_used: bool = False


class RLAgent(ABC, Generic[StateT, ActionT]):
    """Abstract base class for all RL agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for the agent."""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return the agent type."""
        pass

    @abstractmethod
    def get_action(self, state: StateT) -> AgentResponse[ActionT]:
        """
        Get the best action for the given game state (synchronous).
        """
        pass

    @abstractmethod
    def load_model(self, path: Path) -> None:
        """Load pre-trained model weights from file."""
        pass

    @abstractmethod
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded."""
        pass

    def get_fallback_action(self, state: StateT) -> Optional[ActionT]:
        """
        Get a fallback action when primary action selection fails.
        Override for game-specific fallback logic.
        """
        return None
