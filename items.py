from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol

import pygame

from config import FPS, GROUND_Y, WINDOW_WIDTH
from game_state import GameState


# ---------------------------------------------------------------------------
# Item & stage data (single source of truth)
# ---------------------------------------------------------------------------

ITEM_SIZE = 40


@dataclass(frozen=True)
class ItemDef:
    image_path: str
    effects: dict[str, int]


ITEMS: dict[str, ItemDef] = {
    "milk":      ItemDef("assets/images/item_milk.png",       {"health":  5, "happiness":  5}),
    "good_food": ItemDef("assets/images/item_good food.png",  {"health":  5, "happiness":  5}),
    "bad_food":  ItemDef("assets/images/item_bad food.png",   {"health": -10, "happiness":  5}),
    "study":     ItemDef("assets/images/item_book.png",       {"happiness": -5, "intelligence": 10}),
    "art":       ItemDef("assets/images/item_art.png",        {"happiness":  5, "arts":         10}),
    "friend":    ItemDef("assets/images/item_friend.png",     {"happiness": 10, "social":        1}),
    "exercise":  ItemDef("assets/images/item_exercise.png",   {"health": 10, "happiness":  5}),
}


@dataclass(frozen=True)
class StageDef:
    """Items + multipliers + spawn-window trim for one life stage."""
    items: tuple[str, ...]
    multipliers: dict[str, int] = field(default_factory=dict)
    duration_trim_frames: int = 0


STAGES: dict[str, StageDef] = {
    "baby": StageDef(
        items=("milk",) * 10,
    ),
    "toddler": StageDef(
        items=("study",) * 4 + ("art",) * 4 + ("good_food",) * 4 + ("friend",) * 4,
    ),
    "teenager": StageDef(
        items=("study",) * 6 + ("art",) * 3 + ("good_food",) * 3 + ("friend",) * 3
              + ("exercise",) * 3 + ("bad_food",) * 2,
        multipliers={"intelligence": 2, "arts": 2},  # high-school doubles study/art payoff
    ),
    "young_adult": StageDef(
        items=("study",) * 8 + ("art",) * 4 + ("good_food",) * 3 + ("friend",) * 4
              + ("exercise",) * 3 + ("bad_food",) * 2,
        multipliers={"intelligence": 2, "arts": 2},  # university doubles study/art payoff
        duration_trim_frames=int(2 * FPS),  # spawn YA collectibles in a 2s-shorter window
    ),
}


def trim_duration_frames(stage: str, base_frames: int) -> int:
    """Apply ``StageDef.duration_trim_frames`` with a floor so all spawns still fit."""
    s = STAGES.get(stage)
    if not s:
        return base_frames
    return max(len(s.items), base_frames - s.duration_trim_frames)


# ---------------------------------------------------------------------------
# Spawn geometry
# ---------------------------------------------------------------------------

class _PlayerLike(Protocol):
    role: str
    DISPLAY_HEIGHT: float
    rect: pygame.Rect


DOUBLE_JUMP_FEET_Y = 159

SPAWN_X = WINDOW_WIDTH + ITEM_SIZE // 2
SPAWN_BOTTOM_Y_MAX = GROUND_Y - 30

SPAWN_MIDBOTTOM_Y_MIN_ON_SCREEN = ITEM_SIZE

SPAWN_BANDS: dict[str, str] = {
    "baby":        "fit_screen",
    "toddler":     "fit_screen",
    "teenager":    "by_reach",
    "young_adult": "screen_top",
}


def spawn_bottom_y_range(player: _PlayerLike | None) -> tuple[int, int]:
    """Return (min_midbottom_y, max_midbottom_y) for the active player."""
    if player is None:
        return GROUND_Y - 180, SPAWN_BOTTOM_Y_MAX

    h = int(round(player.DISPLAY_HEIGHT))
    raw_min = (DOUBLE_JUMP_FEET_Y - h) + ITEM_SIZE
    policy = SPAWN_BANDS.get(getattr(player, "role", ""), "fit_screen")

    if policy == "screen_top":
        y_min = SPAWN_MIDBOTTOM_Y_MIN_ON_SCREEN
    elif policy == "by_reach":
        y_min = raw_min
    else:
        y_min = max(SPAWN_MIDBOTTOM_Y_MIN_ON_SCREEN, raw_min)

    return min(y_min, SPAWN_BOTTOM_Y_MAX), SPAWN_BOTTOM_Y_MAX


