"""Chess environment for TorchRL."""

from typing import Tuple, Dict, Optional

import numpy as np
import chess

from .base import GameEnvironment
from .registry import register_environment


@register_environment("chess")
class ChessEnvironment(GameEnvironment[chess.Board, chess.Move]):
    """
    Chess environment for TorchRL.

    Observation: (13, 8, 8) tensor
        - 12 planes for piece types (6 white + 6 black)
        - 1 plane for side to move

    Action space: ~4672 discrete actions (all from-to moves + promotions)
    """

    # 12 piece planes + 1 turn indicator
    OBSERVATION_SHAPE = (13, 8, 8)

    def __init__(self) -> None:
        # Pre-compute move index mapping
        self._move_to_index: Dict[str, int] = {}
        self._index_to_move: Dict[int, str] = {}
        self._build_move_index()

    def _build_move_index(self) -> None:
        """Build bidirectional mapping between moves and indices."""
        idx = 0
        for from_sq in range(64):
            for to_sq in range(64):
                if from_sq != to_sq:
                    uci = chess.square_name(from_sq) + chess.square_name(to_sq)
                    self._move_to_index[uci] = idx
                    self._index_to_move[idx] = uci
                    idx += 1
                    # Add promotion variants for pawn moves to back rank
                    from_rank = chess.square_rank(from_sq)
                    to_rank = chess.square_rank(to_sq)
                    if (from_rank == 6 and to_rank == 7) or (
                        from_rank == 1 and to_rank == 0
                    ):
                        for promo in ["q", "r", "b", "n"]:
                            uci_promo = uci + promo
                            self._move_to_index[uci_promo] = idx
                            self._index_to_move[idx] = uci_promo
                            idx += 1
        self._action_space_size = idx

    @property
    def observation_shape(self) -> Tuple[int, ...]:
        return self.OBSERVATION_SHAPE

    @property
    def action_space_size(self) -> int:
        return self._action_space_size

    def state_to_observation(self, board: chess.Board) -> np.ndarray:
        """Convert chess board to tensor representation."""
        obs = np.zeros(self.OBSERVATION_SHAPE, dtype=np.float32)

        piece_map = {
            (chess.PAWN, chess.WHITE): 0,
            (chess.KNIGHT, chess.WHITE): 1,
            (chess.BISHOP, chess.WHITE): 2,
            (chess.ROOK, chess.WHITE): 3,
            (chess.QUEEN, chess.WHITE): 4,
            (chess.KING, chess.WHITE): 5,
            (chess.PAWN, chess.BLACK): 6,
            (chess.KNIGHT, chess.BLACK): 7,
            (chess.BISHOP, chess.BLACK): 8,
            (chess.ROOK, chess.BLACK): 9,
            (chess.QUEEN, chess.BLACK): 10,
            (chess.KING, chess.BLACK): 11,
        }

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                plane = piece_map[(piece.piece_type, piece.color)]
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                obs[plane, rank, file] = 1.0

        # Side to move plane (1.0 for white's turn)
        obs[12, :, :] = 1.0 if board.turn == chess.WHITE else 0.0

        return obs

    def action_to_game_action(
        self, action_idx: int, state: chess.Board
    ) -> chess.Move:
        """Convert action index to chess move."""
        uci = self._index_to_move.get(action_idx)
        if uci:
            return chess.Move.from_uci(uci)
        raise ValueError(f"Invalid action index: {action_idx}")

    def get_legal_action_mask(self, board: chess.Board) -> np.ndarray:
        """Get mask of legal moves."""
        mask = np.zeros(self.action_space_size, dtype=np.float32)
        for move in board.legal_moves:
            uci = move.uci()
            if uci in self._move_to_index:
                mask[self._move_to_index[uci]] = 1.0
        return mask

    def move_to_action_index(self, move: chess.Move) -> Optional[int]:
        """Convert a chess move to its action index."""
        uci = move.uci()
        return self._move_to_index.get(uci)
