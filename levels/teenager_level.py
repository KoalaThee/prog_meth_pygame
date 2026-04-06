from scene_manager import SceneState
from player.teenager_player import TeenagerPlayer
from player.young_adult_player import YoungAdultPlayer
from settings import TEENAGER_BACKGROUND_NORMAL_IMAGES, TEENAGER_BACKGROUND_TRANSITION_IMAGES


class TeenagerLevel:
    SCROLL_SPEED: float = 4
    LEVEL_BACKGROUND_IMAGES: int = 3

    @classmethod
    def get_scene_states(cls) -> list[SceneState]:
        states = [
            SceneState(
                name="teenager_normal",
                image_paths=TEENAGER_BACKGROUND_NORMAL_IMAGES,
                passes=cls.LEVEL_BACKGROUND_IMAGES,
                speed=cls.SCROLL_SPEED,
                player_class=TeenagerPlayer,
            ),
        ]
        if TEENAGER_BACKGROUND_TRANSITION_IMAGES:
            # transition for first image only
            states.append(SceneState(
                name="teenager_transition_1",
                image_paths=TEENAGER_BACKGROUND_TRANSITION_IMAGES[:1],
                passes=1,
                speed=cls.SCROLL_SPEED,
                player_class=None,
            ))
            # transition for remainding images
            remaining = TEENAGER_BACKGROUND_TRANSITION_IMAGES[1:]
            states.append(SceneState(
                name="teenager_transition_2",
                image_paths=remaining,
                passes=len(remaining),
                speed=cls.SCROLL_SPEED,
                player_class=YoungAdultPlayer,
            ))
        return states
