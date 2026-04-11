"""Tree  - Animated obstacle with collision and visual blocking.

The Tree class represents animated foliage obstacles 

Features:
- Animation: Cycles through sprite frames 
- Half-Scale: Renders at 50% scale for efficient memory and smooth performance
- Collision Rect: Trunk-only collision at bottom-center of sprite
- Depth Sorting: Full sprite height used for visual depth (visual layering)
- visual Logic: Visual appearance behind/in front of entities based on Y position
"""
import pygame

from .drawable import Drawable
from utils import SpriteManager, vec


class Tree(Drawable):
    def __init__(self, position, framesPerSecond=3):
        super().__init__(position)
        self.imageName = "Tree1.png"
        rawFrames = SpriteManager.getInstance().getTree1AnimationSprites()
        self.frames = [self._scaleHalf(frame) for frame in rawFrames]
        self.frame = 0
        self.framesPerSecond = framesPerSecond
        self.animationTimer = 0
        self.image = self.frames[self.frame]

    def _scaleHalf(self, frame):
        width, height = frame.get_size()
        return pygame.transform.scale(frame,
                                      (max(1, width // 2),
                                       max(1, height // 2)))

    def update(self, seconds):
        self.animationTimer += seconds

        if self.animationTimer >= 1 / self.framesPerSecond:
            # Subtract frame duration (instead of resetting to 0) to preserve
            # fractional time and keep animation cadence stable across frame spikes.
            self.animationTimer -= 1 / self.framesPerSecond
            self.frame = (self.frame + 1) % len(self.frames)
            self.image = self.frames[self.frame]

    def getCollisionRect(self):
        width, height = self.image.get_size()
        # Only the trunk blocks movement; foliage remains pass-through for nicer feel.
        trunkWidth = int(width * 0.36)
        trunkHeight = int(height * 0.26)

        trunkX = int(self.position[0] + (width - trunkWidth) / 2)
        trunkY = int(self.position[1] + height - trunkHeight)

        return pygame.Rect(trunkX, trunkY, trunkWidth, trunkHeight)

    def getDepthY(self):
        return self.position[1] + self.getSize()[1]

    def isInFrontOf(self, entityFootY):
        return self.getDepthY() > entityFootY

    def getSize(self):
        return vec(*self.image.get_size())
