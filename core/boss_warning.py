import pygame
from core.font_manager import get_font

class BossWarning:
    def __init__(self, duration=2.0):
        self.duration = duration
        self.timer = 0
        self.active = False
        self.flash_interval = 0.2
        self.flash_timer = 0
        self.visible = True
        self.font = get_font(54)

    def trigger(self):
        self.active = True
        self.timer = 0
        self.flash_timer = 0
        self.visible = True

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        self.flash_timer += dt
        if self.flash_timer >= self.flash_interval:
            self.visible = not self.visible
            self.flash_timer = 0
        if self.timer >= self.duration:
            self.active = False

    def draw(self, screen):
        if self.active and self.visible:
            text = "Warning! Boss Wave"
            text_surface = self.font.render(text, True, (255, 40, 40))
            # Semi-transparent background for readability
            overlay = pygame.Surface((screen.get_width(), 100), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            y = screen.get_height() // 5
            screen.blit(overlay, (0, y-20))
            text_rect = text_surface.get_rect(center=(screen.get_width()//2, y+30))
            screen.blit(text_surface, text_rect)
