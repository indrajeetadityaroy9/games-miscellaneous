# Terminal Games Project Context

## Project Overview

**Terminal Games** is a collection of classic arcade and board games re-imagined for the terminal using the [Textual](https://textual.textualize.io/) framework. It features a polished TUI (Terminal User Interface) with mouse support, themes, and integrated AI opponents.

**Available Games:**
*   **Chess:** Full chess implementation with AI (Minimax) and move validation.
*   **Snake:** Classic snake game.
*   **Tetris:** Block stacking game.
*   **Tic-Tac-Toe:** Simple strategy game.
*   **Space Invaders:** Arcade shooter.

## Building and Running

### Prerequisites
*   Python 3.10 or higher
*   `pip`

### Installation
To install the project and its dependencies in editable mode:

```bash
pip install -e .
```

### Running the Games
The project installs several CLI commands:

*   **Launcher (Main Menu):**
    ```bash
    terminal-games
    ```

*   **Direct Launch:**
    ```bash
    tg-chess
    tg-snake
    tg-tetris
    tg-tictactoe
    tg-spaceinvaders
    ```

## Project Structure

The codebase is organized as a standard Python package within `terminal_games/`.

```
terminal_games/
├── launcher.py          # Main entry point (TUI Menu)
├── config.py            # Global configuration (themes, etc.)
├── chess/               # Chess Game Module
│   ├── app.py           # Textual App definition
│   ├── chess_ai.py      # AI Logic (Minimax)
│   ├── models.py        # Game State & Data Classes
│   ├── widgets/         # Custom Widgets (e.g., ChessBoard)
│   └── styles/          # CSS Stylesheets (*.tcss)
├── snake/               # Snake Game Module
├── ...                  # (Other games follow similar structure)
```

## Development Conventions

### UI & Theming (Textual)
*   **Framework:** All UIs are built using **Textual**.
*   **Styling:** Styles are defined in separate `.tcss` files within each game's `styles/` directory (e.g., `chess.tcss`).
*   **Reactivity:** State management relies heavily on Textual's `reactive` properties.
*   **Concurrency:** Heavy computations (like AI thinking) **MUST** be offloaded to a background thread (e.g., `ThreadPoolExecutor`) to prevent freezing the UI. `app.call_from_thread` is used to update the UI from these background threads.

### Game Logic
*   **Separation of Concerns:** Game logic (rules, state) is separated from the UI. Logic often resides in `models.py` or separate logic files, while `app.py` handles the presentation and user input.
*   **State Management:** Games typically use `dataclasses` (often immutable/frozen) to represent game state, facilitating clean updates and undo/redo functionality (if implemented).