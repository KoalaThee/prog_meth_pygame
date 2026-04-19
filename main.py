import sys
from enum import Enum, auto

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE
from game_state import GameState
from levels import all_level_states
from scene_manager import SceneManager
from screens import PauseScreen, StartScreen, StatsOverlay


class GameMode(Enum):
    TITLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    COMPLETE = auto()


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True
        self.mode = GameMode.TITLE

        self.game_state = GameState()
        self.start_screen = StartScreen(self.screen)
        self.pause_screen = PauseScreen(self.screen)
        self.stats_overlay = StatsOverlay(self.game_state)

        self.scene_manager = SceneManager(self.screen, all_level_states(), self.game_state)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.mode is GameMode.TITLE:
                if self.start_screen.handle_event(event):
                    self.mode = GameMode.PLAYING
            elif self.mode is GameMode.PAUSED:
                if self.pause_screen.handle_event(event):
                    self.mode = GameMode.PLAYING
            elif self.mode is GameMode.COMPLETE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.mode = GameMode.PAUSED
                else:
                    self.scene_manager.handle_event(event)

    def update(self):
        if self.mode is not GameMode.PLAYING:
            return
        self.scene_manager.update()
        if self.scene_manager.is_done():
            self.mode = GameMode.COMPLETE

    def draw(self):
        if self.mode is GameMode.TITLE:
            self.start_screen.draw()
        else:
            self.scene_manager.draw()
            self.stats_overlay.draw(self.screen)
            if self.mode is GameMode.PAUSED:
                self.pause_screen.draw()
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
