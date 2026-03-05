from .patrollingEnemy import PatrollingEnemy

class EnemyKirby(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="kirby.png")