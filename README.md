# SWE-Life
A minigame collection built as the final project for CMU 15-112 (Fundamentals of Programming and Computer Science). The game follows a Sofware Engineer attempting to climb the corporate ladder by improving hygiene, grooming, and room cleanliness stats through a series of minigames.

The project grew into a complex, 1300-line system featuring a progression system, an in-game shop with persistent upgrades, cross-stat debuffs, a slingshot minigame, and a vertically scrolling platformer. This project received a 99/100 grade and a feature on CMU's Spring '26 15-112 course website. Built entirely in Python with the cmu_graphics library.


## GAME DESCRIPTION
This is a game where you are a SWE. You are trying to move up the ranks at your company.
However, you've worked so much that your hygiene has taken a huge hit. If you don't
lock in, you won't go anywhere. To upgrade from
bummyAhh to max level swe, you must play minigames. Each minigame corresponds to the
upgrading of either your hygiene, your grooming, or your room. Completion of minigame
will upgrade the relevant stat and give you coins, which you can use to purchase upgrades in
the shop. You can choose which minigame you want to play, but each minigame will take a chunk of your day, 
moving you from morning, to afternoon, to night, back to morning. 
At any point, you can choose to enter into the climb to try to climb the corporate ladder, which will be a 
scrolling platformer with dangers from the other minigames. Be warned though: there are cleanliness-specific debuffs 
that will make the climb impossible at first.

Your hygiene will affect your vision, as low hygiene will result in a stink cloud covering the screen 
(light green rectangle with opacity based on hygiene).
Your grooming will affect your own jumping, as your excess hair might weigh you down. And your room state
will affect the complexity of the map you are in, as well as your speed. 
The climb will be a scrolling vertical platformer, 
in which you have to avoid dandruff, get bubbles, and reach barbershops! See how high you can climb the
corporate ladder.
