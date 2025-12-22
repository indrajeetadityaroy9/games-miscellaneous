"""Pure functions for Tic-Tac-Toe game mechanics."""

from dataclasses import replace
from typing import Optional

from .models import Player, Board, GameState, CellValue


HUMAN_PLAYER = Player.O
AI_PLAYER = Player.X

WIN_COMBOS = (
    (0, 1, 2),  # top row
    (3, 4, 5),  # middle row
    (6, 7, 8),  # bottom row
    (0, 3, 6),  # left column
    (1, 4, 7),  # middle column
    (2, 5, 8),  # right column
    (0, 4, 8),  # diagonal TL-BR
    (6, 4, 2),  # diagonal BL-TR
)


def create_empty_board() -> Board:
    """Create an empty board with indices 0-8."""
    return tuple(range(9))


def create_initial_state() -> GameState:
    """Create a fresh game state."""
    return GameState(
        board=create_empty_board(),
        cursor_position=4,  # Start at center
        is_game_over=False,
        winner=None,
        winning_cells=(),
    )


def get_empty_squares(board: Board) -> list[int]:
    """Get list of empty cell indices."""
    return [cell for cell in board if isinstance(cell, int)]


def check_win(board: Board, player: Player) -> Optional[int]:
    """Check if player has won. Returns winning combo index or None."""
    # Find all cells occupied by player
    plays = [i for i, cell in enumerate(board) if cell == player]

    for combo_idx, combo in enumerate(WIN_COMBOS):
        if all(cell in plays for cell in combo):
            return combo_idx

    return None


def check_tie(board: Board) -> bool:
    """Check if game is a tie (no empty squares left)."""
    return len(get_empty_squares(board)) == 0


def set_cell(board: Board, index: int, value: CellValue) -> Board:
    """Set a cell value and return new board tuple."""
    return tuple(value if i == index else cell for i, cell in enumerate(board))


def minimax(board: Board, player: Player) -> dict:
    """
    Minimax algorithm for AI.
    Returns dict with 'score' and optionally 'index'.
    Uses pure functional approach - no board mutation.
    """
    available_spots = get_empty_squares(board)

    # Check terminal states
    if check_win(board, HUMAN_PLAYER) is not None:
        return {"score": -10}
    elif check_win(board, AI_PLAYER) is not None:
        return {"score": 10}
    elif len(available_spots) == 0:
        return {"score": 0}

    moves = []

    for spot in available_spots:
        move = {"index": spot, "score": 0}

        # Make the move by creating a new board
        new_board = set_cell(board, spot, player)

        # Recurse
        if player == AI_PLAYER:
            result = minimax(new_board, HUMAN_PLAYER)
        else:
            result = minimax(new_board, AI_PLAYER)

        move["score"] = result["score"]
        moves.append(move)

    # Find best move
    if player == AI_PLAYER:
        best_score = -10000
        best_move = moves[0]
        for move in moves:
            if move["score"] > best_score:
                best_score = move["score"]
                best_move = move
    else:
        best_score = 10000
        best_move = moves[0]
        for move in moves:
            if move["score"] < best_score:
                best_score = move["score"]
                best_move = move

    return best_move


def get_best_move(board: Board) -> int:
    """Get the best move for AI."""
    result = minimax(board, AI_PLAYER)
    return result["index"]


def make_move(state: GameState, index: int) -> GameState:
    """
    Make a human move at the given index.
    Returns new state after human move and AI response.
    """
    if state.is_game_over:
        return state

    # Check if cell is empty
    if not isinstance(state.board[index], int):
        return state

    # Human move
    new_board = set_cell(state.board, index, HUMAN_PLAYER)

    # Check human win
    human_win = check_win(new_board, HUMAN_PLAYER)
    if human_win is not None:
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="You Win!",
            winning_cells=WIN_COMBOS[human_win],
        )

    # Check tie
    if check_tie(new_board):
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="Tie Game!",
        )

    # AI move
    ai_move = get_best_move(new_board)
    new_board = set_cell(new_board, ai_move, AI_PLAYER)

    # Check AI win
    ai_win = check_win(new_board, AI_PLAYER)
    if ai_win is not None:
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="You Lose!",
            winning_cells=WIN_COMBOS[ai_win],
        )

    # Check tie after AI move
    if check_tie(new_board):
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="Tie Game!",
        )

    return replace(state, board=new_board)


def move_cursor_up(state: GameState) -> GameState:
    """Move cursor up one row."""
    if state.cursor_position >= 3:
        return replace(state, cursor_position=state.cursor_position - 3)
    return state


def move_cursor_down(state: GameState) -> GameState:
    """Move cursor down one row."""
    if state.cursor_position <= 5:
        return replace(state, cursor_position=state.cursor_position + 3)
    return state


def move_cursor_left(state: GameState) -> GameState:
    """Move cursor left one column."""
    if state.cursor_position % 3 != 0:
        return replace(state, cursor_position=state.cursor_position - 1)
    return state


def move_cursor_right(state: GameState) -> GameState:
    """Move cursor right one column."""
    if state.cursor_position % 3 != 2:
        return replace(state, cursor_position=state.cursor_position + 1)
    return state
