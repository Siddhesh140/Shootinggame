import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load assets
player_img = pygame.image.load("player.png")
enemy_img = pygame.image.load("enemy.png")
laser_img = pygame.image.load("laser.png")
background = pygame.image.load("background.png")
sad_emoji = pygame.image.load("crying.jpg")
happy_emoji = pygame.image.load("smile.png")

# Resize assets
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
laser_img = pygame.transform.scale(laser_img, (10, 30))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
sad_emoji = pygame.transform.scale(sad_emoji, (150, 150))
happy_emoji = pygame.transform.scale(happy_emoji, (150, 150))

# Font
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# FPS clock
clock = pygame.time.Clock()


def draw_text(text, font, color, x, y):
    """Utility function to draw text on the screen."""
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))
    return rendered_text.get_rect(topleft=(x, y))


def show_start_screen():
    """Display the start screen with clickable difficulty options."""
    screen.fill(BLACK)
    title = font.render("Space Shooter", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

    easy_rect = draw_text("Easy", small_font, GREEN, WIDTH // 2 - 50, HEIGHT // 2 - 60)
    medium_rect = draw_text("Medium", small_font, BLUE, WIDTH // 2 - 50, HEIGHT // 2)
    hard_rect = draw_text("Hard", small_font, RED, WIDTH // 2 - 50, HEIGHT // 2 + 60)

    pygame.display.flip()
    return {"easy": easy_rect, "medium": medium_rect, "hard": hard_rect}


def show_game_over():
    """Display the Game Over screen with a Start Again button."""
    screen.fill(BLACK)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = small_font.render(f"Your Score: {score}", True, WHITE)
    emoji = happy_emoji if score >= 100 else sad_emoji
    msg = "Awesome! 😊" if score >= 100 else "Try Again! 😢"
    msg_text = small_font.render(msg, True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(emoji, (WIDTH // 2 - emoji.get_width() // 2, HEIGHT // 2 + 40))
    start_again_rect = draw_text("Start Again", small_font, GREEN, WIDTH // 2 - 80, HEIGHT // 2 + 200)

    pygame.display.flip()
    return start_again_rect


def spawn_enemy():
    """Spawn an enemy at a random x-coordinate."""
    enemy_x = random.randint(0, WIDTH - enemy_img.get_width())
    enemies.append({"x": enemy_x, "y": -50})


def update_enemies():
    """Update enemy positions and handle collisions."""
    global player_lives, score

    for enemy in enemies[:]:
        enemy["y"] += enemy_speed

        # Check for collision with lasers
        for laser in lasers[:]:
            if (
                enemy["x"] < laser[0] < enemy["x"] + enemy_img.get_width()
                and enemy["y"] < laser[1] < enemy["y"] + enemy_img.get_height()
            ):
                lasers.remove(laser)
                enemies.remove(enemy)
                score += 10
                break

        # Check for collision with player
        if (
            abs(player_x - enemy["x"]) < 40
            and abs(player_y - enemy["y"]) < 40
        ):
            enemies.remove(enemy)
            player_lives -= 1
            if player_lives == 0:
                return False

        # Remove enemies that go off-screen
        if enemy["y"] > HEIGHT:
            enemies.remove(enemy)

    return True


def update_difficulty():
    """Increase enemy speed and spawn rate based on score."""
    global enemy_speed, enemy_spawn_time

    if score < 50:
        return
    elif score < 100:
        enemy_speed += 0.01
        enemy_spawn_time = max(0.8, enemy_spawn_time - 0.001)
    elif score < 200:
        enemy_speed += 0.02
        enemy_spawn_time = max(0.5, enemy_spawn_time - 0.002)
    else:
        enemy_speed += 0.03
        enemy_spawn_time = max(0.3, enemy_spawn_time - 0.003)


# Game variables
player_speed = 5
player_lives = 3
score = 0
lasers = []
enemies = []
enemy_speed = 2
enemy_spawn_time = 1.5
last_enemy_spawn_time = time.time()

running = True
game_active = False
difficulty = None

# Game loop
while running:
    if not game_active:
        clickable_rects = show_start_screen() if difficulty is None else show_game_over()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if difficulty is None:
                    if clickable_rects["easy"].collidepoint(mouse_pos):
                        difficulty = "easy"
                        enemy_speed = 2
                        enemy_spawn_time = 1.5
                        game_active = True
                    elif clickable_rects["medium"].collidepoint(mouse_pos):
                        difficulty = "medium"
                        enemy_speed = 3
                        enemy_spawn_time = 1.2
                        game_active = True
                    elif clickable_rects["hard"].collidepoint(mouse_pos):
                        difficulty = "hard"
                        enemy_speed = 4
                        enemy_spawn_time = 1.0
                        game_active = True
                else:
                    # Restart the game if "Start Again" is clicked
                    if clickable_rects.collidepoint(mouse_pos):
                        player_lives = 3
                        score = 0
                        lasers = []
                        enemies = []
                        enemy_speed = 2
                        enemy_spawn_time = 1.5
                        game_active = True

    else:
        clock.tick(60)
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    lasers.append([player_x + player_img.get_width() // 2 - 5, player_y])

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_img.get_width():
            player_x += player_speed

        # Update lasers
        for laser in lasers[:]:
            laser[1] -= 7
            if laser[1] < 0:
                lasers.remove(laser)

        # Spawn enemies periodically
        current_time = time.time()
        if current_time - last_enemy_spawn_time >= enemy_spawn_time:
            spawn_enemy()
            last_enemy_spawn_time = current_time

        # Update enemies and difficulty
        if not update_enemies():
            game_active = False
        update_difficulty()

        # Draw player, enemies, lasers
        screen.blit(player_img, (player_x, player_y))
        for enemy in enemies:
            screen.blit(enemy_img, (enemy["x"], enemy["y"]))
        for laser in lasers:
            screen.blit(laser_img, (laser[0], laser[1]))

        # Draw score and lives
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        lives_text = small_font.render(f"Lives: {player_lives}", True, RED)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))

        pygame.display.flip()

pygame.quit()
