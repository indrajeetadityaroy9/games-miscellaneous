from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional
import chess
class Difficulty(Enum):
    EASY = 1      
    MEDIUM = 2    
    HARD = 3      
    EXPERT = 4    
@dataclass(frozen=True)
class GameConfig:
    player_color: chess.Color = chess.WHITE  
    difficulty: Difficulty = Difficulty.HARD
@dataclass(frozen=True)
class GameState:
    board: chess.Board
    cursor_square: int = chess.E2          
    selected_square: Optional[int] = None  
    config: GameConfig = GameConfig()
    is_thinking: bool = False              
    last_move_from: Optional[int] = None   
    last_move_to: Optional[int] = None     
    def get_legal_moves_from_selected(self) -> list[int]:
        if self.selected_square is None:
            return []
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                moves.append(move.to_square)
        return moves
    def is_player_turn(self) -> bool:
        return self.board.turn == self.config.player_color
    def get_game_status(self) -> str:
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
        return self.board.is_game_over()
def create_initial_state(
    player_color: chess.Color = chess.WHITE,
    difficulty: Difficulty = Difficulty.HARD
) -> GameState:
    config = GameConfig(player_color=player_color, difficulty=difficulty)
    cursor = chess.E2 if player_color == chess.WHITE else chess.E7
    return GameState(
        board=chess.Board(),
        cursor_square=cursor,
        config=config,
    )
def push_move(state: GameState, move: chess.Move) -> GameState:
    new_board = state.board.copy()
    new_board.push(move)
    return replace(
        state,
        board=new_board,
        last_move_from=move.from_square,
        last_move_to=move.to_square,
        selected_square=None,
    )
PIECE_SYMBOLS = {
    (chess.PAWN, chess.WHITE): "♙",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.ROOK, chess.WHITE): "♖",
    (chess.QUEEN, chess.WHITE): "♕",
    (chess.KING, chess.WHITE): "♔",
    (chess.PAWN, chess.BLACK): "♟",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.ROOK, chess.BLACK): "♜",
    (chess.QUEEN, chess.BLACK): "♛",
    (chess.KING, chess.BLACK): "♚",
}
def get_piece_symbol(piece: Optional[chess.Piece]) -> str:
    if piece is None:
        return " "
    return PIECE_SYMBOLS.get((piece.piece_type, piece.color), "?")
COLORS_DARK = {
    "light_square": "#f0d9b5",       
    "dark_square": "#b58863",        
    "cursor": "#ffff00",             
    "selected": "#7fff00",           
    "legal_move": "#66c2ff",         
    "check": "#ff4444",              
    "white_piece": "#ffffff",        
    "black_piece": "#000000",        
}
COLORS_LIGHT = {
    "light_square": "#eeeed2",       
    "dark_square": "#769656",        
    "cursor": "#ff6600",             
    "selected": "#f6f669",           
    "legal_move": "#baca44",         
    "check": "#ff0000",              
    "white_piece": "#4a4a4a",        
    "black_piece": "#000000",        
}
def get_theme_colors(is_light_theme: bool) -> dict:
    return COLORS_LIGHT if is_light_theme else COLORS_DARK
