"""Minimax fallback agents for games with traditional AI."""

from pathlib import Path
from typing import Optional
import random

import chess

from ..base import RLAgent, AgentResponse, AgentType
from ..config import RLConfig
from ...tictactoe.models import GameState as TicTacToeState


class ChessMinimaxAgent(RLAgent[chess.Board, chess.Move]):
    """Chess agent using minimax algorithm."""

    def __init__(self, config: RLConfig, depth: int = 3) -> None:
        self.config = config
        self._depth = depth

    @property
    def name(self) -> str:
        return "Chess Minimax Agent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MINIMAX

    def load_model(self, path: Path) -> None:
        """Minimax doesn't need a model."""
        pass

    def is_model_loaded(self) -> bool:
        return True

    def get_action(self, board: chess.Board) -> AgentResponse[chess.Move]:
        """Get best move from minimax."""
        from ...chess.chess_ai import get_best_move

        move = get_best_move(board, depth=self._depth)
        if move is None:
            legal_moves = list(board.legal_moves)
            if legal_moves:
                move = random.choice(legal_moves)
                return AgentResponse(action=move, fallback_used=True)
            raise ValueError("No legal moves available")

        return AgentResponse(action=move)

    def get_fallback_action(self, board: chess.Board) -> Optional[chess.Move]:
        """Random fallback."""
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None


class TicTacToeMinimaxAgent(RLAgent[TicTacToeState, int]):
    """Tic-Tac-Toe agent using minimax algorithm."""

    def __init__(self, config: RLConfig) -> None:
        self.config = config

    @property
    def name(self) -> str:
        return "Tic-Tac-Toe Minimax Agent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MINIMAX

    def load_model(self, path: Path) -> None:
        """Minimax doesn't need a model."""
        pass

    def is_model_loaded(self) -> bool:
        return True

    def get_action(self, state: TicTacToeState) -> AgentResponse[int]:
        """Get best move from minimax."""
        from ...tictactoe.game_logic import get_best_move

        position = get_best_move(state.board)
        return AgentResponse(action=position)

    def get_fallback_action(self, state: TicTacToeState) -> Optional[int]:
        """Random fallback."""
        empty = [i for i, cell in enumerate(state.board) if isinstance(cell, int)]
        return random.choice(empty) if empty else None
