from dataclasses import replace
from pathlib import Path
from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header
from .models import BoardConfig
from .game_logic import (
    create_initial_state,
    move_player_left,
    move_player_right,
    shoot_player_bullet,
    update_player_bullets,
    update_enemy_bullets,
    update_enemies,
    enemy_shoot,
    check_collisions,
    check_win,
    toggle_pause,
    reset_shoot_cooldown,
    get_enemy_move_interval,
    get_enemy_shoot_interval,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme
from .sprites import PLAYER_SPRITE
TICK_INTERVAL = 0.05
class SpaceInvadersApp(App):
    CSS_PATH = Path(__file__).parent / "styles" / "spaceinvaders.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("left", "move_left", "Left", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("space", "shoot", "Fire"),
        Binding("p", "pause", "Pause"),
        Binding("r", "reset", "Restart"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]
    TITLE = "Terminal Space Invaders"
    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.state = create_initial_state()
        self._board: GameBoard | None = None
        self._hud: HUD | None = None
        self._game_timer: Timer | None = None
        self._shoot_cooldown_timer: Timer | None = None
        self._moving_left = False
        self._moving_right = False
        self._enemy_move_accum = 0.0
        self._enemy_shoot_accum = 0.0
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            HUD(id="hud"),
            GameBoard(id="game-board"),
            id="game-container",
        )
        yield Footer()
    def on_mount(self) -> None:
        self._board = self.query_one("#game-board", GameBoard)
        self._hud = self.query_one("#hud", HUD)
        self._configure_layout(force_reset=True)
        self._start_timers()
        self._update_widgets()
        self.theme = get_theme()

    def on_resize(self, event: events.Resize) -> None:
        self._configure_layout()
    def _start_timers(self) -> None:
        self._reset_accumulators()
        self._game_timer = self.set_interval(TICK_INTERVAL, self._game_tick)
    def _stop_timers(self) -> None:
        if self._game_timer:
            self._game_timer.stop()
        if self._shoot_cooldown_timer:
            self._shoot_cooldown_timer.stop()
    def _restart_timers(self) -> None:
        self._stop_timers()
        self._start_timers()
    def _game_tick(self) -> None:
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        if self._moving_left:
            self.state = move_player_left(self.state)
        if self._moving_right:
            self.state = move_player_right(self.state)
        self._enemy_move_accum += TICK_INTERVAL
        self._enemy_shoot_accum += TICK_INTERVAL

        move_interval = get_enemy_move_interval(self.state.level)
        if self._enemy_move_accum >= move_interval:
            self.state = update_enemies(self.state)
            self._enemy_move_accum -= move_interval

        shoot_interval = get_enemy_shoot_interval(self.state.level)
        if self._enemy_shoot_accum >= shoot_interval:
            self.state = enemy_shoot(self.state)
            self._enemy_shoot_accum -= shoot_interval

        self.state = update_player_bullets(self.state)
        self.state = update_enemy_bullets(self.state)
        self.state = check_collisions(self.state)
        self.state = check_win(self.state)
        self._update_widgets()
    def _reset_shoot_cooldown(self) -> None:
        self.state = reset_shoot_cooldown(self.state)
    def _update_widgets(self) -> None:
        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
                is_won=self.state.is_won,
            )
        if self._board:
            if self.config:
                self._board.set_config(self.config)
            self._board.update_state(
                player=self.state.player,
                enemies=self.state.enemies,
                player_bullets=self.state.player_bullets,
                enemy_bullets=self.state.enemy_bullets,
                is_game_over=self.state.is_game_over,
                is_won=self.state.is_won,
            )
    def on_key(self, event) -> None:
        if event.key == "left" or event.key == "a":
            self._moving_left = True
        elif event.key == "right" or event.key == "d":
            self._moving_right = True
    def on_key_up(self, event) -> None:
        if hasattr(event, 'key'):
            if event.key == "left" or event.key == "a":
                self._moving_left = False
            elif event.key == "right" or event.key == "d":
                self._moving_right = False
    def action_move_left(self) -> None:
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        self.state = move_player_left(self.state)
        self._update_widgets()
    def action_move_right(self) -> None:
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        self.state = move_player_right(self.state)
        self._update_widgets()
    def action_shoot(self) -> None:
        if self.state.is_game_over or self.state.is_paused or self.state.is_won:
            return
        if self.state.can_shoot:
            self.state = shoot_player_bullet(self.state)
            self._update_widgets()
            if self._shoot_cooldown_timer:
                self._shoot_cooldown_timer.stop()
            self._shoot_cooldown_timer = self.set_timer(0.25, self._reset_shoot_cooldown)
    def action_pause(self) -> None:
        self.state = toggle_pause(self.state)
        self._update_widgets()
    def action_reset(self) -> None:
        high_score = self.state.high_score
        if self.state.is_won and self.state.level < 8:
            next_level = self.state.level + 1
            current_score = self.state.score
            self.state = create_initial_state(
                level=next_level,
                high_score=high_score,
                config=self.config,
            )
            self.state = replace(self.state, score=current_score)  
        else:
            self.state = create_initial_state(
                level=1,
                high_score=high_score,
                config=self.config,
            )
        self._moving_left = False
        self._moving_right = False
        self._restart_timers()
        self._update_widgets()
    def action_toggle_theme(self) -> None:
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()

    def _calculate_config(self) -> BoardConfig:
        screen_width = self.size.width
        screen_height = self.size.height

        board_width = max(50, screen_width - 6)
        board_height = max(24, screen_height - 10)

        player_width = len(PLAYER_SPRITE[0])
        player_y = max(6, board_height - 3)

        enemy_width = 3
        enemy_height = 2
        enemy_spacing = 4
        enemy_row_spacing = 3
        max_cols = (board_width + enemy_spacing) // (enemy_width + enemy_spacing)
        enemy_cols = min(8, max(2, max_cols))

        return BoardConfig(
            width=board_width,
            height=board_height,
            player_y=player_y,
            player_width=player_width,
            enemy_rows=3,
            enemy_cols=enemy_cols,
            enemy_width=enemy_width,
            enemy_height=enemy_height,
            enemy_spacing=enemy_spacing,
            enemy_row_spacing=enemy_row_spacing,
        )

    def _configure_layout(self, force_reset: bool = False) -> None:
        new_config = self._calculate_config()
        if (
            not force_reset
            and self.config
            and (self.config.width, self.config.height, self.config.enemy_cols)
            == (new_config.width, new_config.height, new_config.enemy_cols)
        ):
            return

        old_config = self.config
        high_score = self.state.high_score if self.state else 0
        level = self.state.level if self.state else 1
        self.config = new_config
        if self.state and old_config:
            self.state = self._map_state_to_new_config(
                self.state,
                old_config,
                new_config,
            )
        else:
            self.state = create_initial_state(
                level=level,
                high_score=high_score,
                config=self.config,
            )

        if self._board:
            self._board.set_config(self.config)
            self._board.refresh()

        if self._game_timer:
            self._restart_timers()
        self._update_widgets()

    def _reset_accumulators(self) -> None:
        self._enemy_move_accum = 0.0
        self._enemy_shoot_accum = 0.0

    def _map_state_to_new_config(
        self,
        state,
        old_config: BoardConfig,
        new_config: BoardConfig,
    ):
        desired_dx = (new_config.width - old_config.width) // 2
        desired_dy = new_config.player_y - old_config.player_y

        if state.enemies:
            min_x = min(e.x for e in state.enemies)
            max_x = max(e.x + old_config.enemy_width - 1 for e in state.enemies)
            min_y = min(e.y for e in state.enemies)
            max_y = max(e.y + old_config.enemy_height - 1 for e in state.enemies)

            dx_min = -min_x
            dx_max = (new_config.width - 1) - max_x
            dy_min = -min_y
            dy_max = (new_config.height - 1) - max_y

            dx = max(dx_min, min(dx_max, desired_dx))
            dy = max(dy_min, min(dy_max, desired_dy))
        else:
            dx = desired_dx
            dy = desired_dy

        player_x = state.player.x + dx
        player_x = max(0, min(new_config.width - new_config.player_width, player_x))
        new_player = replace(state.player, x=player_x)

        new_enemies = []
        for enemy in state.enemies:
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            new_x = max(0, min(new_config.width - new_config.enemy_width, new_x))
            new_y = max(0, min(new_config.height - new_config.enemy_height, new_y))
            new_enemies.append(replace(enemy, x=new_x, y=new_y))

        new_player_bullets = []
        for bullet in state.player_bullets:
            new_x = bullet.x + dx
            new_y = bullet.y + dy
            if 0 <= new_x < new_config.width and 0 <= new_y < new_config.height:
                new_player_bullets.append(replace(bullet, x=new_x, y=new_y))

        new_enemy_bullets = []
        for bullet in state.enemy_bullets:
            new_x = bullet.x + dx
            new_y = bullet.y + dy
            if 0 <= new_x < new_config.width and 0 <= new_y < new_config.height:
                new_enemy_bullets.append(replace(bullet, x=new_x, y=new_y))

        return replace(
            state,
            config=new_config,
            player=new_player,
            enemies=tuple(new_enemies),
            player_bullets=tuple(new_player_bullets),
            enemy_bullets=tuple(new_enemy_bullets),
        )
def main() -> None:
    app = SpaceInvadersApp()
    app.run()
if __name__ == "__main__":
    main()
