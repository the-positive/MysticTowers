import pygame
import math
from core.config import *
from entities.particle import ParticleManager
from entities.sprite_utils import load_sprite_sheet
import os

death_sounds_loaded = False
def play_monster_death_sound(monster_type):
    """Play the correct death sound for the monster type."""
    global death_sounds_loaded, MONSTER_DEATH_SOUND, GNOME_DEATH_SOUND, SPIDER_FAST_DEATH_SOUND, SPIDER_BIG_DEATH_SOUND
    if not death_sounds_loaded:
        MONSTER_DEATH_SOUND = None
        GNOME_DEATH_SOUND = None
        SPIDER_FAST_DEATH_SOUND = None
        SPIDER_BIG_DEATH_SOUND = None
        try:
            path = os.path.join('assets', 'sounds', 'monsters', 'death.wav')
            if os.path.exists(path):
                MONSTER_DEATH_SOUND = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed to load death.wav: {e}")
        try:
            path = os.path.join('assets', 'sounds', 'monsters', 'gnome_death.wav')
            if os.path.exists(path):
                GNOME_DEATH_SOUND = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed to load gnome_death.wav: {e}")
        try:
            path = os.path.join('assets', 'sounds', 'monsters', 'spider_fast_death.wav')
            if os.path.exists(path):
                SPIDER_FAST_DEATH_SOUND = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed to load spider_fast_death.wav: {e}")
        try:
            path = os.path.join('assets', 'sounds', 'monsters', 'spider_big_death.wav')
            if os.path.exists(path):
                SPIDER_BIG_DEATH_SOUND = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed to load spider_big_death.wav: {e}")
        death_sounds_loaded = True
    # Always play generic death
    if MONSTER_DEATH_SOUND:
        MONSTER_DEATH_SOUND.play()
    # Play specific sound for monster type (bosses use the same sound as their model)
    if monster_type in ('gnome', 'boss_gnome') and GNOME_DEATH_SOUND:
        GNOME_DEATH_SOUND.play()
    elif monster_type in ('fast_spider', 'boss_fast_spider') and SPIDER_FAST_DEATH_SOUND:
        SPIDER_FAST_DEATH_SOUND.play()
    elif monster_type in ('big_spider', 'boss_big_spider') and SPIDER_BIG_DEATH_SOUND:
        SPIDER_BIG_DEATH_SOUND.play()

