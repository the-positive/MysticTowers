import pygame
import os

class CoinAnimation:
    def __init__(self, size=32, frame_duration=0.13):
        self.size = size
        self.frame_duration = frame_duration
        self.frames = []
        self.current_frame = 0
        self.time_accum = 0
        # Load all 8 coin frames
        for i in range(1, 9):
            img = pygame.image.load(os.path.join('assets', 'ui', f'coin{i}.png')).convert_alpha()
            img = pygame.transform.smoothscale(img, (self.size, self.size))
            self.frames.append(img)

    def update(self, dt):
        self.time_accum += dt
        if self.time_accum >= self.frame_duration:
            self.time_accum -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen, x, y):
        screen.blit(self.frames[self.current_frame], (x, y))
