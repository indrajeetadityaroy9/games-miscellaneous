"""Pure functions for Space Invaders game mechanics."""

import random
from dataclasses import replace

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
        player_bullets=(),
        enemy_bullets=(),
        score=0,
        high_score=high_score,
        level=level,
        direction=1,
        is_paused=False,
        is_game_over=False,
        is_won=False,
        can_shoot=True,
    )


def init_enemies() -> tuple[Enemy, ...]:
    """Initialize the enemy grid."""
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

    return tuple(enemies)


def move_player_left(state: GameState) -> GameState:
    """Move player left."""
    if state.is_game_over or state.is_paused:
        return state

    new_x = max(0, state.player.x - 2)
    new_player = replace(state.player, x=new_x)
    return replace(state, player=new_player)


def move_player_right(state: GameState) -> GameState:
    """Move player right."""
    if state.is_game_over or state.is_paused:
        return state

    new_x = min(BOARD_WIDTH - PLAYER_WIDTH, state.player.x + 2)
    new_player = replace(state.player, x=new_x)
    return replace(state, player=new_player)


def shoot_player_bullet(state: GameState) -> GameState:
    """Fire a bullet from the player."""
    if state.is_game_over or state.is_paused or not state.can_shoot:
        return state

    # Spawn bullet at center of player
    bullet_x = state.player.x + PLAYER_WIDTH // 2
    bullet_y = PLAYER_Y - 1

    new_bullet = Bullet(x=bullet_x, y=bullet_y)
    return replace(
        state,
        player_bullets=state.player_bullets + (new_bullet,),
        can_shoot=False,
    )


def update_player_bullets(state: GameState) -> GameState:
    """Move player bullets upward."""
    if state.is_game_over or state.is_paused:
        return state

    new_bullets = tuple(
        replace(bullet, y=bullet.y - 1)
        for bullet in state.player_bullets
        if bullet.active and bullet.y - 1 >= 0
    )
    return replace(state, player_bullets=new_bullets)


def update_enemy_bullets(state: GameState) -> GameState:
    """Move enemy bullets downward."""
    if state.is_game_over or state.is_paused:
        return state

    new_bullets = tuple(
        replace(bullet, y=bullet.y + 1)
        for bullet in state.enemy_bullets
        if bullet.active and bullet.y + 1 < BOARD_HEIGHT
    )
    return replace(state, enemy_bullets=new_bullets)


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
        new_direction = state.direction * -1
        new_enemies = tuple(
            replace(e, y=e.y + 1) if e.active else e
            for e in state.enemies
        )
        # Check if any enemy reached player level
        for enemy in new_enemies:
            if enemy.active and enemy.y + ENEMY_HEIGHT >= PLAYER_Y:
                return replace(
                    state,
                    enemies=new_enemies,
                    direction=new_direction,
                    is_game_over=True,
                    high_score=max(state.high_score, state.score),
                )
        return replace(state, enemies=new_enemies, direction=new_direction)
    else:
        # Move horizontally
        new_enemies = tuple(
            replace(e, x=e.x + state.direction) if e.active else e
            for e in state.enemies
        )
        return replace(state, enemies=new_enemies)


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

    new_bullet = Bullet(x=bullet_x, y=bullet_y, is_enemy=True)
    return replace(
        state,
        enemy_bullets=state.enemy_bullets + (new_bullet,),
    )


def check_collisions(state: GameState) -> GameState:
    """Check all bullet collisions."""
    if state.is_game_over or state.is_paused:
        return state

    # Track which bullets and enemies to update
    player_bullet_active = list(state.player_bullets)
    enemies_active = list(state.enemies)
    score_delta = 0

    # Player bullets hitting enemies
    for i, bullet in enumerate(player_bullet_active):
        if not bullet.active:
            continue

        for j, enemy in enumerate(enemies_active):
            if not enemy.active:
                continue

            # Check collision
            if (enemy.x <= bullet.x < enemy.x + ENEMY_WIDTH and
                enemy.y <= bullet.y < enemy.y + ENEMY_HEIGHT):
                # Hit!
                player_bullet_active[i] = replace(bullet, active=False)
                enemies_active[j] = replace(enemy, active=False)
                score_delta += 10 + state.level * 2
                break

    new_score = state.score + score_delta
    new_high_score = max(state.high_score, new_score)

    # Filter out inactive bullets
    new_player_bullets = tuple(b for b in player_bullet_active if b.active)
    new_enemies = tuple(enemies_active)

    # Enemy bullets hitting player
    player_left = state.player.x
    player_right = state.player.x + PLAYER_WIDTH
    player_top = PLAYER_Y
    player_bottom = PLAYER_Y + 2  # Player is 2 rows tall

    enemy_bullets_active = list(state.enemy_bullets)
    player_hit = False

    for i, bullet in enumerate(enemy_bullets_active):
        if not bullet.active:
            continue

        if (player_left <= bullet.x < player_right and
            player_top <= bullet.y < player_bottom):
            # Player hit!
            player_hit = True
            enemy_bullets_active[i] = replace(bullet, active=False)
            break

    new_enemy_bullets = tuple(b for b in enemy_bullets_active if b.active)

    if player_hit:
        return replace(
            state,
            enemies=new_enemies,
            player_bullets=new_player_bullets,
            enemy_bullets=new_enemy_bullets,
            score=new_score,
            high_score=new_high_score,
            is_game_over=True,
        )

    return replace(
        state,
        enemies=new_enemies,
        player_bullets=new_player_bullets,
        enemy_bullets=new_enemy_bullets,
        score=new_score,
        high_score=new_high_score,
    )


def check_win(state: GameState) -> GameState:
    """Check if all enemies are defeated."""
    if state.is_game_over or state.is_paused:
        return state

    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return replace(state, is_won=True)

    return state


def toggle_pause(state: GameState) -> GameState:
    """Toggle pause state."""
    if state.is_game_over or state.is_won:
        return state

    return replace(state, is_paused=not state.is_paused)


def reset_shoot_cooldown(state: GameState) -> GameState:
    """Reset the shoot cooldown flag."""
    return replace(state, can_shoot=True)


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
