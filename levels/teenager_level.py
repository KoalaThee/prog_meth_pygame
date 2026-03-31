import pygame

from levels.base_level import BaseLevel
from player.teenager_player import TeenagerPlayer
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WORLD_SCROLL_SPEED,
    GROUND_Y,
    WHITE,
    BLACK,
    TEENAGER_BACKGROUND_IMAGE,
)


class TeenagerLevel(BaseLevel):
    def __init__(self, screen: pygame.Surface):
        self.background = pygame.image.load(TEENAGER_BACKGROUND_IMAGE).convert()
        self.background = pygame.transform.scale(
            self.background,
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        self.bg_x1 = 0
        self.bg_x2 = WINDOW_WIDTH

        player = TeenagerPlayer()
        super().__init__(screen, player)

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 28)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()

    def update_background(self):
        self.bg_x1 -= WORLD_SCROLL_SPEED
        self.bg_x2 -= WORLD_SCROLL_SPEED
        self.shift_world(-WORLD_SCROLL_SPEED)

        if self.bg_x1 <= -WINDOW_WIDTH:
            self.bg_x1 = self.bg_x2 + WINDOW_WIDTH

        if self.bg_x2 <= -WINDOW_WIDTH:
            self.bg_x2 = self.bg_x1 + WINDOW_WIDTH

    def update(self):
        self.update_background()
        super().update()

    def draw_ground_line(self):
        pygame.draw.line(
            self.screen,
            BLACK,
            (0, GROUND_Y),
            (WINDOW_WIDTH, GROUND_Y),
            2
        )

    def draw_ui(self):
        title_surface = self.big_font.render("Teenager Level", True, WHITE)
        help_surface = self.font.render("SPACE = Jump", True, WHITE)
        shift_surface = self.font.render(
            f"World Shift: {self.world_shift}",
            True,
            WHITE
        )

        self.screen.blit(title_surface, (16, 14))
        self.screen.blit(help_surface, (16, 42))
        self.screen.blit(shift_surface, (16, 64))

    def draw(self):
        self.screen.blit(self.background, (self.bg_x1, 0))
        self.screen.blit(self.background, (self.bg_x2, 0))

        self.draw_ground_line()
        self.all_sprites.draw(self.screen)
        self.draw_ui()