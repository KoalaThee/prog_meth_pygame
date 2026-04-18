import pygame
import pygwidgets

from config import WINDOW_WIDTH, WINDOW_HEIGHT, START_SCREEN_IMAGE


class StartScreen:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self._bg: pygame.Surface | None = None
        self._load_background()

        btn_w, btn_h = 160, 44
        x = (WINDOW_WIDTH - btn_w) // 2
        y = (WINDOW_HEIGHT - btn_h) // 2
        self.start_button = pygwidgets.TextButton(
            window,
            (x, y),
            "Start",
            width=btn_w,
            height=btn_h,
            textColor=(248, 244, 232),
            upColor=(150, 98, 58),
            overColor=(176, 118, 72),
            downColor=(120, 76, 46),
            fontName=None,
            fontSize=22,
        )

    def _load_background(self) -> None:
        try:
            img = pygame.image.load(START_SCREEN_IMAGE).convert()
            self._bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except (pygame.error, FileNotFoundError, OSError):
            self._bg = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if Start was clicked."""
        return bool(self.start_button.handleEvent(event))

    def draw(self) -> None:
        if self._bg is not None:
            self.window.blit(self._bg, (0, 0))
        else:
            self.window.fill((32, 48, 64))
        self.start_button.draw()
