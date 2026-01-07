from dataclasses import replace
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import chess
from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Static
from .models import GameState, Difficulty, create_initial_state, push_move, PIECE_SYMBOLS
from .chess_ai import get_best_move, get_captured_pieces
from .widgets.chess_board import ChessBoard
from ..config import get_theme, set_theme
class ChessApp(App):
    CSS_PATH = Path(__file__).parent / "styles" / "chess.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("w", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("s", "move_down", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("enter", "select", "Select"),
        Binding("escape", "deselect", "Cancel"),
        Binding("r", "reset", "Restart"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]
    TITLE = "Terminal Chess"
    def __init__(self) -> None:
        super().__init__()
        self.state = create_initial_state()
        self._board: Optional[ChessBoard] = None
        self._sidebar: Optional[Static] = None
        self._executor = ThreadPoolExecutor(max_workers=1)
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Container(
                ChessBoard(id="chess-board"),
                id="board-container",
            ),
            Container(
                Static("Loading...", id="sidebar", markup=True),
                id="sidebar-container",
            ),
            id="game-container",
        )
        yield Footer()
    def on_mount(self) -> None:
        self._board = self.query_one("#chess-board", ChessBoard)
        self._sidebar = self.query_one("#sidebar", Static)
        self._configure_layout(force_reset=True)
        self._update_widgets()
        self.theme = get_theme()
        if not self.state.is_player_turn():
            self._trigger_ai_move()

    def on_resize(self, event: events.Resize) -> None:
        self._configure_layout()

    def _calculate_cell_size(self) -> tuple[int, int]:
        screen_width = self.size.width
        screen_height = self.size.height

        sidebar_width = 34
        available_width = max(40, screen_width - sidebar_width)
        available_height = max(24, screen_height - 6)

        cell_width = max(5, (available_width - 4) // 8)
        cell_height = max(3, (available_height - 2) // 8)

        cell_width = min(cell_width, 13)
        cell_height = min(cell_height, 7)
        return cell_width, cell_height

    def _configure_layout(self, force_reset: bool = False) -> None:
        if not self._board:
            return
        cell_width, cell_height = self._calculate_cell_size()
        if not force_reset:
            if (
                self._board.CELL_WIDTH == cell_width
                and self._board.CELL_HEIGHT == cell_height
            ):
                return
        self._board.CELL_WIDTH = cell_width
        self._board.CELL_HEIGHT = cell_height
        self._board.refresh()
    def _update_widgets(self) -> None:
        if self._board:
            legal_moves = (
                self.state.get_legal_moves_from_selected()
                if self.state.is_player_turn()
                else []
            )
            self._board.update_state(
                board=self.state.board,
                cursor_square=self.state.cursor_square,
                selected_square=self.state.selected_square,
                legal_moves=legal_moves,
                last_move_from=self.state.last_move_from,
                last_move_to=self.state.last_move_to,
                player_color=self.state.config.player_color,
            )
        if self._sidebar:
            self._sidebar.update(self._build_sidebar_content())
    def _build_sidebar_content(self) -> str:
        lines: list[str] = []
        status = self.state.get_game_status()
        if status:
            if "Checkmate" in status or "Draw" in status:
                lines.append(f"[bold magenta]{status}[/bold magenta]")
            elif "Check" in status:
                lines.append(f"[bold red]{status}[/bold red]")
        lines.append("")
        captured = get_captured_pieces(self.state.board)
        lines.append("[bold]Captured:[/bold]")
        if captured[chess.WHITE]:
            pieces_str = "".join(
                PIECE_SYMBOLS.get((pt, chess.WHITE), "?")
                for pt in sorted(captured[chess.WHITE], reverse=True)
            )
            lines.append(f"  White lost: {pieces_str}")
        else:
            lines.append("  White lost: -")
        if captured[chess.BLACK]:
            pieces_str = "".join(
                PIECE_SYMBOLS.get((pt, chess.BLACK), "?")
                for pt in sorted(captured[chess.BLACK], reverse=True)
            )
            lines.append(f"  Black lost: {pieces_str}")
        else:
            lines.append("  Black lost: -")
        return "\n".join(lines)
    def _trigger_ai_move(self) -> None:
        if self.state.is_game_over() or self.state.is_player_turn():
            return
        self.state = replace(self.state, is_thinking=True)
        self._update_widgets()
        depth = self.state.config.difficulty.value
        future = self._executor.submit(get_best_move, self.state.board.copy(), depth)
        future.add_done_callback(self._on_ai_move_complete)
    def _on_ai_move_complete(self, future) -> None:
        move = future.result()
        if move:
            self.state = push_move(
                replace(self.state, is_thinking=False),
                move,
            )
        else:
            self.state = replace(self.state, is_thinking=False)
        self.call_from_thread(self._update_widgets)
    def action_move_up(self) -> None:
        if self.state.is_thinking or self.state.is_game_over():
            return
        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square < 56:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square + 8,
                )
        else:
            if self.state.cursor_square >= 8:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square - 8,
                )
        self._update_widgets()
    def action_move_down(self) -> None:
        if self.state.is_thinking or self.state.is_game_over():
            return
        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square >= 8:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square - 8,
                )
        else:
            if self.state.cursor_square < 56:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square + 8,
                )
        self._update_widgets()
    def action_move_left(self) -> None:
        if self.state.is_thinking or self.state.is_game_over():
            return
        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square % 8 != 0:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square - 1,
                )
        else:
            if self.state.cursor_square % 8 != 7:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square + 1,
                )
        self._update_widgets()
    def action_move_right(self) -> None:
        if self.state.is_thinking or self.state.is_game_over():
            return
        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square % 8 != 7:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square + 1,
                )
        else:
            if self.state.cursor_square % 8 != 0:
                self.state = replace(
                    self.state,
                    cursor_square=self.state.cursor_square - 1,
                )
        self._update_widgets()
    def action_select(self) -> None:
        if self.state.is_thinking or self.state.is_game_over():
            return
        if not self.state.is_player_turn():
            return
        cursor = self.state.cursor_square
        if self.state.selected_square is None:
            piece = self.state.board.piece_at(cursor)
            if piece and piece.color == self.state.config.player_color:
                has_moves = any(
                    m.from_square == cursor for m in self.state.board.legal_moves
                )
                if has_moves:
                    self.state = replace(self.state, selected_square=cursor)
        else:
            legal_moves = self.state.get_legal_moves_from_selected()
            if cursor in legal_moves:
                from_sq = self.state.selected_square
                to_sq = cursor
                move = None
                for m in self.state.board.legal_moves:
                    if m.from_square == from_sq and m.to_square == to_sq:
                        if m.promotion:
                            if m.promotion == chess.QUEEN:
                                move = m
                                break
                        else:
                            move = m
                            break
                if move is None:
                    for m in self.state.board.legal_moves:
                        if m.from_square == from_sq and m.to_square == to_sq:
                            move = m
                            break
                if move:
                    self.state = push_move(self.state, move)
                    self._update_widgets()
                    if not self.state.is_game_over():
                        self._trigger_ai_move()
                    return
            else:
                piece = self.state.board.piece_at(cursor)
                if piece and piece.color == self.state.config.player_color:
                    has_moves = any(
                        m.from_square == cursor for m in self.state.board.legal_moves
                    )
                    if has_moves:
                        self.state = replace(self.state, selected_square=cursor)
                    else:
                        self.state = replace(self.state, selected_square=None)
                else:
                    self.state = replace(self.state, selected_square=None)
        self._update_widgets()
    def action_deselect(self) -> None:
        if self.state.selected_square is not None:
            self.state = replace(self.state, selected_square=None)
            self._update_widgets()
    def action_reset(self) -> None:
        self.state = create_initial_state(
            player_color=self.state.config.player_color,
            difficulty=self.state.config.difficulty,
        )
        self._update_widgets()
        if not self.state.is_player_turn():
            self._trigger_ai_move()
    def action_toggle_theme(self) -> None:
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()
def main() -> None:
    app = ChessApp()
    app.run()
if __name__ == "__main__":
    main()
