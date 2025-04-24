import pygame

class ImageButton:
    """A circular button that displays an image, with hover/pressed effects."""
    def __init__(self, x, y, size, image_path, hover_image_path=None, pressed_offset=4):
        self.x = x
        self.y = y
        self.size = size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (size*2, size*2))
        self.hover_image = None
        if hover_image_path:
            self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
            self.hover_image = pygame.transform.smoothscale(self.hover_image, (size*2, size*2))
        self.hovered = False
        self.pressed = False
        self.pressed_offset = pressed_offset

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.hovered = dx*dx + dy*dy <= self.size*self.size
        draw_x = self.x
        draw_y = self.y
        if self.pressed:
            draw_y += self.pressed_offset
        # Draw shadow
        shadow_offset = 4
        shadow_color = (50, 50, 50)
        pygame.draw.circle(screen, shadow_color, (draw_x, draw_y + shadow_offset), self.size)
        # Draw image
        img = self.hover_image if self.hovered and self.hover_image else self.image
        rect = img.get_rect(center=(draw_x, draw_y))
        screen.blit(img, rect)
