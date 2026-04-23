"""Shared helpers for screen classes."""
from __future__ import annotations

import pygame


def load_background(
    path: str,
    size: tuple[int, int],
    *,
    alpha: bool = True,
) -> pygame.Surface | None:
    """Load *path*, scale it to *size*, and return the surface.

    Returns ``None`` silently when the file is missing or cannot be decoded,
    so callers can skip the blit without crashing.
    """
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        return pygame.transform.smoothscale(img, size)
    except (pygame.error, FileNotFoundError, OSError):
        return None
