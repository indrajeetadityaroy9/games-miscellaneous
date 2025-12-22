"""Pure functions for Space Invaders game mechanics."""

import random
from typing import Optional

from .models import (
    Player,
    Bullet,
    Enemy,
    GameState,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    PLAYER_Y,
    PLAYER_WIDTH,
    ENEMY_ROWS,
    ENEMY_COLS,
    ENEMY_WIDTH,
    ENEMY_HEIGHT,
    ENEMY_SPACING,
    ENEMY_ROW_SPACING,
)


def create_initial_state(level: int = 1, high_score: int = 0) -> GameState:
    """Create a fresh game state for a level."""
    player = Player(x=(BOARD_WIDTH - PLAYER_WIDTH) // 2)
    enemies = init_enemies()

    return GameState(
        player=player,
        enemies=enemies,
        player_bullets=[],
        enemy_bullets=[],
        score=0 if level == 1 else 0,  # Reset score per level or keep?
        high_score=high_score,
        level=level,
        direction=1,
        is_paused=False,
        is_game_over=False,
        is_won=False,
        can_shoot=True,
    )


def init_enemies() -> list[Enemy]:
    """Initialize the 5x10 enemy grid."""
    enemies = []

    # Calculate starting x to center the grid
    grid_width = ENEMY_COLS * (ENEMY_WIDTH + ENEMY_SPACING) - ENEMY_SPACING
    start_x = (BOARD_WIDTH - grid_width) // 2
    start_y = 2  # Start near top

    for row in range(ENEMY_ROWS):
        # Determine enemy type based on row (for 3 rows: one of each type)
        if row == 0:
            enemy_type = 0  # Top row - squid
        elif row == 1:
            enemy_type = 1  # Middle row - crab
        else:
            enemy_type = 2  # Bottom row - octopus

        for col in range(ENEMY_COLS):
            x = start_x + col * (ENEMY_WIDTH + ENEMY_SPACING)
            y = start_y + row * (ENEMY_HEIGHT + ENEMY_ROW_SPACING)
            enemies.append(Enemy(x=x, y=y, enemy_type=enemy_type))

    return enemies


def move_player_left(state: GameState) -> GameState:
    """Move player left."""
    if state.is_game_over or state.is_paused:
        return state

    new_x = max(0, state.player.x - 2)
    state.player.x = new_x
    return state


def move_player_right(state: GameState) -> GameState:
    """Move player right."""
    if state.is_game_over or state.is_paused:
        return state

    new_x = min(BOARD_WIDTH - PLAYER_WIDTH, state.player.x + 2)
    state.player.x = new_x
    return state


def shoot_player_bullet(state: GameState) -> GameState:
    """Fire a bullet from the player."""
    if state.is_game_over or state.is_paused or not state.can_shoot:
        return state

    # Spawn bullet at center of player
    bullet_x = state.player.x + PLAYER_WIDTH // 2
    bullet_y = PLAYER_Y - 1

    state.player_bullets.append(Bullet(x=bullet_x, y=bullet_y))
    state.can_shoot = False  # Will be reset by cooldown timer
    return state


def update_player_bullets(state: GameState) -> GameState:
    """Move player bullets upward."""
    if state.is_game_over or state.is_paused:
        return state

    for bullet in state.player_bullets:
        if bullet.active:
            bullet.y -= 1
            # Deactivate if off screen
            if bullet.y < 0:
                bullet.active = False

    # Remove inactive bullets
    state.player_bullets = [b for b in state.player_bullets if b.active]
    return state


def update_enemy_bullets(state: GameState) -> GameState:
    """Move enemy bullets downward."""
    if state.is_game_over or state.is_paused:
        return state

    for bullet in state.enemy_bullets:
        if bullet.active:
            bullet.y += 1
            # Deactivate if off screen
            if bullet.y >= BOARD_HEIGHT:
                bullet.active = False

    # Remove inactive bullets
    state.enemy_bullets = [b for b in state.enemy_bullets if b.active]
    return state


def update_enemies(state: GameState) -> GameState:
    """Move enemies horizontally and handle descent."""
    if state.is_game_over or state.is_paused:
        return state

    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return state

    # Check if any enemy hits the edge
    hit_edge = False
    for enemy in active_enemies:
        if state.direction == 1:  # Moving right
            if enemy.x + ENEMY_WIDTH >= BOARD_WIDTH - 1:
                hit_edge = True
                break
        else:  # Moving left
            if enemy.x <= 1:
                hit_edge = True
                break

    if hit_edge:
        # Reverse direction and move down
        state.direction *= -1
        for enemy in active_enemies:
            enemy.y += 1
            # Check if enemy reached player level
            if enemy.y + ENEMY_HEIGHT >= PLAYER_Y:
                state.is_game_over = True
                state.high_score = max(state.high_score, state.score)
                return state
    else:
        # Move horizontally
        for enemy in active_enemies:
            enemy.x += state.direction

    return state


def enemy_shoot(state: GameState) -> GameState:
    """Random active enemy fires a bullet."""
    if state.is_game_over or state.is_paused:
        return state

    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return state

    # Pick a random enemy to shoot
    shooter = random.choice(active_enemies)
    bullet_x = shooter.x + ENEMY_WIDTH // 2
    bullet_y = shooter.y + ENEMY_HEIGHT

    state.enemy_bullets.append(Bullet(x=bullet_x, y=bullet_y, is_enemy=True))
    return state


def check_collisions(state: GameState) -> GameState:
    """Check all bullet collisions."""
    if state.is_game_over or state.is_paused:
        return state

    # Player bullets hitting enemies
    for bullet in state.player_bullets:
        if not bullet.active:
            continue

        for enemy in state.enemies:
            if not enemy.active:
                continue

            # Check collision
            if (enemy.x <= bullet.x < enemy.x + ENEMY_WIDTH and
                enemy.y <= bullet.y < enemy.y + ENEMY_HEIGHT):
                # Hit!
                bullet.active = False
                enemy.active = False
                # Score based on level
                state.score += 10 + state.level * 2
                state.high_score = max(state.high_score, state.score)
                break

    # Enemy bullets hitting player
    player_left = state.player.x
    player_right = state.player.x + PLAYER_WIDTH
    player_top = PLAYER_Y
    player_bottom = PLAYER_Y + 2  # Player is 2 rows tall

    for bullet in state.enemy_bullets:
        if not bullet.active:
            continue

        if (player_left <= bullet.x < player_right and
            player_top <= bullet.y < player_bottom):
            # Player hit!
            state.is_game_over = True
            state.high_score = max(state.high_score, state.score)
            return state

    return state


def check_win(state: GameState) -> GameState:
    """Check if all enemies are defeated."""
    if state.is_game_over or state.is_paused:
        return state

    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        state.is_won = True

    return state


def toggle_pause(state: GameState) -> GameState:
    """Toggle pause state."""
    if state.is_game_over or state.is_won:
        return state

    state.is_paused = not state.is_paused
    return state


def get_enemy_move_interval(level: int) -> float:
    """Get enemy movement interval based on level."""
    # Faster each level: 0.4s at level 1, down to 0.16s at level 8
    return max(0.16, 0.4 - (level - 1) * 0.03)


def get_enemy_shoot_interval(level: int) -> float:
    """Get enemy shoot interval based on level."""
    # More frequent each level: 1.2s at level 1, down to 0.5s at level 8
    return max(0.5, 1.2 - (level - 1) * 0.1)


def get_score_per_enemy(level: int) -> int:
    """Get score per enemy kill based on level."""
    return 10 + level * 2
