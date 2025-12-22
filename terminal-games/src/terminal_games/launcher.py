"""Game launcher menu for Terminal Games."""

import sys
from importlib import import_module
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Static
from textual.reactive import reactive

from .config import get_theme, set_theme


GAMES = [
    ("chess", "Chess", "Classic chess with AI opponent"),
    ("snake", "Snake", "Eat food and grow longer"),
    ("tetris", "Tetris", "Stack falling blocks"),
    ("tictactoe", "Tic-Tac-Toe", "Classic X and O game"),
    ("spaceinvaders", "Space Invaders", "Defend against alien invasion"),
]

GAME_ICONS = {
    "chess": "\u265a",        # Black king
    "snake": "\u25cf",        # Circle (snake body)
    "tetris": "\u25a0",       # Black square (block)
    "tictactoe": "\u2715",    # Multiplication X
    "spaceinvaders": "\u25b2", # Black up-pointing triangle
}


class GameMenuItem(Static):
    """A selectable game menu item."""

    def __init__(self, game_id: str, game_name: str, description: str, selected: bool = False) -> None:
        super().__init__()
        self.game_id = game_id
        self.game_name = game_name
        self.description = description
        self._selected = selected

    def render(self) -> str:
        icon = GAME_ICONS.get(self.game_id, "\u25cf")
        if self._selected:
            return f"[bold cyan]> {icon} {self.game_name}[/bold cyan]\n  [dim]{self.description}[/dim]"
        else:
            return f"  {icon} {self.game_name}\n  [dim]{self.description}[/dim]"

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.refresh()


class LauncherApp(App):
    """Terminal Games launcher application."""

    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        align: center middle;
        background: $background;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding: 1 0;
    }

    #menu-container {
        width: auto;
        height: auto;
        min-width: 50;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }

    #menu {
        width: 100%;
        height: auto;
    }

    GameMenuItem {
        width: 100%;
        height: 3;
        padding: 0 1;
        margin: 0 0 1 0;
    }

    #instructions {
        text-align: center;
        color: $text-muted;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("enter", "select_game", "Select"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Games"

    selected_index: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._menu_items: list[GameMenuItem] = []
        self._selected_game: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("[bold]Terminal Games[/bold]", id="title", markup=True),
            Vertical(
                *[
                    GameMenuItem(game_id, name, desc, selected=(i == 0))
                    for i, (game_id, name, desc) in enumerate(GAMES)
                ],
                id="menu",
            ),
            Static("[dim]Arrow keys to navigate, Enter to select, Q to quit[/dim]", id="instructions", markup=True),
            id="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._menu_items = list(self.query(GameMenuItem))
        self._update_selection()
        # Apply saved theme
        self.theme = get_theme()

    def _update_selection(self) -> None:
        for i, item in enumerate(self._menu_items):
            item.set_selected(i == self.selected_index)

    def watch_selected_index(self, new_index: int) -> None:
        self._update_selection()

    def action_move_up(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1

    def action_move_down(self) -> None:
        if self.selected_index < len(GAMES) - 1:
            self.selected_index += 1

    def action_select_game(self) -> None:
        game_id = GAMES[self.selected_index][0]
        self._selected_game = game_id
        self.exit()

    def action_toggle_theme(self) -> None:
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"
        set_theme(self.theme)

    @property
    def selected_game(self) -> Optional[str]:
        return self._selected_game


def launch_game(game_id: str) -> int:
    """Launch a specific game by ID."""
    try:
        module = import_module(f"terminal_games.{game_id}.app")
        main_func = getattr(module, "main")
        main_func()
        return 0
    except (ImportError, AttributeError) as e:
        print(f"Error launching {game_id}: {e}")
        return 1


def main() -> int:
    """Main entry point for terminal-games."""
    # Check for command line argument to launch specific game
    if len(sys.argv) > 1:
        game_id = sys.argv[1].lower()
        valid_games = [g[0] for g in GAMES]
        if game_id in valid_games:
            return launch_game(game_id)
        else:
            print(f"Unknown game: {game_id}")
            print(f"Available games: {', '.join(valid_games)}")
            return 1

    # Show launcher menu
    while True:
        app = LauncherApp()
        app.run()

        selected = app.selected_game
        if selected is None:
            # User quit
            return 0

        # Launch the selected game
        launch_game(selected)
        # After game exits, loop back to launcher


if __name__ == "__main__":
    sys.exit(main())
