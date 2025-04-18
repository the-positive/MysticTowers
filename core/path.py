import pygame
from core.config import *

class Path:
    """Represents the fixed, winding path monsters follow and buildable tile locations."""
    def __init__(self):
        # Define path points in tile coordinates - S-shaped path with multiple turns
        self.path_tiles = [
            # Start at bottom left
            (0, 13), (1, 13), (2, 13), (3, 13), (4, 13), (5, 13),
            # Turn up
            (5, 12), (5, 11), (5, 10), (5, 9),
            # Go right
            (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
            # Turn up again
            (10, 8), (10, 7), (10, 6), (10, 5),
            # Go left
            (9, 5), (8, 5), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5),
            # Up again
            (3, 4), (3, 3),
            # Final stretch to the right
            (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
            (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3), (17, 3), (18, 3)
        ]
        
        # Base position (end of path)
        self.base_pos = (19, 3)
        
        # Convert to pixel coordinates for drawing and movement
        self.points = [(x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
                      for x, y in self.path_tiles]
        
        # Define buildable tiles adjacent to path
        self.buildable_tiles = set()
        self.occupied_tiles = set()
        for x, y in self.path_tiles:
            # Check adjacent tiles
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (new_x, new_y) not in self.path_tiles and \
                       0 <= new_x < GRID_WIDTH and \
                       0 <= new_y < GRID_HEIGHT:
                        self.buildable_tiles.add((new_x, new_y))
    
    def is_buildable_tile(self, x, y):
        """Check if a tile coordinate is buildable and not yet occupied."""
        return (x, y) in self.buildable_tiles and (x, y) not in self.occupied_tiles

    def occupy_tile(self, x, y):
        """Mark a buildable tile as occupied (after tower placed)."""
        self.occupied_tiles.add((x, y))
    
    def get_next_point(self, current_pos):
        """Get the next path point for monster movement."""
        for i, point in enumerate(self.points[:-1]):
            next_point = self.points[i + 1]
            # If monster is between these points, return the next point
            if ((point[0] <= current_pos[0] <= next_point[0] or 
                 point[0] >= current_pos[0] >= next_point[0]) and
                (point[1] <= current_pos[1] <= next_point[1] or
                 point[1] >= current_pos[1] >= next_point[1])):
                return next_point
        return self.points[-1]

    def draw(self, screen):
        # Path visuals are now handled in Game.draw using images
        pass
