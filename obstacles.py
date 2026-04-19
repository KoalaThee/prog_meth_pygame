"""Obstacles: hazardous sprites that scroll in from the right and damage the player.

Design overview
---------------

* ``Obstacle`` (abstract) defines a fixed update pipeline using the **template
  method** pattern: each frame it scrolls with the world, runs subclass-specific
  movement, then despawns if it has left the screen.
* ``StaticObstacle`` only scrolls (e.g. baby's table).
* ``ChasingObstacle`` (abstract) adds extra horizontal velocity *toward* the
  player on top of the world scroll, and delegates the vertical rule to its
  own ``_apply_y`` hook so each subtype owns only the part that differs.
    * ``BullyObstacle``     – ground-locked y, character must jump over.
    * ``GradeObstacle``     – random fly y per spawn (variable y-axis).
    * ``JobRejectObstacle`` – chase x, slow sine oscillation on y.

Per-stage spawn lists, counts, and effects live in ``OBSTACLE_STAGES`` /
``OBSTACLES`` so adding a new stage or obstacle is a data edit, not a code
edit. Spawn timing reuses ``scheduling.SpawnSchedule`` so obstacles are
distributed evenly through each stage's scroll duration, exactly like items.
Each obstacle applies its effects at most once on overlap, then stays visible
until it scrolls off the left edge.
"""

from __future__ import annotations

import math
import random
from abc import abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import pygame

from config import GROUND_Y, WINDOW_WIDTH
from game_state import GameState
from scheduling import SpawnSchedule


# ---------------------------------------------------------------------------
# Base classes — template method pattern
# ---------------------------------------------------------------------------

class Obstacle(pygame.sprite.Sprite):
    """Abstract base. Owns the per-frame pipeline; subclasses fill the hooks."""

    def __init__(
        self,
        image: pygame.Surface,
        midbottom: tuple[int, int],
        effects: dict[str, int],
    ):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=midbottom)
        # Sub-pixel x so float scroll speeds stay accurate over time.
        self._x = float(self.rect.x)
        self.effects = effects
        # Stat effects apply once on first overlap; sprite stays until off-screen left.
        self._hit_applied = False
        # Frame counter local to this obstacle (used by sine motion etc.).
        self._age = 0

    # ---- public pipeline (template method) ----------------------------

    def update(self, scroll_dx: float, player=None) -> None:
        self._scroll(scroll_dx)
        self._move_relative(scroll_dx, player)
        self._despawn_if_off_screen()
        self._age += 1

    def try_hit(self) -> dict[str, int] | None:
        """Consume this obstacle's one-shot hit. Returns effects on first call, else ``None``.

        The sprite is NOT killed — it keeps scrolling until it leaves the screen.
        """
        if self._hit_applied:
            return None
        self._hit_applied = True
        return self.effects

    # ---- shared helpers ----------------------------------------------

    def _scroll(self, dx: float) -> None:
        self._x -= dx
        self.rect.x = int(self._x)

    def _despawn_if_off_screen(self) -> None:
        if self.rect.right < 0:
            self.kill()

    # ---- subclass hook -----------------------------------------------

    @abstractmethod
    def _move_relative(self, scroll_dx: float, player=None) -> None:
        """Add subtype-specific motion on top of world scroll."""
        raise NotImplementedError


class StaticObstacle(Obstacle):
    """Pure scroller — no motion beyond the world (e.g. baby's table)."""

    def _move_relative(self, scroll_dx: float, player=None) -> None:
        return  # nothing else to do


