export type Player = 'X' | 'O';
export type CellValue = Player | number;
export type Board = CellValue[];

export interface GameWon {
  index: number;
  player: Player;
}

export interface MinimaxResult {
  score: number;
  index?: number;
}

export interface GameState {
  board: Board;
  isGameOver: boolean;
  winner: string | null;
  winningCells: number[];
}

export type Theme = 'light' | 'dark';
