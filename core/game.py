import pygame
import os
from .config import *
from .path import Path
from .economy import Economy
from entities.tower import TowerManager
from entities.monster import MonsterManager
from .wave import WaveManager
from .boss_warning import BossWarning
from .danger_warning import DangerWarning
from entities.base import Base
from ui.hud import HUD
from ui.button import Button

class Game:
    """Main game controller: manages state, updates, and rendering."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.boss_music_playing = False
        self.restart_game()
    
    def restart_game(self):
        """Reset the game state to start a new game."""
        self.game_speed = 1.0
        self.paused = False
        
        # Core systems
        self.path = Path()
        self.base = Base()
        self.base.set_position(*self.path.base_pos)  # Set base at end of path
        self.economy = Economy()
        self.tower_manager = TowerManager(self.path)
        self.monster_manager = MonsterManager(self.path, self.economy)
        self.wave_manager = WaveManager(self.monster_manager, self.base)
        self.monster_manager.base = self.base  # Set base reference for monster manager
        self.hud = HUD(self)
        
        # Game state
        self.state = 'preparation'  # 'wave', 'gameover', 'victory'
        self.selected_tower = None
        self.selected_tile = None
        self.boss_music_playing = False
        
        # Boss and danger warning overlays
        self.boss_warning = BossWarning()
        self.danger_warning = DangerWarning()
        self._last_wave_in_progress = False
        
        # Game over screen
        self.game_over_font = pygame.font.SysFont('arial', 64)
        self.restart_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 60,
            SCREEN_HEIGHT // 2 + 20,
            120, 40
        )
        self.restart_text = pygame.font.SysFont('arial', 24).render('Restart?', True, (0, 0, 0))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Right click anywhere to deselect tower selection
            if self.selected_tower is not None and event.button == 3:
                self.selected_tower = None
                return
            
            # Handle game over or completion restart
            if self.state in ('gameover', 'completed'):
                if self.restart_button.collidepoint(mouse_pos):
                    # Play button click sound
                    if HUD.button_click_sound is None:
                        import os
                        try:
                            HUD.button_click_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'button_click.wav'))
                        except Exception as e:
                            print(f"Failed to load button_click sound: {e}")
                    if HUD.button_click_sound:
                        HUD.button_click_sound.play()
                    self.restart_game()
                return
            
            # Handle tower menu selection
            if self.hud.tower_menu_open:
                selected = self.hud.get_clicked_tower(mouse_pos)
                if selected:
                    if self.economy.coins >= TOWER_COSTS[selected]:
                        self.selected_tower = selected
                    return
            
            # Handle tower placement
            tile_x = mouse_pos[0] // TILE_SIZE
            tile_y = mouse_pos[1] // TILE_SIZE
            
            if self.selected_tower and self.path.is_buildable_tile(tile_x, tile_y):
                success = self.tower_manager.place_tower(
                    self.selected_tower,
                    (tile_x * TILE_SIZE + TILE_SIZE//2, tile_y * TILE_SIZE + TILE_SIZE//2),
                    self.economy
                )
                if success:
                    self.path.occupy_tile(tile_x, tile_y)
                    self.selected_tower = None
                    self.hud.tower_menu_open = False  # Close menu after placement
            
            self.selected_tile = (tile_x, tile_y)
        
        # Handle UI events
        if self.state != 'gameover':
            self.hud.handle_event(event)
            self.tower_manager.handle_event(event, self.economy)
        
        # Handle escape key to cancel tower placement
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.selected_tower = None

    def update(self):
        if self.paused:
            return
            
        dt = self.clock.tick(60) / 1000.0 * self.game_speed
        
        # Track boss/danger warning triggers
        wave_num = self.wave_manager.wave_number
        wave_in_prog = self.wave_manager.wave_in_progress
        # Trigger boss warning and danger sound when boss wave starts
        if wave_num == 21 and wave_in_prog and not self._last_wave_in_progress:
            self.boss_warning.trigger()
            # Play danger sound(s) as on every 5th wave
            try:
                from entities.monster import MonsterManager
                if not hasattr(MonsterManager, 'danger_sound'):
                    import os
                    danger_path = os.path.join('assets', 'sounds', 'UI', 'danger.wav')
                    if os.path.exists(danger_path):
                        MonsterManager.danger_sound = pygame.mixer.Sound(danger_path)
                if hasattr(MonsterManager, 'danger_sound') and MonsterManager.danger_sound:
                    MonsterManager.danger_sound.play()
                    # If there is a chained danger sound, set up the timer as in main.py
                    MonsterManager._danger_sounds_left = 1
                    pygame.time.set_timer(pygame.USEREVENT + 50, int(MonsterManager.danger_sound.get_length() * 1000), loops=1)
            except Exception as e:
                print(f"Failed to play danger sound on boss wave: {e}")
            # Play boss music
            boss_music_path = os.path.join('assets', 'sounds', 'ambient', 'boss_music.mp3')
            if os.path.exists(boss_music_path):
                try:
                    pygame.mixer.music.load(boss_music_path)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.boss_music_playing = True
                except Exception as e:
                    print(f"Failed to play boss music: {e}")
        # Trigger danger warning at the start of every 5th wave (except boss)
        if wave_num % 5 == 0 and wave_num < 21 and wave_in_prog and not self._last_wave_in_progress:
            self.danger_warning.trigger()
        self._last_wave_in_progress = wave_in_prog
        self.boss_warning.update(dt)
        self.danger_warning.update(dt)

        # Stop boss music on game over or completed
        if self.boss_music_playing and self.state in ('gameover', 'completed'):
            pygame.mixer.music.stop()
            self.boss_music_playing = False

        if self.state == 'playing':
            self.monster_manager.update(dt)
            self.tower_manager.update(dt, self.monster_manager, self.economy)
            self.wave_manager.update(dt)
            
            # Check victory/defeat conditions
            if self.base.hp <= 0:
                # Play game over sound if not already played
                if not hasattr(self, '_game_over_sound_played') or not self._game_over_sound_played:
                    try:
                        import os
                        if not hasattr(self, '_game_over_sound'):
                            sound_path = os.path.join('assets', 'sounds', 'UI', 'game over.wav')
                            if os.path.exists(sound_path):
                                self._game_over_sound = pygame.mixer.Sound(sound_path)
                            else:
                                self._game_over_sound = None
                        if self._game_over_sound:
                            self._game_over_sound.play()
                        self._game_over_sound_played = True
                    except Exception as e:
                        print(f"Failed to play game over sound: {e}")
                self.state = 'gameover'
            elif self.wave_manager.wave_number > TOTAL_WAVES:
                boss_types = {'boss_gnome', 'boss_fast_spider', 'boss_big_spider'}
                bosses_alive = any(m.type in boss_types for m in self.monster_manager.monsters)
                if not bosses_alive:
                    self.state = 'completed'

    def draw(self):
        # --- Load world images (if not already loaded) ---
        if not hasattr(self, 'world_images'):
            self.world_images = {}
            for name in ['grass', 'path_stone', 'tower_placement_foundation', 'rock1', 'rock2', 'tree', 'dirt1', 'dirt2', 'hole']:
                img = pygame.image.load(os.path.join('assets', 'world', f'{name}.png')).convert_alpha()
                self.world_images[name] = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
        grass_img = self.world_images['grass']
        path_img = self.world_images['path_stone']
        slot_img = self.world_images['tower_placement_foundation']
        rock_imgs = [self.world_images['rock1'], self.world_images['rock2']]
        tree_img = self.world_images['tree']
        dirt_imgs = [self.world_images['dirt1'], self.world_images['dirt2']]
        hole_img = self.world_images['hole']

        # Generate scene interest map once
        if not hasattr(self, 'scene_interest_map'):
            import random
            random.seed(42)  # Consistent visuals per run
            self.scene_interest_map = {}
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if (x, y) in self.path.path_tiles or (x, y) in self.path.buildable_tiles:
                        continue
                    r = random.random()
                    if r < 0.06:
                        import random
                        rock_choice = random.choice(['rock1', 'rock2'])
                        self.scene_interest_map[(x, y)] = rock_choice
                    elif r < 0.12:
                        self.scene_interest_map[(x, y)] = 'tree'
                    elif r < 0.18:
                        import random
                        dirt_choice = random.choice(['dirt1', 'dirt2'])
                        self.scene_interest_map[(x, y)] = dirt_choice
                    # else: no detail

        # --- Draw background (grass) ---
        # Cache rock/tree scales and rock rotations for consistency
        if not hasattr(self, 'rock_scales') or not hasattr(self, 'rock_rotations') or not hasattr(self, 'tree_scales'):
            import random
            self.rock_scales = {}
            self.rock_rotations = {}
            self.tree_scales = {}
            for pos, detail in getattr(self, 'scene_interest_map', {}).items():
                if detail in ('rock1', 'rock2'):
                    self.rock_scales[pos] = random.uniform(0.4, 0.8)
                    self.rock_rotations[pos] = random.uniform(0, 360)
                elif detail == 'tree':
                    self.tree_scales[pos] = random.uniform(0.7, 1.15)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.screen.blit(grass_img, (x * TILE_SIZE, y * TILE_SIZE))
                # Draw scene interest (details) on grass
                if hasattr(self, 'scene_interest_map') and (x, y) in self.scene_interest_map:
                    detail = self.scene_interest_map[(x, y)]
                    if detail in ('rock1', 'rock2'):
                        rock_img = self.world_images[detail]
                        scale = self.rock_scales.get((x, y), 0.6)
                        scaled_size = int(TILE_SIZE * scale)
                        scaled_rock = pygame.transform.smoothscale(rock_img, (scaled_size, scaled_size))
                        angle = self.rock_rotations.get((x, y), 0)
                        rotated_rock = pygame.transform.rotate(scaled_rock, angle)
                        # Center the rotated rock in the tile
                        rect = rotated_rock.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
                        self.screen.blit(rotated_rock, rect.topleft)
                    elif detail == 'tree':
                        scale = self.tree_scales.get((x, y), 1.0)
                        scaled_size = int(TILE_SIZE * scale)
                        scaled_tree = pygame.transform.smoothscale(tree_img, (scaled_size, scaled_size))
                        # Center the scaled tree in the tile
                        rect = scaled_tree.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
                        self.screen.blit(scaled_tree, rect.topleft)
                    elif detail in ('dirt1', 'dirt2'):
                        dirt_img = self.world_images[detail]
                        self.screen.blit(dirt_img, (x * TILE_SIZE, y * TILE_SIZE))

        # --- Draw path (path_stone) ---
        for x, y in self.path.path_tiles:
            self.screen.blit(path_img, (x * TILE_SIZE, y * TILE_SIZE))

        # Draw monster spawn hole above the path for visibility
        spawn_tile = self.path.path_tiles[0]
        HOLE_SCALE = 1.5
        hole_size = int(TILE_SIZE * HOLE_SCALE)
        scaled_hole = pygame.transform.smoothscale(hole_img, (hole_size, hole_size))
        # Center the hole on the spawn tile
        hole_offset = (TILE_SIZE - hole_size) // 2
        self.screen.blit(scaled_hole, (spawn_tile[0] * TILE_SIZE + hole_offset, spawn_tile[1] * TILE_SIZE + hole_offset))

        # --- Draw buildable slots (tower_placement_foundation) ---
        for x, y in self.path.buildable_tiles:
            self.screen.blit(slot_img, (x * TILE_SIZE, y * TILE_SIZE))

        # Draw game elements
        self.path.draw(self.screen)
        # Draw towers and their hit particles
        self.tower_manager.draw(self.screen, monster_particles=self.monster_manager.particles)
        # Draw monsters (without drawing particles again)
        self.monster_manager.draw(self.screen)
        # Draw HUD
        self.hud.draw(self.screen)
        # Draw danger warning overlay (draw before boss warning so boss takes priority)
        self.danger_warning.draw(self.screen)
        # Draw boss warning overlay
        self.boss_warning.draw(self.screen)
        self.base.draw(self.screen)
        
        # Draw game over screen
        if self.state == 'gameover':
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over text
            text_surface = self.game_over_font.render(GAME_OVER_TEXT, True, COLORS['game_over_text'])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text_surface, text_rect)
            
            # Draw restart button
            button_color = COLORS['restart_button_hover'] if self.restart_button.collidepoint(pygame.mouse.get_pos()) else COLORS['restart_button']
            pygame.draw.rect(self.screen, button_color, self.restart_button)
            pygame.draw.rect(self.screen, (0, 0, 0), self.restart_button, 2)
            
            # Draw restart text
            text_rect = self.restart_text.get_rect(center=self.restart_button.center)
            self.screen.blit(self.restart_text, text_rect)
        elif self.state == 'completed':
            # Completion screen overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))
            # Draw congrats text (split into two lines)
            congrats_text1 = 'Congratulations!'
            congrats_text2 = 'You survived'
            text_surface1 = self.game_over_font.render(congrats_text1, True, COLORS['game_over_text'])
            text_surface2 = self.game_over_font.render(congrats_text2, True, COLORS['game_over_text'])
            text_rect1 = text_surface1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            text_rect2 = text_surface2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(text_surface1, text_rect1)
            self.screen.blit(text_surface2, text_rect2)
            # Draw restart button
            button_color = COLORS['restart_button_hover'] if self.restart_button.collidepoint(pygame.mouse.get_pos()) else COLORS['restart_button']
            pygame.draw.rect(self.screen, button_color, self.restart_button)
            pygame.draw.rect(self.screen, (0, 0, 0), self.restart_button, 2)
            # Draw restart text
            text_rect = self.restart_text.get_rect(center=self.restart_button.center)
            self.screen.blit(self.restart_text, text_rect)
        
        # Draw tower preview if placing
        if self.selected_tower:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (255, 255, 255, 128),
                            mouse_pos, TOWER_STATS[self.selected_tower]['range'] * TILE_SIZE, 1)
            

