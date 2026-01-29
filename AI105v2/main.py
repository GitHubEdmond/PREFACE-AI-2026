import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
PLAYER_SPEED = 6

# Bullet
BULLET_WIDTH = 4
BULLET_HEIGHT = 14
BULLET_SPEED = 10

# Enemy
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_X_SPEED = 2
ENEMY_Y_STEP = 25

FONT_LARGE = pygame.font.SysFont(None, 64)
FONT_MED = pygame.font.SysFont(None, 32)
FONT_SMALL = pygame.font.SysFont(None, 24)


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED

    def move(self, direction):
        self.x += direction * self.speed
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, surface):
        # Simple spaceship: body + cockpit
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.polygon(
            surface,
            BLUE,
            [
                (self.x + self.width // 2, self.y - 10),
                (self.x + 10, self.y + 5),
                (self.x + self.width - 10, self.y + 5),
            ],
        )


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.active = True

    def update(self):
        if self.active:
            self.y -= self.speed
            if self.y + BULLET_HEIGHT < 0:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, YELLOW, (self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.alive = True

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(
                surface, BLACK, (self.x + 8, self.y + 8, self.width // 4, self.height // 3)
            )
            pygame.draw.rect(
                surface,
                BLACK,
                (self.x + self.width - 8 - self.width // 4, self.y + 8, self.width // 4, self.height // 3),
            )


def is_collision(bullet: Bullet, enemy: Enemy) -> bool:
    if not bullet.active or not enemy.alive:
        return False
    bullet_center_x = bullet.x + BULLET_WIDTH / 2
    bullet_center_y = bullet.y + BULLET_HEIGHT / 2
    enemy_center_x = enemy.x + enemy.width / 2
    enemy_center_y = enemy.y + enemy.height / 2
    distance = math.hypot(bullet_center_x - enemy_center_x, bullet_center_y - enemy_center_y)
    return distance < (enemy.width / 2)


def create_enemies(rows=4, cols=8, x_margin=60, y_margin=60, spacing_x=20, spacing_y=20):
    enemies = []
    total_width = cols * ENEMY_WIDTH + (cols - 1) * spacing_x
    start_x = (SCREEN_WIDTH - total_width) // 2
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (ENEMY_WIDTH + spacing_x)
            y = y_margin + row * (ENEMY_HEIGHT + spacing_y)
            enemies.append(Enemy(x, y))
    return enemies


def draw_text_center(surface, text, font, color, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(render, rect)


def main():
    clock = pygame.time.Clock()
    running = True

    player = Player()
    bullets = []
    enemies = create_enemies()
    enemy_direction = 1  # 1 -> right, -1 -> left

    score = 0
    lives = 3
    game_over = False
    game_won = False

    # Simple timer for enemy speed-up
    base_enemy_speed = ENEMY_X_SPEED

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_over or game_won:
                    if event.key == pygame.K_r:
                        # Restart the game
                        player = Player()
                        bullets = []
                        enemies = create_enemies()
                        enemy_direction = 1
                        score = 0
                        lives = 3
                        game_over = False
                        game_won = False
                        base_enemy_speed = ENEMY_X_SPEED
                    continue

                if event.key == pygame.K_SPACE:
                    # Shoot bullet from center-top of player
                    bullet_x = player.x + player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = player.y - BULLET_HEIGHT
                    # Only allow a few bullets on screen at once
                    if len([b for b in bullets if b.active]) < 3:
                        bullets.append(Bullet(bullet_x, bullet_y))

        # Keyboard state for continuous movement
        keys = pygame.key.get_pressed()
        if not (game_over or game_won):
            if keys[pygame.K_LEFT]:
                player.move(-1)
            if keys[pygame.K_RIGHT]:
                player.move(1)

        if not (game_over or game_won):
            # Update bullets
            for bullet in bullets:
                bullet.update()

            bullets = [b for b in bullets if b.active]

            # Move enemies as a group
            alive_enemies = [e for e in enemies if e.alive]
            if alive_enemies:
                speed_multiplier = 1 + (1 - len(alive_enemies) / (len(enemies) or 1))
                enemy_dx = base_enemy_speed * enemy_direction * speed_multiplier

                move_down = False
                for enemy in alive_enemies:
                    new_x = enemy.x + enemy_dx
                    if new_x < 0 or new_x + enemy.width > SCREEN_WIDTH:
                        move_down = True
                        enemy_direction *= -1
                        break

                for enemy in alive_enemies:
                    enemy.x += base_enemy_speed * enemy_direction * speed_multiplier

                if move_down:
                    for enemy in alive_enemies:
                        enemy.y += ENEMY_Y_STEP

            # Bullet-enemy collisions
            for bullet in bullets:
                for enemy in enemies:
                    if enemy.alive and is_collision(bullet, enemy):
                        bullet.active = False
                        enemy.alive = False
                        score += 10

            # Check if enemies reach player line
            for enemy in enemies:
                if enemy.alive and enemy.y + enemy.height >= player.y:
                    lives -= 1
                    # Reset enemies higher up
                    enemies = create_enemies()
                    bullets = []
                    enemy_direction = 1
                    break

            if lives <= 0:
                game_over = True

            # Check win condition
            if all(not e.alive for e in enemies):
                game_won = True

        # Drawing
        SCREEN.fill((10, 10, 30))

        # Stars background
        for _ in range(40):
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)
            SCREEN.set_at((x, y), (255, 255, 255))

        # Draw player, bullets, enemies
        player.draw(SCREEN)
        for bullet in bullets:
            bullet.draw(SCREEN)
        for enemy in enemies:
            enemy.draw(SCREEN)

        # HUD
        score_text = FONT_MED.render(f"Score: {score}", True, WHITE)
        lives_text = FONT_MED.render(f"Lives: {lives}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        SCREEN.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

        if game_over:
            draw_text_center(SCREEN, "GAME OVER", FONT_LARGE, WHITE, SCREEN_HEIGHT // 2 - 40)
            draw_text_center(SCREEN, f"Final Score: {score}", FONT_MED, WHITE, SCREEN_HEIGHT // 2 + 10)
            draw_text_center(SCREEN, "Press R to Restart", FONT_SMALL, GRAY, SCREEN_HEIGHT // 2 + 60)

        if game_won:
            draw_text_center(SCREEN, "YOU WIN!", FONT_LARGE, WHITE, SCREEN_HEIGHT // 2 - 40)
            draw_text_center(SCREEN, f"Final Score: {score}", FONT_MED, WHITE, SCREEN_HEIGHT // 2 + 10)
            draw_text_center(SCREEN, "Press R to Play Again", FONT_SMALL, GRAY, SCREEN_HEIGHT // 2 + 60)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

