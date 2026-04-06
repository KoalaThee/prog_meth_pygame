from player.base_player import BasePlayer
from settings import (
    PLAYER_START_X,
    TODDLER_PLAYER_RUN1_IMAGE,
    TODDLER_PLAYER_RUN2_IMAGE,
    TODDLER_PLAYER_JUMP_IMAGE,
)


class ToddlerPlayer(BasePlayer):
    DISPLAY_WIDTH = 200
    DISPLAY_HEIGHT = 200
    JUMP_STRENGTH = -13.5
    SECOND_JUMP_STRENGTH = -13.5

    def __init__(self):
        super().__init__(PLAYER_START_X)
        self._setup_sprites(
            TODDLER_PLAYER_RUN1_IMAGE,
            TODDLER_PLAYER_RUN2_IMAGE,
            TODDLER_PLAYER_JUMP_IMAGE,
        )
