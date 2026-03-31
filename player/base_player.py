import pygame
from settings import GROUND_Y, GRAVITY


class BasePlayer(pygame.sprite.Sprite):
    def __init__(self, start_x: int):
        super().__init__()

        self.image = None
        self.rect = None

        self.start_x = start_x
        self.vel_y = 0.0
        self.on_ground = True

        # Persistent stats for later expansion
        self.health = 100
        self.happiness = 100
        self.social = 100
        self.intelligence = 100
        self.arts = 100

    def get_jump_strength(self) -> float:
        raise NotImplementedError

    def update_animation(self):
        raise NotImplementedError

    def jump(self):
        if self.on_ground:
            self.vel_y = self.get_jump_strength()
            self.on_ground = False

    def calc_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

    def handle_input(self, keys):
        # Endless runner starter:
        # player does not move left/right manually
        pass

    def update(self, keys=None):
        if keys is not None:
            self.handle_input(keys)

        self.calc_gravity()
        self.update_animation()