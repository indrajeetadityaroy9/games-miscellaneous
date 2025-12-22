"""Pure functions for Tetris game mechanics."""

import random
from typing import Optional

from .models import Position, Tetromino, GameState, BoardConfig
from .tetrominoes import ALL_PIECES


def create_empty_board(config: BoardConfig) -> list[list[int]]:
    """Create an empty game board."""
    return [[0] * config.width for _ in range(config.height)]


def spawn_random_piece() -> Tetromino:
    """Select a random tetromino piece."""
    return random.choice(ALL_PIECES)


def create_initial_state(config: BoardConfig, high_score: int = 0) -> GameState:
    """Create a fresh game state."""
    board = create_empty_board(config)
    piece = spawn_random_piece()
    # Spawn at center-top (x=3 for 10-wide board)
    position = Position(x=(config.width - len(piece.shape[0])) // 2, y=0)

    return GameState(
        board=board,
        current_piece=piece,
        position=position,
        high_score=high_score,
    )


def rotate_piece(piece: Tetromino) -> Tetromino:
    """Rotate piece 90 degrees clockwise."""
    shape = piece.shape
    # Transpose and reverse each row
    rotated = tuple(
        tuple(shape[len(shape) - 1 - j][i] for j in range(len(shape)))
        for i in range(len(shape[0]))
    )
    return Tetromino(shape=rotated, color=piece.color)


def can_place_piece(
    piece: Tetromino,
    position: Position,
    board: list[list[int]],
    config: BoardConfig,
) -> bool:
    """Check if piece can be placed at position without collision."""
    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                continue

            new_x = position.x + col_idx
            new_y = position.y + row_idx

            # Check horizontal boundaries
            if new_x < 0 or new_x >= config.width:
                return False

            # Check bottom boundary
            if new_y >= config.height:
                return False

            # Check overlap with existing blocks (only if within board)
            if new_y >= 0 and board[new_y][new_x] != 0:
                return False

    return True


def merge_piece_to_board(
    piece: Tetromino,
    position: Position,
    board: list[list[int]],
) -> list[list[int]]:
    """Lock piece into the board, returning new board state."""
    new_board = [row[:] for row in board]

    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                continue

            new_x = position.x + col_idx
            new_y = position.y + row_idx

            if 0 <= new_y < len(new_board) and 0 <= new_x < len(new_board[0]):
                new_board[new_y][new_x] = cell

    return new_board


def find_complete_rows(board: list[list[int]]) -> list[int]:
    """Find all complete (filled) row indices."""
    complete = []
    for row_idx, row in enumerate(board):
        if all(cell != 0 for cell in row):
            complete.append(row_idx)
    return complete


def clear_rows(board: list[list[int]], rows: list[int], config: BoardConfig) -> list[list[int]]:
    """Remove complete rows and add empty rows at top."""
    new_board = [row[:] for row in board]

    # Remove rows from bottom to top to maintain indices
    for row_idx in sorted(rows, reverse=True):
        del new_board[row_idx]

    # Add empty rows at top
    for _ in range(len(rows)):
        new_board.insert(0, [0] * config.width)

    return new_board


def calculate_line_score(lines: int, level: int, combo: int, was_tetris: bool) -> int:
    """Calculate score for clearing lines."""
    # Base points per number of lines
    base_points = {1: 100, 2: 300, 3: 500, 4: 800}
    points = base_points.get(lines, 0) * level

    # Back-to-back Tetris bonus
    if lines == 4 and was_tetris:
        points = int(points * 1.5)

    # Combo bonus
    if combo > 0:
        points += 50 * combo * level

    return points


def calculate_level(total_lines: int) -> int:
    """Calculate level from total lines cleared."""
    return (total_lines // 5) + 1


def calculate_speed(level: int) -> float:
    """Calculate gravity interval in seconds based on level."""
    # 600ms at level 1, decreasing by 140ms per level, minimum 40ms
    ms = max(40, 600 - (level - 1) * 140)
    return ms / 1000.0


def hard_drop_distance(
    piece: Tetromino,
    position: Position,
    board: list[list[int]],
    config: BoardConfig,
) -> int:
    """Calculate how many rows piece can drop."""
    distance = 0
    test_pos = position

    while can_place_piece(piece, Position(test_pos.x, test_pos.y + 1), board, config):
        distance += 1
        test_pos = Position(test_pos.x, test_pos.y + 1)

    return distance


def move_left(state: GameState, config: BoardConfig) -> GameState:
    """Attempt to move piece left."""
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state

    new_pos = Position(state.position.x - 1, state.position.y)
    if can_place_piece(state.current_piece, new_pos, state.board, config):
        new_state = state.copy()
        new_state.position = new_pos
        return new_state

    return state


def move_right(state: GameState, config: BoardConfig) -> GameState:
    """Attempt to move piece right."""
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state

    new_pos = Position(state.position.x + 1, state.position.y)
    if can_place_piece(state.current_piece, new_pos, state.board, config):
        new_state = state.copy()
        new_state.position = new_pos
        return new_state

    return state


def move_down(state: GameState, config: BoardConfig) -> tuple[GameState, bool]:
    """
    Move piece down one row (gravity tick).
    Returns (new_state, piece_locked) where piece_locked is True if piece was locked.
    """
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state, False

    new_pos = Position(state.position.x, state.position.y + 1)

    if can_place_piece(state.current_piece, new_pos, state.board, config):
        # Can move down
        new_state = state.copy()
        new_state.position = new_pos
        return new_state, False
    else:
        # Lock piece and spawn new one
        return lock_piece(state, config), True


def try_rotate(state: GameState, config: BoardConfig) -> GameState:
    """Attempt to rotate piece clockwise."""
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state

    rotated = rotate_piece(state.current_piece)

    if can_place_piece(rotated, state.position, state.board, config):
        new_state = state.copy()
        new_state.current_piece = rotated
        return new_state

    return state


def do_hard_drop(state: GameState, config: BoardConfig) -> GameState:
    """Instantly drop piece to bottom and lock it."""
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state

    distance = hard_drop_distance(state.current_piece, state.position, state.board, config)
    new_pos = Position(state.position.x, state.position.y + distance)

    new_state = state.copy()
    new_state.position = new_pos
    # Award 2 points per cell dropped
    new_state.score += distance * 2
    new_state.high_score = max(new_state.high_score, new_state.score)

    return lock_piece(new_state, config)


def lock_piece(state: GameState, config: BoardConfig) -> GameState:
    """Lock current piece into board and handle line clears."""
    if state.current_piece is None:
        return state

    new_state = state.copy()

    # Check if piece is locked above the visible board (game over condition)
    for row_idx, row in enumerate(state.current_piece.shape):
        for col_idx, cell in enumerate(row):
            if cell != 0:
                actual_y = state.position.y + row_idx
                if actual_y < 0:
                    # Piece locked above visible board = game over
                    new_state.is_game_over = True
                    new_state.current_piece = None
                    new_state.high_score = max(new_state.high_score, new_state.score)
                    return new_state

    # Merge piece into board
    new_state.board = merge_piece_to_board(
        state.current_piece, state.position, state.board
    )

    # Check for complete rows
    complete_rows = find_complete_rows(new_state.board)

    if complete_rows:
        # Calculate score
        lines = len(complete_rows)
        points = calculate_line_score(
            lines,
            new_state.level,
            new_state.combo,
            new_state.last_clear_was_tetris,
        )
        new_state.score += points
        new_state.high_score = max(new_state.high_score, new_state.score)

        # Update lines and level
        new_state.lines_cleared += lines
        new_state.level = calculate_level(new_state.lines_cleared)

        # Update combo and back-to-back
        new_state.combo += 1
        new_state.last_clear_was_tetris = (lines == 4)

        # Clear the rows
        new_state.board = clear_rows(new_state.board, complete_rows, config)
    else:
        # No clear, reset combo
        new_state.combo = 0
        new_state.last_clear_was_tetris = False

    # Spawn new piece
    new_piece = spawn_random_piece()
    new_pos = Position(x=(config.width - len(new_piece.shape[0])) // 2, y=0)

    # Check if new piece can be placed (game over condition)
    if not can_place_piece(new_piece, new_pos, new_state.board, config):
        new_state.is_game_over = True
        new_state.current_piece = None
    else:
        new_state.current_piece = new_piece
        new_state.position = new_pos

    return new_state


def toggle_pause(state: GameState) -> GameState:
    """Toggle pause state."""
    if state.is_game_over:
        return state

    new_state = state.copy()
    new_state.is_paused = not state.is_paused
    return new_state
