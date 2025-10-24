import { Link } from 'react-router-dom';
import TicTacToe from './TicTacToe';
import '../chess/ChessPage.css';

function TicTacToePage() {
  return (
    <div className="game-page">
      <Link to="/" className="back-button">
        ← Back to Home
      </Link>
      <TicTacToe />
    </div>
  );
}

export default TicTacToePage;
