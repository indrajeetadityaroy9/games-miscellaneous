# Browser Games Collection

A unified game arcade featuring classic browser-based games built with React, TypeScript, and Vite. All games are integrated into a single landing page application with client-side routing.

🎮 **[Play the games here](https://indrajeetadityaroy.github.io/games-miscellaneous/)**

## Games Included

- **♟️ Chess** - Play against an AI opponent with minimax algorithm and alpha-beta pruning. Features configurable difficulty, timed/untimed modes, and captured piece tracking.
- **❌ Tic-Tac-Toe** - Classic tic-tac-toe with AI opponent and dark/light theme support.
- **🐍 Snake** - Retro snake game with pixel art graphics, level progression, and high score tracking.
- **👾 Space Invaders** - Arcade-style space shooter with multiple enemy types and increasing difficulty.
- **🧱 Tetris** - Classic block-stacking puzzle game with smooth controls and scoring system.

## Architecture

This project uses a **unified single-source architecture** where all games are routed pages within a single Vite + React + TypeScript application located in the `landing-page/` directory.

### Key Features
- ✅ Single source of truth - all games in `landing-page/src/games/`
- ✅ Client-side routing with React Router
- ✅ Standardized dark/light theme support across all games
- ✅ Optimized production build (~306 KB total)
- ✅ Deployed to GitHub Pages
- ✅ TypeScript for type safety
- ✅ Canvas-based rendering for pixel art games

## Development

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Setup

```bash
# Install dependencies
cd landing-page
npm install
```

### Running Locally

```bash
# From root directory
npm run dev

# Or from landing-page directory
cd landing-page && npm run dev
```

The dev server will start at `http://localhost:5173/` with access to all games.

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Deploying

```bash
# Deploy to GitHub Pages
npm run deploy
```

## Project Structure

```
landing-page/
├── public/
│   └── images/          # Chess piece images and other assets
├── src/
│   ├── games/
│   │   ├── chess/       # Chess game implementation
│   │   ├── snake/       # Snake game implementation
│   │   ├── space-invaders/  # Space Invaders implementation
│   │   ├── tetris/      # Tetris implementation
│   │   └── tic-tac-toe/ # Tic-Tac-Toe implementation
│   ├── App.tsx          # Main app with routing
│   ├── LandingPage.tsx  # Landing page with game selection
│   └── main.tsx         # Entry point
├── package.json
└── vite.config.ts       # Vite configuration
```

## Technologies Used

- **React 18** - UI library
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and dev server
- **React Router DOM** - Client-side routing
- **chess.js** - Chess game logic and move validation
- **HTML5 Canvas** - Rendering for pixel art games
- **CSS Custom Properties** - Theme system
- **GitHub Pages** - Hosting and deployment

## License

ISC
