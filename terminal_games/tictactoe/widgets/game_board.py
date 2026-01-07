from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget
from ..models import Board, Player


class GameBoard(Widget):
    DEFAULT_CSS = """
    GameBoard {
        width: auto;
        height: auto;
    }
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        cell_width: int = 11,
        cell_height: int = 5,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.CELL_WIDTH = cell_width
        self.CELL_HEIGHT = cell_height
        self.TOTAL_HEIGHT = self.CELL_HEIGHT * 3 + 4
        
        self._board: Board = list(range(9))
        self._cursor_position: int = 4
        self._winning_cells: tuple[int, ...] = ()
        self._is_game_over: bool = False
        self._styles: dict[str, Style] = {}
        self._last_theme: str | None = None

    def update_state(
        self,
        board: Board,
        cursor_position: int,
        winning_cells: tuple[int, ...],
        is_game_over: bool,
    ) -> None:
        self._board = board
        self._cursor_position = cursor_position
        self._winning_cells = winning_cells
        self._is_game_over = is_game_over
        self.refresh()

    def get_content_width(self, container, viewport):
        return 3 * self.CELL_WIDTH + 4

    def get_content_height(self, container, viewport, width):
        return self.TOTAL_HEIGHT

    def _refresh_styles(self) -> None:
        current_theme = getattr(self.app, "theme", "textual-dark")
        if self._styles and self._last_theme == current_theme:
            return

        self._last_theme = current_theme
        is_dark = current_theme == "textual-dark"

        if is_dark:
            colors = {
                "bg": "#0a0a0a",
                "border": "#555555",
                "x": "#00d4ff",
                "o": "#ff69b4",
                "cursor_bg": "#444400",
                "win_bg": "#2d5a2d",
            }
        else:
            colors = {
                "bg": "#f5f5f5",
                "border": "#666666",
                "x": "#0066cc",
                "o": "#cc0066",
                "cursor_bg": "#ffddaa",
                "win_bg": "#90ee90",
            }

        bg_color = colors["bg"]
        self._styles = {
            "border": Style(color=colors["border"], bgcolor=bg_color),
            "bg": Style(bgcolor=bg_color),
            "cursor": Style(bgcolor=colors["cursor_bg"]),
            "win": Style(bgcolor=colors["win_bg"]),
            "x": Style(color=colors["x"], bgcolor=bg_color, bold=True),
            "o": Style(color=colors["o"], bgcolor=bg_color, bold=True),
            "x_cursor": Style(color=colors["x"], bgcolor=colors["cursor_bg"], bold=True),
            "o_cursor": Style(color=colors["o"], bgcolor=colors["cursor_bg"], bold=True),
            "x_win": Style(color=colors["x"], bgcolor=colors["win_bg"], bold=True),
            "o_win": Style(color=colors["o"], bgcolor=colors["win_bg"], bold=True),
        }

    def render_line(self, y: int) -> Strip:
        self._refresh_styles()
        styles = self._styles
        style_border = styles["border"]
        
        cw = self.CELL_WIDTH
        h_line = "─" * cw
        
        # Border rows
        row_1_bottom = 1 + self.CELL_HEIGHT
        row_2_bottom = row_1_bottom + 1 + self.CELL_HEIGHT
        total_height = self.TOTAL_HEIGHT

        segments = []
        if y == 0:
            segments = [
                Segment(f"┌{h_line}┬{h_line}┬{h_line}┐", style_border)
            ]
            return Strip(segments)
        if y == total_height - 1:
            segments = [
                Segment(f"└{h_line}┴{h_line}┴{h_line}┘", style_border)
            ]
            return Strip(segments)
        if y == row_1_bottom or y == row_2_bottom:
            segments = [
                Segment(f"├{h_line}┼{h_line}┼{h_line}┤", style_border)
            ]
            return Strip(segments)

        row_info = self._get_row_info(y)
        if row_info is None:
            return Strip([])

        cell_row, line_in_cell = row_info
        segments.append(Segment("│", style_border))

        for col in range(3):
            cell_index = cell_row * 3 + col
            cell_value = self._board[cell_index]
            is_cursor = cell_index == self._cursor_position
            is_winning = cell_index in self._winning_cells

            # Determine background style
            if is_winning:
                bg_style = styles["win"]
            elif is_cursor:
                bg_style = styles["cursor"]
            else:
                bg_style = styles["bg"]
            
            # Content padding
            pad_len = (self.CELL_WIDTH - 1) // 2
            padding = " " * pad_len
            empty_cell = " " * self.CELL_WIDTH

            # Center vertically
            if line_in_cell == self.CELL_HEIGHT // 2:
                # Center line content (X or O or empty)
                if cell_value == Player.X:
                    if is_winning:
                        content_style = styles["x_win"]
                    elif is_cursor:
                        content_style = styles["x_cursor"]
                    else:
                        content_style = styles["x"]
                    segments.extend([
                        Segment(padding, bg_style),
                        Segment("X", content_style),
                        Segment(padding, bg_style),
                    ])
                elif cell_value == Player.O:
                    if is_winning:
                        content_style = styles["o_win"]
                    elif is_cursor:
                        content_style = styles["o_cursor"]
                    else:
                        content_style = styles["o"]
                    segments.extend([
                        Segment(padding, bg_style),
                        Segment("O", content_style),
                        Segment(padding, bg_style),
                    ])
                else:
                    # Empty
                    segments.append(Segment(empty_cell, bg_style))
            else:
                # Top/Bottom lines of the cell
                segments.append(Segment(empty_cell, bg_style))

            if col < 2:
                segments.append(Segment("│", style_border))

        segments.append(Segment("│", style_border))
        return Strip(segments)

    def _get_row_info(self, y: int) -> tuple[int, int] | None:
        # Row 0: 1 to CELL_HEIGHT
        row_0_start = 1
        row_0_end = row_0_start + self.CELL_HEIGHT
        
        # Row 1: row_0_end + 1 to row_0_end + 1 + CELL_HEIGHT
        row_1_start = row_0_end + 1
        row_1_end = row_1_start + self.CELL_HEIGHT
        
        # Row 2: row_1_end + 1 to row_1_end + 1 + CELL_HEIGHT
        row_2_start = row_1_end + 1
        row_2_end = row_2_start + self.CELL_HEIGHT

        if row_0_start <= y < row_0_end:
            return (0, y - row_0_start)
        elif row_1_start <= y < row_1_end:
            return (1, y - row_1_start)
        elif row_2_start <= y < row_2_end:
            return (2, y - row_2_start)
        return None
