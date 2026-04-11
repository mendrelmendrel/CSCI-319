"""Bush Module - Simple decorative obstacle with visual depth layering.

The Bush class represents small foliage obstacles in the level. Bushes are purely visual
with no collision behavior; they layer via isometric depth sorting (getDepthY) to appear
behind or in front of entities based on their Y position. Different bush sprite variants
can be used for visual variety in level design.

Features:
- Visual Only: No collision detection, purely decorative
- Variable Sprites: Supports different bush variants (bush_1.png, bush2.png, etc)
- Depth Layering: Sorts by Y position for proper front-to-back rendering
"""
from .drawable import Drawable


class Bush(Drawable):
    def __init__(self, position, fileName="bush_1.png"):
        super().__init__(position, fileName)
        self.fileName = fileName

    def getDepthY(self):
        return self.position[1] + self.getSize()[1]