class Monster:
    """Base class for all monsters."""
    def __init__(self, monster_type, path, base, economy, position_offset=0):
        # ... existing code ...
        self.slow_timer = 0
        self.slow_factor = 1.0
        self._original_speed = None

        self.type = monster_type
        self.path = path
        self.base = base
        self.economy = economy
        
        # Boss monster variants: use boss stats, but normal monster sprites
        boss_map = {
            'boss_gnome': 'gnome',
            'boss_fast_spider': 'fast_spider',
            'boss_big_spider': 'big_spider',
        }
        self.is_boss = monster_type in boss_map
        if self.is_boss:
            stats = MONSTER_STATS['boss']
            sprite_type = boss_map[monster_type]
        else:
            stats = MONSTER_STATS[monster_type]
            sprite_type = monster_type
        self.max_hp = stats['health']
        self.hp = self.max_hp
        self.speed = stats['speed']  # pixels per second
        self.size = stats['size']
        self.color = stats['color']
        self.reward = stats['reward']
        
        # Position and movement
        self.path_index = 0
        # Offset the starting position along the path if requested
        if position_offset == 0:
            self.pos = list(self.path.points[0])
        else:
            # Move position_offset pixels along the path direction
            if len(self.path.points) > 1:
                x0, y0 = self.path.points[0]
                x1, y1 = self.path.points[1]
                dx = x1 - x0
                dy = y1 - y0
                dist = math.hypot(dx, dy)
                if dist > 0:
                    ox = dx / dist * position_offset
                    oy = dy / dist * position_offset
                    self.pos = [x0 + ox, y0 + oy]
                    # --- Fix: If the monster is closer to point 1 than point 0, increment path_index ---
                    d0 = math.hypot(self.pos[0] - x0, self.pos[1] - y0)
                    d1 = math.hypot(self.pos[0] - x1, self.pos[1] - y1)
                    if d1 < d0:
                        self.path_index = 1
                else:
                    self.pos = list(self.path.points[0])
            else:
                self.pos = list(self.path.points[0])

        # Sprite animation for gnome
        def load_and_scale(path):
            img = pygame.image.load(path).convert_alpha()
            scale = 2.0 if self.is_boss else 1.0
            scaled_size = int(self.size*2*scale)
            return pygame.transform.smoothscale(img, (scaled_size, scaled_size))

        if sprite_type == 'gnome':
            self.anim_frames = {
                'up':   [load_and_scale(f'assets/monsters/gnome/gnome_up{i}.png') for i in range(1, 4)],
                'left': [load_and_scale(f'assets/monsters/gnome/gnome_left{i}.png') for i in range(1, 4)],
                'right':[load_and_scale(f'assets/monsters/gnome/gnome_right{i}.png') for i in range(1, 4)],
                'down': [load_and_scale(f'assets/monsters/gnome/gnome_up1.png')]*3
            }
            # Death image: gnome_right3 rotated -90 degrees (laying on back)
            base_img = pygame.image.load('assets/monsters/gnome/gnome_right3.png').convert_alpha()
            scale = 2.0 if self.is_boss else 1.0
            scaled_size = int(self.size*2*scale)
            base_img = pygame.transform.smoothscale(base_img, (scaled_size, scaled_size))
            self.dead_image = pygame.transform.rotate(base_img, -90)
            self.anim_direction = 'down'
            self.anim_frame = 0
            self.anim_timer = 0
            self.anim_delay = 0.15
            self._last_pos = self.pos[:]
            self.dead_timer = None
            self.dead_duration = 2.0  # seconds
        elif sprite_type == 'fast_spider':
            self.anim_frames = {
                'up':   [load_and_scale(f'assets/monsters/spider_fast/up{i}.png') for i in range(1, 4)],
                'left': [load_and_scale(f'assets/monsters/spider_fast/left{i}.png') for i in range(1, 4)],
                'right':[load_and_scale(f'assets/monsters/spider_fast/right{i}.png') for i in range(1, 4)],
                'down': [load_and_scale(f'assets/monsters/spider_fast/up1.png')]*3
            }
            # Death image for fast spider (boss and normal)
            img = pygame.image.load('assets/monsters/spider_fast/dead.png').convert_alpha()
            scale = 2.0 if self.is_boss else 1.0
            scaled_size = int(self.size*2*scale)
            self.dead_image = pygame.transform.smoothscale(img, (scaled_size, scaled_size))
            self.anim_direction = 'down'
            self.anim_frame = 0
            self.anim_timer = 0
            self.anim_delay = 0.10
            self._last_pos = self.pos[:]
            self.dead_timer = None
            self.dead_duration = 2.0  # seconds
        elif sprite_type == 'big_spider':
            self.anim_frames = {
                'up':   [load_and_scale(f'assets/monsters/spider_big/up{i}.png') for i in range(1, 4)],
                'left': [load_and_scale(f'assets/monsters/spider_big/left{i}.png') for i in range(1, 4)],
                'right':[load_and_scale(f'assets/monsters/spider_big/right{i}.png') for i in range(1, 4)],
                'down': [load_and_scale(f'assets/monsters/spider_big/up1.png')]*3
            }
            # Death image for big spider (boss and normal)
            img = pygame.image.load('assets/monsters/spider_big/dead.png').convert_alpha()
            scale = 2.0 if self.is_boss else 1.0
            scaled_size = int(self.size*2*scale)
            self.dead_image = pygame.transform.smoothscale(img, (scaled_size, scaled_size))
            self.anim_direction = 'down'
            self.anim_frame = 0
            self.anim_timer = 0
            self.anim_delay = 0.20
            self._last_pos = self.pos[:]
            self.dead_timer = None
            self.dead_duration = 2.0  # seconds
        
    def update(self, dt):
        # Handle slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                # Restore speed
                if self._original_speed is not None:
                    self.speed = self._original_speed
                self.slow_factor = 1.0
                self._original_speed = None
        if not self.is_alive():
            # For spiders and gnomes, start/update dead timer
            if self.type in ('fast_spider', 'big_spider', 'gnome', 'boss_gnome'):
                if self.dead_timer is None:
                    self.dead_timer = 0
                else:
                    self.dead_timer += dt
            return

        # Animation direction and frame update for all monsters with animation
        if hasattr(self, 'anim_frames'):
            dx = self.pos[0] - self._last_pos[0]
            dy = self.pos[1] - self._last_pos[1]
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.anim_direction = 'right'
                elif dx < 0:
                    self.anim_direction = 'left'
            else:
                if dy < 0:
                    self.anim_direction = 'up'
                elif dy > 0:
                    self.anim_direction = 'down'
            self._last_pos = self.pos[:]
            # Animate
            self.anim_timer += dt
            if self.anim_timer >= self.anim_delay:
                self.anim_frame = (self.anim_frame + 1) % 3
                self.anim_timer = 0

        # Get current target point
        if self.path_index >= len(self.path.points):
            # Reached end of path
            if self.is_boss:
                # Boss instantly defeats the player
                self.base.hp = 0
            else:
                self.base.take_damage(10)
            self.hp = 0
            return
        target = self.path.points[self.path_index]
        # Calculate direction to target
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 2:  # Close enough to target
            self.path_index += 1
        else:
            # Move towards target
            move_dist = self.speed * dt * self.slow_factor
            self.pos[0] += (dx/dist) * move_dist
            self.pos[1] += (dy/dist) * move_dist
    
    def take_damage(self, amount, particle_manager=None):
        """Take damage and return True if killed. Optionally emit a hit particle effect."""
        self.hp -= amount
        if particle_manager:
            particle_manager.emit((self.pos[0], self.pos[1] - self.size), self.color, count=8)
        if not self.is_alive():
            # Play death sounds
            play_monster_death_sound(self.type)
            # Give reward to player when monster dies
            self.economy.earn(self.reward)
            return True
        return False
        
    def is_alive(self):
        return self.hp > 0
        
    def apply_slow(self, factor, duration):
        # Only apply if stronger or not already slowed
        if self.slow_timer <= 0 or factor < self.slow_factor:
            if self._original_speed is None:
                self._original_speed = self.speed
            self.slow_factor = factor
            self.speed = self._original_speed * factor
            self.slow_timer = duration

    def draw(self, screen):
        # --- Dead monster image logic (for any monster with dead_image and dead_timer) ---
        if hasattr(self, 'dead_image') and self.dead_timer is not None and self.dead_timer < self.dead_duration:
            sprite_rect = self.dead_image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            # Fade out dead image over dead_duration
            fade_alpha = int(255 * (1 - self.dead_timer / self.dead_duration))
            dead_img = self.dead_image.copy()
            dead_img.set_alpha(max(0, min(255, fade_alpha)))
            screen.blit(dead_img, sprite_rect)
            return
        if not self.is_alive():
            return
        # Draw health bar
        hp_width = 30
        hp_height = 4
        hp_x = self.pos[0] - hp_width//2
        if self.is_boss:
            # Offset further up for boss (scaled sprite)
            hp_y = self.pos[1] - self.size * 2 - 16
        else:
            hp_y = self.pos[1] - self.size - 8
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0),
                        (hp_x, hp_y, hp_width, hp_height))
        # Foreground (green)
        green_width = int(hp_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0, 255, 0),
                        (hp_x, hp_y, green_width, hp_height))
        # Draw monster shape based on type
        # Draw the correct directional frame for all monsters (bosses use scaled-up sprites)
        sprite = self.anim_frames[self.anim_direction][self.anim_frame]
        sprite_rect = sprite.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        # Visual indicator for slow: blue overlay
        if self.slow_timer > 0:
            temp_sprite = sprite.copy()
            blue_overlay = pygame.Surface(temp_sprite.get_size(), pygame.SRCALPHA)
            blue_overlay.fill((80, 180, 255, 70))
            temp_sprite.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(temp_sprite, sprite_rect)
        else:
            screen.blit(sprite, sprite_rect)


