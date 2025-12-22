"""Game board widget for rendering the Tetris game."""

from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from rich.segment import Segment
from rich.style import Style

from ..models import Position, Tetromino, BoardConfig


# Unicode characters for rendering
CHARS = {
    "filled": "\u2588",  # █ FULL BLOCK
    "empty": " ",
    "border_h": "\u2500",  # ─
    "border_v": "\u2502",  # │
    "corner_tl": "\u250c",  # ┌
    "corner_tr": "\u2510",  # ┐
    "corner_bl": "\u2514",  # └
    "corner_br": "\u2518",  # ┘
}

# Color mapping for dark theme
COLORS_DARK = {
    0: "#1a1a1a",    # Empty cell background
    1: "cyan",       # I - cyan
    2: "blue",       # J - blue
    3: "orange1",    # L - orange
    4: "yellow",     # O - yellow
    5: "green",      # S - green
    6: "magenta",    # T - purple
    7: "red",        # Z - red
}

# Color mapping for light theme
COLORS_LIGHT = {
    0: "#d0d0d0",    # Empty cell background
    1: "dark_cyan",
    2: "dark_blue",
    3: "dark_orange",
    4: "gold3",
    5: "dark_green",
    6: "dark_magenta",
    7: "dark_red",
}


class GameBoard(Widget):
    """Custom widget that renders the Tetris game board."""

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
        self._board: list[list[int]] = []
        self._current_piece: Tetromino | None = None
        self._piece_position: Position = Position(0, 0)
        self._is_game_over: bool = False

    def update_state(
        self,
        board: list[list[int]],
        current_piece: Tetromino | None,
        piece_position: Position,
        is_game_over: bool,
    ) -> None:
        """Update board state and trigger redraw."""
        self._board = board
        self._current_piece = current_piece
        self._piece_position = piece_position
        self._is_game_over = is_game_over
        self.refresh()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return width needed for board + borders."""
        # Each cell is 2 chars wide + 2 border chars
        return (self.config.width * 2) + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return height needed for board + borders."""
        return self.config.height + 2  # +2 for top/bottom borders

    def _get_cell_at(self, x: int, y: int) -> int:
        """Get cell value at position, including current falling piece."""
        # Check if current piece occupies this cell
        if self._current_piece is not None:
            piece_x = x - self._piece_position.x
            piece_y = y - self._piece_position.y

            if (0 <= piece_y < len(self._current_piece.shape) and
                0 <= piece_x < len(self._current_piece.shape[0])):
                cell = self._current_piece.shape[piece_y][piece_x]
                if cell != 0:
                    return cell

        # Return board cell
        if 0 <= y < len(self._board) and 0 <= x < len(self._board[0]):
            return self._board[y][x]

        return 0

    def render_line(self, y: int) -> Strip:
        """Render a single line of the game board."""
        is_dark = self.app.theme == "textual-dark" if hasattr(self.app, "theme") else True
        colors = COLORS_DARK if is_dark else COLORS_LIGHT
        bg_color = "#0a0a0a" if is_dark else "#e8e8e8"

        style_border = Style(color="bright_cyan" if is_dark else "dark_cyan", bgcolor=bg_color)

        segments: list[Segment] = []

        # Top border
        if y == 0:
            segments.append(Segment(CHARS["corner_tl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.width * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_tr"], style_border))
            return Strip(segments)

        # Bottom border
        if y == self.config.height + 1:
            segments.append(Segment(CHARS["corner_bl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.width * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_br"], style_border))
            return Strip(segments)

        # Game row (adjust y for border offset)
        row_y = y - 1

        # Left border
        segments.append(Segment(CHARS["border_v"], style_border))

        # Build row content
        for col_x in range(self.config.width):
            cell = self._get_cell_at(col_x, row_y)

            if cell == 0:
                # Empty cell
                style = Style(color=colors[0], bgcolor=bg_color)
                char = CHARS["empty"]
            else:
                # Filled cell with piece color
                color = colors.get(cell, colors[1])
                style = Style(color=color, bgcolor=bg_color, bold=True)
                char = CHARS["filled"]

            # Double-width for square appearance
            segments.append(Segment(char + " ", style))

        # Right border
        segments.append(Segment(CHARS["border_v"], style_border))

        return Strip(segments)
