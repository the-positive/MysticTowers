class WaveManager:
    """Manages wave spawning and progression."""
    def __init__(self, monster_manager, base):
        self.monster_manager = monster_manager
        self.base = base
        self.wave_number = 0
        self.wave_in_progress = False
        
    def start_wave(self):
        """Start a new wave of monsters."""
        if not self.wave_in_progress:
            self.wave_number += 1
            self.wave_in_progress = True
            self.monster_manager.start_wave(self.wave_number, self.base)
        
    def update(self, dt):
        """Update wave state."""
        # Check if current wave is done
        if self.wave_in_progress and not self.monster_manager.wave_in_progress:
            self.wave_in_progress = False
            # Gift 10 gold for completing wave 1
            if self.wave_number == 1:
                self.monster_manager.economy.earn(10)
