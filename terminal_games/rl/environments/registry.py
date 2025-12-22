"""Environment registry for RL module."""

from typing import Dict, Type, TypeVar, Callable

from .base import GameEnvironment

# Type variable for environment classes
EnvT = TypeVar("EnvT", bound=GameEnvironment)

# Registry mapping game names to environment classes
ENV_REGISTRY: Dict[str, Type[GameEnvironment]] = {}


def register_environment(game: str) -> Callable[[Type[EnvT]], Type[EnvT]]:
    """
    Decorator to register an environment class for a game.

    Usage:
        @register_environment("snake")
        class SnakeEnvironment(GameEnvironment):
            ...
    """
    def decorator(cls: Type[EnvT]) -> Type[EnvT]:
        ENV_REGISTRY[game] = cls
        return cls
    return decorator


def get_environment(game: str, **kwargs) -> GameEnvironment:
    """
    Get an environment instance for a game.

    Args:
        game: Game name (e.g., "snake", "chess")
        **kwargs: Arguments to pass to environment constructor

    Returns:
        Environment instance

    Raises:
        ValueError: If no environment is registered for the game
    """
    if game not in ENV_REGISTRY:
        raise ValueError(f"No environment registered for game: {game}")
    return ENV_REGISTRY[game](**kwargs)


def get_registered_games() -> list[str]:
    """Get list of games with registered environments."""
    return list(ENV_REGISTRY.keys())
