import { Chess } from 'chess.js';
import type { Move } from 'chess.js';

const PIECE_VALUES: Record<string, number> = {
  p: 100,
  n: 320,
  b: 330,
  r: 500,
  q: 900,
  k: 20000
};

function evaluateBoard(chess: Chess): number {
  if (chess.isCheckmate()) {
    return chess.turn() === 'w' ? -20000 : 20000;
  }

  if (chess.isDraw() || chess.isStalemate()) {
    return 0;
  }

  let score = 0;
  const board = chess.board();

  for (const row of board) {
    for (const square of row) {
      if (square) {
        const value = PIECE_VALUES[square.type];
        score += square.color === 'w' ? value : -value;
      }
    }
  }

  return score;
}

function minimax(
  chess: Chess,
  depth: number,
  alpha: number,
  beta: number,
  maximizingPlayer: boolean
): number {
  if (depth === 0 || chess.isGameOver()) {
    return evaluateBoard(chess);
  }

  const moves = chess.moves({ verbose: true });

  if (maximizingPlayer) {
    let maxEval = -Infinity;
    for (const move of moves) {
      chess.move(move);
      const evaluation = minimax(chess, depth - 1, alpha, beta, false);
      chess.undo();
      maxEval = Math.max(maxEval, evaluation);
      alpha = Math.max(alpha, evaluation);
      if (beta <= alpha) break;
    }
    return maxEval;
  } else {
    let minEval = Infinity;
    for (const move of moves) {
      chess.move(move);
      const evaluation = minimax(chess, depth - 1, alpha, beta, true);
      chess.undo();
      minEval = Math.min(minEval, evaluation);
      beta = Math.min(beta, evaluation);
      if (beta <= alpha) break;
    }
    return minEval;
  }
}

export function getBestMove(chess: Chess, depth: number = 3): Move | null {
  const moves = chess.moves({ verbose: true });

  if (moves.length === 0) return null;

  let bestMoves: Move[] = [];
  let bestValue = -Infinity;

  for (const move of moves) {
    chess.move(move);
    const boardValue = minimax(chess, depth - 1, -Infinity, Infinity, false);
    chess.undo();

    if (boardValue > bestValue) {
      bestValue = boardValue;
      bestMoves = [move];
    } else if (boardValue === bestValue) {
      bestMoves.push(move);
    }
  }

  const randomIndex = Math.floor(Math.random() * bestMoves.length);
  return bestMoves[randomIndex];
}
