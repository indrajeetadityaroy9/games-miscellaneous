export type Theme = 'light' | 'dark';

export interface Position {
  x: number;
  y: number;
}

export interface Player {
  x: number;
  y: number;
  width: number;
  height: number;
  speed: number;
}

export interface Bullet {
  x: number;
  y: number;
  width: number;
  height: number;
  speed: number;
  active: boolean;
}

export interface Enemy {
  x: number;
  y: number;
  width: number;
  height: number;
  active: boolean;
  type: number;
}

export interface GameConfig {
  canvasWidth: number;
  canvasHeight: number;
  playerColor: string;
  enemyColor: string;
  bulletColor: string;
  backgroundColor: string;
}

export interface ThemeColors {
  player: string;
  enemy: string;
  bullet: string;
  background: string;
  text: string;
}
