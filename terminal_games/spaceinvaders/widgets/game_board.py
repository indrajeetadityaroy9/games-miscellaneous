"""Game board widget for Space Invaders."""

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

from ..models import (
    Player,
    Enemy,
    Bullet,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    PLAYER_Y,
    PLAYER_WIDTH,
    ENEMY_WIDTH,
    ENEMY_HEIGHT,
)
from ..sprites import PLAYER_SPRITE, ENEMY_SPRITES, PLAYER_BULLET, ENEMY_BULLET


class GameBoard(Widget):
    """Main game rendering widget."""

    DEFAULT_CSS = """
    GameBoard {
        width: auto;
        height: auto;
    }
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._player: Player = Player(x=BOARD_WIDTH // 2)
        self._enemies: list[Enemy] = []
        self._player_bullets: list[Bullet] = []
        self._enemy_bullets: list[Bullet] = []
        self._is_game_over: bool = False
        self._is_won: bool = False

    def update_state(
        self,
        player: Player,
        enemies: list[Enemy],
        player_bullets: list[Bullet],
        enemy_bullets: list[Bullet],
        is_game_over: bool,
        is_won: bool,
    ) -> None:
        """Update the game state and trigger a refresh."""
        self._player = player
        self._enemies = enemies
        self._player_bullets = player_bullets
        self._enemy_bullets = enemy_bullets
        self._is_game_over = is_game_over
        self._is_won = is_won
        self.refresh()

    def get_content_width(self, container, viewport):
        """Return the width of the board."""
        return BOARD_WIDTH

    def get_content_height(self, container, viewport, width):
        """Return the height of the board."""
        return BOARD_HEIGHT

    def _get_styles(self):
        """Get theme-aware styles."""
        is_dark = self.app.theme == "textual-dark"

        if is_dark:
            return {
                "bg": "#0a0a0a",
                "player": "#00ff00",
                "enemy0": "#ff0000",
                "enemy1": "#ff6600",
                "enemy2": "#ffff00",
                "player_bullet": "#00ffff",
                "enemy_bullet": "#ff00ff",
            }
        else:
            return {
                "bg": "#f0f0f0",
                "player": "#006600",
                "enemy0": "#cc0000",
                "enemy1": "#cc5500",
                "enemy2": "#999900",
                "player_bullet": "#006699",
                "enemy_bullet": "#990099",
            }

    def render_line(self, y: int) -> Strip:
        """Render a single line of the game board."""
        colors = self._get_styles()
        bg_style = Style(bgcolor=colors["bg"])

        # Build a character buffer for this line
        line_buffer = [" "] * BOARD_WIDTH
        style_buffer = [bg_style] * BOARD_WIDTH

        # Render enemies at this row
        for enemy in self._enemies:
            if not enemy.active:
                continue

            # Check if this enemy occupies this row
            if enemy.y <= y < enemy.y + ENEMY_HEIGHT:
                sprite_row = y - enemy.y
                sprite = ENEMY_SPRITES.get(enemy.enemy_type, ENEMY_SPRITES[0])

                if sprite_row < len(sprite):
                    enemy_color = colors[f"enemy{enemy.enemy_type}"]
                    enemy_style = Style(color=enemy_color, bgcolor=colors["bg"], bold=True)

                    for i, char in enumerate(sprite[sprite_row]):
                        pos = enemy.x + i
                        if 0 <= pos < BOARD_WIDTH:
                            line_buffer[pos] = char
                            style_buffer[pos] = enemy_style

        # Render player at this row
        if PLAYER_Y <= y < PLAYER_Y + len(PLAYER_SPRITE):
            sprite_row = y - PLAYER_Y
            if sprite_row < len(PLAYER_SPRITE):
                player_style = Style(color=colors["player"], bgcolor=colors["bg"], bold=True)

                for i, char in enumerate(PLAYER_SPRITE[sprite_row]):
                    pos = self._player.x + i
                    if 0 <= pos < BOARD_WIDTH:
                        line_buffer[pos] = char
                        style_buffer[pos] = player_style

        # Render player bullets at this row
        bullet_style = Style(color=colors["player_bullet"], bgcolor=colors["bg"], bold=True)
        for bullet in self._player_bullets:
            if bullet.active and bullet.y == y:
                if 0 <= bullet.x < BOARD_WIDTH:
                    line_buffer[bullet.x] = PLAYER_BULLET
                    style_buffer[bullet.x] = bullet_style

        # Render enemy bullets at this row
        enemy_bullet_style = Style(color=colors["enemy_bullet"], bgcolor=colors["bg"], bold=True)
        for bullet in self._enemy_bullets:
            if bullet.active and bullet.y == y:
                if 0 <= bullet.x < BOARD_WIDTH:
                    line_buffer[bullet.x] = ENEMY_BULLET
                    style_buffer[bullet.x] = enemy_bullet_style

        # Build segments from buffer
        segments = []
        current_text = ""
        current_style = style_buffer[0] if style_buffer else bg_style

        for i in range(BOARD_WIDTH):
            if style_buffer[i] == current_style:
                current_text += line_buffer[i]
            else:
                if current_text:
                    segments.append(Segment(current_text, current_style))
                current_text = line_buffer[i]
                current_style = style_buffer[i]

        if current_text:
            segments.append(Segment(current_text, current_style))

        return Strip(segments)
