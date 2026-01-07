from pathlib import Path
from textual.app import App, ComposeResult
from textual import events
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
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()

    def on_mount(self) -> None:
        self._configure_layout(force_reset=True)
        self._update_widgets()
        self.theme = get_theme()

    def on_resize(self, event: events.Resize) -> None:
        self._configure_layout()

    def _calculate_cell_size(self) -> tuple[int, int]:
        screen_width = self.size.width
        screen_height = self.size.height

        available_width = max(30, screen_width - 10)
        available_height = max(15, screen_height - 10)

        cell_width = max(5, (available_width - 4) // 3)
        cell_height = max(3, (available_height - 4) // 3)
        return cell_width, cell_height

    def _configure_layout(self, force_reset: bool = False) -> None:
        cell_width, cell_height = self._calculate_cell_size()
        if self._board and not force_reset:
            if (
                self._board.CELL_WIDTH == cell_width
                and self._board.CELL_HEIGHT == cell_height
            ):
                return

        if self._status is None:
            self._status = Status(id="status")
        if self._board is None:
            self._board = GameBoard(
                id="game-board",
                cell_width=cell_width,
                cell_height=cell_height,
            )
            self.query_one("#game-container").mount(self._status, self._board)
        else:
            self._board.CELL_WIDTH = cell_width
            self._board.CELL_HEIGHT = cell_height
            self._board.TOTAL_HEIGHT = self._board.CELL_HEIGHT * 3 + 4
            self._board.refresh()

        self._update_widgets()

    def _update_widgets(self) -> None:
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

    def action_cursor_up(self) -> None:
        if self.state.is_game_over:
            return
        self.state = move_cursor_up(self.state)
        self._update_widgets()

    def action_cursor_down(self) -> None:
        if self.state.is_game_over:
            return
        self.state = move_cursor_down(self.state)
        self._update_widgets()

    def action_cursor_left(self) -> None:
        if self.state.is_game_over:
            return
        self.state = move_cursor_left(self.state)
        self._update_widgets()

    def action_cursor_right(self) -> None:
        if self.state.is_game_over:
            return
        self.state = move_cursor_right(self.state)
        self._update_widgets()

    def action_place_move(self) -> None:
        if self.state.is_game_over:
            return
        self.state = make_move(self.state, self.state.cursor_position)
        self._update_widgets()

    def action_reset(self) -> None:
        self.state = create_initial_state()
        self._update_widgets()

    def action_toggle_theme(self) -> None:
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()


def main() -> None:
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()
