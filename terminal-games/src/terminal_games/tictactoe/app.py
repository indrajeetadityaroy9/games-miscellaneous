"""Main Textual application for Terminal Tic-Tac-Toe."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from .models import GameState
from .game_logic import (
    create_initial_state,
    make_move,
    move_cursor_up,
    move_cursor_down,
    move_cursor_left,
    move_cursor_right,
)
from .widgets.game_board import GameBoard
from .widgets.status import Status
from ..config import get_theme, set_theme


class TicTacToeApp(App):
    """Terminal Tic-Tac-Toe game application."""

    CSS_PATH = Path(__file__).parent / "styles" / "tictactoe.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("w", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("s", "cursor_down", "Down", show=False),
        Binding("left", "cursor_left", "Left", show=False),
        Binding("a", "cursor_left", "Left", show=False),
        Binding("right", "cursor_right", "Right", show=False),
        Binding("d", "cursor_right", "Right", show=False),
        Binding("enter", "place_move", "Place"),
        Binding("space", "place_move", "Place", show=False),
        Binding("r", "reset", "Restart"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Tic-Tac-Toe"

    def __init__(self) -> None:
        super().__init__()
        self.state = create_initial_state()
        self._board: GameBoard | None = None
        self._status: Status | None = None

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header(show_clock=True)
        yield Container(
            Status(id="status"),
            GameBoard(id="game-board"),
            id="game-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize when app mounts."""
        self._board = self.query_one("#game-board", GameBoard)
        self._status = self.query_one("#status", Status)
        self._update_widgets()
        # Apply saved theme
        self.theme = get_theme()

    def _update_widgets(self) -> None:
        """Push state to child widgets."""
        if self._board:
            self._board.update_state(
                board=self.state.board,
                cursor_position=self.state.cursor_position,
                winning_cells=self.state.winning_cells,
                is_game_over=self.state.is_game_over,
            )

        if self._status:
            if self.state.is_game_over and self.state.winner:
                self._status.update_state(self.state.winner, True)
            else:
                self._status.update_state("Your turn (O)", False)

    # Cursor movement actions
    def action_cursor_up(self) -> None:
        """Move cursor up."""
        if self.state.is_game_over:
            return
        self.state = move_cursor_up(self.state)
        self._update_widgets()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        if self.state.is_game_over:
            return
        self.state = move_cursor_down(self.state)
        self._update_widgets()

    def action_cursor_left(self) -> None:
        """Move cursor left."""
        if self.state.is_game_over:
            return
        self.state = move_cursor_left(self.state)
        self._update_widgets()

    def action_cursor_right(self) -> None:
        """Move cursor right."""
        if self.state.is_game_over:
            return
        self.state = move_cursor_right(self.state)
        self._update_widgets()

    # Game actions
    def action_place_move(self) -> None:
        """Place move at cursor position."""
        if self.state.is_game_over:
            return

        self.state = make_move(self.state, self.state.cursor_position)
        self._update_widgets()

    def action_reset(self) -> None:
        """Reset game to initial state."""
        self.state = create_initial_state()
        self._update_widgets()

    def action_toggle_theme(self) -> None:
        """Switch between dark and light themes."""
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()


def main() -> None:
    """Run the Terminal Tic-Tac-Toe application."""
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()
