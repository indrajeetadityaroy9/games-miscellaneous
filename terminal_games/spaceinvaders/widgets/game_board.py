from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget
from ..models import (
    Player,
    Enemy,
    Bullet,
    BoardConfig,
)
from ..sprites import PLAYER_SPRITE, ENEMY_SPRITES, PLAYER_BULLET, ENEMY_BULLET


class GameBoard(Widget):
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
        self._config = BoardConfig()
        self._player: Player = Player(x=self._config.width // 2)
        self._enemies: list[Enemy] = []
        self._player_bullets: list[Bullet] = []
        self._enemy_bullets: list[Bullet] = []
        self._is_game_over: bool = False
        self._is_won: bool = False
        self._styles: dict[str, Style] = {}
        self._last_theme: str | None = None

    def update_state(
        self,
        player: Player,
        enemies: list[Enemy],
        player_bullets: list[Bullet],
        enemy_bullets: list[Bullet],
        is_game_over: bool,
        is_won: bool,
    ) -> None:
        self._player = player
        self._enemies = enemies
        self._player_bullets = player_bullets
        self._enemy_bullets = enemy_bullets
        self._is_game_over = is_game_over
        self._is_won = is_won
        self.refresh()

    def set_config(self, config: BoardConfig) -> None:
        self._config = config
        self.refresh()

    def get_content_width(self, container, viewport):
        return self._config.width

    def get_content_height(self, container, viewport, width):
        return self._config.height

    def _refresh_styles(self) -> None:
        current_theme = getattr(self.app, "theme", "textual-dark")
        if self._styles and self._last_theme == current_theme:
            return

        self._last_theme = current_theme
        is_dark = current_theme == "textual-dark"

        if is_dark:
            colors = {
                "bg": "#0a0a0a",
                "player": "#00ff00",
                "enemy0": "#ff0000",
                "enemy1": "#ff6600",
                "enemy2": "#ffff00",
                "player_bullet": "#00ffff",
                "enemy_bullet": "#ff00ff",
            }
        else:
            colors = {
                "bg": "#f0f0f0",
                "player": "#006600",
                "enemy0": "#cc0000",
                "enemy1": "#cc5500",
                "enemy2": "#999900",
                "player_bullet": "#006699",
                "enemy_bullet": "#990099",
            }

        bg_style = Style(bgcolor=colors["bg"])
        self._styles = {
            "bg": bg_style,
            "player": Style(color=colors["player"], bgcolor=colors["bg"], bold=True),
            "enemy0": Style(color=colors["enemy0"], bgcolor=colors["bg"], bold=True),
            "enemy1": Style(color=colors["enemy1"], bgcolor=colors["bg"], bold=True),
            "enemy2": Style(color=colors["enemy2"], bgcolor=colors["bg"], bold=True),
            "player_bullet": Style(color=colors["player_bullet"], bgcolor=colors["bg"], bold=True),
            "enemy_bullet": Style(color=colors["enemy_bullet"], bgcolor=colors["bg"], bold=True),
        }

    def render_line(self, y: int) -> Strip:
        self._refresh_styles()
        styles = self._styles
        bg_style = styles["bg"]

        line_buffer = [" "] * self._config.width
        style_buffer = [bg_style] * self._config.width

        # Render enemies
        for enemy in self._enemies:
            if not enemy.active:
                continue
            if enemy.y <= y < enemy.y + self._config.enemy_height:
                sprite_row = y - enemy.y
                sprite = ENEMY_SPRITES.get(enemy.enemy_type, ENEMY_SPRITES[0])
                if sprite_row < len(sprite):
                    enemy_style = styles[f"enemy{enemy.enemy_type}"]
                    for i, char in enumerate(sprite[sprite_row]):
                        pos = enemy.x + i
                        if 0 <= pos < self._config.width:
                            line_buffer[pos] = char
                            style_buffer[pos] = enemy_style

        # Render player
        if self._config.player_y <= y < self._config.player_y + len(PLAYER_SPRITE):
            sprite_row = y - self._config.player_y
            if sprite_row < len(PLAYER_SPRITE):
                player_style = styles["player"]
                for i, char in enumerate(PLAYER_SPRITE[sprite_row]):
                    pos = self._player.x + i
                    if 0 <= pos < self._config.width:
                        line_buffer[pos] = char
                        style_buffer[pos] = player_style

        # Render bullets
        bullet_style = styles["player_bullet"]
        for bullet in self._player_bullets:
            if bullet.active and bullet.y == y:
                if 0 <= bullet.x < self._config.width:
                    line_buffer[bullet.x] = PLAYER_BULLET
                    style_buffer[bullet.x] = bullet_style

        enemy_bullet_style = styles["enemy_bullet"]
        for bullet in self._enemy_bullets:
            if bullet.active and bullet.y == y:
                if 0 <= bullet.x < self._config.width:
                    line_buffer[bullet.x] = ENEMY_BULLET
                    style_buffer[bullet.x] = enemy_bullet_style

        # Compress to segments
        segments = []
        current_text = ""
        current_style = style_buffer[0] if style_buffer else bg_style

        for i in range(self._config.width):
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
