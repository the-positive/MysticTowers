import pygame
import os
from core.config import *

class Base:
    """The player's base to defend."""
    def __init__(self):
        self.hp = BASE_HP
        self.max_hp = BASE_HP
        # Position will be set by the Game class using path.base_pos
        self.tile_pos = None
        self.pos = None
        
    def set_position(self, tile_x, tile_y):
        """Set the base position in tile coordinates."""
        self.tile_pos = (tile_x, tile_y)
        self.pos = (tile_x * TILE_SIZE, tile_y * TILE_SIZE)

    def take_damage(self, amount):
        """Take damage and return True if base is destroyed."""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0

    def draw(self, screen):
        if self.pos is None:
            return
        # Load and scale player_base image if not already
        if not hasattr(self, 'base_img'):
            img = pygame.image.load(os.path.join('assets', 'world', 'player_base.png')).convert_alpha()
            # Make base 2x the size of a tile
            BASE_IMG_SIZE = int(TILE_SIZE * 2)
            self.base_img = pygame.transform.smoothscale(img, (BASE_IMG_SIZE, BASE_IMG_SIZE))
            self.base_img_size = BASE_IMG_SIZE
        # Center the larger image on the base tile
        x = self.pos[0] + TILE_SIZE // 2 - self.base_img_size // 2
        y = self.pos[1] + TILE_SIZE // 2 - self.base_img_size // 2
        screen.blit(self.base_img, (x, y))
        
        # Draw HP bar
        bar_width = TILE_SIZE
        bar_height = 5
        bar_pos = (self.pos[0], self.pos[1] - 10)
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0),
                        (*bar_pos, bar_width, bar_height))
        
        # Foreground (green)
        health_width = int(bar_width * (self.hp / self.max_hp))
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0),
                            (*bar_pos, health_width, bar_height))
