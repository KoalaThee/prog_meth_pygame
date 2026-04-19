from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT
from game_state import GameState
from items import ItemManager, trim_duration_frames
from obstacles import ObstacleManager


# ---------------------------------------------------------------------------
# SceneState — configuration for one named phase of the game
# ---------------------------------------------------------------------------

@dataclass
class SceneState:
    """
    One named phase (e.g. 'baby_normal', 'baby_transition').

    name         – identifier used to query the current state
    image_paths  – ordered list of background image file paths
    passes       – total image-scrolls to play  (images cycle if passes > len)
    speed        – pixels per frame for this state's scroll
    player_class – player to activate on entry; None = keep the current player
    terminal     – if True, game freezes (done) the moment this state is entered
                   (the state's image fills the screen and stays visible)
    """
    name: str
    image_paths: list[str]
    passes: int
    speed: float
    player_class: Callable | None = None
    terminal: bool = False
    stage: str | None = None


# ---------------------------------------------------------------------------
# SceneManager — single continuous scroller across all states
# ---------------------------------------------------------------------------


class SceneManager:
    """
    Builds one flat image sequence from all SceneStates and scrolls through it
    continuously — no hand-offs, no gaps, fully seamless.

    State transitions are driven by milestones (which global pass index each
    state starts at).  The player is swapped automatically when a state with
    a non-None player_class is entered.

    Backgrounds are decoded + scaled **once at construction time** so no disk
    I/O or ``smoothscale`` happens during gameplay (avoids per-pass stutter).
    Distinct paths are deduplicated, so memory is bounded by the unique image
    set, not the number of passes.

    Query `current_state.name` at any time to know the active state.
    """

    def __init__(self, screen: pygame.Surface, states: list[SceneState], game_state: GameState):
        self.screen = screen
        self.states = states
        self.game_state = game_state

        # ---- build flat sequence ----------------------------------------
        self.surfs: list[pygame.Surface] = []         # pre-loaded surface per pass
        self.pass_speeds: list[float] = []
        self.milestones: dict[int, SceneState] = {}   # pass_idx → SceneState
        self.stage_duration_frames: dict[str, int] = {}  # stage_name → total frames in stage

        # Pre-load + pre-scale every distinct background once. Eliminates I/O bound issues
        bg_cache: dict[str, pygame.Surface] = {}

        global_pass = 0
        for state in states:
            if state.passes == 0:
                continue

            self.milestones[global_pass] = state
            for j in range(state.passes):
                path = state.image_paths[j % len(state.image_paths)]
                surf = bg_cache.get(path)
                if surf is None:
                    surf = self._load_bg(path)
                    bg_cache[path] = surf
                self.surfs.append(surf)
                self.pass_speeds.append(state.speed)

            if state.stage is not None and state.speed > 0:
                frames = int(state.passes * WINDOW_WIDTH / state.speed)
                self.stage_duration_frames[state.stage] = (
                    self.stage_duration_frames.get(state.stage, 0) + frames
                )

            global_pass += state.passes

        self.total_passes = global_pass

        # ---- scroll state ------------------------------------------------
        self.scroll_x = 0.0
        self._done = False

        # ---- sprites & first player -------------------------------------
        self.all_sprites = pygame.sprite.Group()
        self.player = None
        self.current_state: SceneState = states[0]

        # Activate the first state that brings a player
        first = next((s for s in states if s.player_class is not None), None)
        if first:
            self._activate_player(first)

        # ---- items + obstacles -------------------------------------------
        self.item_manager = ItemManager(self.game_state)
        self.obstacle_manager = ObstacleManager(self.game_state)
        self.current_stage: str | None = None
        if self.current_state.stage is not None:
            self._begin_stage(self.current_state.stage)

    def _item_spawn_duration_frames(self, stage: str) -> int:
        """Scroll duration for ``stage`` with item-stage trim applied (see ``items``)."""
        return trim_duration_frames(stage, self.stage_duration_frames.get(stage, 0))

    def _begin_stage(self, stage: str) -> None:
        """Activate item + obstacle schedules for the new stage."""
        self.current_stage = stage
        duration = self.stage_duration_frames.get(stage, 0)
        self.item_manager.start_stage(stage, self._item_spawn_duration_frames(stage))
        self.obstacle_manager.start_stage(stage, duration)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_bg(path: str) -> pygame.Surface:
        img = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))

    def _activate_player(self, state: SceneState):
        self.player = state.player_class()
        self.all_sprites.empty()
        self.all_sprites.add(self.player)

    @property
    def _current_pass(self) -> int:
        return int(self.scroll_x // WINDOW_WIDTH)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_done(self) -> bool:
        return self._done

    def is_game_over(self) -> bool:
        return self.obstacle_manager.is_game_over()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.player:
                self.player.jump()

    def update(self):
        if self._done or self.is_game_over():
            return

        prev_pass = self._current_pass
        speed = self.pass_speeds[min(prev_pass, self.total_passes - 1)]
        self.scroll_x += speed
        new_pass = self._current_pass

        # Fire milestones for every pass boundary crossed this frame
        for p in range(prev_pass + 1, new_pass + 1):
            if p in self.milestones:
                state = self.milestones[p]
                self.current_state = state
                if state.player_class is not None:
                    self._activate_player(state)
                if state.stage is not None and state.stage != self.current_stage:
                    self._begin_stage(state.stage)
                if state.terminal:
                    self.scroll_x = p * WINDOW_WIDTH
                    self.item_manager.flush()
                    self.obstacle_manager.flush()
                    self._done = True
                    break

        if not self._done and new_pass >= self.total_passes:
            self.item_manager.flush()
            self.obstacle_manager.flush()
            self._done = True

        if self.player:
            keys = pygame.key.get_pressed()
            self.player.update(keys)

        self.item_manager.update(speed, self.player)
        self.obstacle_manager.update(speed, self.player)

    def draw(self):
        self.screen.fill((0, 0, 0))

        current_pass = self._current_pass
        leading_x = -(self.scroll_x % WINDOW_WIDTH)

        for slot in range(2):  # current image + next image entering from right
            pass_idx = current_pass + slot
            if pass_idx >= self.total_passes:
                break
            x = int(leading_x) + slot * WINDOW_WIDTH
            if x < WINDOW_WIDTH:
                self.screen.blit(self.surfs[pass_idx], (x, 0))

        self.item_manager.draw(self.screen)
        self.obstacle_manager.draw(self.screen)
        self.all_sprites.draw(self.screen)
