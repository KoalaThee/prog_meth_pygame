import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, OVERLAY_SCREEN_IMAGE
from game_state import GameState


class StatsOverlay:
    """Full-window overlay art (during play), then HUD: four stat bars + circle."""

    BAR_W = 120
    BAR_H = 20
    GAP = 30
    TOP = 20
    LEFT = 35
    CIRCLE_R = 18

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self._overlay: pygame.Surface | None = None
        self._load_overlay()

    def _load_overlay(self) -> None:
        try:
            img = pygame.image.load(OVERLAY_SCREEN_IMAGE).convert_alpha()
            self._overlay = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except (pygame.error, FileNotFoundError, OSError):
            self._overlay = None

    def draw(self, surface: pygame.Surface) -> None:
        if self._overlay is not None:
            surface.blit(self._overlay, (0, 0))

        x = self.LEFT
        y = self.TOP
        colors = (
            (200, 80, 80),
            (80, 180, 80),
            (80, 120, 200),
            (200, 160, 60),
        )
        for i in range(4):
            rect = pygame.Rect(x, y, self.BAR_W, self.BAR_H)
            pygame.draw.rect(surface, colors[i], rect, border_radius=3)
            pygame.draw.rect(surface, (40, 40, 40), rect, width=1, border_radius=3)
            x += self.BAR_W + self.GAP

        cx = WINDOW_WIDTH - self.CIRCLE_R - self.LEFT
        cy = y + self.BAR_H // 2
        pygame.draw.circle(surface, (180, 180, 220), (cx, cy), self.CIRCLE_R)
        pygame.draw.circle(surface, (60, 60, 80), (cx, cy), self.CIRCLE_R, width=2)
