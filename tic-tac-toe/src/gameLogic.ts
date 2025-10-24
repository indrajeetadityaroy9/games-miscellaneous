import type { Player, Board, GameWon, MinimaxResult } from './types';

export const HUMAN_PLAYER: Player = 'O';
export const AI_PLAYER: Player = 'X';

export const WIN_COMBOS = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [6, 4, 2],
];

export function createEmptyBoard(): Board {
  return Array.from(Array(9).keys());
}

export function checkWin(board: Board, player: Player): GameWon | null {
  const plays = board.reduce<number[]>(
    (acc, cell, index) => (cell === player ? [...acc, index] : acc),
    []
  );

  for (const [index, combo] of WIN_COMBOS.entries()) {
    if (combo.every((cell) => plays.includes(cell))) {
      return { index, player };
    }
  }

  return null;
}

export function getEmptySquares(board: Board): number[] {
  return board.filter((cell) => typeof cell === 'number') as number[];
}

export function checkTie(board: Board): boolean {
  return getEmptySquares(board).length === 0;
}

export function minimax(board: Board, player: Player): MinimaxResult {
  const availableSpots = getEmptySquares(board);

  const humanWin = checkWin(board, HUMAN_PLAYER);
  const aiWin = checkWin(board, AI_PLAYER);

  if (humanWin) {
    return { score: -10 };
  } else if (aiWin) {
    return { score: 10 };
  } else if (availableSpots.length === 0) {
    return { score: 0 };
  }

  const moves: MinimaxResult[] = [];

  for (const spot of availableSpots) {
    const move: MinimaxResult = {
      index: board[spot] as number,
      score: 0,
    };

    board[spot] = player;

    const result = minimax(
      board,
      player === AI_PLAYER ? HUMAN_PLAYER : AI_PLAYER
    );
    move.score = result.score;

    board[spot] = move.index as number;
    moves.push(move);
  }

  let bestMove: MinimaxResult;
  if (player === AI_PLAYER) {
    let bestScore = -10000;
    bestMove = moves[0];
    for (const move of moves) {
      if (move.score > bestScore) {
        bestScore = move.score;
        bestMove = move;
      }
    }
  } else {
    let bestScore = 10000;
    bestMove = moves[0];
    for (const move of moves) {
      if (move.score < bestScore) {
        bestScore = move.score;
        bestMove = move;
      }
    }
  }

  return bestMove;
}

export function getBestSpot(board: Board): number {
  return minimax(board, AI_PLAYER).index as number;
}
