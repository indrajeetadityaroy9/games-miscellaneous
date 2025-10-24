# Chess - React + TypeScript

A modern chess game with AI opponent built using React, TypeScript, and chess.js library.

## Features

- Full chess rules implementation (using chess.js library)
- AI opponent with minimax algorithm and alpha-beta pruning
- Multiple difficulty levels (Easy, Medium, Hard, Expert)
- Visual feedback for legal moves
- Check/checkmate/stalemate detection
- Clean, responsive UI with smooth animations
- TypeScript for type safety

## Tech Stack

- **React 19** - Component-based UI
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool with HMR
- **chess.js** - Chess game logic library

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

- `ChessBoard.tsx` - Main chess board component with game state
- `chessAI.ts` - AI implementation using minimax with alpha-beta pruning
- `types.ts` - TypeScript type definitions

The AI evaluates positions based on material value and uses minimax search to find optimal moves.
