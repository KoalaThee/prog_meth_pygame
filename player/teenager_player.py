import pygame

from player.base_player import BasePlayer
from settings import (
    PLAYER_START_X,
    PLAYER_DISPLAY_WIDTH,
    PLAYER_DISPLAY_HEIGHT,
    JUMP_STRENGTH,
    RUN_ANIMATION_TICK_RATE,
    TEENAGER_PLAYER_RUN1_IMAGE,
    TEENAGER_PLAYER_RUN2_IMAGE,
    TEENAGER_PLAYER_JUMP_IMAGE,
    GROUND_Y,
)


class TeenagerPlayer(BasePlayer):
    def __init__(self):
        super().__init__(PLAYER_START_X)

        self.run1_image = self._load_and_scale(TEENAGER_PLAYER_RUN1_IMAGE)
        self.run2_image = self._load_and_scale(TEENAGER_PLAYER_RUN2_IMAGE)
        self.jump_image = self._load_and_scale(TEENAGER_PLAYER_JUMP_IMAGE)

        self.image = self.run1_image
        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_START_X
        self.rect.bottom = GROUND_Y

        self.animation_tick = 0
        self.current_run_frame = 0

    def _load_and_scale(self, path: str) -> pygame.Surface:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(
            image,
            (PLAYER_DISPLAY_WIDTH, PLAYER_DISPLAY_HEIGHT)
        )

    def get_jump_strength(self) -> float:
        return JUMP_STRENGTH

    def update_animation(self):
        # If airborne, always show jump frame
        if not self.on_ground:
            current_bottom = self.rect.bottom
            self.image = self.jump_image
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.rect.bottom = current_bottom
            return

        # On ground: alternate run1 / run2
        self.animation_tick += 1
        if self.animation_tick >= RUN_ANIMATION_TICK_RATE:
            self.animation_tick = 0
            self.current_run_frame = 1 - self.current_run_frame

        current_bottom = self.rect.bottom
        current_midbottom = self.rect.midbottom

        if self.current_run_frame == 0:
            self.image = self.run1_image
        else:
            self.image = self.run2_image

        self.rect = self.image.get_rect(midbottom=current_midbottom)
        self.rect.bottom = current_bottom