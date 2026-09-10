# 9/8/2026 Repo Initialization & Game Prototype
Ok, so basically this is my first time seriously handling graphics and utilizing a game development library (Pygame)
This is practically a first for everything, so here's what I did for the first version of the game.

- I used very basic graphics, I wanted to focus more on the actual function of the game:
  - I Implemented a white box that bounds a red square player. This was done with the .clamp_ip() method which bounds a rectangle within another rectangle.
  - Made the player movable with WASD and arrow keys. This was done by using collecting/checking certian events tracked by Pygame.
  - Made a bullet enemy that calculates the vector and angle of the plyers position once and moves towards until it hits the player or goes out of bounds
  - I tracked player health and score and health depletes when bullets hit until health equals zero, then a pop up for the score and game over text appears.
  - I could spend too much time trying to explain all of my code, but that will certainly take too long so I'm just trying to list the important details.
 
