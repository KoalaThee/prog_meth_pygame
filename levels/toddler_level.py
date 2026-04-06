from scene_manager import SceneState
from player.toddler_player import ToddlerPlayer
from settings import TODDLER_BACKGROUND_NORMAL_IMAGES, TODDLER_BACKGROUND_TRANSITION_IMAGES


class ToddlerLevel:
    SCROLL_SPEED: float = 3
    LEVEL_BACKGROUND_IMAGES: int = 2

    @classmethod
    def get_scene_states(cls) -> list[SceneState]:
        states = [
            SceneState(
                name="toddler_normal",
                image_paths=TODDLER_BACKGROUND_NORMAL_IMAGES,
                passes=cls.LEVEL_BACKGROUND_IMAGES,
                speed=cls.SCROLL_SPEED,
                player_class=ToddlerPlayer,
            ),
        ]
        if TODDLER_BACKGROUND_TRANSITION_IMAGES:
            states.append(SceneState(
                name="toddler_transition",
                image_paths=TODDLER_BACKGROUND_TRANSITION_IMAGES,
                passes=len(TODDLER_BACKGROUND_TRANSITION_IMAGES),
                speed=cls.SCROLL_SPEED,
                player_class=None,
            ))
        return states
