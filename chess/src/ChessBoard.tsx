import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Chess } from 'chess.js';
import type { Square, PieceSymbol, Color } from './types';
import { getBestMove } from './chessAI';
import './ChessBoard.css';

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] as const;
const RANKS = ['8', '7', '6', '5', '4', '3', '2', '1'] as const;

function ChessBoard() {
  const [game, setGame] = useState(new Chess());
  const [selectedSquare, setSelectedSquare] = useState<Square | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [difficulty, setDifficulty] = useState(3);
  const [showSetup, setShowSetup] = useState(true);
  const [playerColor, setPlayerColor] = useState<Color>('b');
  const [setupVisible, setSetupVisible] = useState(false);
  const [gameType, setGameType] = useState<'normal' | 'rapid'>('normal');
  const [playerTime, setPlayerTime] = useState(600);
  const [aiTime, setAiTime] = useState(600);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window === 'undefined') return false;
    const stored = window.localStorage.getItem('chess-theme');
    return stored === 'dark';
  });

  const PLAYER_COLOR = playerColor;
  const AI_COLOR: Color = playerColor === 'w' ? 'b' : 'w';

  const getPieceImage = (piece: { type: PieceSymbol; color: Color }) => {
    const color = piece.color === 'w' ? 'w' : 'b';
    const type = piece.type.toUpperCase();
    return `/images/pieces/${color}${type}.png`;
  };

  const getCapturedPieces = () => {
    const initialPieces = {
      w: { p: 8, n: 2, b: 2, r: 2, q: 1, k: 1 },
      b: { p: 8, n: 2, b: 2, r: 2, q: 1, k: 1 }
    };

    const currentPieces = {
      w: { p: 0, n: 0, b: 0, r: 0, q: 0, k: 0 },
      b: { p: 0, n: 0, b: 0, r: 0, q: 0, k: 0 }
    };

    const board = game.board();
    for (const row of board) {
      for (const square of row) {
        if (square) {
          currentPieces[square.color][square.type]++;
        }
      }
    }

    const capturedByWhite: PieceSymbol[] = [];
    const capturedByBlack: PieceSymbol[] = [];

    for (const [piece, count] of Object.entries(initialPieces.b)) {
      const missing = count - currentPieces.b[piece as PieceSymbol];
      for (let i = 0; i < missing; i++) {
        capturedByWhite.push(piece as PieceSymbol);
      }
    }

    for (const [piece, count] of Object.entries(initialPieces.w)) {
      const missing = count - currentPieces.w[piece as PieceSymbol];
      for (let i = 0; i < missing; i++) {
        capturedByBlack.push(piece as PieceSymbol);
      }
    }

    return { capturedByWhite, capturedByBlack };
  };

  useEffect(() => {
    if (gameType === 'rapid' && !showSetup && !game.isGameOver() && !isThinking) {
      const interval = setInterval(() => {
        if (game.turn() === PLAYER_COLOR) {
          setPlayerTime((prev) => {
            if (prev <= 0) {
              clearInterval(interval);
              return 0;
            }
            return prev - 1;
          });
        } else {
          setAiTime((prev) => {
            if (prev <= 0) {
              clearInterval(interval);
              return 0;
            }
            return prev - 1;
          });
        }
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [gameType, showSetup, game, isThinking, PLAYER_COLOR]);

  useEffect(() => {
    if (!showSetup && game.turn() === AI_COLOR && !isThinking && !game.isGameOver()) {
      makeAIMove();
    }
  }, [game, isThinking, showSetup, AI_COLOR]);

  useEffect(() => {
    if (showSetup) {
      const frame = requestAnimationFrame(() => setSetupVisible(true));
      return () => cancelAnimationFrame(frame);
    }
    setSetupVisible(false);
  }, [showSetup]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('chess-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const startGame = () => {
    setGame(new Chess());
    setSelectedSquare(null);
    setIsThinking(false);
    setPlayerTime(600);
    setAiTime(600);
    setShowSetup(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const makeAIMove = async () => {
    setIsThinking(true);

    await new Promise(resolve => setTimeout(resolve, 100));

    const move = await new Promise<any>((resolve) => {
      setTimeout(() => {
        resolve(getBestMove(game, difficulty));
      }, 0);
    });

    if (move) {
      const newGame = new Chess(game.fen());
      newGame.move(move);
      setGame(newGame);
    }

    setIsThinking(false);
  };

  const handleSquareClick = async (square: Square) => {
    if (isThinking || game.isGameOver()) return;

    if (!selectedSquare) {
      const piece = game.get(square);
      if (piece && piece.color === PLAYER_COLOR && game.turn() === PLAYER_COLOR) {
        setSelectedSquare(square);
      }
    } else {
      try {
        const newGame = new Chess(game.fen());
        newGame.move({ from: selectedSquare, to: square });
        setGame(newGame);
        setSelectedSquare(null);

      } catch {
        const piece = game.get(square);
        if (piece && piece.color === PLAYER_COLOR && game.turn() === PLAYER_COLOR) {
          setSelectedSquare(square);
        } else {
          setSelectedSquare(null);
        }
      }
    }
  };

  const handleNewGame = () => {
    setGame(new Chess());
    setSelectedSquare(null);
    setIsThinking(false);
    setPlayerTime(600);
    setAiTime(600);
  };

  const getGameStatus = () => {
    if (game.isCheckmate()) {
      return game.turn() === 'w' ? 'Checkmate! Black wins!' : 'Checkmate! White wins!';
    }
    if (game.isStalemate()) return 'Stalemate!';
    if (game.isDraw()) return 'Draw!';
    if (game.isCheck()) return 'Check!';
    return '';
  };

  const isSquareSelected = (square: Square) => selectedSquare === square;

  const isLegalMove = (square: Square) => {
    if (!selectedSquare) return false;
    const moves = game.moves({ square: selectedSquare, verbose: true });
    return moves.some(move => move.to === square);
  };

  const { capturedByWhite, capturedByBlack } = getCapturedPieces();

  return (
    <div className={`chess-container ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
      <button
        type="button"
        className="theme-toggle-btn"
        onClick={() => setIsDarkMode((prev) => !prev)}
        aria-pressed={isDarkMode}
        aria-label="Toggle dark mode"
      >
        {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
      </button>
      {showSetup && typeof document !== 'undefined' && createPortal(
        <div className={`setup-overlay ${setupVisible ? 'is-visible' : ''}`}>
          <div className={`setup-modal ${setupVisible ? 'is-visible' : ''}`}>
            <h2>Chess Game Setup</h2>

            <div className="setup-option">
              <label>Choose Your Color:</label>
              <div className="color-selector">
                <button
                  className={`color-btn ${playerColor === 'w' ? 'selected' : ''}`}
                  onClick={() => setPlayerColor('w')}
                >
                  ⚪ White (Play First)
                </button>
                <button
                  className={`color-btn ${playerColor === 'b' ? 'selected' : ''}`}
                  onClick={() => setPlayerColor('b')}
                >
                  ⚫ Black (AI Plays First)
                </button>
              </div>
            </div>

            <div className="setup-option">
              <label>Difficulty:</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(Number(e.target.value))}
                className="setup-select"
              >
                <option value={1}>Easy (Depth 1)</option>
                <option value={2}>Medium (Depth 2)</option>
                <option value={3}>Hard (Depth 3)</option>
                <option value={4}>Expert (Depth 4)</option>
              </select>
            </div>

            <div className="setup-option">
              <label>Game Type:</label>
              <div className="game-type-selector">
                <button
                  className={`type-btn ${gameType === 'normal' ? 'selected' : ''}`}
                  onClick={() => setGameType('normal')}
                >
                  🕐 Normal (No Time Limit)
                </button>
                <button
                  className={`type-btn ${gameType === 'rapid' ? 'selected' : ''}`}
                  onClick={() => setGameType('rapid')}
                >
                  ⚡ Rapid (10 min)
                </button>
              </div>
            </div>

            <button className="start-game-btn" onClick={startGame}>
              Start Game
            </button>
          </div>
        </div>,
        document.body
      )}

      <div className="game-board-container">
        <div className="left-sidebar">
          <div className="game-info-box">
            <div className="info-row">
              <span className="info-label">Playing as:</span>
              <span className="info-value">{playerColor === 'w' ? '⚪ White' : '⚫ Black'}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Turn:</span>
              <span className="info-value">
                {game.turn() === PLAYER_COLOR ? '🟢 Player' : '⏳ AI'}
              </span>
            </div>
            <button onClick={handleNewGame} className="new-game-btn-corner">
              New Game
            </button>
          </div>

          <div className="captured-pieces captured-by-white">
            <div className="captured-label">AI Captured</div>
            <div className="captured-pieces-list">
              {capturedByWhite.map((piece, index) => (
                <img
                  key={`w-${piece}-${index}`}
                  src={getPieceImage({ type: piece, color: 'b' })}
                  alt={`captured ${piece}`}
                  className="captured-piece"
                />
              ))}
            </div>
          </div>
        </div>

        <div className="board-section">
          {gameType === 'rapid' && (
            <div className="timer-box">
              <div className="timer-display">
                <div className={`timer ${game.turn() === PLAYER_COLOR ? 'active' : ''}`}>
                  <span className="timer-label">Player Time</span>
                  <span className="timer-value" style={{ color: playerTime < 60 ? '#e74c3c' : '#333' }}>
                    {formatTime(playerTime)}
                  </span>
                </div>
                <div className={`timer ${game.turn() === AI_COLOR ? 'active' : ''}`}>
                  <span className="timer-label">AI Time</span>
                  <span className="timer-value" style={{ color: aiTime < 60 ? '#e74c3c' : '#333' }}>
                    {formatTime(aiTime)}
                  </span>
                </div>
              </div>
              <div className="game-status-container">
                {getGameStatus() && <div className="game-status">{getGameStatus()}</div>}
              </div>
            </div>
          )}

          <div className="chessboard">
        {RANKS.map((rank) => (
          <div key={rank} className="board-row">
            {FILES.map((file) => {
              const square = `${file}${rank}` as Square;
              const piece = game.get(square);
              const isLight = (FILES.indexOf(file) + RANKS.indexOf(rank)) % 2 === 0;
              const isSelected = isSquareSelected(square);
              const isLegal = isLegalMove(square);

              return (
                <div
                  key={square}
                  className={`square ${isLight ? 'light' : 'dark'} ${isSelected ? 'selected' : ''} ${isLegal ? 'legal-move' : ''}`}
                  onClick={() => handleSquareClick(square)}
                >
                  {piece && (
                    <img
                      key={`${square}-${piece.color}-${piece.type}`}
                      src={getPieceImage(piece)}
                      alt={`${piece.color} ${piece.type}`}
                      className="chess-piece"
                      draggable={false}
                    />
                  )}
                  {isLegal && <div className="move-indicator" />}
                </div>
              );
            })}
          </div>
        ))}
          </div>
        </div>

        <div className="captured-pieces captured-by-black">
          <div className="captured-label">Player Captured</div>
          <div className="captured-pieces-list">
            {capturedByBlack.map((piece, index) => (
              <img
                key={`b-${piece}-${index}`}
                src={getPieceImage({ type: piece, color: 'w' })}
                alt={`captured ${piece}`}
                className="captured-piece"
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChessBoard;
