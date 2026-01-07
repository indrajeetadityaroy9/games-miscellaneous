from pathlib import Path
from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header
from .models import BoardConfig, Direction, GameState, Position, Snake
from .game_logic import (
    create_initial_state,
    tick,
    change_direction,
    toggle_pause,
    spawn_apple,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme

TICK_INTERVAL = 1 / 10


class SnakeApp(App):
    CSS_PATH = Path(__file__).parent / "styles" / "snake.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("w", "move_up", "Up", show=False),
        Binding("s", "move_down", "Down", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("r", "reset", "Reset"),
        Binding("p", "pause", "Pause"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Snake"

    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.state: GameState | None = None
        self._game_timer: Timer | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None
        self._last_size: tuple[int, int] | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()

    def on_mount(self) -> None:
        self._configure_layout(force_reset=True)
        self._start_game_loop()
        self._update_widgets()
        self.theme = get_theme()

    def on_resize(self, event: events.Resize) -> None:
        self._configure_layout()

    def _calculate_board_config(self) -> BoardConfig:
        screen_width = self.size.width
        screen_height = self.size.height

        # Snake board renders each cell as 2 chars wide + borders
        available_width = max(40, screen_width - 6)
        cols = max(16, (available_width - 2) // 2)

        # Height: Header + Footer + HUD + borders + padding
        available_height = max(20, screen_height - 9)
        rows = max(12, available_height - 2)

        return BoardConfig(columns=cols, rows=rows)

    def _configure_layout(self, force_reset: bool = False) -> None:
        new_config = self._calculate_board_config()
        if (
            not force_reset
            and self.config
            and (self.config.columns, self.config.rows)
            == (new_config.columns, new_config.rows)
        ):
            return

        high_score = self.state.high_score if self.state else 0
        old_config = self.config
        self.config = new_config
        if self.state:
            self.state = self._map_state_to_new_config(
                self.state,
                old_config or new_config,
                new_config,
            )
        else:
            self.state = create_initial_state(self.config, high_score=high_score)

        if self._hud is None:
            self._hud = HUD(id="hud")
        if self._board is None:
            self._board = GameBoard(config=self.config, id="game-board")
            self.query_one("#game-container").mount(self._hud, self._board)
        else:
            self._board.config = self.config
            self._board.refresh()

        if self._game_timer:
            self._game_timer.resume()

        self._update_widgets()

    def _scale_coord(self, value: int, old_max: int, new_max: int) -> int:
        if old_max <= 1:
            return 0
        return int(round(value * (new_max - 1) / (old_max - 1)))

    def _map_state_to_new_config(
        self,
        state: GameState,
        old_config: BoardConfig,
        new_config: BoardConfig,
    ) -> GameState:
        old_cols = old_config.columns
        old_rows = old_config.rows

        snake_cells = list(state.snake.cells)
        min_x = min(cell.x for cell in snake_cells)
        max_x = max(cell.x for cell in snake_cells)
        min_y = min(cell.y for cell in snake_cells)
        max_y = max(cell.y for cell in snake_cells)

        snake_width = max_x - min_x + 1
        snake_height = max_y - min_y + 1

        mapped_cells: list[Position] = []
        if snake_width <= new_config.columns and snake_height <= new_config.rows:
            desired_dx = (new_config.columns - old_cols) // 2
            desired_dy = (new_config.rows - old_rows) // 2

            dx_min = -min_x
            dx_max = (new_config.columns - 1) - max_x
            dy_min = -min_y
            dy_max = (new_config.rows - 1) - max_y

            dx = max(dx_min, min(dx_max, desired_dx))
            dy = max(dy_min, min(dy_max, desired_dy))

            mapped_cells = [
                Position(cell.x + dx, cell.y + dy)
                for cell in snake_cells
            ]
        else:
            seen: set[Position] = set()
            for cell in snake_cells:
                new_x = self._scale_coord(cell.x, old_cols, new_config.columns)
                new_y = self._scale_coord(cell.y, old_rows, new_config.rows)
                new_pos = Position(
                    max(0, min(new_config.columns - 1, new_x)),
                    max(0, min(new_config.rows - 1, new_y)),
                )
                if new_pos not in seen:
                    seen.add(new_pos)
                    mapped_cells.append(new_pos)

        if not mapped_cells:
            mapped_cells = [Position(new_config.columns // 2, new_config.rows // 2)]

        mapped_head = mapped_cells[0]
        mapped_snake = Snake(
            head=mapped_head,
            velocity=state.snake.velocity,
            cells=tuple(mapped_cells),
            max_cells=state.snake.max_cells,
        )

        if snake_width <= new_config.columns and snake_height <= new_config.rows:
            desired_dx = (new_config.columns - old_cols) // 2
            desired_dy = (new_config.rows - old_rows) // 2
            dx_min = -min_x
            dx_max = (new_config.columns - 1) - max_x
            dy_min = -min_y
            dy_max = (new_config.rows - 1) - max_y
            dx = max(dx_min, min(dx_max, desired_dx))
            dy = max(dy_min, min(dy_max, desired_dy))
            apple_x = state.apple.x + dx
            apple_y = state.apple.y + dy
        else:
            apple_x = self._scale_coord(state.apple.x, old_cols, new_config.columns)
            apple_y = self._scale_coord(state.apple.y, old_rows, new_config.rows)

        mapped_apple = Position(
            max(0, min(new_config.columns - 1, apple_x)),
            max(0, min(new_config.rows - 1, apple_y)),
        )
        if mapped_apple in mapped_snake.cells:
            mapped_apple = spawn_apple(mapped_snake.cells, new_config)

        return GameState(
            snake=mapped_snake,
            apple=mapped_apple,
            score=state.score,
            high_score=state.high_score,
            is_game_over=state.is_game_over,
            is_paused=state.is_paused,
        )

    def _start_game_loop(self) -> None:
        self._game_timer = self.set_interval(
            TICK_INTERVAL,
            self._game_tick,
        )

    def _game_tick(self) -> None:
        if self.state is None or self.state.is_game_over or self.state.is_paused:
            return
        self.state = tick(self.state, self.config)
        self._update_widgets()
        if self.state.is_game_over and self._game_timer:
            self._game_timer.pause()

    def _update_widgets(self) -> None:
        if self.state is None:
            return
            
        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
            )
        if self._board:
            self._board.update_state(
                snake_cells=self.state.snake.cells,
                apple=self.state.apple,
                is_game_over=self.state.is_game_over,
            )

    def action_move_up(self) -> None:
        if self.state:
            self.state = change_direction(self.state, Direction.UP)

    def action_move_down(self) -> None:
        if self.state:
            self.state = change_direction(self.state, Direction.DOWN)

    def action_move_left(self) -> None:
        if self.state:
            self.state = change_direction(self.state, Direction.LEFT)

    def action_move_right(self) -> None:
        if self.state:
            self.state = change_direction(self.state, Direction.RIGHT)

    def action_reset(self) -> None:
        if self.state:
            high_score = self.state.high_score
            self.state = create_initial_state(self.config, high_score=high_score)
            if self._game_timer:
                self._game_timer.resume()
            self._update_widgets()

    def action_pause(self) -> None:
        if self.state:
            self.state = toggle_pause(self.state)
            if self._game_timer:
                if self.state.is_paused:
                    self._game_timer.pause()
                else:
                    self._game_timer.resume()
            self._update_widgets()

    def action_toggle_theme(self) -> None:
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()


def main() -> None:
    app = SnakeApp()
    app.run()


if __name__ == "__main__":
    main()
