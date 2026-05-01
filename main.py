import pygame
import os
import sys
from core.game import Game
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

# Global variables for mouse coordinate transformation
global_scale = 1.0
global_x_offset = 0
global_y_offset = 0

# Override pygame.mouse.get_pos to return transformed coordinates
original_get_pos = pygame.mouse.get_pos
def transformed_get_pos():
    real_pos = original_get_pos()
    # Transform from screen to game coordinates
    mx = int((real_pos[0] - global_x_offset) / global_scale)
    my = int((real_pos[1] - global_y_offset) / global_scale)
    # Clamp to valid range
    mx = max(0, min(SCREEN_WIDTH-1, mx))
    my = max(0, min(SCREEN_HEIGHT-1, my))
    return (mx, my)

# Replace the original function with our transformed version
pygame.mouse.get_pos = transformed_get_pos

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    pygame.init()
    # Get the display size
    info = pygame.display.Info()
    display_width, display_height = info.current_w, info.current_h
    # Create a borderless fullscreen window
    window = pygame.display.set_mode((display_width, display_height), pygame.NOFRAME)
    pygame.display.set_caption("Mystic Towers")
    clock = pygame.time.Clock()
    # Create the fixed-resolution game surface
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(game_surface)
    running = True

    # Hide the system cursor
    pygame.mouse.set_visible(False)
    # Load and scale the custom cursor image using script-relative path
    cursor_img_path = os.path.join(BASE_DIR, 'assets', 'UI', 'cursor_image.png')
    cursor_img = pygame.image.load(cursor_img_path).convert_alpha()
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))
    cursor_offset = (16, 16)  # Center the cursor image

    while running:
        # Calculate scale and offsets for aspect ratio
        scale = min(display_width / SCREEN_WIDTH, display_height / SCREEN_HEIGHT)
        scaled_width = int(SCREEN_WIDTH * scale)
        scaled_height = int(SCREEN_HEIGHT * scale)
        x_offset = (display_width - scaled_width) // 2
        y_offset = (display_height - scaled_height) // 2
        
        # Update global transformation variables
        global global_scale, global_x_offset, global_y_offset
        global_scale = scale
        global_x_offset = x_offset
        global_y_offset = y_offset
        
        for event in pygame.event.get():
            # Transform mouse event positions to game surface coordinates
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                # Adjust event.pos if present
                if hasattr(event, 'pos'):
                    mx, my = event.pos
                    # Convert to game surface coordinates
                    mx = int((mx - x_offset) / scale)
                    my = int((my - y_offset) / scale)
                    # Clamp to surface bounds
                    mx = max(0, min(SCREEN_WIDTH-1, mx))
                    my = max(0, min(SCREEN_HEIGHT-1, my))
                    # Replace event with new pos
                    event = pygame.event.Event(event.type, {**event.dict, 'pos': (mx, my)})
            if event.type == pygame.QUIT:
                running = False
            # Danger sound chaining for every 5th wave
            if event.type == pygame.USEREVENT + 50:
                try:
                    from entities.monster import MonsterManager
                    if hasattr(MonsterManager, 'danger_sound') and getattr(MonsterManager, '_danger_sounds_left', 0) > 0:
                        MonsterManager.danger_sound.play()
                        MonsterManager._danger_sounds_left -= 1
                        if MonsterManager._danger_sounds_left > 0:
                            pygame.time.set_timer(pygame.USEREVENT + 50, int(MonsterManager.danger_sound.get_length() * 1000), loops=1)
                except Exception as e:
                    print(f"Error playing chained danger sound: {e}")
            game.handle_event(event)
        game.update()
        game_surface.fill((0, 0, 0))  # Clear the game surface every frame
        game.draw()
        # Draw the custom cursor last so it appears above everything
        # Use the original mouse position for drawing the cursor in screen space
        mouse_x, mouse_y = original_get_pos()
        # Scale the game surface
        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))
        window.fill((0, 0, 0))  # Letterbox
        window.blit(scaled_surface, (x_offset, y_offset))
        # Adjust mouse position to game surface coordinates for cursor
        game_mouse_x = int((mouse_x - x_offset) / scale)
        game_mouse_y = int((mouse_y - y_offset) / scale)
        # Only draw cursor if inside the scaled area
        if 0 <= game_mouse_x < SCREEN_WIDTH and 0 <= game_mouse_y < SCREEN_HEIGHT:
            # Draw cursor in screen space (not game space)
            cursor_rect = cursor_img.get_rect(center=(mouse_x - cursor_offset[0], mouse_y - cursor_offset[1]))
            window.blit(cursor_img, cursor_rect)
        
        # Add ESC key to quit for convenience
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