# ---------------------------------------------------------------------------
# Sprite
# ---------------------------------------------------------------------------

class Item(pygame.sprite.Sprite):
    """One on-screen collectible: scrolls left and applies stat deltas on pickup."""

    def __init__(
        self,
        name: str,
        image: pygame.Surface,
        midbottom: tuple[int, int],
        effects: dict[str, int],
    ):
        super().__init__()
        self.name = name
        self.image = image
        self.rect = self.image.get_rect(midbottom=midbottom)
        self._x = float(self.rect.x)
        self.effects = effects

    def scroll(self, dx: float) -> None:
        self._x -= dx
        self.rect.x = int(self._x)


# ---------------------------------------------------------------------------
# Spawn schedule
# ---------------------------------------------------------------------------

@dataclass
class SpawnSchedule:
    """Pre-computed (item, frame) plan for one stage."""
    items: list[str]
    spawn_frames: list[int]
    next_index: int = 0

    @classmethod
    def for_stage(cls, stage: str, duration_frames: int) -> SpawnSchedule:
        s = STAGES.get(stage)
        if not s or duration_frames <= 0 or not s.items:
            return cls([], [])
        items = list(s.items)
        random.shuffle(items)
        n = len(items)
        # Even spacing
        frames = [int((k + 0.5) * duration_frames / n) for k in range(n)]
        return cls(items, frames)

    def pop_due(self, frame: int) -> list[str]:
        out: list[str] = []
        while self.next_index < len(self.spawn_frames) and frame >= self.spawn_frames[self.next_index]:
            out.append(self.items[self.next_index])
            self.next_index += 1
        return out


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class ItemManager:
    """Owns active items for the current stage: scheduling, scrolling, pickups."""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.items: pygame.sprite.Group = pygame.sprite.Group()
        self._image_cache: dict[str, pygame.Surface] = {}
        self._schedule = SpawnSchedule([], [])
        self._multipliers: dict[str, int] = {}
        self._frame = 0

    # ---- lifecycle ----------------------------------------------------

    def start_stage(self, stage: str, duration_frames: int) -> None:
        """Begin spawning items for ``stage`` over ``duration_frames``.

        Existing on-screen items keep scrolling — only the schedule resets.
        """
        self._schedule = SpawnSchedule.for_stage(stage, duration_frames)
        s = STAGES.get(stage)
        self._multipliers = dict(s.multipliers) if s else {}
        self._frame = 0

    def flush(self) -> None:
        """Clear all items and cancel pending spawns (call at end-of-run)."""
        for sprite in list(self.items):
            sprite.kill()
        self._schedule = SpawnSchedule([], [])
        self._multipliers = {}
        self._frame = 0

    # ---- per-frame ----------------------------------------------------

    def update(self, scroll_dx: float, player: _PlayerLike | None) -> None:
        for name in self._schedule.pop_due(self._frame):
            self._spawn(name, player)

        for item in list(self.items):
            item.scroll(scroll_dx)
            if item.rect.right < 0:
                item.kill()

        if player is not None:
            for item in list(self.items):
                if player.rect.colliderect(item.rect):
                    self.game_state.apply(item.effects)
                    item.kill()

        self._frame += 1

    def draw(self, surface: pygame.Surface) -> None:
        self.items.draw(surface)

    # ---- helpers ------------------------------------------------------

    def _spawn(self, name: str, player: _PlayerLike | None) -> None:
        defn = ITEMS[name]
        image = self._load(defn.image_path)
        effects = {stat: delta * self._multipliers.get(stat, 1)
                   for stat, delta in defn.effects.items()}
        y_lo, y_hi = spawn_bottom_y_range(player)
        midbottom = (SPAWN_X, random.randint(y_lo, y_hi))
        self.items.add(Item(name, image, midbottom, effects))

    def _load(self, path: str) -> pygame.Surface:
        cached = self._image_cache.get(path)
        if cached is None:
            img = pygame.image.load(path).convert_alpha()
            cached = pygame.transform.smoothscale(img, (ITEM_SIZE, ITEM_SIZE))
            self._image_cache[path] = cached
        return cached
