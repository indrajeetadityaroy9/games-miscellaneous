from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from rich.segment import Segment
from rich.style import Style
from ..models import Position, Tetromino, BoardConfig

CHARS = {
    "filled": "\u2588",
    "empty": " ",
    "border_h": "\u2500",
    "border_v": "\u2502",
    "corner_tl": "\u250c",
    "corner_tr": "\u2510",
    "corner_bl": "\u2514",
    "corner_br": "\u2518",
}

COLORS_DARK = {
    0: "#1a1a1a",
    1: "cyan",
    2: "blue",
    3: "orange1",
    4: "yellow",
    5: "green",
    6: "magenta",
    7: "red",
}

COLORS_LIGHT = {
    0: "#d0d0d0",
    1: "dark_cyan",
    2: "dark_blue",
    3: "dark_orange",
    4: "gold3",
    5: "dark_green",
    6: "dark_magenta",
    7: "dark_red",
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
        self._board: list[list[int]] = []
        self._current_piece: Tetromino | None = None
        self._piece_position: Position = Position(0, 0)
        self._is_game_over: bool = False
        self._styles: dict = {}
        self._last_theme: str | None = None

    def update_state(
        self,
        board: list[list[int]],
        current_piece: Tetromino | None,
        piece_position: Position,
        is_game_over: bool,
    ) -> None:
        self._board = board
        self._current_piece = current_piece
        self._piece_position = piece_position
        self._is_game_over = is_game_over
        self.refresh()

    def _refresh_styles(self) -> None:
        current_theme = getattr(self.app, "theme", "textual-dark")
        if self._styles and self._last_theme == current_theme:
            return

        self._last_theme = current_theme
        is_dark = current_theme == "textual-dark"
        colors = COLORS_DARK if is_dark else COLORS_LIGHT
        bg_color = "#0a0a0a" if is_dark else "#e8e8e8"

        self._styles = {
            "border": Style(color="bright_cyan" if is_dark else "dark_cyan", bgcolor=bg_color),
            0: Style(color=colors[0], bgcolor=bg_color),
        }
        for i in range(1, 8):
            self._styles[i] = Style(color=colors[i], bgcolor=bg_color, bold=True)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return (self.config.width * 2) + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.config.height + 2

    def _get_cell_at(self, x: int, y: int) -> int:
        if self._current_piece is not None:
            piece_x = x - self._piece_position.x
            piece_y = y - self._piece_position.y
            if (0 <= piece_y < len(self._current_piece.shape) and
                0 <= piece_x < len(self._current_piece.shape[0])):
                cell = self._current_piece.shape[piece_y][piece_x]
                if cell != 0:
                    return cell
        if 0 <= y < len(self._board) and 0 <= x < len(self._board[0]):
            return self._board[y][x]
        return 0

    def render_line(self, y: int) -> Strip:
        self._refresh_styles()
        styles = self._styles
        style_border = styles["border"]

        segments: list[Segment] = []

        if y == 0:
            segments.append(Segment(CHARS["corner_tl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.width * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_tr"], style_border))
            return Strip(segments)

        if y == self.config.height + 1:
            segments.append(Segment(CHARS["corner_bl"], style_border))
            segments.append(
                Segment(CHARS["border_h"] * (self.config.width * 2), style_border)
            )
            segments.append(Segment(CHARS["corner_br"], style_border))
            return Strip(segments)

        row_y = y - 1
        segments.append(Segment(CHARS["border_v"], style_border))
        
        for col_x in range(self.config.width):
            cell = self._get_cell_at(col_x, row_y)
            if cell == 0:
                segments.append(Segment(CHARS["empty"] + " ", styles[0]))
            else:
                # Fallback to default style 1 if cell type unknown
                segments.append(Segment(CHARS["filled"] + " ", styles.get(cell, styles[1])))
                
        segments.append(Segment(CHARS["border_v"], style_border))
        return Strip(segments)
