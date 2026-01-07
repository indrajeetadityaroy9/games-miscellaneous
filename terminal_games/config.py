_current_theme: str = "textual-dark"
def get_theme() -> str:
    return _current_theme
def set_theme(theme: str) -> None:
    global _current_theme
    _current_theme = theme
