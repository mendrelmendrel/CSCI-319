from . import Mobile
from FSMs import WalkingFSM
from utils import vec, WORLD_SIZE, normalize, magnitude

class PatrollingEnemy(Mobile):
    def __init__(self, position, minX, maxX, spriteName="kirby.png"):
        super().__init__(position, spriteName)
        
        # Path constraints
        self.minX = minX
        self.maxX = maxX
        self.speed = 100  # pixels per second
        self.velocity = vec(self.speed, 0)  # Start moving right
        
        # Player reference for tracking
        self.player = None
        
        # Animation variables
        self.framesPerSecond = 2 
        self.nFrames = 2
        
        self.nFramesList = {
            "moving"   : 4,
            "standing" : 2
        }
        
        self.rowList = {
            "moving"   : 1,
            "standing" : 0
        }
        
        self.framesPerSecondList = {
            "moving"   : 8,
            "standing" : 2
        }
        
        self.frame = 0
        self.animationTimer = 0
        self.row = 0
        
        # Animation FSM
        self.FSManimated = WalkingFSM(self)
    
    def update(self, seconds):
        # Track and move toward player if available
        if self.player:
            direction = self.player.position - self.position
            direction_length = magnitude(direction)
            if direction_length > 0:
                direction = normalize(direction)
                self.velocity = direction * self.speed
                # Flip sprite based on direction
                if direction[0] < 0:
                    self.flipped = True
                elif direction[0] > 0:
                    self.flipped = False
        
        super().update(seconds)
        
        # Clamp to world boundaries
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
        elif self.position[0] + self.getSize()[0] > WORLD_SIZE[0]:
            self.position[0] = WORLD_SIZE[0] - self.getSize()[0]
            self.velocity[0] = 0
        
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
        elif self.position[1] + self.getSize()[1] > WORLD_SIZE[1]:
            self.position[1] = WORLD_SIZE[1] - self.getSize()[1]
            self.velocity[1] = 0