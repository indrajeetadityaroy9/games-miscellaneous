import type { Square, PieceSymbol, Color } from 'chess.js';

export type { Square, PieceSymbol, Color };

export type Theme = 'light' | 'dark';

export interface ChessPiece {
  type: PieceSymbol;
  color: Color;
}

export interface GameStatus {
  inCheck: boolean;
  inCheckmate: boolean;
  inStalemate: boolean;
  inDraw: boolean;
  isGameOver: boolean;
}

export interface Move {
  from: Square;
  to: Square;
  promotion?: PieceSymbol;
}
