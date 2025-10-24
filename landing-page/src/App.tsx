import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import ChessPage from './games/chess/ChessPage';
import TicTacToePage from './games/tic-tac-toe/TicTacToePage';
import SnakePage from './games/snake/SnakePage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chess" element={<ChessPage />} />
        <Route path="/tic-tac-toe" element={<TicTacToePage />} />
        <Route path="/snake" element={<SnakePage />} />
      </Routes>
    </Router>
  );
}

export default App;
