"""Game board widget for rendering the snake game."""

from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from rich.segment import Segment
from rich.style import Style

from ..models import Position, BoardConfig


# Unicode characters for rendering
CHARS = {
    "empty": " ",
    "snake_head": "\u2588",  # █ FULL BLOCK
    "snake_body": "\u2593",  # ▓ DARK SHADE
    "snake_tail": "\u2591",  # ░ LIGHT SHADE
    "apple": "\u25cf",  # ● BLACK CIRCLE
    "border_h": "\u2500",  # ─ BOX DRAWINGS LIGHT HORIZONTAL
    "border_v": "\u2502",  # │ BOX DRAWINGS LIGHT VERTICAL
    "corner_tl": "\u250c",  # ┌ BOX DRAWINGS LIGHT DOWN AND RIGHT
    "corner_tr": "\u2510",  # ┐ BOX DRAWINGS LIGHT DOWN AND LEFT
    "corner_bl": "\u2514",  # └ BOX DRAWINGS LIGHT UP AND RIGHT
    "corner_br": "\u2518",  # ┘ BOX DRAWINGS LIGHT UP AND LEFT
}


class GameBoard(Widget):
    """Custom widget that renders the snake game board."""

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
        self._apple: Position = Position(0, 0)
        self._is_game_over: bool = False

    def update_state(
        self,
        snake_cells: tuple[Position, ...],
        apple: Position,
        is_game_over: bool,
    ) -> None:
        """Update board state and trigger redraw."""
        self._snake_cells = snake_cells
        self._apple = apple
        self._is_game_over = is_game_over
        self.refresh()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return width needed for board + borders."""
        # Each cell is 2 chars wide + 2 border chars
        return (self.config.columns * 2) + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return height needed for board + borders."""
        return self.config.rows + 2  # +2 for top/bottom borders

    def render_line(self, y: int) -> Strip:
        """Render a single line of the game board."""
        # Get theme-aware styles based on app theme
        is_dark = self.app.theme == "textual-dark" if hasattr(self.app, "theme") else True

        if is_dark:
            bg_color = "#0a0a0a"
            style_head = Style(color="bright_white", bgcolor=bg_color, bold=True)
            style_body = Style(color="grey70", bgcolor=bg_color)
            style_tail = Style(color="grey50", bgcolor=bg_color)
            style_apple = Style(color="bright_red", bgcolor=bg_color, bold=True)
            style_empty = Style(color="#1a1a1a", bgcolor=bg_color)
            style_border = Style(color="bright_cyan", bgcolor=bg_color)
        else:
            bg_color = "#e8e8e8"
            style_head = Style(color="grey11", bgcolor=bg_color, bold=True)
            style_body = Style(color="grey35", bgcolor=bg_color)
            style_tail = Style(color="grey58", bgcolor=bg_color)
            style_apple = Style(color="red3", bgcolor=bg_color, bold=True)
            style_empty = Style(color="#d0d0d0", bgcolor=bg_color)
            style_border = Style(color="dark_cyan", bgcolor=bg_color)

        segments: list[Segment] = []

        # Top border
        if y == 0:
            segments.append(Segment(CHARS["corner_tl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.columns * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_tr"], style_border))
            return Strip(segments)

        # Bottom border
        if y == self.config.rows + 1:
            segments.append(Segment(CHARS["corner_bl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.columns * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_br"], style_border))
            return Strip(segments)

        # Game row (adjust y for border offset)
        row_y = y - 1

        # Left border
        segments.append(Segment(CHARS["border_v"], style_border))

        # Build row content
        for col_x in range(self.config.columns):
            pos = Position(col_x, row_y)
            char, style = self._get_cell_char_style(
                pos, style_head, style_body, style_tail, style_apple, style_empty
            )
            # Double-width characters for square cells
            segments.append(Segment(char + " ", style))

        # Right border
        segments.append(Segment(CHARS["border_v"], style_border))

        return Strip(segments)

    def _get_cell_char_style(
        self,
        pos: Position,
        style_head: Style,
        style_body: Style,
        style_tail: Style,
        style_apple: Style,
        style_empty: Style,
    ) -> tuple[str, Style]:
        """Determine character and style for a cell."""
        # Check apple
        if pos == self._apple:
            return CHARS["apple"], style_apple

        # Check snake
        if pos in self._snake_cells:
            idx = self._snake_cells.index(pos)
            if idx == 0:  # Head
                return CHARS["snake_head"], style_head
            elif idx == len(self._snake_cells) - 1:  # Tail
                return CHARS["snake_tail"], style_tail
            else:  # Body
                return CHARS["snake_body"], style_body

        # Empty cell
        return CHARS["empty"], style_empty
