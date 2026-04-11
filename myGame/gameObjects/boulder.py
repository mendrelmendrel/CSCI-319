"""Boulder Module - Static obstacle with customizable collision sizing and scaling.

The Boulder class represents immobile level obstacles that block both player and enemy
movement. Boulders support custom collision sizing (can be different from visual size),
scaling factors for fine-tuning collision difficulty, and optional draw scaling for
visual variety while maintaining collision consistency.

Features:
- Collision Rect: Separate from visual size for gameplay tuning
- Scaling: collisionScale factor (0.1-1.0) to adjust effective obstacle size
- Draw Scaling: Optional drawSize parameter to resize sprite without affecting collision
- Color Key: Preserves transparency when scaling sprites
- Depth Sorting: getDepthY() enables isometric-style rendering depth
"""
from .drawable import Drawable
from utils import vec

import pygame


class Boulder(Drawable):
    def __init__(self, position, fileName="Boulder.png", collisionSize=(17, 14), collisionScale=0.75, drawSize=None):
        super().__init__(position, fileName)
        self.fileName = fileName
        self.collisionSize = vec(*collisionSize)
        self.collisionScale = max(0.1, min(float(collisionScale), 1.0))

        if drawSize is not None:
            width = max(1, int(drawSize[0]))
            height = max(1, int(drawSize[1]))
            colorKey = self.image.get_colorkey()
            if colorKey is not None:
                self.image = pygame.transform.scale(self.image,
                                                    (width, height))
                self.image.set_colorkey(colorKey)
            else:
                self.image = pygame.transform.smoothscale(self.image,
                                                          (width, height))

    def getCollisionRect(self):
        width, height = self.getSize()
        baseWidth, baseHeight = self.collisionSize
        rectWidth = max(2, int(baseWidth * self.collisionScale))
        rectHeight = max(2, int(baseHeight * self.collisionScale))

        centerX = self.position[0] + (width / 2)
        centerY = self.position[1] + (height / 2)

        return pygame.Rect(
            int(centerX - (rectWidth / 2)),
            int(centerY - (rectHeight / 2)),
            int(rectWidth),
            int(rectHeight)
        )

    def getDepthY(self):
        return self.position[1] + self.getSize()[1]
