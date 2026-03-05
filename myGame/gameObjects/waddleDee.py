from .patrollingEnemy import PatrollingEnemy

class WaddleDee(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="waddledee.png")
        
        # Override animation settings for waddledee's layout
        self.nFramesList = {
            "moving"   : 2,  # 2 frames for walking
            "standing" : 2   # 2 frames for idle
        }
        
        self.rowList = {
            "moving"   : 1,  # Walking is row 1
            "standing" : 0   # Idle is row 0
        }
        
        self.framesPerSecondList = {
            "moving"   : 8,
            "standing" : 2
        }