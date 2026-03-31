import sys
import pygame

from levels.teenager_level import TeenagerLevel
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_level = TeenagerLevel(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.current_level.handle_event(event)

    def update(self):
        self.current_level.update()

    def draw(self):
        self.current_level.draw()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()