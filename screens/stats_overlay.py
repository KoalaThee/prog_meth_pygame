import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    OVERLAY_SCREEN_IMAGE,
    STAT_MAX_HEALTH,
    STAT_MAX_HAPPINESS,
    STAT_MAX_INTELLIGENCE,
    STAT_MAX_ARTS,
)
from game_state import GameState
from .util import load_background


def _ratio(value: int, max_val: int) -> float:
    if max_val <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_val))


class StatsOverlay:
    """Overlay art + four stat bars (health, happiness, intelligence, arts) + social number in circle."""

    BAR_W = 120
    BAR_H = 20
    GAP = 30
    TOP = 20
    LEFT = 35
    CIRCLE_R = 18

    BAR_BG = (220, 220, 220)
    OUTLINE = (40, 40, 40)
    BRANCH_SCIENCE_TEXT = "Branch: Science"
    BRANCH_ARTS_TEXT = "Branch: Arts"
    BRANCH_TEXT_COLOR = (30, 30, 40)
    HUD_TEXT_MARGIN_X = 8

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self._overlay = load_background(OVERLAY_SCREEN_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self._font = pygame.font.Font(None, 18)

    def _draw_fill_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        value: int,
        max_val: int,
        fill_color: tuple[int, int, int],
    ) -> None:
        bg_rect = pygame.Rect(x, y, self.BAR_W, self.BAR_H)
        pygame.draw.rect(surface, self.BAR_BG, bg_rect, border_radius=3)

        rw = int(self.BAR_W * _ratio(value, max_val))
        if rw > 0:
            fill_rect = pygame.Rect(x, y, rw, self.BAR_H)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

        pygame.draw.rect(surface, self.OUTLINE, bg_rect, width=1, border_radius=3)

    def _blit_clamped_text_under_circle(
        self,
        surface: pygame.Surface,
        text: str,
        y_top: int,
        cx: int,
    ) -> pygame.Rect:
        """Draw text centered near the circle, clamped to stay fully on-screen."""
        surf = self._font.render(text, True, self.BRANCH_TEXT_COLOR)
        rect = surf.get_rect(midtop=(cx - 6, y_top))
        if rect.left < self.HUD_TEXT_MARGIN_X:
            rect.left = self.HUD_TEXT_MARGIN_X
        if rect.right > WINDOW_WIDTH - self.HUD_TEXT_MARGIN_X:
            rect.right = WINDOW_WIDTH - self.HUD_TEXT_MARGIN_X
        surface.blit(surf, rect)
        return rect

    def draw(
        self,
        surface: pygame.Surface,
        stage: str | None = None,
        branch_choice: str | None = None,
        faculty_choice: str | None = None,
    ) -> None:
        gs = self.game_state
        x = self.LEFT
        y = self.TOP

        bars = (
            (gs.health, STAT_MAX_HEALTH, (200, 80, 80)),
            (gs.happiness, STAT_MAX_HAPPINESS, (80, 180, 80)),
            (gs.intelligence, STAT_MAX_INTELLIGENCE, (80, 120, 200)),
            (gs.arts, STAT_MAX_ARTS, (170, 126, 52) ),
        )
        for value, vmax, color in bars:
            self._draw_fill_bar(surface, x, y, value, vmax, color)
            x += self.BAR_W + self.GAP

        cx = WINDOW_WIDTH - self.CIRCLE_R - self.LEFT
        cy = y + self.BAR_H // 2

        pygame.draw.circle(surface, (226, 214, 188) , (cx, cy), self.CIRCLE_R)
        pygame.draw.circle(surface, (60, 60, 80), (cx, cy), self.CIRCLE_R, width=2)

        text = str(int(gs.social))
        text_surf = self._font.render(text, True, (30, 30, 40))
        text_rect = text_surf.get_rect(center=(cx, cy))
        surface.blit(text_surf, text_rect)

        # Show branch text only from high school stage onward.
        if stage in {"teenager", "young_adult"}:
            if branch_choice == "science":
                branch_text = self.BRANCH_SCIENCE_TEXT
            elif branch_choice == "arts":
                branch_text = self.BRANCH_ARTS_TEXT
            elif gs.intelligence > gs.arts:
                branch_text = self.BRANCH_SCIENCE_TEXT
            elif gs.arts > gs.intelligence:
                branch_text = self.BRANCH_ARTS_TEXT
            else:
                branch_text = None

            if branch_text is not None:
                branch_rect = self._blit_clamped_text_under_circle(
                    surface,
                    branch_text,
                    cy + self.CIRCLE_R + 6,
                    cx,
                )
            else:
                branch_rect = None

            if stage == "young_adult" and faculty_choice and branch_rect is not None:
                faculty_text = f"Faculty: {faculty_choice}"
                self._blit_clamped_text_under_circle(
                    surface,
                    faculty_text,
                    branch_rect.bottom + 2,
                    cx,
                )

        # Draw overlay art last so it appears in front of the bars/circle.
        if self._overlay is not None:
            surface.blit(self._overlay, (0, 0))
