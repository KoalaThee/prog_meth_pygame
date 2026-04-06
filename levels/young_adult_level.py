from scene_manager import SceneState
from player.young_adult_player import YoungAdultPlayer
from settings import (
    YOUNG_ADULT_BACKGROUND_NORMAL_IMAGES,
    YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES,
    ENDING_IMAGE,
)


class YoungAdultLevel:
    SCROLL_SPEED: float = 5
    LEVEL_BACKGROUND_IMAGES: int = 3

    @classmethod
    def get_scene_states(cls) -> list[SceneState]:
        states = [
            SceneState(
                name="young_adult_normal",
                image_paths=YOUNG_ADULT_BACKGROUND_NORMAL_IMAGES,
                passes=cls.LEVEL_BACKGROUND_IMAGES,
                speed=cls.SCROLL_SPEED,
                player_class=YoungAdultPlayer,
            ),
        ]
        if YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES:
            # transition for first image only
            states.append(SceneState(
                name="young_adult_transition_1",
                image_paths=YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES[:1],
                passes=1,
                speed=cls.SCROLL_SPEED,
                player_class=None,
            ))
            # transition for remainding images
            remaining = YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES[1:]
            states.append(SceneState(
                name="young_adult_transition_2",
                image_paths=remaining,
                passes=len(remaining),
                speed=cls.SCROLL_SPEED,
                player_class=None,
            ))

        # Ending screen — freezes on screen the moment the transition exits
        states.append(SceneState(
            name="ending",
            image_paths=[ENDING_IMAGE],
            passes=1,
            speed=cls.SCROLL_SPEED,
            player_class=None,
            terminal=True,
        ))
        return states
