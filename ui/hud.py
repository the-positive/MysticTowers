import pygame
from core.config import *
from .button import Button
from .wave_select_menu import WaveSelectMenu

class HUD:
    """Heads-up display for coins, HP, wave, and controls."""
    button_click_sound = None
    towerselection_click_sound = None
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('arial', 28)
        self.small_font = pygame.font.SysFont('arial', 16)
        
        # Create buttons
        button_y = SCREEN_HEIGHT - BUTTON_MARGIN - BUTTON_SIZE
        # Load button click sound if not already loaded
        import os
        if HUD.button_click_sound is None:
            try:
                HUD.button_click_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'button_click.wav'))
            except Exception as e:
                print(f"Failed to load button_click sound: {e}")
        # Load towerselection click sound if not already loaded
        if HUD.towerselection_click_sound is None:
            try:
                HUD.towerselection_click_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'UI', 'towerselection_click.wav'))
            except Exception as e:
                print(f"Failed to load towerselection_click sound: {e}")
        self.start_wave_button = Button(
            SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_SIZE,
            button_y,
            BUTTON_SIZE,
            COLORS['start_wave'],
            COLORS['start_wave_hover'],
            '►',
            self.font
        )
        
        self.tower_menu_button = Button(
            SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_SIZE * 4,
            button_y,
            BUTTON_SIZE,
            COLORS['tower_menu'],
            COLORS['tower_menu_hover'],
            '⚔',
            self.font
        )
        
        self.tower_menu_open = False

        # Wave select font (for dev buttons)
        self.wave_select_font = pygame.font.SysFont('arial', 18, bold=True)

        # Gold button (for dev)
        # Wave select button (for dev)
        self.wave_select_button = Button(
            SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_SIZE,
            button_y - BUTTON_SIZE - 24,  # 24px above the main buttons for more separation
            BUTTON_SIZE // 2,
            (70, 120, 255),
            (120, 170, 255),
            'W',
            self.wave_select_font
        )
        # Gold button: just above and lined up with the W button
        gold_button_x = self.wave_select_button.x
        # Ensure a clear gap: gold button height + BUTTON_SPACING + 8px between gold and W button
        gold_button_y = self.wave_select_button.y - (BUTTON_SIZE // 2) - BUTTON_SPACING - (BUTTON_SIZE // 2) - 8
        self.gold_button = Button(
            gold_button_x,
            gold_button_y,
            BUTTON_SIZE // 2,
            (255, 215, 0),  # gold color
            (255, 235, 80),  # lighter gold on hover
            '$',
            self.wave_select_font
        )
        self.wave_select_menu = WaveSelectMenu(self.font, total_waves=21)
        # Move menu to left of HUD buttons, above bottom bar to avoid blocking tower slots
        self.wave_select_menu.menu_rect.x = SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_SIZE * 5 - self.wave_select_menu.menu_width
        self.wave_select_menu.menu_rect.y = SCREEN_HEIGHT - BUTTON_MARGIN - BUTTON_SIZE - self.wave_select_menu.menu_height - 10

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos if hasattr(event, 'pos') else pygame.mouse.get_pos()
            for btn in [self.start_wave_button, self.tower_menu_button, self.gold_button, self.wave_select_button]:
                dx = mouse_pos[0] - btn.x
                dy = mouse_pos[1] - btn.y
                btn.hovered = dx*dx + dy*dy <= btn.size*btn.size

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Only visually press the button that is hovered
            if self.start_wave_button.hovered:
                self.start_wave_button.pressed = True
                if HUD.button_click_sound:
                    HUD.button_click_sound.play()
            if self.tower_menu_button.hovered:
                self.tower_menu_button.pressed = True
                if HUD.button_click_sound:
                    HUD.button_click_sound.play()
            if self.gold_button.hovered:
                self.gold_button.pressed = True
            if self.wave_select_button.hovered:
                self.wave_select_button.pressed = True

            # Dev: Check gold button (for dev only)
            if self.gold_button.hovered:
                self.game.economy.coins += 1000

            # Dev: Check wave select button
            if self.wave_select_button.hovered:
                self.wave_select_menu.open()

            # Check start wave button
            if self.start_wave_button.hovered:
                if not self.game.wave_manager.wave_in_progress:
                    self.game.wave_manager.start_wave()
                    self.game.state = 'playing'
            
            # Check tower menu button
            if self.tower_menu_button.hovered:
                self.tower_menu_open = not self.tower_menu_open

        elif event.type == pygame.MOUSEBUTTONUP:
            # Reset pressed state for all buttons
            self.start_wave_button.pressed = False
            self.tower_menu_button.pressed = False
            self.gold_button.pressed = False
            self.wave_select_button.pressed = False

        # Play button click for restart button (if present in HUD)
        if hasattr(self, 'restart_button') and event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_button.hovered and HUD.button_click_sound:
                HUD.button_click_sound.play()

        # Handle wave select menu
        selected_wave = self.wave_select_menu.handle_event(event)
        if selected_wave is not None:
            # Start selected wave (for dev)
            self.game.wave_manager.wave_number = selected_wave - 1
            self.game.wave_manager.start_wave()
            self.game.state = 'playing'

        # --- Tower selection menu: close on right click if nothing is selected ---
        if self.tower_menu_open and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Only close menu if click is outside the menu and button, and no tower is selected
            menu_width = 250
            menu_height = 240
            menu_x = SCREEN_WIDTH - menu_width - BUTTON_MARGIN
            menu_y = SCREEN_HEIGHT - menu_height - BUTTON_SIZE - BUTTON_MARGIN - BUTTON_SPACING
            menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
            if (event.button in (1, 3)
                and self.game.tower_manager.selected_tower is None
                and not menu_rect.collidepoint(mouse_pos)
                and not self.tower_menu_button.hovered):
                self.tower_menu_open = False
                return
            if hasattr(self, 'tower_buttons'):
                for button_rect, tower_type in self.tower_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        if HUD.towerselection_click_sound:
                            HUD.towerselection_click_sound.play()
                        break

    def draw(self, screen):
        # Draw game stats
        coins = self.game.economy.coins
        hp = self.game.base.hp

        # Draw gold button (for dev only)
        self.gold_button.draw(screen)
        wave = self.game.wave_manager.wave_number
        text = self.font.render(f"Coins: {coins}   HP: {hp}   Wave: {wave}", True, COLORS['text'])
        screen.blit(text, (20, 20))
        
        # Draw buttons
        self.start_wave_button.draw(screen)
        self.tower_menu_button.draw(screen)
        # Draw dev wave select button
        self.wave_select_button.draw(screen)
        self.wave_select_menu.draw(screen)
        
        # Draw tower menu if open
        if self.tower_menu_open:
            menu_width = 250
            menu_height = 240
            menu_x = SCREEN_WIDTH - menu_width - BUTTON_MARGIN
            menu_y = SCREEN_HEIGHT - menu_height - BUTTON_SIZE - BUTTON_MARGIN - BUTTON_SPACING
            
            # Draw menu background
            pygame.draw.rect(screen, COLORS['button'],
                           (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(screen, COLORS['text'],
                           (menu_x, menu_y, menu_width, menu_height), 2)
            
            # Draw tower options
            self.tower_buttons = []  # Reset tower buttons
            for i, tower_type in enumerate(['cannon', 'water', 'fire']):
                cost = TOWER_COSTS[tower_type]
                can_afford = self.game.economy.coins >= cost
                stats = TOWER_STATS[tower_type]
                # Fire tower locked until wave 10
                locked = (tower_type == 'fire' and self.game.wave_manager.wave_number < 10)
                
                # Calculate button rectangle (taller to fit all info)
                button_rect = pygame.Rect(menu_x + 10, menu_y + 10 + i * 70, menu_width - 20, 60)
                self.tower_buttons.append((button_rect, tower_type))
                
                # Draw button background
                if tower_type == 'fire' and self.game.wave_manager.wave_number < 10:
                    button_color = (120, 120, 120)  # Grayed out
                else:
                    button_color = COLORS['button_hover'] if can_afford else (100, 100, 100)
                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, COLORS['text'], button_rect, 1)
                
                # Colors
                text_color = COLORS['text'] if can_afford else (150, 150, 150)
                
                # Prepare all lines
                display_name = 'Ice' if tower_type == 'water' else tower_type.title()
                text = f"{display_name} Tower (${cost})"
                dmg_text = f"Damage: {stats['damage']}"
                range_text = f"Range: {stats['range']}  Speed: {stats['attack_speed']}/s"

                text_surface = self.small_font.render(text, True, text_color)
                dmg_surface = self.small_font.render(dmg_text, True, text_color)
                range_surface = self.small_font.render(range_text, True, text_color)

                # Calculate total height
                line_surfaces = [text_surface, dmg_surface, range_surface]
                total_text_height = sum(surf.get_height() for surf in line_surfaces)
                spacing = 2  # pixels between lines
                total_height = total_text_height + spacing * (len(line_surfaces) - 1)

                # Start y so that all lines are centered
                start_y = button_rect.y + (button_rect.height - total_height) // 2
                x = button_rect.x + 10

                # Draw all lines centered vertically
                screen.blit(text_surface, (x, start_y))
                screen.blit(dmg_surface, (x, start_y + text_surface.get_height() + spacing))
                screen.blit(range_surface, (x, start_y + text_surface.get_height() + spacing + dmg_surface.get_height() + spacing))

                # Overlay lock text if fire tower is locked
                if tower_type == 'fire' and self.game.wave_manager.wave_number < 10:
                    # Use a larger, bold font for visibility
                    bold_font = pygame.font.SysFont('arial', 20, bold=True)
                    lock_text = bold_font.render('unlocked on wave 10', True, (255,255,255))
                    lock_rect = lock_text.get_rect(center=button_rect.center)
                    # Draw semi-transparent black rectangle behind text
                    s = pygame.Surface((lock_rect.width+12, lock_rect.height+6), pygame.SRCALPHA)
                    s.fill((0,0,0,180))
                    screen.blit(s, (lock_rect.x-6, lock_rect.y-3))
                    # Draw text shadow for extra contrast
                    shadow = bold_font.render('unlocked on wave 10', True, (40,40,40))
                    screen.blit(shadow, (lock_rect.x+2, lock_rect.y+2))
                    # Draw main text
                    screen.blit(lock_text, lock_rect)
    
    def update(self):
        """Update any HUD animations or states. Currently unused."""
        pass

    def get_clicked_tower(self, mouse_pos):
        """Check if a tower option was clicked in the menu. Plays sound if selection is valid."""
        if not self.tower_menu_open:
            return None
        for rect, tower_type in self.tower_buttons:
            if rect.collidepoint(mouse_pos):
                # Prevent fire tower selection if locked
                if tower_type == 'fire' and self.game.wave_manager.wave_number < 10:
                    return None
                if self.game.economy.coins >= TOWER_COSTS[tower_type]:
                    # Play tower selection sound only on valid selection
                    if HUD.towerselection_click_sound:
                        HUD.towerselection_click_sound.play()
                    return tower_type
        return None
