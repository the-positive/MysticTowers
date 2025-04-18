"""Game configuration constants."""

# Map Configuration
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE  # 640
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE  # 480

# Game Balance
STARTING_GOLD = 160  # Slightly higher so player can build a second tower after wave 1
BASE_HP = 80        # Less room for error
TOTAL_WAVES = 21

# Tower Stats
TOWER_COSTS = {
    'cannon': 60,    # Cheaper
    'water': 85,
    'fire': 120
}

TOWER_STATS = {
    'cannon': {
        'damage': 7,          # Buffed for early game
        'range': 3,          # Short range
        'attack_speed': 1.0,  # Back to 1 shot/sec
        'splash_radius': 0,   # Single target
        'projectile_speed': 300,
        'projectile_color': (139, 69, 19),  # Brown
        'projectile_size': 3,
        'upgrades': [
            {'name': 'Rapid Fire', 'cost': 195, 'speed_bonus': 0.4},    # 1.2 shots/sec
            {'name': 'Sharp Arrows', 'cost': 260, 'damage_bonus': 5}     # 10 damage
        ]
    },
    'water': {
        'damage': 15,         # Lower base damage
        'range': 4,          # Medium range
        'attack_speed': 0.4,  # 1 shot every 2.5 seconds
        'splash_radius': 0,   # Single target
        'projectile_speed': 200,
        'projectile_color': (0, 0, 255),  # Blue
        'projectile_size': 5,
        'upgrades': [
            {'name': 'Ice Bolt', 'cost': 225, 'slow_effect': 0.25},     # Weaker slow
            {'name': 'Arcane Power', 'cost': 325, 'damage_bonus': 12}    # 27 damage
        ]
    },
    'fire': {
        'damage': 25,         # Lower base damage
        'range': 5,          # Long range
        'attack_speed': 0.3,  # Slightly slower
        'splash_radius': 1,   # Area damage
        'projectile_speed': 150,
        'projectile_color': (128, 128, 128),  # Gray
        'projectile_size': 6,
        'upgrades': [
            {'name': 'Larger Splash', 'cost': 260, 'splash_bonus': 1},   # 2 tile splash
            {'name': 'Heavy Impact', 'cost': 390, 'damage_bonus': 20}     # 45 damage
        ]
    }
}

# Monster Stats
# Types: gnome, fast_spider, big_spider, boss
MONSTER_STATS = {
    'gnome': {
        'health': 24,   # Easier for early game
        'speed': 80,    # Faster
        'size': 10,     # Small
        'color': (40, 100, 200),  # Darker blue
        'reward': 7  # Default, will be dynamically assigned in code
    },
    'fast_spider': {
        'health': 80,  # Much tankier
        'speed': 120,   # Even faster
        'size': 12,     # Medium
        'color': (139, 69, 19),  # Brownish
        'reward': 12    # Less gold reward
    },
    'big_spider': {
        'health': 300,  # Much tankier
        'speed': 60,    # Slightly faster
        'size': 16,     # Large
        'color': (0, 90, 40),  # Dark green
        'reward': 35    # Less gold reward
    },
    'boss': {
        'health': 1500, # Much tankier
        'speed': 45,    # Slightly faster
        'size': 24,     # Huge
        'color': (139, 0, 0),  # Dark red
        'reward': 250   # Less gold reward
    },
    'boss_gnome': {
        'health': 1500,
        'speed': 45,
        'size': 32,
        'color': (40, 100, 200),  # Darker blue (like gnome)
        'reward': 250
    },
    'boss_fast_spider': {
        'color': (139, 69, 19),  # Brownish
        'health': 1500,
        'speed': 45,
        'size': 32,
        'color': (139, 69, 19),  # Brownish (like fast spider)
        'reward': 250
    },
    'boss_big_spider': {
        'color': (0, 90, 40),  # Dark green
        'health': 1500,
        'speed': 45,
        'size': 32,
        'color': (139, 69, 19),  # Brown (like big spider)
        'reward': 250
    }
}

# Wave Configuration
WAVE_CONFIGS = {
    # Waves 1-5: Fewer gnomes, slower ramp
    'early': {
        'gnome': {
        'count': lambda wave: [7, 10, 13, 16, 19][wave-1],
        'delay': 0.9,
        'reward': lambda wave: 8 if wave == 1 else 7  # Wave 1 gnomes give 8 gold, others 7
    }
    },
    # Waves 6-15: Smoother scaling
    'mid': {
        'gnome': {'count': lambda wave: int(wave * 2.2), 'delay': 1.0},
        'fast_spider': {'count': lambda wave: max(0, wave-5), 'delay': 1.6},
        'big_spider': {'count': lambda wave: max(0, (wave-8)//2), 'delay': 2.2}
    },
    # Waves 16-20: Still tough, but less overwhelming
    'late': {
        'gnome': {'count': lambda wave: int(wave * 2.8), 'delay': 0.8},
        'fast_spider': {'count': lambda wave: wave-10, 'delay': 1.2},
        'big_spider': {'count': lambda wave: wave-13, 'delay': 1.6}
    }
}

# Colors
COLORS = {
    'background': (90, 170, 255),
    'path': (120, 80, 40),
    'buildable': (200, 255, 200),
    'selected': (255, 255, 200),
    'text': (0, 0, 0),
    'button': (150, 150, 150),
    'button_hover': (180, 180, 180),
    'start_wave': (255, 50, 50),  # Red for start wave button
    'start_wave_hover': (255, 100, 100),
    'tower_menu': (50, 150, 255),  # Blue for tower menu button
    'tower_menu_hover': (100, 175, 255),
    'game_over_bg': (0, 0, 0, 180),  # Semi-transparent black
    'game_over_text': (255, 0, 0),  # Blood red
    'restart_button': (0, 200, 0),  # Green
    'restart_button_hover': (0, 255, 0)  # Bright green
}

# Waves
TOTAL_WAVES = 21  # Boss wave is wave 21

# Game over text
GAME_OVER_TEXT = "Game Over!"

# UI Configuration
BUTTON_SIZE = 40  # Size of circular buttons
BUTTON_MARGIN = 20  # Margin from screen edges
BUTTON_SPACING = 10  # Space between buttons
