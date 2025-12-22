"""Model loading utilities for TorchRL agents."""

from pathlib import Path

import torch
import torch.nn as nn

from .errors import RLModelError


class ModelLoader:
    """Utility class for loading trained RL models."""

    @staticmethod
    def load_model(
        path: Path,
        device: str = "cpu",
    ) -> nn.Module:
        """
        Load a trained model from file.

        Supports:
        - TorchScript models (.pt)
        - State dict checkpoints (.pth, .ckpt)

        Args:
            path: Path to model file
            device: Device to load model to (cpu, cuda, mps)

        Returns:
            Loaded PyTorch model

        Raises:
            RLModelError: If model cannot be loaded
        """
        if not path.exists():
            raise RLModelError(f"Model file not found: {path}")

        try:
            # Try loading as TorchScript first
            if path.suffix == ".pt":
                try:
                    model = torch.jit.load(str(path), map_location=device)
                    model.eval()
                    return model
                except Exception:
                    # Fall through to try as state dict
                    pass

            # Try loading as state dict checkpoint
            checkpoint = torch.load(str(path), map_location=device, weights_only=False)

            # Handle different checkpoint formats
            if isinstance(checkpoint, nn.Module):
                # Direct model save
                model = checkpoint
            elif isinstance(checkpoint, dict):
                if "model" in checkpoint:
                    model = checkpoint["model"]
                elif "state_dict" in checkpoint:
                    # Need model architecture - this is a limitation
                    raise RLModelError(
                        f"Checkpoint at {path} contains only state_dict. "
                        "Please save the full model or use TorchScript format."
                    )
                elif "policy" in checkpoint:
                    # TorchRL checkpoint format
                    model = checkpoint["policy"]
                else:
                    raise RLModelError(
                        f"Unknown checkpoint format at {path}. "
                        "Expected 'model', 'state_dict', or 'policy' key."
                    )
            else:
                raise RLModelError(
                    f"Unexpected checkpoint type at {path}: {type(checkpoint)}"
                )

            model.eval()
            return model

        except RLModelError:
            raise
        except Exception as e:
            raise RLModelError(f"Failed to load model from {path}: {e}")

    @staticmethod
    def get_device(preferred: str = "cpu") -> torch.device:
        """
        Get the best available device.

        Args:
            preferred: Preferred device (cpu, cuda, mps)

        Returns:
            torch.device for the selected device
        """
        if preferred == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        elif preferred == "mps" and hasattr(torch.backends, "mps"):
            if torch.backends.mps.is_available():
                return torch.device("mps")
        return torch.device("cpu")
