"""HUD widget for displaying game status."""

from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static


class HUD(Widget):
    """Heads-up display showing score, level, and controls."""

    DEFAULT_CSS = """
    HUD {
        width: 100%;
        height: 3;
        layout: horizontal;
    }

    HUD .hud-stat {
        width: auto;
        padding: 0 2;
        text-style: bold;
        content-align: center middle;
    }

    HUD .status-display {
        width: 1fr;
        padding: 0 2;
        content-align: left middle;
    }
    """

    # Reactive properties trigger automatic updates
    level: reactive[int] = reactive(1)
    score: reactive[int] = reactive(0)
    high_score: reactive[int] = reactive(0)
    is_paused: reactive[bool] = reactive(False)
    is_game_over: reactive[bool] = reactive(False)

    def compose(self):
        """Build HUD layout."""
        yield Static(id="level-display", classes="hud-stat")
        yield Static(id="score-display", classes="hud-stat")
        yield Static(id="high-score-display", classes="hud-stat")
        yield Static(id="status-display", classes="status-display")

    def on_mount(self) -> None:
        """Initialize displays on mount."""
        self._update_level_display()
        self._update_score_display()
        self._update_high_score_display()
        self._update_status_display()

    def update_state(
        self,
        level: int,
        score: int,
        high_score: int,
        is_paused: bool,
        is_game_over: bool,
    ) -> None:
        """Update all HUD values."""
        self.level = level
        self.score = score
        self.high_score = high_score
        self.is_paused = is_paused
        self.is_game_over = is_game_over

    def watch_level(self, level: int) -> None:
        """Update level display when level changes."""
        self._update_level_display()

    def watch_score(self, score: int) -> None:
        """Update score display when score changes."""
        self._update_score_display()

    def watch_high_score(self, high_score: int) -> None:
        """Update high score display."""
        self._update_high_score_display()

    def watch_is_paused(self, is_paused: bool) -> None:
        """Update pause indicator."""
        self._update_status_display()

    def watch_is_game_over(self, is_game_over: bool) -> None:
        """Update game over indicator."""
        self._update_status_display()

    def _update_level_display(self) -> None:
        """Update the level display."""
        try:
            display = self.query_one("#level-display", Static)
            display.update(f"[dim]LVL[/] {self.level}/8")
        except Exception:
            pass  # Widget not mounted yet

    def _update_score_display(self) -> None:
        """Update the score display."""
        try:
            display = self.query_one("#score-display", Static)
            display.update(f"[dim]SCORE[/] {self.score:04d}")
        except Exception:
            pass

    def _update_high_score_display(self) -> None:
        """Update the high score display."""
        try:
            display = self.query_one("#high-score-display", Static)
            display.update(f"[dim]HIGH[/] {self.high_score:04d}")
        except Exception:
            pass

    def _update_status_display(self) -> None:
        """Update the status display based on game state."""
        try:
            display = self.query_one("#status-display", Static)
            if self.is_game_over:
                display.update("[bold red]GAME OVER[/] [dim]Press R to restart[/]")
            elif self.is_paused:
                display.update("[bold yellow]PAUSED[/] [dim]Press P to resume[/]")
            else:
                display.update("")
        except Exception:
            pass
