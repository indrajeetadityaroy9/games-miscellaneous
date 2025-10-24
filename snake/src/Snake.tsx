import { useEffect, useRef, useState, useCallback } from 'react';
import type { Snake as SnakeType, Position, GameConfig, Theme, ThemeColors } from './types';
import './Snake.css';

const baseConfig = {
  canvasWidth: 768,
  canvasHeight: 448,
  grid: 32,
};

const themeColors: Record<Theme, ThemeColors> = {
  dark: {
    primary: '#AF1E2D',
    secondary: '#FFCE00',
    canvasBackground: '#000000',
    scoreOverlay: 'rgba(255, 255, 255, 0.25)',
  },
  light: {
    primary: '#2ECC71',
    secondary: '#E74C3C',
    canvasBackground: '#F0F0F0',
    scoreOverlay: 'rgba(0, 0, 0, 0.15)',
  },
};

function Snake() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [theme, setTheme] = useState<Theme>('light');

  const config: GameConfig = {
    ...baseConfig,
    primary: themeColors[theme].primary,
    secondary: themeColors[theme].secondary,
  };

  const snakeRef = useRef<SnakeType>({
    x: config.grid * 5,
    y: config.grid * 5,
    vx: config.grid,
    vy: 0,
    cells: [],
    maxCells: 4,
  });
  const appleRef = useRef<Position>({
    x: config.grid * 10,
    y: config.grid * 10,
  });
  const countRef = useRef(0);
  const animationRef = useRef<number | undefined>(undefined);

  const getRandomInt = (min: number, max: number): number => {
    return Math.floor(Math.random() * (max - min)) + min;
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const resetGame = useCallback(() => {
    snakeRef.current = {
      x: config.grid * 5,
      y: config.grid * 5,
      vx: config.grid,
      vy: 0,
      cells: [],
      maxCells: 4,
    };
    appleRef.current = {
      x: config.grid * 10,
      y: config.grid * 10,
    };
    setScore(0);
  }, []);

  const update = useCallback(() => {
    animationRef.current = requestAnimationFrame(update);

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    countRef.current++;
    if (countRef.current < 4) {
      return;
    }
    countRef.current = 0;

    const snake = snakeRef.current;
    const apple = appleRef.current;

    ctx.fillStyle = themeColors[theme].canvasBackground;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    snake.x += snake.vx;
    snake.y += snake.vy;

    if (snake.x < 0) {
      snake.x = canvas.width - config.grid;
    } else if (snake.x >= canvas.width) {
      snake.x = 0;
    }

    if (snake.y < 0) {
      snake.y = canvas.height - config.grid;
    } else if (snake.y >= canvas.height) {
      snake.y = 0;
    }

    snake.cells.unshift({ x: snake.x, y: snake.y });

    if (snake.cells.length > snake.maxCells) {
      snake.cells.pop();
    }

    ctx.fillStyle = config.secondary;
    ctx.fillRect(apple.x, apple.y, config.grid - 1, config.grid - 1);

    ctx.fillStyle = config.primary;
    snake.cells.forEach((cell, index) => {
      ctx.fillRect(cell.x, cell.y, config.grid - 1, config.grid - 1);

      if (cell.x === apple.x && cell.y === apple.y) {
        snake.maxCells++;
        setScore((prev) => prev + 1);

        apple.x = getRandomInt(0, 24) * config.grid;
        apple.y = getRandomInt(0, 14) * config.grid;
      }

      for (let i = index + 1; i < snake.cells.length; i++) {
        if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
          resetGame();
        }
      }
    });

    ctx.font = '72px Helvetica';
    ctx.fillStyle = themeColors[theme].scoreOverlay;
    ctx.textAlign = 'center';
    ctx.fillText(score.toString(), canvas.width / 2, canvas.height / 2);
  }, [score, resetGame, theme]);

  useEffect(() => {
    const handleKeyDown = (evt: KeyboardEvent) => {
      const snake = snakeRef.current;

      if (evt.which === 37 && snake.vx === 0) {
        snake.vx = -config.grid;
        snake.vy = 0;
      }
      else if (evt.which === 38 && snake.vy === 0) {
        snake.vy = -config.grid;
        snake.vx = 0;
      }
      else if (evt.which === 39 && snake.vx === 0) {
        snake.vx = config.grid;
        snake.vy = 0;
      }
      else if (evt.which === 40 && snake.vy === 0) {
        snake.vy = config.grid;
        snake.vx = 0;
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    animationRef.current = requestAnimationFrame(update);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [update]);

  return (
    <div className={`snake-game ${theme}`}>
      <div className="game-header">
        <div className="score-display">Score: {score}</div>
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
      <canvas
        ref={canvasRef}
        width={config.canvasWidth}
        height={config.canvasHeight}
      />
      <div className="controls-info">
        Use arrow keys to control the snake
      </div>
    </div>
  );
}

export default Snake;
