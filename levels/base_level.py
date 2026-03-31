import pygame


class BaseLevel:
    def __init__(self, screen: pygame.Surface, player: pygame.sprite.Sprite):
        self.screen = screen
        self.player = player
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.world_shift = 0

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)

    def draw(self):
        self.all_sprites.draw(self.screen)

    def shift_world(self, shift_x: int):
        self.world_shift += shift_x