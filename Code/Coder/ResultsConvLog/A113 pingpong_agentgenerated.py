import pygame
import random

# Initialize the game
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong Game")

# Paddle Class
class Paddle(pygame.sprite.Sprite):
    """
    A class to represent a paddle in the game.

    Attributes:
    - x: x-coordinate of the paddle
    - y: y-coordinate of the paddle
    """

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 60))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, change_in_y):
        """
        Update the paddle's position based on the change in y-coordinate.

        Parameters:
        - change_in_y: Amount to change the y-coordinate by
        """
        self.rect.y += change_in_y
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Ball Class
class Ball(pygame.sprite.Sprite):
    """
    A class to represent the ball in the game.

    Attributes:
    - speed: Speed of the ball
    """

    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = speed
        self.dx = random.choice([-1, 1]) * speed
        self.dy = random.choice([-1, 1]) * speed

    def update(self):
        """
        Update the ball's position based on its speed and direction.
        """
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Ball collision with top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy = -self.dy

# Score class
class Score:
    """
    A class to keep track of the scores for both players.

    Attributes:
    - player_score: Score of the player
    - computer_score: Score of the computer
    """

    def __init__(self):
        self.player_score = 0
        self.computer_score = 0

    def update_score(self, player=False):
        """
        Update the scores based on the player who scored.

        Parameters:
        - player: Boolean flag to indicate if the player scored
        """
        if player:
            self.player_score += 1
        else:
            self.computer_score += 1

# Create sprites
player_paddle = Paddle(20, SCREEN_HEIGHT // 2)
computer_paddle = Paddle(780, SCREEN_HEIGHT // 2)

ball = Ball(5)

# Groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player_paddle, computer_paddle, ball)

clock = pygame.time.Clock()
score = Score()

# Game Loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_paddle.update(-5)
    if keys[pygame.K_DOWN]:
        player_paddle.update(5)

    # Computer paddle movement (AI)
    if ball.dy > 0:
        if computer_paddle.rect.centery < ball.rect.centery - 15:
            computer_paddle.update(5)
        if computer_paddle.rect.centery > ball.rect.centery + 15:
            computer_paddle.update(-5)

    all_sprites.update()

    # Ball collision with paddles
    if pygame.sprite.collide_rect(player_paddle, ball) or pygame.sprite.collide_rect(computer_paddle, ball):
        ball.dx = -ball.dx

    # Ball out of bounds
    if ball.rect.left <= 0:
        score.update_score()
        ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ball.dy = random.choice([-1, 1]) * 5
    if ball.rect.right >= SCREEN_WIDTH:
        score.update_score(player=True)
        ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ball.dy = random.choice([-1, 1]) * 5

    all_sprites.draw(screen)

    # Display scores
    font = pygame.font.Font(None, 36)
    player_score_text = font.render(f"Player: {score.player_score}", True, WHITE)
    computer_score_text = font.render(f"Computer: {score.computer_score}", True, WHITE)
    screen.blit(player_score_text, (20, 20))
    screen.blit(computer_score_text, (SCREEN_WIDTH - 200, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()