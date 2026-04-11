"""HumanSoldierEnemy Module - Mid-tier enemy with attacking capability.

The HumanSoldierEnemy is a standard patrol enemy with the same 2 HP and 120 px/s speed
as OrcEnemy but includes an attacking animation state. This prepares the framework for
future AI that could perform ranged or melee attacks, though current implementation
relies on PatrollingEnemy's passive collision damage.

Stats:
- Speed: 120 px/s (60% of player speed)
- Health: 2 HP
- Sprite: Human_Soldier_Sword_Shield-Sheet.png with attack animation row
- Special: Includes attacking animation state for future AI expansion
"""
from .patrollingEnemy import PatrollingEnemy


class HumanSoldierEnemy(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Human_Soldier_Sword_Shield-Sheet.png")

        # Set speed to 60% of player speed (200 * 0.6 = 120)
        self.speed = 120
        # Set HP to 2
        self.maxHp = 2
        self.hp = self.maxHp

        self.nFramesList = {
            "moving": 8,
            "standing": 6,
            "hurting": 4,
            "attacking": 8
        }

        self.rowList = {
            "moving": 1,
            "standing": 0,
            "hurting": 6,
            "attacking": 4
        }

        self.framesPerSecondList = {
            "moving": 12,
            "standing": 8,
            "hurting": 8,
            "attacking": 12
        }

        self.FSManimated.on_enter_state()