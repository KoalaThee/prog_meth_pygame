import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_OVER_SCREEN_IMAGE


class GameOverScreen:
    """Full-screen image shown when the player's health hits 0."""

    def __init__(self, window: pygame.Surface):
        self.window = window
        self._bg: pygame.Surface | None = None
        self._load_background()

    def _load_background(self) -> None:
        try:
            img = pygame.image.load(GAME_OVER_SCREEN_IMAGE).convert_alpha()
            self._bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except (pygame.error, FileNotFoundError, OSError):
            self._bg = None

    def draw(self) -> None:
        if self._bg is not None:
            self.window.blit(self._bg, (0, 0))
        else:
            self.window.fill((0, 0, 0))
