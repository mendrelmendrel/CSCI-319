from .patrollingEnemy import PatrollingEnemy

class OrcEnemy(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Orc.png")
        self.rowList["hurting"] = 4
        self.nFramesList["hurting"] = 4
        self.framesPerSecondList["hurting"] = 12
