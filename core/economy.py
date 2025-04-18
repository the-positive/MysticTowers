from .config import STARTING_GOLD

class Economy:
    """Tracks coins and handles spending/earning."""
    def __init__(self):
        self.coins = STARTING_GOLD

    def earn(self, amount):
        self.coins += amount

    def spend(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
