"""Shared configuration for Terminal Games."""

# Global theme state - persists across game sessions
_current_theme: str = "textual-dark"


def get_theme() -> str:
    """Get the current theme."""
    return _current_theme


def set_theme(theme: str) -> None:
    """Set the current theme."""
    global _current_theme
    _current_theme = theme
