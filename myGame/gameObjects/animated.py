"""Animated Module - Extends Drawable to add frame-based sprite animation.

The Animated class adds animation capabilities on top of the Drawable base class.
It manages frame-by-frame sprite animation with timing, FSM state integration, and
dynamic sprite sheet selection. Animation state is synchronized with the object's
finite state machine (FSM) to ensure correct sprite sheet and row are displayed.

Animation System:
- Frame timing: Controls animation speed via framesPerSecond and animationTimer
- FSM integration: Automatically fetches correct sprite sheet based on current state
- Frame cycling: Loops through nFrames with wrapping on frame overflow
- State-based sheets: Different states may use different sprite sheets or files
"""
from . import Drawable
from utils import SpriteManager

class Animated(Drawable):
    
    def __init__(self, position=(0,0), fileName=""):
        super().__init__(position, fileName, (0,0))
        self.fileName = fileName
        self.row = 0
        self.frame = 0
        self.nFrames = 1
        self.animate = True
        self.framesPerSecond = 8
        self.animationTimer = 0
        self.FSManimated = None
    
    def update(self, seconds):
        if self.FSManimated:
            self.FSManimated.update(seconds)
            
        if not self.animate:
            return
        
        self.animationTimer += seconds 
           
        if self.animationTimer > 1 / self.framesPerSecond:
            self.frame += 1
            self.frame %= self.nFrames
            self.animationTimer -= 1 / self.framesPerSecond
            currentState = self.FSManimated.current_state.id \
                if self.FSManimated else None
            sheetName = self.getAnimationSheet(currentState) \
                if (currentState is not None and hasattr(self, "getAnimationSheet")) \
                else self.imageName
            self.image = SpriteManager.getInstance().getSprite(sheetName,
                                        (self.frame, self.row))
    
