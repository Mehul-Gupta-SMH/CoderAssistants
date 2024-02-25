import pygame
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption('Ping Pong Game')
        self.clock = pygame.time.Clock()

        self.paddle1 = Paddle(30, 170)
        self.paddle2 = Paddle(760, 170)
        self.ball = Ball(395, 195)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))

            self.paddle1.move(5)
            self.paddle2.move(5)
            self.ball.move()

            self.paddle1.draw(self.screen)
            self.paddle2.draw(self.screen)
            self.ball.draw(self.screen)

            pygame.draw.aaline(self.screen, (255, 255, 255), (400, 0), (400, 400))

            pygame.display.flip()
            self.clock.tick(60)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 60
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, speed):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.y -= speed
        if keys[pygame.K_DOWN]:
            self.y += speed
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.speed_x = 3
        self.speed_y = 3

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y <= 0 or self.y >= 390:
            self.speed_y = -self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect)

if __name__ == "__main__":
    game = Game()
    game.run()