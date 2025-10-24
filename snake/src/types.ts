export interface Position {
  x: number;
  y: number;
}

export interface Snake {
  x: number;
  y: number;
  vx: number;
  vy: number;
  cells: Position[];
  maxCells: number;
}

export interface GameConfig {
  canvasWidth: number;
  canvasHeight: number;
  grid: number;
  primary: string;
  secondary: string;
}

export type Theme = 'dark' | 'light';

export interface ThemeColors {
  primary: string;
  secondary: string;
  canvasBackground: string;
  scoreOverlay: string;
}
