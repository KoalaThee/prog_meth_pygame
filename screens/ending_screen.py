"""End-of-run overlay: radar chart of the five stats + graduation message.

Design notes:
- Angles are fixed, values change per run → unit vectors are cached at init so
  the per-frame draw is pure arithmetic and `blit`s.
- ``draw()`` is split into three small helpers (radar, HUD info, message) so
  each concern is independently readable and tunable.
- Colors, layout, and text styles live as class constants (one place to tweak).
"""

from __future__ import annotations

import math

import pygame

from branching import BRANCH_ARTS, BRANCH_SCIENCE
from config import (
    STAT_MAX_ARTS,
    STAT_MAX_HAPPINESS,
    STAT_MAX_HEALTH,
    STAT_MAX_INTELLIGENCE,
    STAT_MAX_SOCIAL,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from game_state import GameState


class EndingScreen:
    """Radar chart + branch/faculty summary + graduation message."""

    # ---- radar layout ------------------------------------------------------
    CX, CY, MAX_R = 460, 180, 120
    RING_FRACTIONS = (0.25, 0.5, 0.75, 1.0)
    AXES: tuple[tuple[str, str, int, float], ...] = (
        ("happiness",    "Happiness",    STAT_MAX_HAPPINESS,    -90.0),
        ("intelligence", "Intelligence", STAT_MAX_INTELLIGENCE, -18.0),
        ("social",       "Social",       STAT_MAX_SOCIAL,         0.0),
        ("arts",         "Arts",         STAT_MAX_ARTS,          54.0),
        ("health",       "Health",       STAT_MAX_HEALTH,       180.0),
    )
    LABEL_PAD = 10

    # ---- radar colors ------------------------------------------------------
    GRID_COLOR = (190, 190, 190)
    AXIS_COLOR = (155, 155, 155)
    FILL_COLOR = (86, 156, 236, 95)
    OUTLINE_COLOR = (52, 106, 170)
    LABEL_COLOR = (36, 36, 36)

    # ---- graduation message -----------------------------------------------
    MESSAGE_FONT_SIZE = 34
    MESSAGE_LINE_GAP = 8
    MESSAGE_OFFSET_Y = 50
    MESSAGE_COLOR = (255, 255, 255)
    CAREER_COLOR = (79, 163, 165)
    FALLBACK_CAREER = "Professional"

    # ---- HUD (branch/faculty) — mirrors StatsOverlay size + anchor --------
    HUD_FONT_SIZE = 18
    HUD_INFO_COLOR = (30, 30, 40)
    HUD_TEXT_MARGIN_X = 8
    HUD_ANCHOR_X = WINDOW_WIDTH - 18 - 35 - 6
    HUD_ANCHOR_Y = 20 + 20 // 2 + 18 + 6
    HUD_LINE_GAP = 2

    def __init__(self) -> None:
        self._label_font = pygame.font.Font(None, 20)
        self._hud_font = pygame.font.Font(None, self.HUD_FONT_SIZE)
        self._message_font = pygame.font.Font(None, self.MESSAGE_FONT_SIZE)
        self._fill_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        self._axis_units: tuple[tuple[float, float], ...] = tuple(
            (math.cos(math.radians(a)), math.sin(math.radians(a)))
            for _attr, _label, _cap, a in self.AXES
        )

    # ---- public API -------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
        game_state: GameState,
        career_title: str | None = None,
        branch_choice: str | None = None,
        faculty_choice: str | None = None,
    ) -> None:
        self._draw_radar(surface, game_state)
        self._draw_hud_info(surface, branch_choice, faculty_choice)
        self._draw_message(surface, career_title)

    # ---- radar ------------------------------------------------------------

    def _point(self, axis_index: int, r: float) -> tuple[int, int]:
        ux, uy = self._axis_units[axis_index]
        return int(self.CX + ux * r), int(self.CY + uy * r)

    def _draw_radar(self, surface: pygame.Surface, game_state: GameState) -> None:
        n = len(self.AXES)

        # Grid rings.
        for fraction in self.RING_FRACTIONS:
            r = self.MAX_R * fraction
            pygame.draw.polygon(
                surface, self.GRID_COLOR,
                [self._point(i, r) for i in range(n)], width=1,
            )

        # Axis spokes.
        for i in range(n):
            pygame.draw.line(
                surface, self.AXIS_COLOR, (self.CX, self.CY),
                self._point(i, self.MAX_R), width=1,
            )

        # Data polygon (fill + outline).
        data_pts: list[tuple[int, int]] = []
        for i, (attr, _label, cap, _angle) in enumerate(self.AXES):
            ratio = self._clamped_ratio(getattr(game_state, attr), cap)
            data_pts.append(self._point(i, self.MAX_R * ratio))

        self._fill_surf.fill((0, 0, 0, 0))
        pygame.draw.polygon(self._fill_surf, self.FILL_COLOR, data_pts)
        surface.blit(self._fill_surf, (0, 0))
        pygame.draw.polygon(surface, self.OUTLINE_COLOR, data_pts, width=2)

        # Axis labels.
        for i, (_attr, label, _cap, _angle) in enumerate(self.AXES):
            lx, ly = self._point(i, self.MAX_R + self.LABEL_PAD)
            text_surf = self._label_font.render(label, True, self.LABEL_COLOR)
            surface.blit(text_surf, self._anchor_label_rect(text_surf, lx, ly))

    @staticmethod
    def _clamped_ratio(value: int, cap: int) -> float:
        if cap <= 0:
            return 0.0
        return max(0.0, min(1.0, value / cap))

    def _anchor_label_rect(
        self, surf: pygame.Surface, lx: int, ly: int,
    ) -> pygame.Rect:
        """Anchor text away from the chart center so it does not overlap the polygon."""
        rect = surf.get_rect(center=(lx, ly))
        if lx > self.CX + 8:
            rect.left = lx
        elif lx < self.CX - 8:
            rect.right = lx
        if ly > self.CY + 8:
            rect.top = ly
        elif ly < self.CY - 8:
            rect.bottom = ly
        return rect

    # ---- HUD info (branch + faculty, HUD-style) ---------------------------

    def _draw_hud_info(
        self,
        surface: pygame.Surface,
        branch_choice: str | None,
        faculty_choice: str | None,
    ) -> None:
        branch_text = self._branch_text(branch_choice)
        if branch_text is None:
            return

        branch_rect = self._blit_clamped_hud_text(
            surface,
            branch_text,
            self.HUD_ANCHOR_Y,
            self.HUD_ANCHOR_X,
        )

        if faculty_choice:
            self._blit_clamped_hud_text(
                surface,
                f"Faculty: {faculty_choice}",
                branch_rect.bottom + self.HUD_LINE_GAP,
                self.HUD_ANCHOR_X,
            )

    @staticmethod
    def _branch_text(branch_choice: str | None) -> str | None:
        if branch_choice == BRANCH_SCIENCE:
            return "Branch: Science"
        if branch_choice == BRANCH_ARTS:
            return "Branch: Arts"
        return None

    def _blit_clamped_hud_text(
        self,
        surface: pygame.Surface,
        text: str,
        y_top: int,
        anchor_x: int,
    ) -> pygame.Rect:
        """Draw HUD text with horizontal clamping to keep it fully visible."""
        text_surf = self._hud_font.render(text, True, self.HUD_INFO_COLOR)
        rect = text_surf.get_rect(midtop=(anchor_x, y_top))
        if rect.left < self.HUD_TEXT_MARGIN_X:
            rect.left = self.HUD_TEXT_MARGIN_X
        if rect.right > WINDOW_WIDTH - self.HUD_TEXT_MARGIN_X:
            rect.right = WINDOW_WIDTH - self.HUD_TEXT_MARGIN_X
        surface.blit(text_surf, rect)
        return rect

    # ---- graduation message ----------------------------------------------

    def _draw_message(
        self, surface: pygame.Surface, career_title: str | None,
    ) -> None:
        title = career_title or self.FALLBACK_CAREER
        msg_y = self.CY + self.MAX_R + self.MESSAGE_OFFSET_Y

        line1 = self._message_font.render(
            "Congratulations! You graduated", True, self.MESSAGE_COLOR,
        )
        line1_rect = line1.get_rect(center=(self.CX, msg_y))
        surface.blit(line1, line1_rect)

        prefix = self._message_font.render("and became a ", True, self.MESSAGE_COLOR)
        career = self._message_font.render(title, True, self.CAREER_COLOR)
        line2_y = line1_rect.bottom + self.MESSAGE_LINE_GAP
        line2_x = self.CX - (prefix.get_width() + career.get_width()) // 2
        surface.blit(prefix, (line2_x, line2_y))
        surface.blit(career, (line2_x + prefix.get_width(), line2_y))
