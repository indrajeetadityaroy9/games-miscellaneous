"""Data models for Space Invaders game."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Player:
    """Player ship."""
    x: int  # Horizontal position (0 to board_width - player_width)
    width: int = 5  # Player ship width in chars


@dataclass(frozen=True)
class Bullet:
    """Projectile (player or enemy)."""
    x: int
    y: int
    active: bool = True
    is_enemy: bool = False  # True for enemy bullets


@dataclass(frozen=True)
class Enemy:
    """Enemy invader."""
    x: int
    y: int
    enemy_type: int  # 0, 1, or 2 for different sprites
    active: bool = True
    width: int = 3  # Enemy width in chars
    height: int = 2  # Enemy height in rows


@dataclass(frozen=True)
class GameState:
    """Complete game state."""
    player: Player
    enemies: tuple[Enemy, ...] = ()
    player_bullets: tuple[Bullet, ...] = ()
    enemy_bullets: tuple[Bullet, ...] = ()
    score: int = 0
    high_score: int = 0
    level: int = 1
    direction: int = 1  # 1 = right, -1 = left
    is_paused: bool = False
    is_game_over: bool = False
    is_won: bool = False
    can_shoot: bool = True  # Cooldown flag


# Board dimensions
BOARD_WIDTH = 60
BOARD_HEIGHT = 38  # Tall board for more play space
PLAYER_Y = BOARD_HEIGHT - 3  # Player at bottom (row 35)
PLAYER_WIDTH = 5

# Enemy grid configuration
ENEMY_ROWS = 3  # Reduced from 5 for easier gameplay
ENEMY_COLS = 8  # Reduced from 10 for easier gameplay
ENEMY_WIDTH = 3
ENEMY_HEIGHT = 2
ENEMY_SPACING = 4  # Horizontal space between enemies (more space = fewer edge hits)
ENEMY_ROW_SPACING = 3  # Vertical space between enemy rows
