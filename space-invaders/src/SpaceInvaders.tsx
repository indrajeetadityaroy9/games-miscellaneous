import { useEffect, useRef, useState, useCallback } from 'react';
import type { Player, Bullet, Enemy, Theme, ThemeColors } from './types';
import './SpaceInvaders.css';

const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const PLAYER_WIDTH = 50;
const PLAYER_HEIGHT = 30;
const ENEMY_WIDTH = 40;
const ENEMY_HEIGHT = 30;
const BULLET_WIDTH = 4;
const BULLET_HEIGHT = 15;

const themeColors: Record<Theme, ThemeColors> = {
  dark: {
    player: '#00FF00',
    enemy: '#FF0000',
    bullet: '#FFFF00',
    background: '#000000',
    text: 'rgba(255, 255, 255, 0.15)',
  },
  light: {
    player: '#2ECC71',
    enemy: '#E74C3C',
    bullet: '#F39C12',
    background: '#0a0e27',
    text: 'rgba(255, 255, 255, 0.1)',
  },
};

function SpaceInvaders() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [won, setWon] = useState(false);
  const [theme, setTheme] = useState<Theme>('light');

  const playerRef = useRef<Player>({
    x: CANVAS_WIDTH / 2 - PLAYER_WIDTH / 2,
    y: CANVAS_HEIGHT - 60,
    width: PLAYER_WIDTH,
    height: PLAYER_HEIGHT,
    speed: 5,
  });

  const bulletsRef = useRef<Bullet[]>([]);
  const enemyBulletsRef = useRef<Bullet[]>([]);
  const enemiesRef = useRef<Enemy[]>([]);
  const keysRef = useRef<{ [key: string]: boolean }>({});
  const enemyDirectionRef = useRef(1);
  const lastShotRef = useRef(0);
  const lastEnemyShotRef = useRef(0);
  const animationRef = useRef<number | undefined>(undefined);
  const starsRef = useRef<{ x: number; y: number; size: number; speed: number }[]>([]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const drawPlayer = (ctx: CanvasRenderingContext2D, x: number, y: number, color: string) => {
    const pixelSize = 5;
    ctx.fillStyle = color;

    const pattern = [
      [0,0,0,0,0,1,0,0,0,0,0],
      [0,0,0,0,1,1,1,0,0,0,0],
      [0,0,0,0,1,1,1,0,0,0,0],
      [0,1,1,1,1,1,1,1,1,1,0],
      [1,1,1,1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1,1,1,1],
    ];

    pattern.forEach((row, i) => {
      row.forEach((pixel, j) => {
        if (pixel) {
          ctx.fillRect(x + j * pixelSize, y + i * pixelSize, pixelSize, pixelSize);
        }
      });
    });
  };

  const drawEnemy = (ctx: CanvasRenderingContext2D, x: number, y: number, color: string, type: number) => {
    const pixelSize = 4;
    ctx.fillStyle = color;

    let pattern: number[][] = [];

    if (type === 0) {
      pattern = [
        [0,0,1,0,0,0,0,0,1,0,0],
        [0,0,0,1,0,0,0,1,0,0,0],
        [0,0,1,1,1,1,1,1,1,0,0],
        [0,1,1,0,1,1,1,0,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1],
        [1,0,1,1,1,1,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,1,0,1],
        [0,0,0,1,1,0,1,1,0,0,0],
      ];
    } else if (type === 1) {
      pattern = [
        [0,0,1,0,0,0,0,0,1,0,0],
        [0,1,0,1,0,0,0,1,0,1,0],
        [0,1,1,1,1,1,1,1,1,1,0],
        [1,1,0,1,1,1,1,1,0,1,1],
        [1,1,1,1,1,1,1,1,1,1,1],
        [0,0,1,0,0,0,0,0,1,0,0],
        [0,1,0,1,0,0,0,1,0,1,0],
        [1,0,1,0,0,0,0,0,1,0,1],
      ];
    } else {
      pattern = [
        [0,0,0,0,1,1,1,1,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,0,0,1,1,0,0,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [0,0,0,1,1,0,0,1,1,0,0,0],
        [0,0,1,1,0,1,1,0,1,1,0,0],
        [1,1,0,0,0,0,0,0,0,0,1,1],
      ];
    }

    pattern.forEach((row, i) => {
      row.forEach((pixel, j) => {
        if (pixel) {
          ctx.fillRect(x + j * pixelSize, y + i * pixelSize, pixelSize, pixelSize);
        }
      });
    });
  };

  const initStars = useCallback(() => {
    const stars: { x: number; y: number; size: number; speed: number }[] = [];
    for (let i = 0; i < 150; i++) {
      stars.push({
        x: Math.random() * CANVAS_WIDTH,
        y: Math.random() * CANVAS_HEIGHT,
        size: Math.random() * 2,
        speed: Math.random() * 0.5 + 0.2,
      });
    }
    return stars;
  }, []);

  const initEnemies = useCallback(() => {
    const enemies: Enemy[] = [];
    const rows = 5;
    const cols = 10;
    const padding = 60;
    const spacing = 10;

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const type = row < 2 ? 0 : row < 4 ? 1 : 2;
        enemies.push({
          x: padding + col * (ENEMY_WIDTH + spacing),
          y: 50 + row * (ENEMY_HEIGHT + spacing),
          width: ENEMY_WIDTH,
          height: ENEMY_HEIGHT,
          active: true,
          type: type,
        });
      }
    }
    return enemies;
  }, []);

  const resetGame = useCallback(() => {
    playerRef.current = {
      x: CANVAS_WIDTH / 2 - PLAYER_WIDTH / 2,
      y: CANVAS_HEIGHT - 60,
      width: PLAYER_WIDTH,
      height: PLAYER_HEIGHT,
      speed: 5,
    };
    bulletsRef.current = [];
    enemyBulletsRef.current = [];
    enemiesRef.current = initEnemies();
    starsRef.current = initStars();
    enemyDirectionRef.current = 1;
    setScore(0);
    setGameOver(false);
    setWon(false);
  }, [initEnemies, initStars]);

  const shootBullet = useCallback(() => {
    const now = Date.now();
    if (now - lastShotRef.current > 300) {
      bulletsRef.current.push({
        x: playerRef.current.x + playerRef.current.width / 2 - BULLET_WIDTH / 2,
        y: playerRef.current.y,
        width: BULLET_WIDTH,
        height: BULLET_HEIGHT,
        speed: 7,
        active: true,
      });
      lastShotRef.current = now;
    }
  }, []);

  const enemyShoot = useCallback(() => {
    const now = Date.now();
    if (now - lastEnemyShotRef.current > 1000) {
      const activeEnemies = enemiesRef.current.filter((e) => e.active);
      if (activeEnemies.length > 0) {
        const randomEnemy = activeEnemies[Math.floor(Math.random() * activeEnemies.length)];
        enemyBulletsRef.current.push({
          x: randomEnemy.x + randomEnemy.width / 2 - BULLET_WIDTH / 2,
          y: randomEnemy.y + randomEnemy.height,
          width: BULLET_WIDTH,
          height: BULLET_HEIGHT,
          speed: 4,
          active: true,
        });
        lastEnemyShotRef.current = now;
      }
    }
  }, []);

  const checkCollision = (rect1: any, rect2: any) => {
    return (
      rect1.x < rect2.x + rect2.width &&
      rect1.x + rect1.width > rect2.x &&
      rect1.y < rect2.y + rect2.height &&
      rect1.y + rect1.height > rect2.y
    );
  };

  const update = useCallback(() => {
    if (gameOver || won) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const player = playerRef.current;
    const enemies = enemiesRef.current;
    const bullets = bulletsRef.current;
    const enemyBullets = enemyBulletsRef.current;
    const stars = starsRef.current;

    ctx.fillStyle = themeColors[theme].background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#FFFFFF';
    stars.forEach((star) => {
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fill();

      star.y += star.speed;

      if (star.y > CANVAS_HEIGHT) {
        star.y = 0;
        star.x = Math.random() * CANVAS_WIDTH;
      }
    });

    if (keysRef.current['ArrowLeft'] && player.x > 0) {
      player.x -= player.speed;
    }
    if (keysRef.current['ArrowRight'] && player.x < CANVAS_WIDTH - player.width) {
      player.x += player.speed;
    }
    if (keysRef.current[' ']) {
      shootBullet();
    }

    drawPlayer(ctx, player.x, player.y, themeColors[theme].player);

    ctx.fillStyle = themeColors[theme].bullet;
    bullets.forEach((bullet) => {
      if (bullet.active) {
        bullet.y -= bullet.speed;
        if (bullet.y < 0) bullet.active = false;
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
      }
    });

    enemyBullets.forEach((bullet) => {
      if (bullet.active) {
        bullet.y += bullet.speed;
        if (bullet.y > CANVAS_HEIGHT) bullet.active = false;
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);

        if (checkCollision(bullet, player)) {
          bullet.active = false;
          setGameOver(true);
        }
      }
    });

    let hitEdge = false;
    enemies.forEach((enemy) => {
      if (!enemy.active) return;
      enemy.x += enemyDirectionRef.current * 2;
      if (enemy.x <= 0 || enemy.x >= CANVAS_WIDTH - enemy.width) {
        hitEdge = true;
      }
    });

    if (hitEdge) {
      enemyDirectionRef.current *= -1;
      enemies.forEach((enemy) => {
        if (enemy.active) {
          enemy.y += 20;
          if (enemy.y + enemy.height >= player.y) {
            setGameOver(true);
          }
        }
      });
    }

    enemies.forEach((enemy) => {
      if (enemy.active) {
        drawEnemy(ctx, enemy.x, enemy.y, themeColors[theme].enemy, enemy.type);
      }
    });

    bullets.forEach((bullet) => {
      if (!bullet.active) return;
      enemies.forEach((enemy) => {
        if (!enemy.active) return;
        if (checkCollision(bullet, enemy)) {
          bullet.active = false;
          enemy.active = false;
          setScore((prev) => prev + 10);
        }
      });
    });

    enemyShoot();

    bulletsRef.current = bullets.filter((b) => b.active);
    enemyBulletsRef.current = enemyBullets.filter((b) => b.active);

    if (enemies.every((e) => !e.active)) {
      setWon(true);
    }

    ctx.font = '120px Helvetica';
    ctx.fillStyle = themeColors[theme].text;
    ctx.textAlign = 'center';
    ctx.fillText(score.toString(), canvas.width / 2, canvas.height / 2);
  }, [gameOver, won, theme, score, shootBullet, enemyShoot]);

  const gameLoop = useCallback(() => {
    update();
    animationRef.current = requestAnimationFrame(gameLoop);
  }, [update]);

  useEffect(() => {
    enemiesRef.current = initEnemies();
    starsRef.current = initStars();
  }, [initEnemies, initStars]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysRef.current[e.key] = true;
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      keysRef.current[e.key] = false;
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    animationRef.current = requestAnimationFrame(gameLoop);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [gameLoop]);

  return (
    <div className={`space-invaders ${theme}`}>
      <div className="game-header">
        <h1 className="game-title">Space Invaders</h1>
        <button onClick={toggleTheme} className="theme-toggle">
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
      </div>

      <canvas
        ref={canvasRef}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
        className="game-canvas"
      />

      <div className="controls-info">
        <div>← → Arrow keys to move</div>
        <div>SPACE to shoot</div>
      </div>

      {(gameOver || won) && (
        <div className="game-over-overlay">
          <div className="game-over-message">
            {won ? 'You Won!' : 'Game Over!'}
            <div className="final-score">Final Score: {score}</div>
            <button onClick={resetGame} className="restart-btn">
              Play Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SpaceInvaders;
