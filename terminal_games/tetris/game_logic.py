import random
from dataclasses import replace
from .models import Position, Tetromino, GameState, BoardConfig
from .tetrominoes import ALL_PIECES
def create_empty_board(config: BoardConfig) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(0 for _ in range(config.width)) for _ in range(config.height))
def spawn_random_piece() -> Tetromino:
    return random.choice(ALL_PIECES)
def create_initial_state(config: BoardConfig, high_score: int = 0) -> GameState:
    board = create_empty_board(config)
    piece = spawn_random_piece()
    position = Position(x=(config.width - len(piece.shape[0])) // 2, y=0)
    return GameState(
        board=board,
        current_piece=piece,
        position=position,
        high_score=high_score,
    )
def rotate_piece(piece: Tetromino) -> Tetromino:
    shape = piece.shape
    rotated = tuple(
        tuple(shape[len(shape) - 1 - j][i] for j in range(len(shape)))
        for i in range(len(shape[0]))
    )
    return Tetromino(shape=rotated, color=piece.color)
def can_place_piece(
    piece: Tetromino,
    position: Position,
    board: tuple[tuple[int, ...], ...],
    config: BoardConfig,
) -> bool:
    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                continue
            new_x = position.x + col_idx
            new_y = position.y + row_idx
            if new_x < 0 or new_x >= config.width:
                return False
            if new_y >= config.height:
                return False
            if new_y >= 0 and board[new_y][new_x] != 0:
                return False
    return True
def merge_piece_to_board(
    piece: Tetromino,
    position: Position,
    board: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    new_board = [list(row) for row in board]
    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                continue
            new_x = position.x + col_idx
            new_y = position.y + row_idx
            if 0 <= new_y < len(new_board) and 0 <= new_x < len(new_board[0]):
                new_board[new_y][new_x] = cell
    return tuple(tuple(row) for row in new_board)
def find_complete_rows(board: tuple[tuple[int, ...], ...]) -> list[int]:
    complete = []
    for row_idx, row in enumerate(board):
        if all(cell != 0 for cell in row):
            complete.append(row_idx)
    return complete
def clear_rows(
    board: tuple[tuple[int, ...], ...],
    rows: list[int],
    config: BoardConfig
) -> tuple[tuple[int, ...], ...]:
    new_board = [list(row) for row in board]
    for row_idx in sorted(rows, reverse=True):
        del new_board[row_idx]
    for _ in range(len(rows)):
        new_board.insert(0, [0] * config.width)
    return tuple(tuple(row) for row in new_board)
def calculate_line_score(lines: int, level: int, combo: int, was_tetris: bool) -> int:
    base_points = {1: 100, 2: 300, 3: 500, 4: 800}
    points = base_points.get(lines, 0) * level
    if lines == 4 and was_tetris:
        points = int(points * 1.5)
    if combo > 0:
        points += 50 * combo * level
    return points
def calculate_level(total_lines: int) -> int:
    return (total_lines // 5) + 1
def calculate_speed(level: int) -> float:
    ms = max(40, 600 - (level - 1) * 140)
    return ms / 1000.0
def hard_drop_distance(
    piece: Tetromino,
    position: Position,
    board: tuple[tuple[int, ...], ...],
    config: BoardConfig,
) -> int:
    distance = 0
    test_pos = position
    while can_place_piece(piece, Position(test_pos.x, test_pos.y + 1), board, config):
        distance += 1
        test_pos = Position(test_pos.x, test_pos.y + 1)
    return distance
def move_left(state: GameState, config: BoardConfig) -> GameState:
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state
    new_pos = Position(state.position.x - 1, state.position.y)
    if can_place_piece(state.current_piece, new_pos, state.board, config):
        return replace(state, position=new_pos)
    return state
def move_right(state: GameState, config: BoardConfig) -> GameState:
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state
    new_pos = Position(state.position.x + 1, state.position.y)
    if can_place_piece(state.current_piece, new_pos, state.board, config):
        return replace(state, position=new_pos)
    return state
def move_down(state: GameState, config: BoardConfig) -> tuple[GameState, bool]:
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state, False
    new_pos = Position(state.position.x, state.position.y + 1)
    if can_place_piece(state.current_piece, new_pos, state.board, config):
        return replace(state, position=new_pos), False
    else:
        return lock_piece(state, config), True
def try_rotate(state: GameState, config: BoardConfig) -> GameState:
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state
    rotated = rotate_piece(state.current_piece)
    if can_place_piece(rotated, state.position, state.board, config):
        return replace(state, current_piece=rotated)
    return state
def do_hard_drop(state: GameState, config: BoardConfig) -> GameState:
    if state.is_game_over or state.is_paused or state.current_piece is None:
        return state
    distance = hard_drop_distance(state.current_piece, state.position, state.board, config)
    new_pos = Position(state.position.x, state.position.y + distance)
    new_score = state.score + distance * 2
    new_high_score = max(state.high_score, new_score)
    dropped_state = replace(
        state,
        position=new_pos,
        score=new_score,
        high_score=new_high_score,
    )
    return lock_piece(dropped_state, config)
def lock_piece(state: GameState, config: BoardConfig) -> GameState:
    if state.current_piece is None:
        return state
    for row_idx, row in enumerate(state.current_piece.shape):
        for col_idx, cell in enumerate(row):
            if cell != 0:
                actual_y = state.position.y + row_idx
                if actual_y < 0:
                    return replace(
                        state,
                        is_game_over=True,
                        current_piece=None,
                        high_score=max(state.high_score, state.score),
                    )
    new_board = merge_piece_to_board(
        state.current_piece, state.position, state.board
    )
    complete_rows = find_complete_rows(new_board)
    if complete_rows:
        lines = len(complete_rows)
        points = calculate_line_score(
            lines,
            state.level,
            state.combo,
            state.last_clear_was_tetris,
        )
        new_score = state.score + points
        new_high_score = max(state.high_score, new_score)
        new_lines_cleared = state.lines_cleared + lines
        new_level = calculate_level(new_lines_cleared)
        cleared_board = clear_rows(new_board, complete_rows, config)
        new_piece = spawn_random_piece()
        new_pos = Position(x=(config.width - len(new_piece.shape[0])) // 2, y=0)
        if not can_place_piece(new_piece, new_pos, cleared_board, config):
            return replace(
                state,
                board=cleared_board,
                current_piece=None,
                score=new_score,
                high_score=new_high_score,
                level=new_level,
                lines_cleared=new_lines_cleared,
                combo=state.combo + 1,
                last_clear_was_tetris=(lines == 4),
                is_game_over=True,
            )
        return replace(
            state,
            board=cleared_board,
            current_piece=new_piece,
            position=new_pos,
            score=new_score,
            high_score=new_high_score,
            level=new_level,
            lines_cleared=new_lines_cleared,
            combo=state.combo + 1,
            last_clear_was_tetris=(lines == 4),
        )
    else:
        new_piece = spawn_random_piece()
        new_pos = Position(x=(config.width - len(new_piece.shape[0])) // 2, y=0)
        if not can_place_piece(new_piece, new_pos, new_board, config):
            return replace(
                state,
                board=new_board,
                current_piece=None,
                is_game_over=True,
            )
        return replace(
            state,
            board=new_board,
            current_piece=new_piece,
            position=new_pos,
            combo=0,
            last_clear_was_tetris=False,
        )
def toggle_pause(state: GameState) -> GameState:
    if state.is_game_over:
        return state
    return replace(state, is_paused=not state.is_paused)
