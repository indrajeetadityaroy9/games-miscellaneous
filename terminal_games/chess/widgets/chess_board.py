"""Chess board widget with cursor navigation and highlighting."""

from typing import Optional

import chess
from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

from ..models import get_piece_symbol, get_theme_colors


class ChessBoard(Widget):
    """Widget that renders the chess board with pieces and highlighting."""

    # Board dimensions
    CELL_WIDTH = 5    # Characters per cell width
    CELL_HEIGHT = 3   # Lines per cell height

    def __init__(
        self,
        id: Optional[str] = None,
    ) -> None:
        super().__init__(id=id)
        self._board: chess.Board = chess.Board()
        self._cursor_square: int = chess.E2
        self._selected_square: Optional[int] = None
        self._legal_moves: list[int] = []
        self._last_move_from: Optional[int] = None
        self._last_move_to: Optional[int] = None
        self._player_color: chess.Color = chess.WHITE
        self._is_flipped: bool = False  # If True, show black's perspective

    def update_state(
        self,
        board: chess.Board,
        cursor_square: int,
        selected_square: Optional[int],
        legal_moves: list[int],
        last_move_from: Optional[int],
        last_move_to: Optional[int],
        player_color: chess.Color,
    ) -> None:
        """Update the board state and refresh."""
        self._board = board
        self._cursor_square = cursor_square
        self._selected_square = selected_square
        self._legal_moves = legal_moves
        self._last_move_from = last_move_from
        self._last_move_to = last_move_to
        self._player_color = player_color
        # Show board from player's perspective
        self._is_flipped = player_color == chess.BLACK
        self.refresh()

    def _get_colors(self) -> dict:
        """Get colors based on current theme."""
        is_light = self.app.theme == "textual-light" if self.app else False
        return get_theme_colors(is_light)

    def get_content_width(self, container, viewport):
        """Calculate widget width."""
        # 8 cells * CELL_WIDTH + rank labels (2 chars each side) + borders
        return 8 * self.CELL_WIDTH + 4

    def get_content_height(self, container, viewport, width):
        """Calculate widget height."""
        # 8 cells * CELL_HEIGHT + file labels (1 line each) + borders
        return 8 * self.CELL_HEIGHT + 2

    def render_line(self, y: int) -> Strip:
        """Render a single line of the board."""
        total_height = 8 * self.CELL_HEIGHT + 2
        board_start_y = 1  # After top file labels
        board_end_y = board_start_y + 8 * self.CELL_HEIGHT

        segments: list[Segment] = []

        # Top file labels (a-h)
        if y == 0:
            segments.append(Segment("  "))  # Padding for rank label
            for file_idx in range(8):
                file = file_idx if not self._is_flipped else 7 - file_idx
                file_label = chr(ord('a') + file)
                # Center the label in cell width
                label = file_label.center(self.CELL_WIDTH)
                segments.append(Segment(label, Style(color="cyan", bold=True)))
            return Strip(segments)

        # Bottom file labels (a-h)
        if y == total_height - 1:
            segments.append(Segment("  "))  # Padding for rank label
            for file_idx in range(8):
                file = file_idx if not self._is_flipped else 7 - file_idx
                file_label = chr(ord('a') + file)
                label = file_label.center(self.CELL_WIDTH)
                segments.append(Segment(label, Style(color="cyan", bold=True)))
            return Strip(segments)

        # Board rows
        if board_start_y <= y < board_end_y:
            board_y = y - board_start_y
            row_idx = board_y // self.CELL_HEIGHT  # Which row (0-7)
            cell_y = board_y % self.CELL_HEIGHT    # Line within cell (0-2)

            # Calculate chess rank (8-1 from top to bottom, or 1-8 if flipped)
            if self._is_flipped:
                rank = row_idx  # 0-7 maps to rank 1-8
            else:
                rank = 7 - row_idx  # 0-7 maps to rank 8-1

            # Rank label on left (only on middle line of cell)
            if cell_y == 1:
                rank_label = str(rank + 1)
                segments.append(Segment(f"{rank_label} ", Style(color="cyan", bold=True)))
            else:
                segments.append(Segment("  "))

            # Render each cell in this row
            for file_idx in range(8):
                file = file_idx if not self._is_flipped else 7 - file_idx
                square = chess.square(file, rank)

                cell_segments = self._render_cell(square, cell_y)
                segments.extend(cell_segments)

            # Rank label on right (only on middle line of cell)
            if cell_y == 1:
                rank_label = str(rank + 1)
                segments.append(Segment(f" {rank_label}", Style(color="cyan", bold=True)))

            return Strip(segments)

        return Strip([])

    def _render_cell(self, square: int, cell_y: int) -> list[Segment]:
        """Render a single cell of the board."""
        colors = self._get_colors()
        piece = self._board.piece_at(square)
        file = chess.square_file(square)
        rank = chess.square_rank(square)

        # Determine square color (light or dark)
        is_light_square = (file + rank) % 2 == 1

        # Determine if this square has special highlighting
        is_cursor = square == self._cursor_square
        is_selected = square == self._selected_square
        is_legal_move = square in self._legal_moves
        is_check = (
            piece is not None
            and piece.piece_type == chess.KING
            and self._board.is_check()
            and piece.color == self._board.turn
        )

        # Determine background color
        if is_selected:
            bg_color = colors["selected"]
        elif is_legal_move:
            bg_color = colors["legal_move"]
        elif is_check:
            bg_color = colors["check"]
        elif is_light_square:
            bg_color = colors["light_square"]
        else:
            bg_color = colors["dark_square"]

        bg_style = Style(bgcolor=bg_color)

        # Determine piece style
        if piece:
            piece_color = colors["black_piece"] if piece.color == chess.BLACK else colors["white_piece"]
            piece_style = Style(color=piece_color, bgcolor=bg_color, bold=True)
        else:
            piece_style = bg_style

        # Get piece symbol
        piece_char = get_piece_symbol(piece) if piece else " "

        # Cursor style
        cursor_style = Style(color=colors["cursor"], bgcolor=bg_color, bold=True)

        # Render based on which line of the cell we're on (3 lines per cell)
        # Line 1 (middle) shows the piece with cursor, lines 0 and 2 are padding
        if cell_y == 1:
            # Middle line - show piece here with cursor brackets if selected
            if is_cursor:
                if piece:
                    return [
                        Segment("[", cursor_style),
                        Segment(piece_char.center(self.CELL_WIDTH - 2), piece_style),
                        Segment("]", cursor_style),
                    ]
                else:
                    content = f"[{' '.center(self.CELL_WIDTH - 2)}]"
                    return [Segment(content, cursor_style)]
            else:
                content = piece_char.center(self.CELL_WIDTH)
                if piece:
                    return [Segment(content, piece_style)]
                elif is_legal_move:
                    dot_char = "\u2022"  # Bullet point
                    dot_style = Style(color="#004080", bgcolor=bg_color, bold=True)
                    return [Segment(dot_char.center(self.CELL_WIDTH), dot_style)]
                else:
                    return [Segment(content, bg_style)]
        else:
            # Padding lines (0 and 2) - no cursor brackets, just background
            return [Segment(" " * self.CELL_WIDTH, bg_style)]
