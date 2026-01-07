from typing import Optional
import chess
from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget
from ..models import get_piece_symbol, get_theme_colors


class ChessBoard(Widget):
    CELL_WIDTH = 9
    CELL_HEIGHT = 5

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
        self._is_flipped: bool = False
        self._colors: dict = {}
        # Cache for styles to reduce object creation
        self._style_cache: dict = {}

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
        self._board = board
        self._cursor_square = cursor_square
        self._selected_square = selected_square
        self._legal_moves = legal_moves
        self._last_move_from = last_move_from
        self._last_move_to = last_move_to
        self._player_color = player_color
        self._is_flipped = player_color == chess.BLACK
        
        # Update caches
        self._refresh_colors()
        self.refresh()

    def _refresh_colors(self) -> None:
        """Cache colors and styles based on current theme."""
        is_light = self.app.theme == "textual-light" if self.app else False
        self._colors = get_theme_colors(is_light)
        
        # Pre-calculate base styles
        self._style_cache = {
            "light_square": Style(bgcolor=self._colors["light_square"]),
            "dark_square": Style(bgcolor=self._colors["dark_square"]),
            "selected": Style(bgcolor=self._colors["selected"]),
            "legal_move": Style(bgcolor=self._colors["legal_move"]),
            "check": Style(bgcolor=self._colors["check"]),
            "cursor": Style(bgcolor=self._colors["cursor"]),
            "label": Style(color="cyan", bold=True),
            "dot": Style(color="#004080", bold=True),
        }

    def get_content_width(self, container, viewport):
        return 8 * self.CELL_WIDTH + 4

    def get_content_height(self, container, viewport, width):
        return 8 * self.CELL_HEIGHT + 2

    def render_line(self, y: int) -> Strip:
        total_height = 8 * self.CELL_HEIGHT + 2
        board_start_y = 1
        board_end_y = board_start_y + 8 * self.CELL_HEIGHT
        
        # Ensure cache is initialized
        if not self._colors:
            self._refresh_colors()

        segments: list[Segment] = []
        label_style = self._style_cache["label"]

        if y == 0 or y == total_height - 1:
            segments.append(Segment("  "))
            for file_idx in range(8):
                file = file_idx if not self._is_flipped else 7 - file_idx
                file_label = chr(ord('a') + file)
                label = file_label.center(self.CELL_WIDTH)
                segments.append(Segment(label, label_style))
            return Strip(segments)

        if board_start_y <= y < board_end_y:
            board_y = y - board_start_y
            row_idx = board_y // self.CELL_HEIGHT
            cell_y = board_y % self.CELL_HEIGHT
            
            if self._is_flipped:
                rank = row_idx
            else:
                rank = 7 - row_idx

            # Left rank label
            if cell_y == 2:
                rank_label = str(rank + 1)
                segments.append(Segment(f"{rank_label} ", label_style))
            else:
                segments.append(Segment("  "))

            # Board cells
            for file_idx in range(8):
                file = file_idx if not self._is_flipped else 7 - file_idx
                square = chess.square(file, rank)
                cell_segments = self._render_cell(square, cell_y)
                segments.extend(cell_segments)

            # Right rank label
            if cell_y == 2:
                rank_label = str(rank + 1)
                segments.append(Segment(f" {rank_label}", label_style))

            return Strip(segments)

        return Strip([])

    def _render_cell(self, square: int, cell_y: int) -> list[Segment]:
        piece = self._board.piece_at(square)
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Determine background style
        is_cursor = square == self._cursor_square
        is_selected = square == self._selected_square
        is_legal_move = square in self._legal_moves
        
        is_check = (
            piece is not None
            and piece.piece_type == chess.KING
            and self._board.is_check()
            and piece.color == self._board.turn
        )

        # Priority: Selected > Cursor > Check > Legal Move > Normal
        if is_selected:
            bg_style = self._style_cache["selected"]
            bg_color = self._colors["selected"]
        elif is_cursor:
            bg_style = self._style_cache["cursor"]
            bg_color = self._colors["cursor"]
        elif is_check:
            bg_style = self._style_cache["check"]
            bg_color = self._colors["check"]
        elif is_legal_move:
            bg_style = self._style_cache["legal_move"]
            bg_color = self._colors["legal_move"]
        else:
            is_light_square = (file + rank) % 2 == 1
            bg_style = self._style_cache["light_square"] if is_light_square else self._style_cache["dark_square"]
            bg_color = self._colors["light_square"] if is_light_square else self._colors["dark_square"]

        # Content
        content = " " * self.CELL_WIDTH
        
        if cell_y == 2:
            if piece:
                piece_char = get_piece_symbol(piece)
                piece_color = self._colors["black_piece"] if piece.color == chess.BLACK else self._colors["white_piece"]
                # Merge piece style with background
                style = Style(color=piece_color, bgcolor=bg_color, bold=True)
                return [Segment(piece_char.center(self.CELL_WIDTH), style)]
            elif is_legal_move and not is_cursor and not is_selected:
                # Draw dot for legal move if empty
                dot_char = "\u2022"
                style = Style(color=self._style_cache["dot"].color, bgcolor=bg_color, bold=True)
                return [Segment(dot_char.center(self.CELL_WIDTH), style)]
        
        return [Segment(content, bg_style)]
