# settings.py

WINDOW_WIDTH = 720
WINDOW_HEIGHT = 405
FPS = 60
WINDOW_TITLE = "Life is a Game"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ground
GROUND_Y = 375

# Player start position, fixed Y coordinate
PLAYER_START_X = 110

# Physics
GRAVITY = 0.75

# Animation
RUN_ANIMATION_TICK_RATE = 8

# --- Baby ---
BABY_PLAYER_RUN1_IMAGE = "assets/images/baby_player_run1.png"
BABY_PLAYER_RUN2_IMAGE = "assets/images/baby_player_run2.png"
BABY_PLAYER_JUMP_IMAGE = "assets/images/baby_player_jump.png"
BABY_BACKGROUND_NORMAL_IMAGES = [
    "assets/images/baby_background_normal1.png",
    "assets/images/baby_background_normal2.png",
]
BABY_BACKGROUND_TRANSITION_IMAGES = [
    "assets/images/baby_background_transition1.png",
    "assets/images/baby_background_transition2.png",
    "assets/images/baby_background_transition3.png",
]

# --- Toddler ---
# toddler_player_run1 does not exist; reuse run2 for both frames
TODDLER_PLAYER_RUN1_IMAGE = "assets/images/toddler_player_run1.png"
TODDLER_PLAYER_RUN2_IMAGE = "assets/images/toddler_player_run2.png"
TODDLER_PLAYER_JUMP_IMAGE = "assets/images/toddler_player_jump.png"
TODDLER_BACKGROUND_NORMAL_IMAGES = [
    "assets/images/toddler_background_normal1.png",
    "assets/images/toddler_background_normal2.png",
]
TODDLER_BACKGROUND_TRANSITION_IMAGES = []  # no transition art for this stage

# --- Teenager ---
TEENAGER_PLAYER_RUN1_IMAGE = "assets/images/teenager_player_run1.png"
TEENAGER_PLAYER_RUN2_IMAGE = "assets/images/teenager_player_run2.png"
TEENAGER_PLAYER_JUMP_IMAGE = "assets/images/teenager_player_jump.png"
TEENAGER_BACKGROUND_NORMAL_IMAGES = [
    "assets/images/teenager_background_normal1.png",
    "assets/images/teenager_background_normal2.png",
    "assets/images/teenager_background_normal3.png",
]
TEENAGER_BACKGROUND_TRANSITION_IMAGES = [
    "assets/images/teenager_background_transition1.png",
    "assets/images/teenager_background_transition2.png",
]

# --- Young Adult ---
YOUNG_ADULT_PLAYER_RUN1_IMAGE = "assets/images/young_adult_player_run1.png"
YOUNG_ADULT_PLAYER_RUN2_IMAGE = "assets/images/young_adult_player_run2.png"
YOUNG_ADULT_PLAYER_JUMP_IMAGE = "assets/images/young_adult_player_jump.png"
YOUNG_ADULT_BACKGROUND_NORMAL_IMAGES = [
    "assets/images/young_adult_background_normal1.png",
    "assets/images/young_adult_background_normal2.png",
    "assets/images/young_adult_background_normal3.png",
]
YOUNG_ADULT_BACKGROUND_TRANSITION_IMAGES = [
    "assets/images/young_adult_background_transition.png",
]
ENDING_IMAGE = "assets/images/ending_screen.png"
