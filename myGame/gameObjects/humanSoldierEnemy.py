from .patrollingEnemy import PatrollingEnemy


class HumanSoldierEnemy(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Human_Soldier_Sword_Shield-Sheet.png")

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