from . import AbstractGameFSM
from utils import magnitude, EPSILON, SpriteManager

from statemachine import State

class AnimateFSM(AbstractGameFSM):
    """For anything that animates. Adds behavior on
       transitioning into a state to change animation."""
    def __init__(self, obj):
        super().__init__(obj)
        self.on_enter_state()

    def on_enter_state(self):
        state = self.current_state.id
       
        self.obj.nFrames = self.obj.nFramesList[state]
        self.obj.frame = 0
        self.obj.row = self.obj.rowList[state]
        self.obj.framesPerSecond = self.obj.framesPerSecondList[state]
        self.obj.animationTimer = 0
        self.obj.image = SpriteManager.getInstance().getSprite(self.obj.imageName,
                                                                   (self.obj.frame, self.obj.row))
         
        
class WalkingFSM(AnimateFSM):
    """Two-state FSM for walking / stopping in
       a top-down environment."""
       
    standing = State(initial=True)
    moving   = State()
    
    move = standing.to(moving)
    stop = moving.to(standing)
        
    def update(self, seconds=0):
        """Update state based on velocity"""
        self.updateState()
    
    def updateState(self):
        if self.hasVelocity() and self != "moving":
            self.move()
        elif not self.hasVelocity() and self != "standing":
            self.stop()
    
    def hasVelocity(self):
        return magnitude(self.obj.velocity) > EPSILON
    
    def noVelocity(self):
        return not self.hasVelocity()