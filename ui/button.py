import pygame
from core.config import COLORS

class Button:
    """A circular button that can be clicked and hovered."""
    def __init__(self, x, y, size, color, hover_color, text, font):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.font = font
        self.hovered = False
        self.pressed = False  # New: pressed state
    
    def draw(self, screen):
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.hovered = dx*dx + dy*dy <= self.size*self.size

        # Pressed visual: offset and darken
        draw_x = self.x
        draw_y = self.y
        if self.pressed:
            draw_y += 4
        # Draw 3D shadow
        shadow_offset = 4
        shadow_color = (50, 50, 50)
        pygame.draw.circle(screen, shadow_color, (draw_x, draw_y + shadow_offset), self.size)
        # Draw button base (with gradient)
        color = self.hover_color if self.hovered else self.color
        if self.pressed:
            color = tuple(max(0, int(c * 0.7)) for c in color)  # Darken
        for i in range(self.size, 0, -1):
            blend = i / self.size
            grad_color = (
                int(color[0] * blend + 220 * (1-blend)),
                int(color[1] * blend + 220 * (1-blend)),
                int(color[2] * blend + 220 * (1-blend))
            )
            pygame.draw.circle(screen, grad_color, (draw_x, draw_y), i)
        # Draw border
        pygame.draw.circle(screen, (0, 0, 0), (draw_x, draw_y), self.size, 2)
        # Draw tower silhouette if this is the tower selection button
        if self.text == '⚔':
            # Draw a simple tower: base, body, battlements
            tower_w = self.size // 2
            tower_h = int(self.size * 0.95)
            base_h = tower_h // 4
            body_h = tower_h - base_h
            tower_x = self.x - tower_w // 2
            tower_y = self.y - tower_h // 2
            # Body
            pygame.draw.rect(screen, (0,0,0), (tower_x, tower_y + base_h//2, tower_w, body_h), border_radius=4)
            # Base
            pygame.draw.rect(screen, (0,0,0), (tower_x, tower_y + body_h + base_h//2, tower_w, base_h), border_radius=5)
            # Battlements
            battlement_w = tower_w // 5
            battlement_h = base_h // 2
            # Center battlements over the tower body
            total_battlements_w = 3 * battlement_w + 2 * 2  # 2px spacing between
            battlements_start_x = tower_x + (tower_w - total_battlements_w) // 2
            battlements_y = tower_y + base_h//2 - battlement_h
            for i in range(3):
                bx = battlements_start_x + i * (battlement_w + 2)
                pygame.draw.rect(screen, (0,0,0), (bx, battlements_y, battlement_w, battlement_h))
        else:
            # Draw text
            text_surface = self.font.render(self.text, True, COLORS['text'])
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
