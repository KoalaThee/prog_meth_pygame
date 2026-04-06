import sys
import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Import after pygame.init() so image loading works immediately
        from scene_manager import SceneManager
        from levels.baby_level import BabyLevel
        from levels.toddler_level import ToddlerLevel
        from levels.teenager_level import TeenagerLevel
        from levels.young_adult_level import YoungAdultLevel

        all_states = []
        for LevelClass in [BabyLevel, ToddlerLevel, TeenagerLevel, YoungAdultLevel]:
            all_states.extend(LevelClass.get_scene_states())

        self.scene_manager = SceneManager(self.screen, all_states)

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
