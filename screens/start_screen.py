import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, START_SCREEN_IMAGE


class StartScreen:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self._bg: pygame.Surface | None = None
        self._load_background()

    def _load_background(self) -> None:
        try:
            img = pygame.image.load(START_SCREEN_IMAGE).convert()
            self._bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except (pygame.error, FileNotFoundError, OSError):
            self._bg = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when Space is pressed to start."""
        return bool(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)

    def draw(self) -> None:
        if self._bg is not None:
            self.window.blit(self._bg, (0, 0))
        else:
            self.window.fill((32, 48, 64))
