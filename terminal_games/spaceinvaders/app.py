"""Main Textual application for Terminal Space Invaders."""

from dataclasses import replace
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from .models import BOARD_WIDTH
from .game_logic import (
    create_initial_state,
    move_player_left,
    move_player_right,
    shoot_player_bullet,
    update_player_bullets,
    update_enemy_bullets,
    update_enemies,
    enemy_shoot,
    check_collisions,
    check_win,
    toggle_pause,
    reset_shoot_cooldown,
    get_enemy_move_interval,
    get_enemy_shoot_interval,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme


class SpaceInvadersApp(App):
    """Terminal Space Invaders game application."""

    CSS_PATH = Path(__file__).parent / "styles" / "spaceinvaders.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("left", "move_left", "Left", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("space", "shoot", "Fire"),
        Binding("p", "pause", "Pause"),
        Binding("r", "reset", "Restart"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Space Invaders"

    def __init__(self) -> None:
        super().__init__()
        self.state = create_initial_state()
        self._board: GameBoard | None = None
        self._hud: HUD | None = None

        # Timers
        self._game_timer: Timer | None = None
        self._enemy_move_timer: Timer | None = None
        self._enemy_shoot_timer: Timer | None = None
        self._shoot_cooldown_timer: Timer | None = None

        # Movement state for continuous movement
        self._moving_left = False
        self._moving_right = False

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header(show_clock=True)
        yield Container(
            HUD(id="hud"),
            GameBoard(id="game-board"),
            id="game-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start the game loop when app mounts."""
        self._board = self.query_one("#game-board", GameBoard)
        self._hud = self.query_one("#hud", HUD)
        self._start_timers()
        self._update_widgets()
        # Apply saved theme
        self.theme = get_theme()

    def _start_timers(self) -> None:
        """Start all game timers."""
        # Main game tick (bullet movement, collisions)
        self._game_timer = self.set_interval(0.05, self._game_tick)

        # Enemy movement timer
        interval = get_enemy_move_interval(self.state.level)
        self._enemy_move_timer = self.set_interval(interval, self._enemy_move_tick)

        # Enemy shooting timer
        shoot_interval = get_enemy_shoot_interval(self.state.level)
        self._enemy_shoot_timer = self.set_interval(shoot_interval, self._enemy_shoot_tick)

    def _stop_timers(self) -> None:
        """Stop all game timers."""
        if self._game_timer:
            self._game_timer.stop()
        if self._enemy_move_timer:
            self._enemy_move_timer.stop()
        if self._enemy_shoot_timer:
            self._enemy_shoot_timer.stop()
        if self._shoot_cooldown_timer:
            self._shoot_cooldown_timer.stop()

    def _restart_timers(self) -> None:
        """Restart timers with current level settings."""
        self._stop_timers()
        self._start_timers()

    def _game_tick(self) -> None:
        """Main game loop tick."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return

        # Handle continuous movement
        if self._moving_left:
            self.state = move_player_left(self.state)
        if self._moving_right:
            self.state = move_player_right(self.state)

        # Update bullets
        self.state = update_player_bullets(self.state)
        self.state = update_enemy_bullets(self.state)

        # Check collisions
        self.state = check_collisions(self.state)

        # Check win condition
        self.state = check_win(self.state)

        self._update_widgets()

    def _enemy_move_tick(self) -> None:
        """Enemy movement tick."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return

        self.state = update_enemies(self.state)
        self._update_widgets()

    def _enemy_shoot_tick(self) -> None:
        """Enemy shooting tick."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return

        self.state = enemy_shoot(self.state)
        self._update_widgets()

    def _reset_shoot_cooldown(self) -> None:
        """Reset player shooting cooldown."""
        self.state = reset_shoot_cooldown(self.state)

    def _update_widgets(self) -> None:
        """Push state to child widgets."""
        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
                is_won=self.state.is_won,
            )

        if self._board:
            self._board.update_state(
                player=self.state.player,
                enemies=self.state.enemies,
                player_bullets=self.state.player_bullets,
                enemy_bullets=self.state.enemy_bullets,
                is_game_over=self.state.is_game_over,
                is_won=self.state.is_won,
            )

    # Key press handlers for continuous movement
    def on_key(self, event) -> None:
        """Handle key press for continuous movement."""
        if event.key == "left" or event.key == "a":
            self._moving_left = True
        elif event.key == "right" or event.key == "d":
            self._moving_right = True

    def on_key_up(self, event) -> None:
        """Handle key release."""
        if hasattr(event, 'key'):
            if event.key == "left" or event.key == "a":
                self._moving_left = False
            elif event.key == "right" or event.key == "d":
                self._moving_right = False

    # Action handlers
    def action_move_left(self) -> None:
        """Move player left."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        self.state = move_player_left(self.state)
        self._update_widgets()

    def action_move_right(self) -> None:
        """Move player right."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        self.state = move_player_right(self.state)
        self._update_widgets()

    def action_shoot(self) -> None:
        """Fire a bullet."""
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return

        if self.state.can_shoot:
            self.state = shoot_player_bullet(self.state)
            self._update_widgets()

            # Start cooldown timer
            if self._shoot_cooldown_timer:
                self._shoot_cooldown_timer.stop()
            self._shoot_cooldown_timer = self.set_timer(0.25, self._reset_shoot_cooldown)

    def action_pause(self) -> None:
        """Toggle pause state."""
        self.state = toggle_pause(self.state)
        self._update_widgets()

    def action_reset(self) -> None:
        """Reset or advance to next level."""
        high_score = self.state.high_score

        if self.state.is_won and self.state.level < 8:
            # Advance to next level
            next_level = self.state.level + 1
            current_score = self.state.score
            self.state = create_initial_state(level=next_level, high_score=high_score)
            self.state = replace(self.state, score=current_score)  # Keep score across levels
        else:
            # Full reset
            self.state = create_initial_state(level=1, high_score=high_score)

        self._moving_left = False
        self._moving_right = False
        self._restart_timers()
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
    """Run the Terminal Space Invaders application."""
    app = SpaceInvadersApp()
    app.run()


if __name__ == "__main__":
    main()
