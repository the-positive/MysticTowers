import pygame
import random
import math

class Particle:
    def __init__(self, pos, color, image=None):
        self.x, self.y = pos
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(40, 120)
        self.dx = speed * random.uniform(0.5, 1.0) * math.cos(angle)
        self.dy = speed * random.uniform(0.5, 1.0) * math.sin(angle)
        self.life = random.uniform(0.15, 0.3)  # seconds
        self.color = color
        self.radius = random.randint(2, 4)
        self.image = image
        self.rotation = random.uniform(0, 360) if image else 0
        self.scale = random.uniform(0.4, 0.7) if image else 1

    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.life -= dt
        self.radius = max(0, self.radius - 8 * dt)

    def draw(self, screen):
        if self.life > 0 and (self.radius > 0 or self.image):
            if self.image:
                # Draw small, rotated, faded version of the projectile image
                img = pygame.transform.rotozoom(self.image, self.rotation, self.scale)
                img.set_alpha(max(0, int(255 * (self.life / 0.3))))
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(img, rect)
            else:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def emit(self, pos, color, count=8, image=None):
        for _ in range(count):
            self.particles.append(Particle(pos, color, image=image))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0 and p.radius > 0]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
