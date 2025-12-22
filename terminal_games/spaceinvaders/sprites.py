"""Unicode sprite patterns for Space Invaders."""

# Player ship (2 lines tall, 5 chars wide)
PLAYER_SPRITE = [
    " ▄█▄ ",
    "█████",
]

# Enemy types (2 lines tall, 3 chars wide)
ENEMY_SPRITES = {
    0: ["▄█▄", "▀ ▀"],  # Squid (top row)
    1: ["█▀█", "▀▄▀"],  # Crab (middle rows)
    2: ["▀█▀", " ▀ "],  # Octopus (bottom rows)
}

# Bullets
PLAYER_BULLET = "│"
ENEMY_BULLET = "▼"

# Explosion effect (single char)
EXPLOSION = "✦"
