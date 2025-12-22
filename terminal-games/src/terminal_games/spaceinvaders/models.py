"""Data models for Space Invaders game."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Player:
    """Player ship."""
    x: int  # Horizontal position (0 to board_width - player_width)
    width: int = 5  # Player ship width in chars


@dataclass
class Bullet:
    """Projectile (player or enemy)."""
    x: int
    y: int
    active: bool = True
    is_enemy: bool = False  # True for enemy bullets


@dataclass
class Enemy:
    """Enemy invader."""
    x: int
    y: int
    enemy_type: int  # 0, 1, or 2 for different sprites
    active: bool = True
    width: int = 3  # Enemy width in chars
    height: int = 2  # Enemy height in rows


@dataclass
class GameState:
    """Complete game state."""
    player: Player
    enemies: list[Enemy] = field(default_factory=list)
    player_bullets: list[Bullet] = field(default_factory=list)
    enemy_bullets: list[Bullet] = field(default_factory=list)
    score: int = 0
    high_score: int = 0
    level: int = 1
    direction: int = 1  # 1 = right, -1 = left
    is_paused: bool = False
    is_game_over: bool = False
    is_won: bool = False
    can_shoot: bool = True  # Cooldown flag

    def copy(self) -> "GameState":
        """Create a copy of the game state."""
        return GameState(
            player=Player(x=self.player.x, width=self.player.width),
            enemies=[
                Enemy(x=e.x, y=e.y, enemy_type=e.enemy_type, active=e.active)
                for e in self.enemies
            ],
            player_bullets=[
                Bullet(x=b.x, y=b.y, active=b.active, is_enemy=b.is_enemy)
                for b in self.player_bullets
            ],
            enemy_bullets=[
                Bullet(x=b.x, y=b.y, active=b.active, is_enemy=b.is_enemy)
                for b in self.enemy_bullets
            ],
            score=self.score,
            high_score=self.high_score,
            level=self.level,
            direction=self.direction,
            is_paused=self.is_paused,
            is_game_over=self.is_game_over,
            is_won=self.is_won,
            can_shoot=self.can_shoot,
        )


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
