from scene_manager import SceneState
from player.baby_player import BabyPlayer
from player.toddler_player import ToddlerPlayer
from settings import BABY_BACKGROUND_NORMAL_IMAGES, BABY_BACKGROUND_TRANSITION_IMAGES


class BabyLevel:
    SCROLL_SPEED: float = 2
    LEVEL_BACKGROUND_IMAGES: int = 2

    @classmethod
    def get_scene_states(cls) -> list[SceneState]:
        states = [
            SceneState(
                name="baby_normal",
                image_paths=BABY_BACKGROUND_NORMAL_IMAGES,
                passes=cls.LEVEL_BACKGROUND_IMAGES,
                speed=cls.SCROLL_SPEED,
                player_class=BabyPlayer,
            ),
        ]
        if BABY_BACKGROUND_TRANSITION_IMAGES:
            # transition for first image only
            states.append(SceneState(
                name="baby_transition_1",
                image_paths=BABY_BACKGROUND_TRANSITION_IMAGES[:1],
                passes=1,
                speed=cls.SCROLL_SPEED,
                player_class=None,
            ))
            # transition for remainding images
            remaining = BABY_BACKGROUND_TRANSITION_IMAGES[1:]
            states.append(SceneState(
                name="baby_transition_2",
                image_paths=remaining,
                passes=len(remaining),
                speed=cls.SCROLL_SPEED,
                player_class=ToddlerPlayer,
            ))
        return states