class MonsterManager:
    """Manages all monsters in the game."""
    def __init__(self, path, economy):
        self.monsters = []
        self.path = path
        self.economy = economy
        self.base = None  # Will be set when starting wave
        self.spawn_timer = 0
        self.wave_in_progress = False
        self.monsters_to_spawn = []
        self.particles = ParticleManager()
    
    def start_wave(self, wave_number, base):
        self.base = base  # Store base reference
        self.current_wave = wave_number  # Store for dynamic rewards
        # Set up monsters and mark wave as in progress
        import math
        # Every 5th wave is a challenge wave: spawn 1.5x monsters
        challenge_wave = (wave_number % 5 == 0 and wave_number <= 20)
        if wave_number <= 5:
            gnome_count = WAVE_CONFIGS['early']['gnome']['count'](wave_number)
            if challenge_wave:
                gnome_count = math.ceil(gnome_count * 1.5)
            # For wave 5, add a group of 5 fast spiders
            if wave_number == 5:
                self.monsters_to_spawn = ['gnome'] * gnome_count + ['fast_spider'] * 5
            else:
                self.monsters_to_spawn = ['gnome'] * gnome_count
        elif wave_number <= 15:
            num_gnomes = WAVE_CONFIGS['mid']['gnome']['count'](wave_number)
            num_wolves = WAVE_CONFIGS['mid']['fast_spider']['count'](wave_number)
            num_big_spiders = WAVE_CONFIGS['mid']['big_spider']['count'](wave_number)
            if challenge_wave:
                num_gnomes = math.ceil(num_gnomes * 1.5)
                num_wolves = math.ceil(num_wolves * 1.5)
                num_big_spiders = math.ceil(num_big_spiders * 1.5)
            # Mix in extra fast spiders on every even wave (not boss)
            extra_spiders = 0
            if wave_number % 2 == 0:
                extra_spiders = 2 + wave_number // 6
            self.monsters_to_spawn = (
                ['gnome'] * num_gnomes +
                ['fast_spider'] * (num_wolves + extra_spiders) +
                ['big_spider'] * num_big_spiders
            )
        elif wave_number <= 20:
            num_gnomes = WAVE_CONFIGS['late']['gnome']['count'](wave_number)
            num_wolves = WAVE_CONFIGS['late']['fast_spider']['count'](wave_number)
            num_big_spiders = WAVE_CONFIGS['late']['big_spider']['count'](wave_number)
            if challenge_wave:
                num_gnomes = math.ceil(num_gnomes * 1.5)
                num_wolves = math.ceil(num_wolves * 1.5)
                num_big_spiders = math.ceil(num_big_spiders * 1.5)
            # Mix in extra fast spiders on every even wave (not boss)
            extra_spiders = 0
            if wave_number % 2 == 0:
                extra_spiders = 2 + wave_number // 6
            self.monsters_to_spawn = (
                ['gnome'] * num_gnomes +
                ['fast_spider'] * (num_wolves + extra_spiders) +
                ['big_spider'] * num_big_spiders
            )
        else:
            # Final Boss Wave: Giant version of each monster
            self.monsters_to_spawn = ['boss_gnome', 'boss_fast_spider', 'boss_big_spider']
        self.wave_in_progress = True
        self.spawn_timer = 0
        # Play wave start sound for normal waves, warning/danger for every 5th wave
        import os
        if wave_number % 5 == 0:
            # Load warning/danger sounds if needed
            if not hasattr(MonsterManager, 'warning_sound'):
                try:
                    MonsterManager.warning_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'warning.wav'))
                except Exception as e:
                    print(f"Failed to load warning sound: {e}")
            if not hasattr(MonsterManager, 'danger_sound'):
                try:
                    MonsterManager.danger_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'danger.wav'))
                except Exception as e:
                    print(f"Failed to load danger sound: {e}")
            # Play warning and danger at the same time, then chain a second danger after the first danger finishes
            if getattr(MonsterManager, 'warning_sound', None):
                MonsterManager.warning_sound.play()
            if getattr(MonsterManager, 'danger_sound', None):
                MonsterManager.danger_sound.play()
                # Schedule only the second danger sound to play after the first finishes
                pygame.time.set_timer(pygame.USEREVENT + 50, int(MonsterManager.danger_sound.get_length() * 1000), loops=1)
                MonsterManager._danger_sounds_left = 1
        else:
            if not hasattr(MonsterManager, 'wave_start_sound'):
                try:
                    MonsterManager.wave_start_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'wave_start.wav'))
                except Exception as e:
                    print(f"Failed to load wave_start sound: {e}")
            if getattr(MonsterManager, 'wave_start_sound', None):
                MonsterManager.wave_start_sound.play()

        # Every 5th wave is a challenge wave: spawn 1.5x monsters
        challenge_wave = (wave_number % 5 == 0 and wave_number <= 20)
        if wave_number <= 5:
            gnome_count = WAVE_CONFIGS['early']['gnome']['count'](wave_number)
            if challenge_wave:
                gnome_count = math.ceil(gnome_count * 1.5)
            # For wave 5, add a group of 5 fast spiders
            if wave_number == 5:
                self.monsters_to_spawn = ['gnome'] * gnome_count + ['fast_spider'] * 5
            else:
                self.monsters_to_spawn = ['gnome'] * gnome_count
        elif wave_number <= 15:
            num_gnomes = WAVE_CONFIGS['mid']['gnome']['count'](wave_number)
            num_wolves = WAVE_CONFIGS['mid']['fast_spider']['count'](wave_number)
            num_big_spiders = WAVE_CONFIGS['mid']['big_spider']['count'](wave_number)
            if challenge_wave:
                num_gnomes = math.ceil(num_gnomes * 1.5)
                num_wolves = math.ceil(num_wolves * 1.5)
                num_big_spiders = math.ceil(num_big_spiders * 1.5)
            # Mix in extra fast spiders on every even wave (not boss)
            extra_spiders = 0
            if wave_number % 2 == 0:
                extra_spiders = 2 + wave_number // 6
            self.monsters_to_spawn = (
                ['gnome'] * num_gnomes +
                ['fast_spider'] * (num_wolves + extra_spiders) +
                ['big_spider'] * num_big_spiders
            )
        elif wave_number <= 20:
            num_gnomes = WAVE_CONFIGS['late']['gnome']['count'](wave_number)
            num_wolves = WAVE_CONFIGS['late']['fast_spider']['count'](wave_number)
            num_big_spiders = WAVE_CONFIGS['late']['big_spider']['count'](wave_number)
            if challenge_wave:
                num_gnomes = math.ceil(num_gnomes * 1.5)
                num_wolves = math.ceil(num_wolves * 1.5)
                num_big_spiders = math.ceil(num_big_spiders * 1.5)
            # Mix in extra fast spiders on every even wave (not boss)
            extra_spiders = 0
            if wave_number % 2 == 0:
                extra_spiders = 2 + wave_number // 6
            self.monsters_to_spawn = (
                ['gnome'] * num_gnomes +
                ['fast_spider'] * (num_wolves + extra_spiders) +
                ['big_spider'] * num_big_spiders
            )
        else:
            # Final Boss Wave: Giant version of each monster
            self.monsters_to_spawn = ['boss_gnome', 'boss_fast_spider', 'boss_big_spider']
        self.wave_in_progress = True
        self.spawn_timer = 0
    
    def update(self, dt):
        # Update existing monsters
        for monster in self.monsters:
            monster.update(dt)
        # Only remove monsters after dead image duration if they have a dead_image (fade-out)
        new_monsters = []
        for m in self.monsters:
            if hasattr(m, 'dead_image'):
                if m.is_alive() or (m.dead_timer is not None and m.dead_timer < m.dead_duration):
                    new_monsters.append(m)
            else:
                if m.is_alive():
                    new_monsters.append(m)
        self.monsters = new_monsters
        self.particles.update(dt)
        
        # Spawn new monsters
        if self.wave_in_progress and self.monsters_to_spawn:
            self.spawn_timer += dt
            boss_types = {'boss_gnome', 'boss_fast_spider', 'boss_big_spider'}
            # Use config for gnome spawn delay (early/mid/late)
            if self.current_wave <= 5:
                spawn_delay = WAVE_CONFIGS['early']['gnome']['delay']
            elif self.current_wave <= 15:
                spawn_delay = WAVE_CONFIGS['mid']['gnome']['delay']
            elif self.current_wave <= 20:
                spawn_delay = WAVE_CONFIGS['late']['gnome']['delay']
            else:
                spawn_delay = 5.0 if self.monsters_to_spawn[0] in boss_types else 1.0
            if self.spawn_timer >= spawn_delay:
                monster_type = self.monsters_to_spawn.pop(0)
                # Dynamic gnome reward: use config for early waves
                if monster_type == 'gnome':
                    if self.current_wave <= 5:
                        reward = WAVE_CONFIGS['early']['gnome']['reward'](self.current_wave)
                    elif self.current_wave <= 15:
                        reward = 8 + (self.current_wave // 4)  # 8-11 gold
                    else:
                        reward = 10 + (self.current_wave // 5)  # 10-14 gold
                    monster = Monster(monster_type, self.path, self.base, self.economy)
                    monster.reward = reward
                    self.monsters.append(monster)
                else:
                    self.monsters.append(Monster(monster_type, self.path, self.base, self.economy))
                self.spawn_timer = 0  # Reset timer

                # Starting on wave 5, 60% chance to immediately spawn next monster (not on boss wave)
                import random
                if self.current_wave >= 5 and self.current_wave != 21 and self.monsters_to_spawn:
                    if random.random() < 0.6:
                        monster_type = self.monsters_to_spawn.pop(0)
                        if monster_type == 'gnome':
                            if self.current_wave <= 5:
                                reward = WAVE_CONFIGS['early']['gnome']['reward'](self.current_wave)
                            elif self.current_wave <= 15:
                                reward = 8 + (self.current_wave // 4)  # 8-11 gold
                            else:
                                reward = 10 + (self.current_wave // 5)  # 10-14 gold
                            monster = Monster(monster_type, self.path, self.base, self.economy, position_offset=18)
                            monster.reward = reward
                            self.monsters.append(monster)
                        else:
                            self.monsters.append(Monster(monster_type, self.path, self.base, self.economy, position_offset=18))
                        last_spawn_offset = 0


        if not self.monsters_to_spawn and not self.monsters:
            self.wave_in_progress = False

    def draw(self, screen):
        for monster in self.monsters:
            monster.draw(screen)
        # Particle drawing is now handled by the tower manager for projectile effects
        # self.particles.draw(screen)
