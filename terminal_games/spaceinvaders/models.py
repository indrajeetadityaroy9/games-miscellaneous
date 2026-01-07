from dataclasses import dataclass

DEFAULT_BOARD_WIDTH = 80
DEFAULT_BOARD_HEIGHT = 45
DEFAULT_PLAYER_WIDTH = 5
DEFAULT_PLAYER_Y = DEFAULT_BOARD_HEIGHT - 3
DEFAULT_ENEMY_ROWS = 3
DEFAULT_ENEMY_COLS = 8
DEFAULT_ENEMY_WIDTH = 3
DEFAULT_ENEMY_HEIGHT = 2
DEFAULT_ENEMY_SPACING = 4
DEFAULT_ENEMY_ROW_SPACING = 3
@dataclass(frozen=True)
class Player:
    x: int  
    width: int = 5  
@dataclass(frozen=True)
class Bullet:
    x: int
    y: int
    active: bool = True
    is_enemy: bool = False  
@dataclass(frozen=True)
class Enemy:
    x: int
    y: int
    enemy_type: int  
    active: bool = True
    width: int = 3  
    height: int = 2  

@dataclass(frozen=True)
class BoardConfig:
    width: int = DEFAULT_BOARD_WIDTH
    height: int = DEFAULT_BOARD_HEIGHT
    player_y: int = DEFAULT_PLAYER_Y
    player_width: int = DEFAULT_PLAYER_WIDTH
    enemy_rows: int = DEFAULT_ENEMY_ROWS
    enemy_cols: int = DEFAULT_ENEMY_COLS
    enemy_width: int = DEFAULT_ENEMY_WIDTH
    enemy_height: int = DEFAULT_ENEMY_HEIGHT
    enemy_spacing: int = DEFAULT_ENEMY_SPACING
    enemy_row_spacing: int = DEFAULT_ENEMY_ROW_SPACING
@dataclass(frozen=True)
class GameState:
    config: BoardConfig
    player: Player
    enemies: tuple[Enemy, ...] = ()
    player_bullets: tuple[Bullet, ...] = ()
    enemy_bullets: tuple[Bullet, ...] = ()
    score: int = 0
    high_score: int = 0
    level: int = 1
    direction: int = 1  
    is_paused: bool = False
    is_game_over: bool = False
    is_won: bool = False
    can_shoot: bool = True  
BOARD_WIDTH = DEFAULT_BOARD_WIDTH
BOARD_HEIGHT = DEFAULT_BOARD_HEIGHT
PLAYER_Y = DEFAULT_PLAYER_Y
PLAYER_WIDTH = DEFAULT_PLAYER_WIDTH
ENEMY_ROWS = DEFAULT_ENEMY_ROWS
ENEMY_COLS = DEFAULT_ENEMY_COLS
ENEMY_WIDTH = DEFAULT_ENEMY_WIDTH
ENEMY_HEIGHT = DEFAULT_ENEMY_HEIGHT
ENEMY_SPACING = DEFAULT_ENEMY_SPACING
ENEMY_ROW_SPACING = DEFAULT_ENEMY_ROW_SPACING
