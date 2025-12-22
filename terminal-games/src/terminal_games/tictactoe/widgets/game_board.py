"""Game board widget for Tic-Tac-Toe."""

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

from ..models import Board, Player


class GameBoard(Widget):
    """3x3 Tic-Tac-Toe grid with cursor navigation."""

    DEFAULT_CSS = """
    GameBoard {
        width: auto;
        height: auto;
    }
    """

    # Layout:
    # y=0: ┌─────┬─────┬─────┐
    # y=1: │     │     │     │  (row 0, line 0)
    # y=2: │  X  │  O  │     │  (row 0, line 1 - content)
    # y=3: │     │     │     │  (row 0, line 2)
    # y=4: ├─────┼─────┼─────┤
    # y=5: │     │     │     │  (row 1, line 0)
    # y=6: │     │[ ]  │     │  (row 1, line 1 - content)
    # y=7: │     │     │     │  (row 1, line 2)
    # y=8: ├─────┼─────┼─────┤
    # y=9: │     │     │     │  (row 2, line 0)
    # y=10: │  O  │     │  X  │  (row 2, line 1 - content)
    # y=11: │     │     │     │  (row 2, line 2)
    # y=12: └─────┴─────┴─────┘

    TOTAL_HEIGHT = 13
    CELL_WIDTH = 5

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._board: Board = list(range(9))
        self._cursor_position: int = 4
        self._winning_cells: tuple[int, ...] = ()
        self._is_game_over: bool = False

    def update_state(
        self,
        board: Board,
        cursor_position: int,
        winning_cells: tuple[int, ...],
        is_game_over: bool,
    ) -> None:
        """Update the board state and trigger a refresh."""
        self._board = board
        self._cursor_position = cursor_position
        self._winning_cells = winning_cells
        self._is_game_over = is_game_over
        self.refresh()

    def get_content_width(self, container, viewport):
        """Return the width of the board."""
        # │ + 5*3 cells + 2 inner │ + │ = 1 + 15 + 2 + 1 = 19
        return 19

    def get_content_height(self, container, viewport, width):
        """Return the height of the board."""
        return self.TOTAL_HEIGHT

    def _get_styles(self):
        """Get theme-aware styles."""
        is_dark = self.app.theme == "textual-dark"

        if is_dark:
            return {
                "bg": "#0a0a0a",
                "border": "#555555",
                "x": "#00d4ff",
                "o": "#ff69b4",
                "cursor": "#ffff00",
                "win_bg": "#2d5a2d",
            }
        else:
            return {
                "bg": "#f5f5f5",
                "border": "#666666",
                "x": "#0066cc",
                "o": "#cc0066",
                "cursor": "#cc8800",
                "win_bg": "#90ee90",
            }

    def render_line(self, y: int) -> Strip:
        """Render a single line of the game board."""
        colors = self._get_styles()
        style_border = Style(color=colors["border"], bgcolor=colors["bg"])

        segments = []

        # Top border
        if y == 0:
            segments = [
                Segment("┌─────┬─────┬─────┐", style_border)
            ]
            return Strip(segments)

        # Bottom border
        if y == 12:
            segments = [
                Segment("└─────┴─────┴─────┘", style_border)
            ]
            return Strip(segments)

        # Horizontal dividers
        if y == 4 or y == 8:
            segments = [
                Segment("├─────┼─────┼─────┤", style_border)
            ]
            return Strip(segments)

        # Cell content rows
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

            # Cell background
            cell_bg = colors["win_bg"] if is_winning else colors["bg"]

            # Render cell content (5 chars wide)
            if line_in_cell == 1:  # Middle line - show content
                cell_content = self._render_cell_content(
                    cell_value, is_cursor, is_winning, colors, cell_bg
                )
            else:
                # Top or bottom line - empty
                cell_content = [Segment("     ", Style(bgcolor=cell_bg))]

            segments.extend(cell_content)

            if col < 2:
                segments.append(Segment("│", style_border))

        segments.append(Segment("│", style_border))
        return Strip(segments)

    def _render_cell_content(
        self, cell_value, is_cursor: bool, is_winning: bool, colors: dict, cell_bg: str
    ) -> list[Segment]:
        """Render the content of a single cell (5 chars wide)."""
        bg_style = Style(bgcolor=cell_bg)
        cursor_style = Style(color=colors["cursor"], bgcolor=cell_bg, bold=True)

        if isinstance(cell_value, int):
            # Empty cell
            if is_cursor:
                return [
                    Segment(" ", bg_style),
                    Segment("[", cursor_style),
                    Segment(" ", bg_style),
                    Segment("]", cursor_style),
                    Segment(" ", bg_style),
                ]
            else:
                return [Segment("     ", bg_style)]
        elif cell_value == Player.X:
            x_style = Style(color=colors["x"], bgcolor=cell_bg, bold=True)
            if is_cursor:
                return [
                    Segment(" ", bg_style),
                    Segment("[", cursor_style),
                    Segment("X", x_style),
                    Segment("]", cursor_style),
                    Segment(" ", bg_style),
                ]
            return [
                Segment("  ", bg_style),
                Segment("X", x_style),
                Segment("  ", bg_style),
            ]
        else:  # Player.O
            o_style = Style(color=colors["o"], bgcolor=cell_bg, bold=True)
            if is_cursor:
                return [
                    Segment(" ", bg_style),
                    Segment("[", cursor_style),
                    Segment("O", o_style),
                    Segment("]", cursor_style),
                    Segment(" ", bg_style),
                ]
            return [
                Segment("  ", bg_style),
                Segment("O", o_style),
                Segment("  ", bg_style),
            ]

    def _get_row_info(self, y: int) -> tuple[int, int] | None:
        """
        Get cell row and line within cell for a given y coordinate.
        Returns (cell_row, line_in_cell) or None if y is a border/divider.

        Layout:
        y=1,2,3 -> row 0, lines 0,1,2
        y=5,6,7 -> row 1, lines 0,1,2
        y=9,10,11 -> row 2, lines 0,1,2
        """
        if 1 <= y <= 3:
            return (0, y - 1)
        elif 5 <= y <= 7:
            return (1, y - 5)
        elif 9 <= y <= 11:
            return (2, y - 9)
        return None
