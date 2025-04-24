import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from core.font_manager import get_font

class WaveSelectMenu:
    def __init__(self, font, total_waves=21):
        # Use our own font instead of the passed font
        self.font = get_font(22)
        self.total_waves = total_waves
        self.visible = False
        self.selected_wave = None
        self.button_rects = []
        self.menu_width = 220
        self.menu_height = 320
        self.button_size = 40
        self.button_margin = 10
        self.menu_rect = pygame.Rect(
            SCREEN_WIDTH - self.menu_width - 40, 80, self.menu_width, self.menu_height)
        self.just_opened = False

    def open(self):
        self.visible = True
        self.selected_wave = None
        self.just_opened = True

    def close(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return None
        if self.just_opened:
            # Ignore the first click after opening
            self.just_opened = False
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for idx, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_wave = idx + 1
                    self.visible = False
                    return self.selected_wave
            # Click outside menu closes it
            if not self.menu_rect.collidepoint(mouse_pos):
                self.visible = False
        return None

    def draw(self, screen):
        if not self.visible:
            return
        # Draw menu background
        pygame.draw.rect(screen, (30, 30, 30), self.menu_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 180, 180), self.menu_rect, 3, border_radius=12)
        # Draw title
        title = self.font.render("Select Wave", True, (255,255,255))
        screen.blit(title, (self.menu_rect.x + 30, self.menu_rect.y + 16))
        # Draw wave buttons
        self.button_rects = []
        cols = 3
        for i in range(self.total_waves):
            row = i // cols
            col = i % cols
            x = self.menu_rect.x + 20 + col * (self.button_size + self.button_margin)
            y = self.menu_rect.y + 60 + row * (self.button_size + self.button_margin)
            rect = pygame.Rect(x, y, self.button_size, self.button_size)
            self.button_rects.append(rect)
            color = (70, 120, 255) if not self.selected_wave == i+1 else (255, 200, 80)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            wave_text = self.font.render(str(i+1), True, (0,0,0))
            text_rect = wave_text.get_rect(center=rect.center)
            screen.blit(wave_text, text_rect)
