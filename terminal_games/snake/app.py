"""Main Textual application for Terminal Snake."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from .models import BoardConfig, Direction, GameState
from .game_logic import (
    create_initial_state,
    tick,
    change_direction,
    toggle_pause,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme


# Game tick rate: ~10 FPS for comfortable snake speed
TICK_INTERVAL = 1 / 10


class SnakeApp(App):
    """Terminal Snake game application."""

    CSS_PATH = Path(__file__).parent / "styles" / "snake.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("w", "move_up", "Up", show=False),
        Binding("s", "move_down", "Down", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("r", "reset", "Reset"),
        Binding("p", "pause", "Pause"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Snake"

    def __init__(self) -> None:
        super().__init__()
        self.config = BoardConfig(columns=23, rows=20)
        self.state = create_initial_state(self.config)
        self._game_timer: Timer | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header(show_clock=True)
        yield Container(
            HUD(id="hud"),
            GameBoard(config=self.config, id="game-board"),
            id="game-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start the game loop when app mounts."""
        self._board = self.query_one("#game-board", GameBoard)
        self._hud = self.query_one("#hud", HUD)
        self._start_game_loop()
        self._update_widgets()
        # Apply saved theme
        self.theme = get_theme()

    def _start_game_loop(self) -> None:
        """Initialize the game timer."""
        self._game_timer = self.set_interval(
            TICK_INTERVAL,
            self._game_tick,
        )

    def _game_tick(self) -> None:
        """Process one game tick."""
        if self.state.is_game_over or self.state.is_paused:
            return

        self.state = tick(self.state, self.config)
        self._update_widgets()

        if self.state.is_game_over and self._game_timer:
            self._game_timer.pause()

    def _update_widgets(self) -> None:
        """Push state to child widgets."""
        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
            )

        if self._board:
            self._board.update_state(
                snake_cells=self.state.snake.cells,
                apple=self.state.apple,
                is_game_over=self.state.is_game_over,
            )

    # Direction actions
    def action_move_up(self) -> None:
        """Move snake up."""
        self.state = change_direction(self.state, Direction.UP)

    def action_move_down(self) -> None:
        """Move snake down."""
        self.state = change_direction(self.state, Direction.DOWN)

    def action_move_left(self) -> None:
        """Move snake left."""
        self.state = change_direction(self.state, Direction.LEFT)

    def action_move_right(self) -> None:
        """Move snake right."""
        self.state = change_direction(self.state, Direction.RIGHT)

    def action_reset(self) -> None:
        """Reset game to initial state."""
        # Preserve high score across resets
        high_score = self.state.high_score
        self.state = create_initial_state(self.config, high_score=high_score)

        if self._game_timer:
            self._game_timer.resume()

        self._update_widgets()

    def action_pause(self) -> None:
        """Toggle pause state."""
        self.state = toggle_pause(self.state)

        if self._game_timer:
            if self.state.is_paused:
                self._game_timer.pause()
            else:
                self._game_timer.resume()

        self._update_widgets()

    def action_toggle_theme(self) -> None:
        """Switch between dark and light themes."""
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        # Refresh the game board to apply new theme colors
        if self._board:
            self._board.refresh()


def main() -> None:
    """Run the Terminal Snake application."""
    app = SnakeApp()
    app.run()


if __name__ == "__main__":
    main()
