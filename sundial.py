"""
name.py
This file xxx
Developed on Python x.x.x
Nathaniel Schmucker
"""

import pygame
import random

# --- Global constants ---
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
LT_BROWN = (236, 162,  77)
DK_BROWN = (180,  83,  38)

SCREEN_WIDTH  = 750
SCREEN_HEIGHT = 550

# --- Classes ---
class Button:
    """ This class is for all the buttons on the screen """

    def __init__(self, rect, text):
        
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        self.rect = pygame.Rect(rect)
        self.text = font.render(text, True, WHITE)
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.function = function

    def draw(self, surf):
        surf.blit(self.rect, self.rect)
        surf.blit(self.text, self.text_rect)

# --- Main loop ---
# Initialize Pygame and set up the window
pygame.init()

size = [SCREEN_WIDTH, SCREEN_HEIGHT]

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Create an instance of the Game class
game = Game(stack_size=4, burnt=True, font=font)

# Main loop
while True:

    # Process events (keystrokes, mouse clicks, etc)
    done = game.process_events()

    # Update object positions
    game.run_logic()

    # Draw the current frame
    game.display_frame(screen, font)

    # Limit to 60 frames per second
    clock.tick(60)
