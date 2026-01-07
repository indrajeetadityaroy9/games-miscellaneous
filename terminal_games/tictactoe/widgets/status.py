from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static
class Status(Widget):
    DEFAULT_CSS = """
    Status {
        width: 100%;
        height: 3;
        layout: horizontal;
    }
    Status .status-text {
        width: 1fr;
        padding: 0 2;
        text-style: bold;
        content-align: center middle;
    }
    """
    message: reactive[str] = reactive("Your turn (O)")
    is_game_over: reactive[bool] = reactive(False)
    def compose(self):
        yield Static(id="status-text", classes="status-text")
    def on_mount(self) -> None:
        self._update_display()
    def update_state(self, message: str, is_game_over: bool) -> None:
        self.message = message
        self.is_game_over = is_game_over
    def watch_message(self, message: str) -> None:
        self._update_display()
    def watch_is_game_over(self, is_game_over: bool) -> None:
        self._update_display()
    def _update_display(self) -> None:
        try:
            display = self.query_one("#status-text", Static)
            if self.is_game_over:
                if "Win" in self.message:
                    display.update(f"[bold green]{self.message}[/] [dim]Press R to restart[/]")
                elif "Lose" in self.message:
                    display.update(f"[bold red]{self.message}[/] [dim]Press R to restart[/]")
                else:  
                    display.update(f"[bold yellow]{self.message}[/] [dim]Press R to restart[/]")
            else:
                display.update(f"[bold cyan]{self.message}[/]")
        except Exception:
            pass
