from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from rich.segment import Segment
from rich.style import Style
from ..models import Position, BoardConfig

CHARS = {
    "empty": " ",
    "snake_head": "\u2588",
    "snake_body": "\u2593",
    "snake_tail": "\u2591",
    "apple": "\u25cf",
    "border_h": "\u2500",
    "border_v": "\u2502",
    "corner_tl": "\u250c",
    "corner_tr": "\u2510",
    "corner_bl": "\u2514",
    "corner_br": "\u2518",
}

class GameBoard(Widget):
    DEFAULT_CSS = """
    GameBoard {
        width: auto;
        height: auto;
    }
    """

    def __init__(
        self,
        config: BoardConfig | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.config = config or BoardConfig()
        self._snake_cells: tuple[Position, ...] = ()
        self._snake_set: dict[Position, str] = {}
        self._apple: Position = Position(0, 0)
        self._is_game_over: bool = False
        self._styles: dict[str, Style] = {}
        self._last_theme: str | None = None

    def update_state(
        self,
        snake_cells: tuple[Position, ...],
        apple: Position,
        is_game_over: bool,
    ) -> None:
        self._snake_cells = snake_cells
        self._apple = apple
        self._is_game_over = is_game_over
        
        # O(N) preprocessing for O(1) lookup during render
        self._snake_set.clear()
        if snake_cells:
            self._snake_set[snake_cells[0]] = "head"
            for cell in snake_cells[1:-1]:
                self._snake_set[cell] = "body"
            if len(snake_cells) > 1:
                self._snake_set[snake_cells[-1]] = "tail"
        
        self.refresh()

    def _refresh_styles(self) -> None:
        current_theme = getattr(self.app, "theme", "textual-dark")
        if self._styles and self._last_theme == current_theme:
            return

        self._last_theme = current_theme
        is_dark = current_theme == "textual-dark"

        if is_dark:
            bg_color = "#0a0a0a"
            self._styles = {
                "head": Style(color="bright_white", bgcolor=bg_color, bold=True),
                "body": Style(color="grey70", bgcolor=bg_color),
                "tail": Style(color="grey50", bgcolor=bg_color),
                "apple": Style(color="bright_red", bgcolor=bg_color, bold=True),
                "empty": Style(color="#1a1a1a", bgcolor=bg_color),
                "border": Style(color="bright_cyan", bgcolor=bg_color),
            }
        else:
            bg_color = "#e8e8e8"
            self._styles = {
                "head": Style(color="grey11", bgcolor=bg_color, bold=True),
                "body": Style(color="grey35", bgcolor=bg_color),
                "tail": Style(color="grey58", bgcolor=bg_color),
                "apple": Style(color="red3", bgcolor=bg_color, bold=True),
                "empty": Style(color="#d0d0d0", bgcolor=bg_color),
                "border": Style(color="dark_cyan", bgcolor=bg_color),
            }

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return (self.config.columns * 2) + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.config.rows + 2

    def render_line(self, y: int) -> Strip:
        self._refresh_styles()
        styles = self._styles
        border_style = styles["border"]

        segments: list[Segment] = []

        if y == 0:
            segments.append(Segment(CHARS["corner_tl"], border_style))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.columns * 2), border_style)
            )
            segments.append(Segment(CHARS["corner_tr"], border_style))
            return Strip(segments)

        if y == self.config.rows + 1:
            segments.append(Segment(CHARS["corner_bl"], border_style))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.columns * 2), border_style)
            )
            segments.append(Segment(CHARS["corner_br"], border_style))
            return Strip(segments)

        row_y = y - 1
        segments.append(Segment(CHARS["border_v"], border_style))
        
        for col_x in range(self.config.columns):
            pos = Position(col_x, row_y)
            if pos == self._apple:
                segments.append(Segment(CHARS["apple"] + " ", styles["apple"]))
            elif pos in self._snake_set:
                part_type = self._snake_set[pos]
                char_key = f"snake_{part_type}"
                segments.append(Segment(CHARS[char_key] + " ", styles[part_type]))
            else:
                segments.append(Segment(CHARS["empty"] + " ", styles["empty"]))

        segments.append(Segment(CHARS["border_v"], border_style))
        return Strip(segments)
