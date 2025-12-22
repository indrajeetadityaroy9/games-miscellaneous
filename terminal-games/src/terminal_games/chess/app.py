"""Main Textual application for Terminal Chess."""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import chess
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Static

from .models import GameState, Difficulty, create_initial_state, PIECE_SYMBOLS
from .chess_ai import get_best_move, get_captured_pieces
from .widgets.chess_board import ChessBoard
from ..config import get_theme, set_theme


class ChessApp(App):
    """Terminal Chess game application."""

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
        """Build the widget tree."""
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
        """Initialize game when app mounts."""
        self._board = self.query_one("#chess-board", ChessBoard)
        self._sidebar = self.query_one("#sidebar", Static)
        self._update_widgets()

        # Apply saved theme
        self.theme = get_theme()

        # If AI plays first (player chose black), trigger AI move
        if not self.state.is_player_turn():
            self._trigger_ai_move()

    def _update_widgets(self) -> None:
        """Push state to child widgets."""
        if self._board:
            # Only show legal moves during player's turn
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
        """Build the sidebar content string."""
        lines: list[str] = []

        # Status message (check, checkmate, etc.)
        status = self.state.get_game_status()
        if status:
            if "Checkmate" in status or "Draw" in status:
                lines.append(f"[bold magenta]{status}[/bold magenta]")
            elif "Check" in status:
                lines.append(f"[bold red]{status}[/bold red]")

        lines.append("")

        # Captured pieces
        captured = get_captured_pieces(self.state.board)
        lines.append("[bold]Captured:[/bold]")

        # White pieces lost
        if captured[chess.WHITE]:
            pieces_str = "".join(
                PIECE_SYMBOLS.get((pt, chess.WHITE), "?")
                for pt in sorted(captured[chess.WHITE], reverse=True)
            )
            lines.append(f"  White lost: {pieces_str}")
        else:
            lines.append("  White lost: -")

        # Black pieces lost
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
        """Start AI move calculation in background thread."""
        if self.state.is_game_over() or self.state.is_player_turn():
            return

        self.state.is_thinking = True
        self._update_widgets()

        # Run AI in background thread
        depth = self.state.config.difficulty.value
        future = self._executor.submit(get_best_move, self.state.board.copy(), depth)
        future.add_done_callback(self._on_ai_move_complete)

    def _on_ai_move_complete(self, future) -> None:
        """Handle AI move completion."""
        move = future.result()
        self.state.is_thinking = False

        if move:
            self.state.last_move_from = move.from_square
            self.state.last_move_to = move.to_square
            self.state.board.push(move)

        # Use call_from_thread to update UI from background thread
        self.call_from_thread(self._update_widgets)

    # Navigation actions
    def action_move_up(self) -> None:
        """Move cursor up."""
        if self.state.is_thinking or self.state.is_game_over():
            return

        # Respect board orientation
        if self.state.config.player_color == chess.WHITE:
            # White at bottom: up increases rank
            if self.state.cursor_square < 56:
                self.state.cursor_square += 8
        else:
            # Black at bottom: up decreases rank
            if self.state.cursor_square >= 8:
                self.state.cursor_square -= 8

        self._update_widgets()

    def action_move_down(self) -> None:
        """Move cursor down."""
        if self.state.is_thinking or self.state.is_game_over():
            return

        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square >= 8:
                self.state.cursor_square -= 8
        else:
            if self.state.cursor_square < 56:
                self.state.cursor_square += 8

        self._update_widgets()

    def action_move_left(self) -> None:
        """Move cursor left."""
        if self.state.is_thinking or self.state.is_game_over():
            return

        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square % 8 != 0:
                self.state.cursor_square -= 1
        else:
            if self.state.cursor_square % 8 != 7:
                self.state.cursor_square += 1

        self._update_widgets()

    def action_move_right(self) -> None:
        """Move cursor right."""
        if self.state.is_thinking or self.state.is_game_over():
            return

        if self.state.config.player_color == chess.WHITE:
            if self.state.cursor_square % 8 != 7:
                self.state.cursor_square += 1
        else:
            if self.state.cursor_square % 8 != 0:
                self.state.cursor_square -= 1

        self._update_widgets()

    def action_select(self) -> None:
        """Select a piece or make a move."""
        if self.state.is_thinking or self.state.is_game_over():
            return

        if not self.state.is_player_turn():
            return

        cursor = self.state.cursor_square

        if self.state.selected_square is None:
            # No piece selected - try to select one
            piece = self.state.board.piece_at(cursor)
            if piece and piece.color == self.state.config.player_color:
                # Check if this piece has any legal moves
                has_moves = any(
                    m.from_square == cursor for m in self.state.board.legal_moves
                )
                if has_moves:
                    self.state.selected_square = cursor
        else:
            # Piece is selected - try to move
            legal_moves = self.state.get_legal_moves_from_selected()

            if cursor in legal_moves:
                # Valid move - execute it
                from_sq = self.state.selected_square
                to_sq = cursor

                # Find the move (handle promotions)
                move = None
                for m in self.state.board.legal_moves:
                    if m.from_square == from_sq and m.to_square == to_sq:
                        # For pawn promotion, default to queen
                        if m.promotion:
                            if m.promotion == chess.QUEEN:
                                move = m
                                break
                        else:
                            move = m
                            break

                if move is None:
                    # Fallback - just use first matching move
                    for m in self.state.board.legal_moves:
                        if m.from_square == from_sq and m.to_square == to_sq:
                            move = m
                            break

                if move:
                    self.state.last_move_from = from_sq
                    self.state.last_move_to = to_sq
                    self.state.board.push(move)
                    self.state.selected_square = None

                    self._update_widgets()

                    # Trigger AI move if game is not over
                    if not self.state.is_game_over():
                        self._trigger_ai_move()
                    return
            else:
                # Clicked on a different piece of same color - select it
                piece = self.state.board.piece_at(cursor)
                if piece and piece.color == self.state.config.player_color:
                    has_moves = any(
                        m.from_square == cursor for m in self.state.board.legal_moves
                    )
                    if has_moves:
                        self.state.selected_square = cursor
                    else:
                        self.state.selected_square = None
                else:
                    # Deselect
                    self.state.selected_square = None

        self._update_widgets()

    def action_deselect(self) -> None:
        """Deselect the current piece."""
        if self.state.selected_square is not None:
            self.state.selected_square = None
            self._update_widgets()

    def action_reset(self) -> None:
        """Reset the game."""
        self.state = create_initial_state(
            player_color=self.state.config.player_color,
            difficulty=self.state.config.difficulty,
        )
        self._update_widgets()

        # If AI plays first
        if not self.state.is_player_turn():
            self._trigger_ai_move()

    def action_toggle_theme(self) -> None:
        """Switch between dark and light themes."""
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()


def main() -> None:
    """Run the Terminal Chess application."""
    app = ChessApp()
    app.run()


if __name__ == "__main__":
    main()
