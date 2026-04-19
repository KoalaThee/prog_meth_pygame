from scene_manager import SceneState
from players import BabyPlayer, ToddlerPlayer, TeenagerPlayer, YoungAdultPlayer
from config import (
    BABY_BACKGROUND_NORMAL_IMAGES, BABY_BACKGROUND_TRANSITION_IMAGES,
    TODDLER_BACKGROUND_NORMAL_IMAGES, TODDLER_BACKGROUND_TRANSITION_IMAGES,
    TEENAGER_BACKGROUND_NORMAL_IMAGES, TEENAGER_BACKGROUND_TRANSITION_IMAGES,
    YOUNG_ADULT_BACKGROUND_NORMAL_IMAGES, YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES,
    ENDING_IMAGE,
)


def get_level_states(name, speed, normal_images, normal_passes, normal_player,
                     transition_images, next_player=None, terminal_image=None,
                     stage=None,
                     item_stage_after_player_swap=None):
    if stage is None:
        stage = name

    states = [
        SceneState(
            name=f"{name}_normal",
            image_paths=normal_images,
            passes=normal_passes,
            speed=speed,
            player_class=normal_player,
            stage=stage,
        )
    ]

    if transition_images:
        states.append(SceneState(
            name=f"{name}_transition_1",
            image_paths=transition_images[:1],
            passes=1,
            speed=speed,
            player_class=None,
            stage=stage,
        ))
        remaining = transition_images[1:]
        if remaining:
            t2_item_stage = (
                item_stage_after_player_swap
                if item_stage_after_player_swap is not None
                else stage
            )
            states.append(SceneState(
                name=f"{name}_transition_2",
                image_paths=remaining,
                passes=len(remaining),
                speed=speed,
                player_class=next_player,
                stage=t2_item_stage,
            ))

    if terminal_image:
        states.append(SceneState(
            name="ending",
            image_paths=[terminal_image],
            passes=1,
            speed=speed,
            player_class=None,
            terminal=True,
            stage=None,
        ))

    return states


def all_level_states():
    states = []
    states += get_level_states(
        "baby",
        speed=4,
        normal_images=BABY_BACKGROUND_NORMAL_IMAGES,
        normal_passes=4,
        normal_player=BabyPlayer,
        transition_images=BABY_BACKGROUND_TRANSITION_IMAGES,
        next_player=ToddlerPlayer,
        item_stage_after_player_swap="toddler",
    )
    states += get_level_states(
        "toddler",
        speed=4.5,
        normal_images=TODDLER_BACKGROUND_NORMAL_IMAGES,
        normal_passes=4,
        normal_player=ToddlerPlayer,
        transition_images=TODDLER_BACKGROUND_TRANSITION_IMAGES,
        next_player=TeenagerPlayer,
        item_stage_after_player_swap="teenager",
    )
    states += get_level_states(
        "teenager",
        speed=5,
        normal_images=TEENAGER_BACKGROUND_NORMAL_IMAGES,
        normal_passes=6,
        normal_player=TeenagerPlayer,
        transition_images=TEENAGER_BACKGROUND_TRANSITION_IMAGES,
        next_player=YoungAdultPlayer,
        item_stage_after_player_swap="young_adult",
    )
    states += get_level_states(
        "young_adult",
        speed=5.5,
        normal_images=YOUNG_ADULT_BACKGROUND_NORMAL_IMAGES,
        normal_passes=6,
        normal_player=YoungAdultPlayer,
        transition_images=YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES,
        terminal_image=ENDING_IMAGE,
    )
    return states
