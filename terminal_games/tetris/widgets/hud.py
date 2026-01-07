from textual.widget import Widget
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static, Digits, Label


class HUD(Widget):
    DEFAULT_CSS = """
    HUD {
        width: 100%;
        height: 5;
        layout: horizontal;
        padding: 0 1;
    }

    HUD .hud-stat {
        width: auto;
        height: auto;
        margin-right: 2;
        align-horizontal: center;
    }

    HUD Label {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }

    HUD Digits {
        width: auto;
        min-width: 8;
        text-align: center;
    }

    HUD .status-display {
        width: 1fr;
        content-align: right middle;
        padding-right: 2;
    }
    """

    level: reactive[int] = reactive(1)
    score: reactive[int] = reactive(0)
    high_score: reactive[int] = reactive(0)
    lines: reactive[int] = reactive(0)
    is_paused: reactive[bool] = reactive(False)
    is_game_over: reactive[bool] = reactive(False)

    def compose(self):
        yield Vertical(
            Label("LEVEL"),
            Digits(id="level-digits"),
            classes="hud-stat"
        )
        yield Vertical(
            Label("LINES"),
            Digits(id="lines-digits"),
            classes="hud-stat"
        )
        yield Vertical(
            Label("SCORE"),
            Digits(id="score-digits"),
            classes="hud-stat"
        )
        yield Vertical(
            Label("HIGH SCORE"),
            Digits(id="high-score-digits"),
            classes="hud-stat"
        )
        yield Static(id="status-display", classes="status-display")

    def on_mount(self) -> None:
        self._update_level_display()
        self._update_lines_display()
        self._update_score_display()
        self._update_high_score_display()
        self._update_status_display()

    def update_state(
        self,
        level: int,
        score: int,
        high_score: int,
        lines: int,
        is_paused: bool,
        is_game_over: bool,
    ) -> None:
        self.level = level
        self.score = score
        self.high_score = high_score
        self.lines = lines
        self.is_paused = is_paused
        self.is_game_over = is_game_over

    def watch_level(self, level: int) -> None:
        self._update_level_display()

    def watch_score(self, score: int) -> None:
        self._update_score_display()

    def watch_high_score(self, high_score: int) -> None:
        self._update_high_score_display()

    def watch_lines(self, lines: int) -> None:
        self._update_lines_display()

    def watch_is_paused(self, is_paused: bool) -> None:
        self._update_status_display()

    def watch_is_game_over(self, is_game_over: bool) -> None:
        self._update_status_display()

    def _update_level_display(self) -> None:
        try:
            self.query_one("#level-digits", Digits).update(f"{self.level}")
        except Exception:
            pass

    def _update_lines_display(self) -> None:
        try:
            self.query_one("#lines-digits", Digits).update(f"{self.lines}")
        except Exception:
            pass

    def _update_score_display(self) -> None:
        try:
            self.query_one("#score-digits", Digits).update(f"{self.score:06d}")
        except Exception:
            pass

    def _update_high_score_display(self) -> None:
        try:
            self.query_one("#high-score-digits", Digits).update(f"{self.high_score:06d}")
        except Exception:
            pass

    def _update_status_display(self) -> None:
        try:
            display = self.query_one("#status-display", Static)
            if self.is_game_over:
                display.update("[bold red]GAME OVER[/]\n[dim]Press R to restart[/]")
            elif self.is_paused:
                display.update("[bold yellow]PAUSED[/]\n[dim]Press P to resume[/]")
            else:
                display.update("")
        except Exception:
            pass
