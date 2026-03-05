from . import AnimateFSM
from utils import magnitude, EPSILON

from statemachine import State

class AttackFSM(AnimateFSM):
    """Three-state FSM for walking, stopping, and attacking in
       a top-down environment."""
    
    standing = State(initial=True)
    moving   = State()
    attacking = State()
    
    move = standing.to(moving) | moving.to.itself(internal=True) | attacking.to(moving)
    stop = moving.to(standing) | standing.to.itself(internal=True) | attacking.to(standing)
    attack = standing.to(attacking) | moving.to(attacking) | attacking.to.itself(internal=True)
    endAttack = attacking.to(standing) | attacking.to(moving)
    
    def __init__(self, obj):
        super().__init__(obj)
        self.attackTimer = 0
        self.attackDuration = 0
    
    def update(self, seconds=0):
        """Override update to decrement timer properly"""
        if self.attackTimer > 0:
            self.attackTimer -= seconds
        self.updateState()
    
    def updateState(self):
        # If attack animation is finished, return to standing/moving
        if self == "attacking" and self.attackTimer <= 0:
            if self.hasVelocity():
                self.move()
            else:
                self.endAttack()
        # Handle normal movement states
        elif self.hasVelocity() and self != "moving" and self != "attacking":
            self.move()
        elif not self.hasVelocity() and self != "standing" and self != "attacking":
            self.stop()
    
    def hasVelocity(self):
        return magnitude(self.obj.velocity) > EPSILON
    
    def startAttack(self):
        """Called when attack key is pressed"""
        self.attack()
        # Calculate duration in seconds: frames / fps
        nFrames = self.obj.nFramesList.get("attacking", 4)
        fps = self.obj.framesPerSecondList.get("attacking", 8)
        self.attackDuration = nFrames / fps
        self.attackTimer = self.attackDuration
