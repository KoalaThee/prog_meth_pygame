import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_OVER_SCREEN_IMAGE
from .util import load_background


class GameOverScreen:
    """Full-screen image shown when the player's health hits 0."""

    def __init__(self, window: pygame.Surface):
        self.window = window
        self._bg = load_background(GAME_OVER_SCREEN_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw(self) -> None:
        if self._bg is not None:
            self.window.blit(self._bg, (0, 0))
        else:
            self.window.fill((0, 0, 0))
