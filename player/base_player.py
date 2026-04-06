import pygame
from settings import GROUND_Y, GRAVITY, RUN_ANIMATION_TICK_RATE


class BasePlayer(pygame.sprite.Sprite):
    # Override in each subclass to customise that stage's appearance and feel
    DISPLAY_WIDTH: int = 128
    DISPLAY_HEIGHT: int = 128
    JUMP_STRENGTH: float = -13.5 
    SECOND_JUMP_STRENGTH: float = -13.5

    def __init__(self, start_x: int):
        super().__init__()

        self.start_x = start_x
        self.vel_y = 0.0
        self.on_ground = True
        self.jumps_remaining = 2  # reset to 2 on landing

        self.image = None
        self.rect = None

        # Sprite frames - populated by _setup_sprites()
        self.run1_image = None
        self.run2_image = None
        self.jump_image = None
        self.animation_tick = 0
        self.current_run_frame = 0

        # Persistent stats
        self.health = 0
        self.happiness = 0
        self.social = 0
        self.intelligence = 0
        self.arts = 0

    # ------------------------------------------------------------------
    # Shared sprite helpers
    # ------------------------------------------------------------------

    def _load_and_scale(self, path: str) -> pygame.Surface:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

    def _setup_sprites(self, run1_path: str, run2_path: str, jump_path: str):
        """Load, scale and position all animation frames. Call from subclass __init__."""
        self.run1_image = self._load_and_scale(run1_path)
        self.run2_image = self._load_and_scale(run2_path)
        self.jump_image = self._load_and_scale(jump_path)

        self.image = self.run1_image
        self.rect = self.image.get_rect()
        self.rect.x = self.start_x
        self.rect.bottom = GROUND_Y

    def get_jump_strength(self) -> float:
        return self.JUMP_STRENGTH

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
            # First jump - must be on the ground
            if self.on_ground:
                self.vel_y = self.get_jump_strength()
                self.on_ground = False
                self.jumps_remaining -= 1
        elif self.jumps_remaining == 1:
            # Second (air) jump - available once while airborne
            self.vel_y = self.SECOND_JUMP_STRENGTH
            self.jumps_remaining -= 1

    def calc_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
            self.jumps_remaining = 2  # restore both jumps on landing

    def handle_input(self, keys):
        pass

    def update(self, keys=None):
        if keys is not None:
            self.handle_input(keys)
        self.calc_gravity()
        self.update_animation()
