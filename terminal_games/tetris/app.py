"""Main Textual application for Terminal Tetris."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from .models import BoardConfig, GameState
from .game_logic import (
    create_initial_state,
    move_left,
    move_right,
    move_down,
    try_rotate,
    do_hard_drop,
    toggle_pause,
    calculate_speed,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme


class TetrisApp(App):
    """Terminal Tetris game application."""

    CSS_PATH = Path(__file__).parent / "styles" / "tetris.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("up", "rotate", "Rotate", show=False),
        Binding("w", "rotate", "Rotate", show=False),
        Binding("down", "soft_drop", "Down", show=False),
        Binding("s", "soft_drop", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("space", "hard_drop", "Drop"),
        Binding("r", "reset", "Reset"),
        Binding("p", "pause", "Pause"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Tetris"

    def __init__(self) -> None:
        super().__init__()
        self.config = BoardConfig(width=10, height=18)
        self.state = create_initial_state(self.config)
        self._gravity_timer: Timer | None = None
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
        self._start_gravity()
        self._update_widgets()
        # Apply saved theme
        self.theme = get_theme()

    def _start_gravity(self) -> None:
        """Start or restart gravity timer based on current level."""
        if self._gravity_timer:
            self._gravity_timer.stop()

        speed = calculate_speed(self.state.level)
        self._gravity_timer = self.set_interval(speed, self._gravity_tick)

    def _gravity_tick(self) -> None:
        """Process gravity (piece falling down)."""
        if self.state.is_game_over or self.state.is_paused:
            return

        old_level = self.state.level
        self.state, locked = move_down(self.state, self.config)
        self._update_widgets()

        # Restart timer if level changed (speed increases)
        if self.state.level != old_level:
            self._start_gravity()

        if self.state.is_game_over and self._gravity_timer:
            self._gravity_timer.pause()

    def _update_widgets(self) -> None:
        """Push state to child widgets."""
        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                lines=self.state.lines_cleared,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
            )

        if self._board:
            self._board.update_state(
                board=self.state.board,
                current_piece=self.state.current_piece,
                piece_position=self.state.position,
                is_game_over=self.state.is_game_over,
            )

    # Movement actions
    def action_move_left(self) -> None:
        """Move piece left."""
        if self.state.is_game_over or self.state.is_paused:
            return
        self.state = move_left(self.state, self.config)
        self._update_widgets()

    def action_move_right(self) -> None:
        """Move piece right."""
        if self.state.is_game_over or self.state.is_paused:
            return
        self.state = move_right(self.state, self.config)
        self._update_widgets()

    def action_soft_drop(self) -> None:
        """Soft drop (move down faster)."""
        if self.state.is_game_over or self.state.is_paused:
            return
        old_level = self.state.level
        self.state, _ = move_down(self.state, self.config)
        self._update_widgets()

        if self.state.level != old_level:
            self._start_gravity()

    def action_rotate(self) -> None:
        """Rotate piece clockwise."""
        if self.state.is_game_over or self.state.is_paused:
            return
        self.state = try_rotate(self.state, self.config)
        self._update_widgets()

    def action_hard_drop(self) -> None:
        """Hard drop piece to bottom."""
        if self.state.is_game_over or self.state.is_paused:
            return
        old_level = self.state.level
        self.state = do_hard_drop(self.state, self.config)
        self._update_widgets()

        if self.state.level != old_level:
            self._start_gravity()

        if self.state.is_game_over and self._gravity_timer:
            self._gravity_timer.pause()

    def action_reset(self) -> None:
        """Reset game to initial state."""
        high_score = self.state.high_score
        self.state = create_initial_state(self.config, high_score=high_score)
        self._start_gravity()
        self._update_widgets()

    def action_pause(self) -> None:
        """Toggle pause state."""
        self.state = toggle_pause(self.state)

        if self._gravity_timer:
            if self.state.is_paused:
                self._gravity_timer.pause()
            else:
                self._gravity_timer.resume()

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
    """Run the Terminal Tetris application."""
    app = TetrisApp()
    app.run()


if __name__ == "__main__":
    main()
