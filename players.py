import pygame
from config import (
    GROUND_Y, GRAVITY, RUN_ANIMATION_TICK_RATE,
    PLAYER_START_X,
    BABY_PLAYER_RUN1_IMAGE, BABY_PLAYER_RUN2_IMAGE, BABY_PLAYER_JUMP_IMAGE,
    TODDLER_PLAYER_RUN1_IMAGE, TODDLER_PLAYER_RUN2_IMAGE, TODDLER_PLAYER_JUMP_IMAGE,
    TEENAGER_PLAYER_RUN1_IMAGE, TEENAGER_PLAYER_RUN2_IMAGE, TEENAGER_PLAYER_JUMP_IMAGE,
    YOUNG_ADULT_PLAYER_RUN1_IMAGE, YOUNG_ADULT_PLAYER_RUN2_IMAGE, YOUNG_ADULT_PLAYER_JUMP_IMAGE,
)


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        start_x: int,
        *,
        width: int = 128,
        height: int = 128,
        jump_strength: float = -13.5,
        second_jump_strength: float = -13.5,
        run1: str,
        run2: str,
        jump_img: str,
        role: str = "",
    ):
        super().__init__()

        self.role = role
        self.DISPLAY_WIDTH = width
        self.DISPLAY_HEIGHT = height
        self.JUMP_STRENGTH = jump_strength
        self.SECOND_JUMP_STRENGTH = second_jump_strength

        self.start_x = start_x
        self.vel_y = 0.0
        self.on_ground = True
        self.jumps_remaining = 2

        self.image = None
        self.rect = None

        self.run1_image = None
        self.run2_image = None
        self.jump_image = None
        self.animation_tick = 0
        self.current_run_frame = 0

        self._setup_sprites(run1, run2, jump_img)

    def _load_and_scale(self, path: str) -> pygame.Surface:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

    def _setup_sprites(self, run1_path: str, run2_path: str, jump_path: str):
        self.run1_image = self._load_and_scale(run1_path)
        self.run2_image = self._load_and_scale(run2_path)
        self.jump_image = self._load_and_scale(jump_path)

        self.image = self.run1_image
        self.rect = self.image.get_rect()
        self.rect.x = self.start_x
        self.rect.bottom = GROUND_Y

    def update_animation(self):
        if not self.on_ground:
            self.image = self.jump_image
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            return

        self.animation_tick += 1
        if self.animation_tick >= RUN_ANIMATION_TICK_RATE:
            self.animation_tick = 0
            self.current_run_frame = 1 - self.current_run_frame

        midbottom = self.rect.midbottom
        self.image = self.run1_image if self.current_run_frame == 0 else self.run2_image
        self.rect = self.image.get_rect(midbottom=midbottom)

    def jump(self):
        if self.jumps_remaining == 2:
            if self.on_ground:
                self.vel_y = self.JUMP_STRENGTH
                self.on_ground = False
                self.jumps_remaining -= 1
        elif self.jumps_remaining == 1:
            self.vel_y = self.SECOND_JUMP_STRENGTH
            self.jumps_remaining -= 1

    def calc_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
            self.jumps_remaining = 2

    def handle_input(self, keys):
        pass

    def update(self, keys=None):
        if keys is not None:
            self.handle_input(keys)
        self.calc_gravity()
        self.update_animation()


def BabyPlayer():
    return Player(PLAYER_START_X, width=100, height=65.84, jump_strength=-13.5,
                  run1=BABY_PLAYER_RUN1_IMAGE, run2=BABY_PLAYER_RUN2_IMAGE, jump_img=BABY_PLAYER_JUMP_IMAGE,
                  role="baby")

def ToddlerPlayer():
    return Player(PLAYER_START_X, width=156.60, height=200, jump_strength=-13.5,
                  run1=TODDLER_PLAYER_RUN1_IMAGE, run2=TODDLER_PLAYER_RUN2_IMAGE, jump_img=TODDLER_PLAYER_JUMP_IMAGE,
                  role="toddler")

def TeenagerPlayer():
    return Player(PLAYER_START_X, width=186.66, height=250, jump_strength=-13.5,
                  run1=TEENAGER_PLAYER_RUN1_IMAGE, run2=TEENAGER_PLAYER_RUN2_IMAGE, jump_img=TEENAGER_PLAYER_JUMP_IMAGE,
                  role="teenager")

def YoungAdultPlayer():
    return Player(PLAYER_START_X, width=186.66, height=250, jump_strength=-13.5,
                  run1=YOUNG_ADULT_PLAYER_RUN1_IMAGE, run2=YOUNG_ADULT_PLAYER_RUN2_IMAGE, jump_img=YOUNG_ADULT_PLAYER_JUMP_IMAGE,
                  role="young_adult")
