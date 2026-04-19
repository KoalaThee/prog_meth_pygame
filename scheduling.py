"""Reusable spawn scheduler shared by items and obstacles.

"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class SpawnSchedule:
    """Pre-computed (entity, frame) plan for one stage."""

    entries: list[str]
    spawn_frames: list[int]
    next_index: int = 0

    @classmethod
    def evenly_spaced(cls, entries, duration_frames: int) -> "SpawnSchedule":
        """Shuffle ``entries`` and place them at evenly-spaced spawn frames."""
        items = list(entries)
        if not items or duration_frames <= 0:
            return cls([], [])
        random.shuffle(items)
        n = len(items)
        frames = [int((k + 0.5) * duration_frames / n) for k in range(n)]
        return cls(items, frames)

    def pop_due(self, frame: int) -> list[str]:
        """Return all entries whose scheduled frame has been reached by ``frame``."""
        out: list[str] = []
        while (
            self.next_index < len(self.spawn_frames)
            and frame >= self.spawn_frames[self.next_index]
        ):
            out.append(self.entries[self.next_index])
            self.next_index += 1
        return out
