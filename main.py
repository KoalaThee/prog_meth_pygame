import sys
from enum import Enum, auto

import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    WINDOW_TITLE,
    DAMAGE_EFFECT_IMAGE,
)
from branching import BranchManager
from game_state import GameState
from levels import all_level_states
from scene_manager import SceneManager
from screens import BranchScreen, EndingScreen, GameOverScreen, PauseScreen, StartScreen, StatsOverlay


class GameMode(Enum):
    TITLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    BRANCH_SELECT = auto()
    COMPLETE = auto()
    GAME_OVER = auto()


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        try:
            self.screen = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.DOUBLEBUF,
                vsync=1,
            )
            self._vsync = True
        except pygame.error:
            self.screen = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.DOUBLEBUF,
            )
            self._vsync = False

        self.clock = pygame.time.Clock()
        self.running = True
        self.mode = GameMode.TITLE

        self.game_state = GameState()
        self.start_screen = StartScreen(self.screen)
        self.pause_screen = PauseScreen(self.screen)
        self.branch_screen = BranchScreen(self.screen)
        self.ending_screen = EndingScreen()
        self.game_over_screen = GameOverScreen(self.screen)
        self.stats_overlay = StatsOverlay(self.game_state)
        self.branch_manager = BranchManager()
        self._damage_flash_surface: pygame.Surface | None = None
        try:
            img = pygame.image.load(DAMAGE_EFFECT_IMAGE).convert_alpha()
            self._damage_flash_surface = pygame.transform.smoothscale(
                img, (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        except (pygame.error, FileNotFoundError, OSError):
            pass

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
            elif self.mode is GameMode.BRANCH_SELECT:
                choice = self.branch_screen.handle_event(event)
                if choice is not None:
                    self.branch_manager.choose(choice)
                    self.scene_manager.set_branch_choice(choice)
                    self.mode = GameMode.PLAYING
            elif self.mode is GameMode.COMPLETE or self.mode is GameMode.GAME_OVER:
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
        self._ensure_branch_selected()
        if self.scene_manager.is_game_over():
            self.mode = GameMode.GAME_OVER
        elif self.scene_manager.is_done():
            self.mode = GameMode.COMPLETE

    def _ensure_branch_selected(self) -> None:
        """Lock branch before multiplier stages; show chooser only on ties."""
        needs_choice = self.branch_manager.ensure_for_stage(
            self.scene_manager.current_stage,
            self.game_state,
        )
        if needs_choice:
            self.mode = GameMode.BRANCH_SELECT
            return
        if self.branch_manager.branch_choice is not None:
            self.scene_manager.set_branch_choice(self.branch_manager.branch_choice)

    def draw(self):
        if self.mode is GameMode.TITLE:
            self.start_screen.draw()
        elif self.mode is GameMode.GAME_OVER:
            self.game_over_screen.draw()
        elif self.mode is GameMode.COMPLETE:
            self.scene_manager.draw()
            self.ending_screen.draw(
                self.screen,
                self.game_state,
                self.branch_manager.career_title,
                self.branch_manager.branch_choice,
                self.branch_manager.faculty_choice,
            )
        elif self.mode is GameMode.BRANCH_SELECT:
            self.scene_manager.draw()
            self.stats_overlay.draw(
                self.screen,
                self.scene_manager.current_stage,
                self.branch_manager.branch_choice,
                self.branch_manager.faculty_choice,
            )
            self.branch_screen.draw()
        else:
            self.scene_manager.draw()
            self.stats_overlay.draw(
                self.screen,
                self.scene_manager.current_stage,
                self.branch_manager.branch_choice,
                self.branch_manager.faculty_choice,
            )
            if (
                self._damage_flash_surface is not None
                and self.scene_manager.consume_damage_flash()
            ):
                self.screen.blit(self._damage_flash_surface, (0, 0))
            if self.mode is GameMode.PAUSED:
                self.pause_screen.draw()
        pygame.display.flip()

    def run(self):
        tick = self.clock.tick if self._vsync else self.clock.tick_busy_loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