class ChasingObstacle(Obstacle):
    """Adds extra leftward velocity (toward the player) and delegates y to ``_apply_y``."""

    def __init__(
        self,
        image: pygame.Surface,
        midbottom: tuple[int, int],
        effects: dict[str, int],
        chase_speed: float,
    ):
        super().__init__(image, midbottom, effects)
        self.chase_speed = chase_speed

    def _move_relative(self, scroll_dx: float, player=None) -> None:
        self._x -= self.chase_speed
        self.rect.x = int(self._x)
        self._apply_y(player)

    @abstractmethod
    def _apply_y(self, player=None) -> None:
        """Update ``self.rect`` y-position for this frame."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Concrete obstacles
# ---------------------------------------------------------------------------

class BullyObstacle(ChasingObstacle):
    """Runs along the ground toward the player; jump over to dodge."""

    def _apply_y(self, player=None) -> None:
        self.rect.bottom = GROUND_Y


class GradeObstacle(ChasingObstacle):
    """Flies in at a random fly-band y chosen at spawn (variable y-axis)."""

    def _apply_y(self, player=None) -> None:
        return  # y is fixed at the value chosen at spawn time


class JobRejectObstacle(ChasingObstacle):
    """Flies in with a slow sine oscillation on y."""

    def __init__(
        self,
        image: pygame.Surface,
        midbottom: tuple[int, int],
        effects: dict[str, int],
        chase_speed: float,
        amplitude: float,
        omega: float,
        phase: float,
    ):
        super().__init__(image, midbottom, effects, chase_speed)
        self._base_y = midbottom[1]
        self._amplitude = amplitude
        self._omega = omega
        self._phase = phase

    def _apply_y(self, player=None) -> None:
        offset = self._amplitude * math.sin(self._phase + self._omega * self._age)
        self.rect.bottom = int(self._base_y + offset)


# ---------------------------------------------------------------------------
# Spawn geometry and per-stage data
# ---------------------------------------------------------------------------

def _on_screen_min_midbottom_y(height: int) -> int:
    return height


# Per-subtype physics tuning. Kept as module constants because they describe
# *how a kind moves*, not per-instance data.
JOB_REJECT_AMPLITUDE = 35.0
JOB_REJECT_OMEGA = 0.06  # rad/frame
BULLY_CHASE_SPEED = 3
GRADE_CHASE_SPEED = 2
JOB_REJECT_CHASE_SPEED = 2


@dataclass(frozen=True)
class ObstacleDef:
    """Static description of one obstacle type (image + display size + effects + factory).

    ``midbottom_y_choices`` is an optional list of discrete ``midbottom`` y values
    for flying obstacles; spawn picks one at random. Leave empty for obstacles
    that don't need a y choice (e.g. ground-locked ones).
    """

    image_path: str
    width: int
    height: int
    effects: dict[str, int]
    # Builds a sprite at the right edge for a fresh spawn.
    factory: Callable[[pygame.Surface, "ObstacleDef"], Obstacle]
    midbottom_y_choices: tuple[int, ...] = field(default_factory=tuple)


# ---- factories --------------------------------------------------------

def _spawn_x(width: int) -> int:
    return WINDOW_WIDTH + width // 2


def _pick_midbottom_y(candidates: Sequence[int], height: int) -> int:
    """Pick a random ``midbottom`` y from ``candidates`` that keeps the sprite on-screen.

    If no candidate satisfies the on-screen constraint, falls back to the minimum
    safe y (top of the sprite touches y=0). Pass a real sequence — a one-element
    tuple needs a trailing comma (``(400,)``); ``(400)`` is just an int.
    """
    y_min = _on_screen_min_midbottom_y(height)
    valid = [y for y in candidates if y >= y_min]
    if not valid:
        return y_min
    return random.choice(valid)


def _make_table(image: pygame.Surface, defn: ObstacleDef) -> Obstacle:
    return StaticObstacle(image, (_spawn_x(defn.width), GROUND_Y), defn.effects)


def _make_bully(image: pygame.Surface, defn: ObstacleDef) -> Obstacle:
    return BullyObstacle(
        image,
        (_spawn_x(defn.width), GROUND_Y),
        defn.effects,
        chase_speed=BULLY_CHASE_SPEED,
    )


def _make_grade(image: pygame.Surface, defn: ObstacleDef) -> Obstacle:
    y = _pick_midbottom_y(defn.midbottom_y_choices, defn.height)
    return GradeObstacle(
        image,
        (_spawn_x(defn.width), y),
        defn.effects,
        chase_speed=GRADE_CHASE_SPEED,
    )


def _make_job_reject(image: pygame.Surface, defn: ObstacleDef) -> Obstacle:
    y = _pick_midbottom_y(defn.midbottom_y_choices, defn.height)
    return JobRejectObstacle(
        image,
        (_spawn_x(defn.width), y),
        defn.effects,
        chase_speed=JOB_REJECT_CHASE_SPEED,
        amplitude=JOB_REJECT_AMPLITUDE,
        omega=JOB_REJECT_OMEGA,
        phase=random.uniform(0.0, 2 * math.pi),
    )


# ---- registry ---------------------------------------------------------

OBSTACLES: dict[str, ObstacleDef] = {
    "table": ObstacleDef(
        image_path="assets/images/obsticle_baby.png",
        width=50,
        height=80,
        effects={"health": -10},
        factory=_make_table,
    ),
    "bully": ObstacleDef(
        image_path="assets/images/obsticle_toddler.png",
        width=160,
        height=80,
        effects={"health": -12, "happiness": -8},
        factory=_make_bully,
    ),
    "grade": ObstacleDef(
        image_path="assets/images/obsticle_teenager.png",
        width=65,
        height=65,
        effects={"health": -10, "happiness": -10, "intelligence": -8},
        factory=_make_grade,
        midbottom_y_choices=(350, 100),
    ),
    "job_reject": ObstacleDef(
        image_path="assets/images/obsticle_young adult.png",
        width=50,
        height=50,
        effects={"health": -12, "happiness": -12, "social": -1},
        factory=_make_job_reject,
        midbottom_y_choices=(350, 75),
    ),
}


# Per-stage spawn list
OBSTACLE_STAGES: dict[str, tuple[str, ...]] = {
    "baby":        ("table",) * 3,
    "toddler":     ("bully",) * 5,
    "teenager":    ("grade",) * 6,
    "young_adult": ("job_reject",) * 8,
}


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class ObstacleManager:
    """Owns active obstacles for the current stage: scheduling, scrolling, hits."""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.obstacles: pygame.sprite.Group = pygame.sprite.Group()
        self._image_cache: dict[str, pygame.Surface] = {}
        self._schedule = SpawnSchedule([], [])
        self._frame = 0
        self._game_over = False

    # ---- lifecycle ----------------------------------------------------

    def start_stage(self, stage: str, duration_frames: int) -> None:
        """Begin spawning obstacles for ``stage`` over ``duration_frames``."""
        entries = OBSTACLE_STAGES.get(stage, ())
        self._schedule = SpawnSchedule.evenly_spaced(entries, duration_frames)
        self._frame = 0

    def flush(self) -> None:
        """Clear all obstacles and cancel pending spawns."""
        for sprite in list(self.obstacles):
            sprite.kill()
        self._schedule = SpawnSchedule([], [])
        self._frame = 0

    # ---- per-frame ----------------------------------------------------

    def update(self, scroll_dx: float, player=None) -> None:
        if self._game_over:
            return

        for name in self._schedule.pop_due(self._frame):
            self._spawn(name)

        for obs in list(self.obstacles):
            obs.update(scroll_dx, player)

        if player is not None:
            self._resolve_collisions(player)

        self._frame += 1

    def draw(self, surface: pygame.Surface) -> None:
        self.obstacles.draw(surface)

    def is_game_over(self) -> bool:
        return self._game_over

    # ---- helpers ------------------------------------------------------

    def _resolve_collisions(self, player) -> None:
        """Apply at most one hit per obstacle on overlap; trigger game over at 0 HP."""
        for obs in self.obstacles:
            if not player.rect.colliderect(obs.rect):
                continue
            effects = obs.try_hit()
            if effects is None:
                continue
            self.game_state.apply(effects)
            if self.game_state.health <= 0:
                self.game_state.health = 0
                self._game_over = True
                return

    def _spawn(self, name: str) -> None:
        defn = OBSTACLES[name]
        image = self._load(defn.image_path, defn.width, defn.height)
        self.obstacles.add(defn.factory(image, defn))

    def _load(self, path: str, width: int, height: int) -> pygame.Surface:
        key = f"{path}@{width}x{height}"
        cached = self._image_cache.get(key)
        if cached is None:
            img = pygame.image.load(path).convert_alpha()
            cached = pygame.transform.smoothscale(img, (width, height))
            self._image_cache[key] = cached
        return cached
