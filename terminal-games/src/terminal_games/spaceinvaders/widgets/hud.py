"""HUD widget for displaying Space Invaders game status."""

from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static


class HUD(Widget):
    """Heads-up display showing score, level, and status."""

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
        content-align: center middle;
    }
    """

    # Reactive properties
    level: reactive[int] = reactive(1)
    score: reactive[int] = reactive(0)
    high_score: reactive[int] = reactive(0)
    is_paused: reactive[bool] = reactive(False)
    is_game_over: reactive[bool] = reactive(False)
    is_won: reactive[bool] = reactive(False)

    def compose(self):
        """Build HUD layout."""
        yield Static(id="score-display", classes="hud-stat")
        yield Static(id="status-display", classes="status-display")
        yield Static(id="level-display", classes="hud-stat")
        yield Static(id="high-score-display", classes="hud-stat")

    def on_mount(self) -> None:
        """Initialize displays on mount."""
        self._update_score_display()
        self._update_level_display()
        self._update_high_score_display()
        self._update_status_display()

    def update_state(
        self,
        level: int,
        score: int,
        high_score: int,
        is_paused: bool,
        is_game_over: bool,
        is_won: bool,
    ) -> None:
        """Update all HUD values."""
        self.level = level
        self.score = score
        self.high_score = high_score
        self.is_paused = is_paused
        self.is_game_over = is_game_over
        self.is_won = is_won

    def watch_level(self, level: int) -> None:
        self._update_level_display()

    def watch_score(self, score: int) -> None:
        self._update_score_display()

    def watch_high_score(self, high_score: int) -> None:
        self._update_high_score_display()

    def watch_is_paused(self, is_paused: bool) -> None:
        self._update_status_display()

    def watch_is_game_over(self, is_game_over: bool) -> None:
        self._update_status_display()

    def watch_is_won(self, is_won: bool) -> None:
        self._update_status_display()

    def _update_score_display(self) -> None:
        try:
            display = self.query_one("#score-display", Static)
            display.update(f"[dim]SCORE[/] {self.score:05d}")
        except Exception:
            pass

    def _update_level_display(self) -> None:
        try:
            display = self.query_one("#level-display", Static)
            display.update(f"[dim]LVL[/] {self.level}")
        except Exception:
            pass

    def _update_high_score_display(self) -> None:
        try:
            display = self.query_one("#high-score-display", Static)
            display.update(f"[dim]HI[/] {self.high_score:05d}")
        except Exception:
            pass

    def _update_status_display(self) -> None:
        try:
            display = self.query_one("#status-display", Static)
            if self.is_game_over:
                display.update("[bold red]GAME OVER[/] [dim]Press R to restart[/]")
            elif self.is_won:
                if self.level >= 8:
                    display.update("[bold green]YOU WIN![/] [dim]Press R to play again[/]")
                else:
                    display.update("[bold green]STAGE CLEAR![/] [dim]Press R for next level[/]")
            elif self.is_paused:
                display.update("[bold yellow]PAUSED[/] [dim]Press P to resume[/]")
            else:
                display.update("")
        except Exception:
            pass
