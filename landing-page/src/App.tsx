import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import ChessPage from './games/chess/ChessPage';
import TicTacToePage from './games/tic-tac-toe/TicTacToePage';
import SnakePage from './games/snake/SnakePage';
import SpaceInvadersPage from './games/space-invaders/SpaceInvadersPage';

function App() {
  return (
    <Router basename="/games-miscellaneous">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chess" element={<ChessPage />} />
        <Route path="/tic-tac-toe" element={<TicTacToePage />} />
        <Route path="/snake" element={<SnakePage />} />
        <Route path="/space-invaders" element={<SpaceInvadersPage />} />
      </Routes>
    </Router>
  );
}

export default App;
