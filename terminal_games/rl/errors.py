"""Custom exceptions for RL module."""


class RLError(Exception):
    """Base exception for RL-related errors."""

    pass


class RLModelError(RLError):
    """Error loading or using model."""

    pass


class RLInferenceError(RLError):
    """Error during inference."""

    pass


class RLConfigError(RLError):
    """Error in RL configuration."""

    pass
