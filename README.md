# **Life is a Game | Pygame Project**

**Life is a Game** is an **endless runner** style of game built on a Linear State Machine where the character automatically runs forward through 4 life stages (Baby, Primary, High School, University).
<br>
<p align="center"><img src="https://github.com/KoalaThee/prog_meth_pygame/blob/1b31c52eabe2132d1e43f2d434e49ec6345c4020/assets/images/start_screen.png" width="700"/></p>
<p align="center"><i><b>Figure 1:</b> App Start Screen </i></p><br>

# **Information**
Gameplay involves controlling a Player Object to navigate obstacles and collect Items (Food, Study, Art/Hobby, Exercise), which influence five key stats: health, happiness, social, intelligence, and arts. A crucial feature is the branching path logic that occurs between the High School and University stages, where the player's stats (intelligence vs. arts) determine their educational track ("Science" or "Arts") or trigger a "pause state" popup for manual selection. Throughout the game, obstacles with stage-specific behaviors cause stat reductions upon collision, while the end of the game transitions to a final screen that utilizes trigonometry to display a "Wheel of Life" 5-point radar chart and a derived "Career Title" based on the accumulated stats and life path.
<br>
<p align="center"><img src="https://github.com/KoalaThee/prog_meth_pygame/blob/84b142c8944ab54ef40b223c22545f7f8a54a793/assets/resources/baby_screen_example.png" width="700"/></p>
<p align="center"><i><b>Figure 2:</b> Gameplay - Baby Stage </i></p><br>
<br>
<p align="center"><img src="https://github.com/KoalaThee/prog_meth_pygame/blob/84b142c8944ab54ef40b223c22545f7f8a54a793/assets/resources/toddler_screen_example.png" width="700"/></p>
<p align="center"><i><b>Figure 3:</b> Gameplay - Toddler Stage </i></p><br>

# **Program Architecture - Class Diagram: Specification**
- Game is the single entry point
- UI screens are grouped by role: input screens (Start, Pause, Branch) and overlay views (GameOver, Stats, Ending). Game owns one of each and activates them based on the current GameMode.
- The gameplay logic is in the SceneManager, which builds the scrolling sceens based on the SceenState where it owns the player throughout the run
- The ItemManager and ObsticleManger are responsible for spawning and updating the items and obstacles
- Each type of Player and Item is an instance of their baseclass while Obsticles subclass inherit the superclass and they have different functions for their movement
<br>
<p align="center"><img src="https://github.com/KoalaThee/prog_meth_pygame/blob/84b142c8944ab54ef40b223c22545f7f8a54a793/assets/resources/program_architecture.png" width="1400"/></p>
<p align="center"><i><b>Figure 4:</b> Program Architecture </i></p><br>
