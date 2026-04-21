import pygame
import pygwidgets

from config import WINDOW_WIDTH, WINDOW_HEIGHT, BRANCHING_SCREEN_IMAGE


class BranchScreen:
    """Translucent branch-choice overlay with two buttons."""

    def __init__(self, window: pygame.Surface):
        self.window = window
        self._bg: pygame.Surface | None = None
        self._load_background()

        btn_w, btn_h = 180, 44
        gap = 60
        total_w = btn_w * 2 + gap
        x0 = (WINDOW_WIDTH - total_w) // 2
        y = (WINDOW_HEIGHT - btn_h) // 2

        self.science_button = pygwidgets.TextButton(
            window,
            (x0, y),
            "Science",
            width=btn_w,
            height=btn_h,
            textColor=(248, 244, 232),
            upColor=(70, 104, 156),
            overColor=(88, 124, 178),
            downColor=(56, 84, 124),
            fontName=None,
            fontSize=22,
        )
        self.arts_button = pygwidgets.TextButton(
            window,
            (x0 + btn_w + gap, y),
            "Arts",
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
            img = pygame.image.load(BRANCHING_SCREEN_IMAGE).convert_alpha()
            self._bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except (pygame.error, FileNotFoundError, OSError):
            self._bg = None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Return chosen branch ('science'/'arts') when a button is clicked."""
        if self.science_button.handleEvent(event):
            return "science"
        if self.arts_button.handleEvent(event):
            return "arts"
        return None

    def draw(self) -> None:
        if self._bg is not None:
            self.window.blit(self._bg, (0, 0))
        else:
            dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 110))
            self.window.blit(dim, (0, 0))
        self.science_button.draw()
        self.arts_button.draw()
