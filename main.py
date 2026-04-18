import sys
import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE
from scene_manager import SceneManager
from levels import all_level_states


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene_manager = SceneManager(self.screen, all_level_states())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scene_manager.handle_event(event)

    def update(self):
        self.scene_manager.update()
        if self.scene_manager.is_done():
            self.running = False

    def draw(self):
        self.scene_manager.draw()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()