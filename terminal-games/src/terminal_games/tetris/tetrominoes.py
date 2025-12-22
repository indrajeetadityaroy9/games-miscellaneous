"""Tetromino piece definitions for Terminal Tetris."""

from .models import Tetromino

# All 7 standard Tetris pieces
# Shape matrices use the piece's color ID (1-7) for filled cells, 0 for empty
# Shapes are defined in their spawn orientation

# I-piece (cyan) - horizontal bar
I_PIECE = Tetromino(
    shape=(
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    ),
    color=1,
)

# J-piece (blue) - J shape
J_PIECE = Tetromino(
    shape=(
        (2, 0, 0),
        (2, 2, 2),
        (0, 0, 0),
    ),
    color=2,
)

# L-piece (orange) - L shape
L_PIECE = Tetromino(
    shape=(
        (0, 0, 3),
        (3, 3, 3),
        (0, 0, 0),
    ),
    color=3,
)

# O-piece (yellow) - square
O_PIECE = Tetromino(
    shape=(
        (4, 4),
        (4, 4),
    ),
    color=4,
)

# S-piece (green) - S shape
S_PIECE = Tetromino(
    shape=(
        (0, 5, 5),
        (5, 5, 0),
        (0, 0, 0),
    ),
    color=5,
)

# T-piece (purple) - T shape
T_PIECE = Tetromino(
    shape=(
        (0, 6, 0),
        (6, 6, 6),
        (0, 0, 0),
    ),
    color=6,
)

# Z-piece (red) - Z shape
Z_PIECE = Tetromino(
    shape=(
        (7, 7, 0),
        (0, 7, 7),
        (0, 0, 0),
    ),
    color=7,
)

# List of all pieces for random selection
ALL_PIECES = [I_PIECE, J_PIECE, L_PIECE, O_PIECE, S_PIECE, T_PIECE, Z_PIECE]

# Color names for each piece type (used for rendering)
PIECE_COLORS = {
    0: "default",    # Empty
    1: "cyan",       # I
    2: "blue",       # J
    3: "orange1",    # L
    4: "yellow",     # O
    5: "green",      # S
    6: "magenta",    # T
    7: "red",        # Z
}

# Light theme colors
PIECE_COLORS_LIGHT = {
    0: "default",
    1: "dark_cyan",
    2: "dark_blue",
    3: "dark_orange",
    4: "gold3",
    5: "dark_green",
    6: "dark_magenta",
    7: "dark_red",
}
