from player.base_player import BasePlayer
from settings import (
    PLAYER_START_X,
    YOUNG_ADULT_PLAYER_RUN1_IMAGE,
    YOUNG_ADULT_PLAYER_RUN2_IMAGE,
    YOUNG_ADULT_PLAYER_JUMP_IMAGE,
)


class YoungAdultPlayer(BasePlayer):
    DISPLAY_WIDTH = 250
    DISPLAY_HEIGHT = 250
    JUMP_STRENGTH = -13.5
    SECOND_JUMP_STRENGTH = -13.5

    def __init__(self):
        super().__init__(PLAYER_START_X)
        self._setup_sprites(
            YOUNG_ADULT_PLAYER_RUN1_IMAGE,
            YOUNG_ADULT_PLAYER_RUN2_IMAGE,
            YOUNG_ADULT_PLAYER_JUMP_IMAGE,
        )
