import { Link } from 'react-router-dom';
import Snake from './Snake';
import '../chess/ChessPage.css';

function SnakePage() {
  return (
    <div className="game-page">
      <Link to="/" className="back-button">
        ← Back to Home
      </Link>
      <Snake />
    </div>
  );
}

export default SnakePage;
