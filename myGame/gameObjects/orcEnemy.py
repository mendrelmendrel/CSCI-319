"""OrcEnemy Module - Moderately strong standard enemy with medium speed and health.

The OrcEnemy is a standard patrol enemy introduced mid-game. Speed set to 60% of player
speed (120 px/s) with 2 HP, making it tougher than the Slime but weaker than the
Human Soldier. Uses default PatrollingEnemy animation setup with no special abilities.

Stats:
- Speed: 120 px/s (60% of player speed)
- Health: 2 HP
- Sprite: Orc.png with standard animation rows
"""
from .patrollingEnemy import PatrollingEnemy

class OrcEnemy(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Orc.png")
        
        # Set speed to 60% of player speed (200 * 0.6 = 120)
        self.speed = 120
        # Set HP to 2
        self.maxHp = 2
        self.hp = self.maxHp
        
        self.rowList["hurting"] = 4
        self.nFramesList["hurting"] = 4
        self.framesPerSecondList["hurting"] = 12
