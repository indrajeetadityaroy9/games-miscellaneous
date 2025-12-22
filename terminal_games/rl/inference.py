"""Inference utilities for RL agents."""

from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .errors import RLInferenceError
from .config import RLConfig


class RLInference:
    """
    Inference engine for RL policy networks.

    Handles:
    - Converting observations to tensors
    - Running forward pass
    - Applying action masking
    - Sampling or selecting actions
    """

    def __init__(
        self,
        model: nn.Module,
        config: RLConfig,
    ) -> None:
        """
        Initialize inference engine.

        Args:
            model: Loaded policy network
            config: RL configuration
        """
        self.model = model
        self.config = config
        self.device = torch.device(config.device)
        self.model.to(self.device)
        self.model.eval()

    def get_action(
        self,
        observation: np.ndarray,
        legal_mask: Optional[np.ndarray] = None,
    ) -> int:
        """
        Get action from policy network.

        Args:
            observation: Observation tensor (numpy array)
            legal_mask: Optional binary mask of legal actions

        Returns:
            Selected action index
        """
        with torch.no_grad():
            # Convert observation to tensor
            obs_tensor = torch.from_numpy(observation).float().unsqueeze(0)
            obs_tensor = obs_tensor.to(self.device)

            # Forward pass
            try:
                logits = self.model(obs_tensor)
            except Exception as e:
                raise RLInferenceError(f"Model forward pass failed: {e}")

            # Ensure logits is 2D (batch, actions)
            if logits.dim() == 1:
                logits = logits.unsqueeze(0)

            # Apply action masking if provided
            if legal_mask is not None:
                mask_tensor = torch.from_numpy(legal_mask).float().to(self.device)
                # Set illegal actions to very negative value
                logits = logits.masked_fill(mask_tensor == 0, float("-inf"))

            # Select action
            if self.config.deterministic:
                # Greedy selection
                action = logits.argmax(dim=-1).item()
            else:
                # Sample from distribution
                if self.config.temperature != 1.0:
                    logits = logits / self.config.temperature

                probs = F.softmax(logits, dim=-1)
                action = torch.multinomial(probs, num_samples=1).item()

            return int(action)

    def get_action_probs(
        self,
        observation: np.ndarray,
        legal_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Get action probabilities from policy network.

        Args:
            observation: Observation tensor (numpy array)
            legal_mask: Optional binary mask of legal actions

        Returns:
            Action probabilities as numpy array
        """
        with torch.no_grad():
            # Convert observation to tensor
            obs_tensor = torch.from_numpy(observation).float().unsqueeze(0)
            obs_tensor = obs_tensor.to(self.device)

            # Forward pass
            logits = self.model(obs_tensor)

            if logits.dim() == 1:
                logits = logits.unsqueeze(0)

            # Apply action masking if provided
            if legal_mask is not None:
                mask_tensor = torch.from_numpy(legal_mask).float().to(self.device)
                logits = logits.masked_fill(mask_tensor == 0, float("-inf"))

            # Apply temperature
            if self.config.temperature != 1.0:
                logits = logits / self.config.temperature

            probs = F.softmax(logits, dim=-1)
            return probs.cpu().numpy().squeeze(0)
