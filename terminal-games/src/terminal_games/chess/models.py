"""Data models for Terminal Chess."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import chess


class Difficulty(Enum):
    """AI difficulty levels."""
    EASY = 1      # Depth 1
    MEDIUM = 2    # Depth 2
    HARD = 3      # Depth 3
    EXPERT = 4    # Depth 4


@dataclass
class GameConfig:
    """Game configuration."""
    player_color: chess.Color = chess.WHITE  # Player plays white by default
    difficulty: Difficulty = Difficulty.HARD


@dataclass
class GameState:
    """Complete game state."""
    board: chess.Board = field(default_factory=chess.Board)
    cursor_square: int = chess.E2          # Current cursor position (0-63)
    selected_square: Optional[int] = None  # Selected piece square
    config: GameConfig = field(default_factory=GameConfig)
    is_thinking: bool = False              # AI thinking flag
    last_move_from: Optional[int] = None   # Last move source square
    last_move_to: Optional[int] = None     # Last move destination square

    def get_legal_moves_from_selected(self) -> list[int]:
        """Get destination squares for selected piece."""
        if self.selected_square is None:
            return []
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                moves.append(move.to_square)
        return moves

    def is_player_turn(self) -> bool:
        """Check if it's the player's turn."""
        return self.board.turn == self.config.player_color

    def get_game_status(self) -> str:
        """Get current game status message."""
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate! {winner} wins!"
        if self.board.is_stalemate():
            return "Stalemate - Draw!"
        if self.board.is_insufficient_material():
            return "Draw - Insufficient material"
        if self.board.is_seventyfive_moves():
            return "Draw - 75 move rule"
        if self.board.is_fivefold_repetition():
            return "Draw - Fivefold repetition"
        if self.board.is_check():
            return "Check!"
        return ""

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()


def create_initial_state(
    player_color: chess.Color = chess.WHITE,
    difficulty: Difficulty = Difficulty.HARD
) -> GameState:
    """Create a fresh game state."""
    config = GameConfig(player_color=player_color, difficulty=difficulty)
    # Start cursor on e2 (white's pawn) or e7 (black's pawn)
    cursor = chess.E2 if player_color == chess.WHITE else chess.E7
    return GameState(
        board=chess.Board(),
        cursor_square=cursor,
        config=config,
    )


# Unicode chess pieces
PIECE_SYMBOLS = {
    # White pieces (filled)
    (chess.PAWN, chess.WHITE): "♙",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.ROOK, chess.WHITE): "♖",
    (chess.QUEEN, chess.WHITE): "♕",
    (chess.KING, chess.WHITE): "♔",
    # Black pieces (outlined)
    (chess.PAWN, chess.BLACK): "♟",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.ROOK, chess.BLACK): "♜",
    (chess.QUEEN, chess.BLACK): "♛",
    (chess.KING, chess.BLACK): "♚",
}


def get_piece_symbol(piece: Optional[chess.Piece]) -> str:
    """Get the Unicode symbol for a chess piece."""
    if piece is None:
        return " "
    return PIECE_SYMBOLS.get((piece.piece_type, piece.color), "?")


# Board colors for dark theme
COLORS_DARK = {
    "light_square": "#f0d9b5",       # Light tan
    "dark_square": "#b58863",        # Dark brown
    "cursor": "#ffff00",             # Yellow
    "selected": "#7fff00",           # Chartreuse green
    "legal_move": "#66c2ff",         # Light blue
    "check": "#ff4444",              # Red
    "white_piece": "#ffffff",        # White
    "black_piece": "#000000",        # Black
}

# Board colors for light theme
COLORS_LIGHT = {
    "light_square": "#eeeed2",       # Light cream
    "dark_square": "#769656",        # Green (chess.com style)
    "cursor": "#ff6600",             # Orange (more visible on light)
    "selected": "#f6f669",           # Yellow highlight
    "legal_move": "#baca44",         # Yellow-green (visible on light theme)
    "check": "#ff0000",              # Red
    "white_piece": "#4a4a4a",        # Dark gray (for visibility on light bg)
    "black_piece": "#000000",        # Black
}


def get_theme_colors(is_light_theme: bool) -> dict:
    """Get colors based on theme."""
    return COLORS_LIGHT if is_light_theme else COLORS_DARK
