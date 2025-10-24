import { Link } from 'react-router-dom';
import './LandingPage.css';

interface GameCard {
  id: string;
  title: string;
  path: string;
  icon: string;
}

const games: GameCard[] = [
  {
    id: 'chess',
    title: 'Chess',
    path: '/chess',
    icon: '♟️',
  },
  {
    id: 'tic-tac-toe',
    title: 'Tic-Tac-Toe',
    path: '/tic-tac-toe',
    icon: '❌',
  },
  {
    id: 'snake',
    title: 'Snake',
    path: '/snake',
    icon: '🐍',
  },
];

function LandingPage() {
  return (
    <div className="landing-page">
      <header className="header">
        <p className="subtitle">Choose a game to play</p>
      </header>

      <div className="games-grid">
        {games.map((game) => (
          <Link key={game.id} to={game.path} className="game-card">
            <div className="game-icon">{game.icon}</div>
            <h2 className="game-title">{game.title}</h2>
            <button className="play-button">Play Now</button>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default LandingPage;
