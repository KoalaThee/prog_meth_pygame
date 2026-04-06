from player.base_player import BasePlayer
from settings import (
    PLAYER_START_X,
    BABY_PLAYER_RUN1_IMAGE,
    BABY_PLAYER_RUN2_IMAGE,
    BABY_PLAYER_JUMP_IMAGE,
)


class BabyPlayer(BasePlayer):
    DISPLAY_WIDTH = 100
    DISPLAY_HEIGHT = 100
    JUMP_STRENGTH = -13.5
    SECOND_JUMP_STRENGTH = -13.5

    def __init__(self):
        super().__init__(PLAYER_START_X)
        self._setup_sprites(
            BABY_PLAYER_RUN1_IMAGE,
            BABY_PLAYER_RUN2_IMAGE,
            BABY_PLAYER_JUMP_IMAGE,
        )
