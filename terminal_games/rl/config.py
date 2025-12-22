"""RL configuration management."""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import os


@dataclass
class RLConfig:
    """Configuration for RL agents."""

    model_dir: Optional[Path] = None  # Directory containing trained models
    device: str = "cpu"  # cpu, cuda, mps
    deterministic: bool = False  # Use argmax vs sampling
    temperature: float = 1.0  # For action sampling
    fallback_to_minimax: bool = True  # Use minimax if model unavailable

    def __post_init__(self) -> None:
        # Load from environment if not set
        if self.model_dir is None:
            env_path = os.getenv("TERMINAL_GAMES_MODEL_DIR")
            if env_path:
                self.model_dir = Path(env_path)

        env_device = os.getenv("TERMINAL_GAMES_DEVICE")
        if env_device:
            self.device = env_device

    def get_model_path(self, game: str) -> Optional[Path]:
        """Get path to model file for a specific game."""
        if self.model_dir is None:
            return None
        game_dir = self.model_dir / game
        if not game_dir.exists():
            return None
        # Look for model file
        for ext in [".pt", ".pth", ".ckpt"]:
            model_file = game_dir / f"model{ext}"
            if model_file.exists():
                return model_file
        return None


# Global RL config instance
_rl_config: Optional[RLConfig] = None


def get_rl_config() -> RLConfig:
    """Get the current RL configuration."""
    global _rl_config
    if _rl_config is None:
        _rl_config = RLConfig()
    return _rl_config


def set_rl_config(config: RLConfig) -> None:
    """Set the RL configuration."""
    global _rl_config
    _rl_config = config
