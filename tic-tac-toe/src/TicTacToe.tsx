import { useState, useCallback } from 'react';
import {
  createEmptyBoard,
  checkWin,
  checkTie,
  getBestSpot,
  HUMAN_PLAYER,
  AI_PLAYER,
  WIN_COMBOS,
} from './gameLogic';
import type { GameState, Theme } from './types';
import './TicTacToe.css';

function TicTacToe() {
  const [gameState, setGameState] = useState<GameState>({
    board: createEmptyBoard(),
    isGameOver: false,
    winner: null,
    winningCells: [],
  });
  const [theme, setTheme] = useState<Theme>('light');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const startGame = useCallback(() => {
    setGameState({
      board: createEmptyBoard(),
      isGameOver: false,
      winner: null,
      winningCells: [],
    });
  }, []);

  const handleCellClick = (index: number) => {
    if (
      gameState.isGameOver ||
      typeof gameState.board[index] !== 'number'
    ) {
      return;
    }

    const newBoard = [...gameState.board];
    newBoard[index] = HUMAN_PLAYER;

    const humanWin = checkWin(newBoard, HUMAN_PLAYER);
    if (humanWin) {
      setGameState({
        board: newBoard,
        isGameOver: true,
        winner: 'You Win!',
        winningCells: WIN_COMBOS[humanWin.index],
      });
      setTimeout(startGame, 3000);
      return;
    }

    if (checkTie(newBoard)) {
      setGameState({
        board: newBoard,
        isGameOver: true,
        winner: 'Tie Game!',
        winningCells: [],
      });
      setTimeout(startGame, 3000);
      return;
    }

    const aiMove = getBestSpot(newBoard);
    newBoard[aiMove] = AI_PLAYER;

    const aiWin = checkWin(newBoard, AI_PLAYER);
    if (aiWin) {
      setGameState({
        board: newBoard,
        isGameOver: true,
        winner: 'You Lose!',
        winningCells: WIN_COMBOS[aiWin.index],
      });
      setTimeout(startGame, 3000);
      return;
    }

    if (checkTie(newBoard)) {
      setGameState({
        board: newBoard,
        isGameOver: true,
        winner: 'Tie Game!',
        winningCells: [],
      });
      setTimeout(startGame, 3000);
      return;
    }

    setGameState({
      ...gameState,
      board: newBoard,
    });
  };

  const getCellClassName = (index: number): string => {
    const classes = ['cell'];

    if (gameState.winningCells.includes(index)) {
      classes.push('winning-cell');
    }

    return classes.join(' ');
  };

  const getCellStyle = (index: number): React.CSSProperties => {
    if (gameState.isGameOver) {
      if (gameState.winningCells.includes(index)) {
        return {
          backgroundColor: gameState.winner?.includes('Win') ? '#2ECC71' : '#E74C3C',
        };
      }
      if (gameState.winner === 'Tie Game!') {
        return { backgroundColor: '#F39C12' };
      }
    }
    return {};
  };

  return (
    <div className={`tic-tac-toe ${theme}`}>
      <div className="game-header">
        <button onClick={toggleTheme} className="theme-toggle">
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
      </div>

      <div className="game-container">
        <table>
        <tbody>
          {[0, 1, 2].map((row) => (
            <tr key={row}>
              {[0, 1, 2].map((col) => {
                const index = row * 3 + col;
                const cellValue = gameState.board[index];
                return (
                  <td
                    key={index}
                    className={getCellClassName(index)}
                    style={getCellStyle(index)}
                    onClick={() => handleCellClick(index)}
                  >
                    {typeof cellValue === 'string' ? cellValue : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

        <button onClick={startGame} className="new-game-btn">
          New Game
        </button>

        {gameState.winner && (
          <div className="endgame">
            <div className="text">{gameState.winner}</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TicTacToe;
