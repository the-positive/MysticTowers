import pygame
from core.config import *
import math
import os

class Projectile:
    """Represents a tower's projectile."""
    def __init__(self, start_pos, target, speed, color, size, proj_type=None):
        self.pos = list(start_pos)
        self.target = target  # Store reference to target monster
        self.speed = speed
        self.color = color
        self.size = size
        self.proj_type = proj_type  # Used for image lookup
        
    def update(self, dt):
        # Get current target position
        target_pos = self.target.pos
        
        # Calculate direction to target
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 5:  # Hit target
            return True
            
        # Move towards target
        self.pos[0] += (dx/dist) * self.speed * dt
        self.pos[1] += (dy/dist) * self.speed * dt
        return False
        
    def draw(self, screen):
        img = Tower.projectile_images.get(self.proj_type) if Tower.projectile_images else None
        x, y = int(self.pos[0]), int(self.pos[1])
        if img:
            rect = img.get_rect(center=(x, y))
            screen.blit(img, rect)
        elif self.size == 'small':
            pygame.draw.circle(screen, self.color, (x, y), 3)
        elif self.size == 'medium':
            points = [
                (x, y - 4),
                (x - 4, y + 4),
                (x + 4, y + 4)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:  # large
            pygame.draw.rect(screen, self.color,
                           (x - 5, y - 5, 10, 10))

class Tower:
    """Base class for all towers."""
    tower_images = None
    projectile_images = None

    @staticmethod
    def load_images():
        if Tower.tower_images is None:
            Tower.tower_images = {}
            for ttype in ['cannon', 'water', 'fire']:
                img_path = os.path.join('assets', 'towers', f'{ttype}_tower.png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    # Revert tower size to 1.5x TILE_SIZE
                    TOWER_IMG_SIZE = int(TILE_SIZE * 1.5)
                    Tower.tower_images[ttype] = pygame.transform.smoothscale(img, (TOWER_IMG_SIZE, TOWER_IMG_SIZE))
                else:
                    Tower.tower_images[ttype] = None
        if Tower.projectile_images is None:
            Tower.projectile_images = {}
            for ttype in ['cannon', 'water', 'fire']:
                img_path = os.path.join('assets', 'projectiles', f'{ttype}_projectile.png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    Tower.projectile_images[ttype] = pygame.transform.smoothscale(img, (16, 16))
                else:
                    Tower.projectile_images[ttype] = None

    def __init__(self, tower_type, pos):
        Tower.load_images()
        self.tower_type = tower_type
        self.pos = pos
        self.level = 1
        self.selected = False
        
        # Load stats from config
        stats = TOWER_STATS[tower_type]
        self.damage = stats['damage']
        self.range = stats['range'] * TILE_SIZE  # Convert from tiles to pixels
        self.attack_speed = 1.0 / stats['attack_speed']  # Convert to seconds between attacks
        # Only fire towers have splash; water and cannon are single-target
        if tower_type == 'fire':
            self.splash_radius = stats.get('splash_radius', 0) * TILE_SIZE
        else:
            self.splash_radius = 0
        self.upgrades = stats['upgrades']
        
        # Attack cooldown and projectiles
        self.attack_timer = 0
        self.target = None
        self.projectiles = []
        
        # Set projectile properties based on tower type
        self.projectile_type = tower_type  # For image lookup
        if tower_type == 'cannon':
            self.projectile_color = (150, 75, 0)
            self.projectile_size = 'small'
            self.projectile_speed = 400
        elif tower_type == 'water':
            self.projectile_color = (0, 100, 255)
            self.projectile_size = 'medium'
            self.projectile_speed = 300
        else:
            self.projectile_color = (100, 100, 100)
            self.projectile_size = 'large'
            self.projectile_speed = 200

    def can_attack(self, dt):
        self.attack_timer -= dt
        return self.attack_timer <= 0

    def find_target(self, monsters):
        closest_dist = float('inf')
        closest_monster = None
        
        for monster in monsters:
            if not monster.is_alive():
                continue
            dx = monster.pos[0] - self.pos[0]
            dy = monster.pos[1] - self.pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= self.range and dist < closest_dist:
                closest_dist = dist
                closest_monster = monster
        
        return closest_monster

    def attack(self, monster, monster_manager):
        # Create new projectile
        self.projectiles.append(Projectile(
            self.pos,
            monster,  # Pass monster reference instead of just position
            self.projectile_speed,
            self.projectile_color,
            self.projectile_size,
            self.projectile_type
        ))
        self.attack_timer = self.attack_speed

    def update(self, dt, monster_manager, economy):
        # Update projectiles
        for proj in self.projectiles[:]:  # Copy list to safely remove while iterating
            proj.update(dt)
            if proj.update(dt):  # Returns True when hit target
                if self.splash_radius > 0:
                    # Area damage
                    for monster in monster_manager.monsters:
                        dx = monster.pos[0] - proj.pos[0]
                        dy = monster.pos[1] - proj.pos[1]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist <= self.splash_radius:
                            # Emit monster color particles
                            monster_manager.particles.emit((monster.pos[0], monster.pos[1] - monster.size), monster.color, count=8)
                            # Emit projectile image particles
                            proj_img = Tower.projectile_images.get(self.projectile_type) if Tower.projectile_images else None
                            monster_manager.particles.emit((monster.pos[0], monster.pos[1] - monster.size), self.projectile_color, count=6, image=proj_img)
                            monster.take_damage(self.damage, monster_manager.particles)
                            # Water tower: apply slow effect
                            if self.tower_type == 'water':
                                monster.apply_slow(0.9, 3.0)
                else:
                    # Single target damage
                    # Emit monster color particles
                    monster_manager.particles.emit((proj.target.pos[0], proj.target.pos[1] - proj.target.size), proj.target.color, count=8)
                    # Emit projectile image particles
                    proj_img = Tower.projectile_images.get(self.projectile_type) if Tower.projectile_images else None
                    monster_manager.particles.emit((proj.target.pos[0], proj.target.pos[1] - proj.target.size), self.projectile_color, count=6, image=proj_img)
                    proj.target.take_damage(self.damage, monster_manager.particles)
                    # Water tower: apply slow effect
                    if self.tower_type == 'water':
                        proj.target.apply_slow(0.9, 3.0)
                
                self.projectiles.remove(proj)
        
        # Find and attack target
        if self.can_attack(dt):
            target = self.find_target(monster_manager.monsters)
            if target:
                self.attack(target, monster_manager)
                self.target = target
            else:
                self.target = None

    def draw(self, screen, monster_particles=None):
        # Draw tower image if available, else fallback to color circle
        img = Tower.tower_images.get(self.tower_type) if Tower.tower_images else None
        if img:
            rect = img.get_rect(center=self.pos)
            screen.blit(img, rect)
        else:
            color = {
                'cannon': (150, 100, 50),
                'water': (50, 50, 200),
                'fire': (100, 100, 100)
            }[self.tower_type]
            pygame.draw.circle(screen, color, self.pos, TILE_SIZE // 2)
        # Draw range circle if this tower is selected
        if self.selected:
            # Draw a fully opaque, 2px wide circle matching the targeting logic
            # (Targeting uses distance from self.pos to monster.pos <= self.range)
            pygame.draw.circle(screen, (255, 255, 255), self.pos, int(self.range), 2)
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(screen)
        # Draw hit particles created by tower hits (if provided)
        if monster_particles:
            monster_particles.draw(screen)


class TowerManager:
    """Manages all towers on the map."""
    def __init__(self, path):
        self.towers = []
        self.path = path
        self.selected_tower = None

    def place_tower(self, tower_type, pos, economy):
        """Try to place a tower at the given position."""
        cost = TOWER_COSTS[tower_type]
        
        # Check if we can afford it
        if not economy.spend(cost):
            return False
            
        # Create and add the tower
        tower = Tower(tower_type, pos)
        self.towers.append(tower)
        return True

    def handle_event(self, event, economy):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            clicked_any = False
            for tower in self.towers:
                dx = mouse_pos[0] - tower.pos[0]
                dy = mouse_pos[1] - tower.pos[1]
                if dx*dx + dy*dy <= (TILE_SIZE//2) * (TILE_SIZE//2):
                    # Select this tower, deselect others
                    for t in self.towers:
                        t.selected = False
                    tower.selected = True
                    self.selected_tower = tower
                    clicked_any = True
                    break
            if not clicked_any:
                # Deselect all towers if clicked empty space
                for t in self.towers:
                    t.selected = False
                self.selected_tower = None

    def update(self, dt, monster_manager, economy):
        for tower in self.towers:
            tower.update(dt, monster_manager, economy)

    def draw(self, screen, monster_particles=None):
        # Draw towers sorted by Y (so lower towers are drawn in front)
        for tower in sorted(self.towers, key=lambda t: t.pos[1]):
            tower.draw(screen, monster_particles=monster_particles)
