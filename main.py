import pygame
from core.game import Game
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mystic Towers")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True

    # Hide the system cursor
    pygame.mouse.set_visible(False)
    # Load and scale the custom cursor image
    cursor_img = pygame.image.load('assets/UI/cursor_image.png').convert_alpha()
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))
    cursor_offset = (16, 16)  # Center the cursor image

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        game.update()
        screen.fill((0, 0, 0))  # Clear the screen every frame
        game.draw()
        # Draw the custom cursor last so it appears above everything
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(cursor_img, (mouse_x - cursor_offset[0], mouse_y - cursor_offset[1]))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
