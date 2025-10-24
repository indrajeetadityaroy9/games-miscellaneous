import { Link } from 'react-router-dom';
import ChessBoard from './ChessBoard';
import './ChessPage.css';

function ChessPage() {
  return (
    <div className="game-page">
      <Link to="/" className="back-button">
        ← Back to Home
      </Link>
      <ChessBoard />
    </div>
  );
}

export default ChessPage;
