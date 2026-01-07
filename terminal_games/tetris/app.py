from pathlib import Path
from dataclasses import replace
from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header
from .models import BoardConfig, GameState, Position
from .game_logic import (
    create_initial_state,
    can_place_piece,
    move_left,
    move_right,
    move_down,
    try_rotate,
    do_hard_drop,
    toggle_pause,
    calculate_speed,
)
from .widgets.game_board import GameBoard
from .widgets.hud import HUD
from ..config import get_theme, set_theme
class TetrisApp(App):
    CSS_PATH = Path(__file__).parent / "styles" / "tetris.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("up", "rotate", "Rotate", show=False),
        Binding("w", "rotate", "Rotate", show=False),
        Binding("down", "soft_drop", "Down", show=False),
        Binding("s", "soft_drop", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("a", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("d", "move_right", "Right", show=False),
        Binding("space", "hard_drop", "Drop"),
        Binding("r", "reset", "Reset"),
        Binding("p", "pause", "Pause"),
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Tetris"

    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.state: GameState | None = None
        self._gravity_timer: Timer | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()

    def on_mount(self) -> None:
        self._configure_layout(force_reset=True)
        self._start_gravity()
        self._update_widgets()
        self.theme = get_theme()

    def on_resize(self, event: events.Resize) -> None:
        self._configure_layout()

    def _calculate_board_config(self) -> BoardConfig:
        screen_width = self.size.width
        screen_height = self.size.height

        # Tetris board renders each cell as 2 chars wide + borders
        available_width = max(22, screen_width - 6)
        cols = max(10, (available_width - 2) // 2)

        available_height = max(20, screen_height - 9)
        rows = max(14, available_height - 2)

        return BoardConfig(width=cols, height=rows)

    def _configure_layout(self, force_reset: bool = False) -> None:
        new_config = self._calculate_board_config()
        if (
            not force_reset
            and self.config
            and (self.config.width, self.config.height)
            == (new_config.width, new_config.height)
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

        self._start_gravity()
        self._update_widgets()

    def _map_state_to_new_config(
        self,
        state: GameState,
        old_config: BoardConfig,
        new_config: BoardConfig,
    ) -> GameState:
        old_w = old_config.width
        old_h = old_config.height

        delta_x = (new_config.width - old_w) // 2
        delta_y = new_config.height - old_h

        new_board = [
            [0 for _ in range(new_config.width)]
            for _ in range(new_config.height)
        ]
        for y in range(old_h):
            for x in range(old_w):
                cell = state.board[y][x]
                if cell == 0:
                    continue
                new_x = x + delta_x
                new_y = y + delta_y
                if 0 <= new_x < new_config.width and 0 <= new_y < new_config.height:
                    new_board[new_y][new_x] = cell

        new_position = state.position
        if state.current_piece is not None:
            pos_x = state.position.x + delta_x
            pos_y = state.position.y + delta_y
            max_x = max(0, new_config.width - len(state.current_piece.shape[0]))
            pos_x = max(0, min(max_x, pos_x))
            pos_y = max(-2, min(new_config.height - 1, pos_y))
            new_position = Position(pos_x, pos_y)

            if not can_place_piece(
                state.current_piece,
                new_position,
                tuple(tuple(r) for r in new_board),
                new_config,
            ):
                new_position = self._find_valid_position(
                    state.current_piece,
                    new_position,
                    tuple(tuple(r) for r in new_board),
                    new_config,
                )

        mapped = replace(
            state,
            board=tuple(tuple(r) for r in new_board),
            position=new_position,
        )

        if state.current_piece and not can_place_piece(
            state.current_piece,
            new_position,
            mapped.board,
            new_config,
        ):
            mapped = replace(mapped, current_piece=None, is_game_over=True)

        return mapped

    def _find_valid_position(
        self,
        piece,
        start_pos: Position,
        board: tuple[tuple[int, ...], ...],
        config: BoardConfig,
    ) -> Position:
        for delta in range(config.height):
            for dy in (0, -delta, delta):
                test_y = start_pos.y + dy
                if test_y < -2 or test_y >= config.height:
                    continue
                test_pos = Position(start_pos.x, test_y)
                if can_place_piece(piece, test_pos, board, config):
                    return test_pos
        return start_pos

    def _start_gravity(self) -> None:
        if self._gravity_timer:
            self._gravity_timer.stop()
        if self.state:
            speed = calculate_speed(self.state.level)
            self._gravity_timer = self.set_interval(speed, self._gravity_tick)

    def _gravity_tick(self) -> None:
        if self.state is None or self.state.is_game_over or self.state.is_paused:
            return
        old_level = self.state.level
        self.state, locked = move_down(self.state, self.config)
        self._update_widgets()
        if self.state.level != old_level:
            self._start_gravity()
        if self.state.is_game_over and self._gravity_timer:
            self._gravity_timer.pause()

    def _update_widgets(self) -> None:
        if self.state is None:
            return

        if self._hud:
            self._hud.update_state(
                level=self.state.level,
                score=self.state.score,
                high_score=self.state.high_score,
                lines=self.state.lines_cleared,
                is_paused=self.state.is_paused,
                is_game_over=self.state.is_game_over,
            )
        if self._board:
            self._board.update_state(
                board=self.state.board,
                current_piece=self.state.current_piece,
                piece_position=self.state.position,
                is_game_over=self.state.is_game_over,
            )

    def action_move_left(self) -> None:
        if self.state and not (self.state.is_game_over or self.state.is_paused):
            self.state = move_left(self.state, self.config)
            self._update_widgets()

    def action_move_right(self) -> None:
        if self.state and not (self.state.is_game_over or self.state.is_paused):
            self.state = move_right(self.state, self.config)
            self._update_widgets()

    def action_soft_drop(self) -> None:
        if self.state and not (self.state.is_game_over or self.state.is_paused):
            old_level = self.state.level
            self.state, _ = move_down(self.state, self.config)
            self._update_widgets()
            if self.state.level != old_level:
                self._start_gravity()

    def action_rotate(self) -> None:
        if self.state and not (self.state.is_game_over or self.state.is_paused):
            self.state = try_rotate(self.state, self.config)
            self._update_widgets()

    def action_hard_drop(self) -> None:
        if self.state and not (self.state.is_game_over or self.state.is_paused):
            old_level = self.state.level
            self.state = do_hard_drop(self.state, self.config)
            self._update_widgets()
            if self.state.level != old_level:
                self._start_gravity()
            if self.state.is_game_over and self._gravity_timer:
                self._gravity_timer.pause()

    def action_reset(self) -> None:
        if self.state:
            high_score = self.state.high_score
            self.state = create_initial_state(self.config, high_score=high_score)
            self._start_gravity()
            self._update_widgets()

    def action_pause(self) -> None:
        if self.state:
            self.state = toggle_pause(self.state)
            if self._gravity_timer:
                if self.state.is_paused:
                    self._gravity_timer.pause()
                else:
                    self._gravity_timer.resume()
            self._update_widgets()

    def action_toggle_theme(self) -> None:
        self.theme = (
            "textual-light" if self.theme == "textual-dark" else "textual-dark"
        )
        set_theme(self.theme)
        if self._board:
            self._board.refresh()
def main() -> None:
    app = TetrisApp()
    app.run()
if __name__ == "__main__":
    main()
