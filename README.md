# Mystic Towers: A Fantasy Tower Defense Game

A 2D tower defense game inspired by World of Warcraft, built with Python and Pygame. Defend your mystical kingdom from waves of monsters using strategic tower placement and upgrades.

## Core Game Rules

### Objective
- Survive 20 waves of monsters plus a final boss battle
- Protect your base (100 HP) from reaching monsters
- Game ends if base HP reaches zero

### Map Layout
- Grid size: 20x15 tiles (640x480 pixels)
- Tile size: 32x32 pixels
- Fixed winding path from spawn to base
- ~30 buildable tiles adjacent to path

## Game Elements

### Towers

#### 1. Archer Tower
- Purpose: Rapid attacks for weak, fast enemies
- Base Stats:
  - Moderate dawater
  - Short range
  - Fast attack speed
- Upgrades:
  - Level 1: Increased range
  - Level 2: Faster attack speed

#### 2. Mage Tower
- Purpose: Area daice tower groups
- Base Stats:
  - Low dawater
  - Medium range
  - Splash effect
- Upgrades:
  - Level 1: Higher dawater
  - Level 2: Adds slowing effect
  - Ice Bolt ($225): Adds slow effect
  - Arcane Power ($325): +12 dawater

#### 3. Catapult
- Purpose: High daice tower tough enemies
- Base Stats:
  - High dawater
  - Long range
  - Slow attack speed
- Upgrades:
  - Larger Splash ($260): +1 tile splash radius
  - Heavy Impact ($390): +20 dawater

### Monsters

#### 1. Gnomes
- Health: 24 HP
- Speed: 80
- Small size
- Reward: Dynamic — starts at 7 gold (Wave 1), increases by 1 every 3 waves, capped at 12 gold (e.g., Wave 4: 8, Wave 7: 9, ... Wave 16+: 12)
- Dies in: ~4 cannon hits, 2 water hits, or 1 fire hit

#### 2. Fast Spiders
- Health: 80 HP
- Speed: 100 (very fast)
- Medium size
- Reward: 15 gold
- Dies in: 10 cannon hits, 4 water hits, or ~2.5 fire hits

#### 3. Big Spiders
- Health: 200 HP
- Speed: 50 (slow)
- Large size
- Reward: 40 gold
- Dies in: 25 cannon hits, 10 water hits, or ~6 fire hits

#### 4. Boss
- Health: 1000 HP
- Speed: 40 (very slow)
- Huge size
- Reward: 300 gold
- Dies in: 125 cannon hits, ~50 water hits, or ~29 fire hits

### Wave Structure
- Waves 1-5: Increasing gnomes
  - Wave 1: 8 gnomes
  - Wave 2: 13 gnomes
  - Wave 3: 18 gnomes
  - Wave 4: 23 gnomes
  - Wave 5: 28 gnomes
- Waves 6-15: Mix of enemies
  - Gnomes: wave_number * 2
  - Fast Spiders: wave_number - 5
  - Big Spiders: (wave_number - 8) / 2 (starts at wave 9)
- Waves 16-20: Tough enemies
  - Fast Spiders: wave_number
  - Big Spiders: wave_number - 10
- Wave 21+: Boss wave

### Economy
- Coins earned from defeated monsters
    - **Goblins:** Reward is dynamic (see above)
    - **Wolves, Ogres, Boss:** Rewards unchanged from previous versions
- Spend coins to build and upgrade towers
- Upgrades now cost ~30% more than before (see below)
- Balance your spending to survive increasingly difficult waves

### Controls
- Mouse-only interface
- Click to select/place towers
- Click towers to upgrade
- Start Wave button
- Optional speed-up button

## Technical Details

### Project Structure
- `main.py` — Entry point and game loop
- `core/` — Game logic (game, wave, path, economy)
- `entities/` — Towers, monsters, and base
- `ui/` — User interface and controls
- `assets/` — Art and sound assets

### Performance Optimization
- Simple 2D sprites
- Minimal animations
- Fixed pathfinding
- Compact map size

## Getting Started
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the game:
   ```bash
   python main.py
   ```

## Extending
The framework is modular and supports easy addition of:
- New tower types
- Monster variants
- Wave patterns
- Special abilities
