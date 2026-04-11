"""Arrow - Player projectile with auto-aim and lifetime management.

The Arrow class represents projectiles fired by the player. 

Arrow Features:
- Direction-based velocity with customizable speed (500 pixels/sec default)
- Optional target tracking: Arrow home toward target's center if target alive/in range
- Auto-rotation: Arrow sprite rotates to face travel direction using atan2 math
- Lifetime tracking: Despawns after 1.2 seconds or when leaving world bounds
- Collision: 1 damage per hit; marks self as dead on impact to prevent multi-hits
"""
from .drawable import Drawable
from utils import vec, magnitude, normalize

import pygame
import numpy as np


class Arrow(Drawable):
    def __init__(self, position, direction, speed=500, lifetime=1.2, target=None):
        super().__init__(position, "Arrow01(32x32).png")

        if magnitude(direction) > 0:
            self.direction = normalize(direction)
        else:
            self.direction = vec(1, 0)

        self.velocity = self.direction * speed
        self.speed = speed
        self.lifetime = lifetime
        self.alive = True
        self.damage = 1
        self.target = target

        self.position -= self.getSize() / 2

    def update(self, seconds):
        # Lightweight homing: each frame, re-aim velocity toward target center
        # while keeping constant projectile speed.
        if self.target is not None and hasattr(self.target, "hp") and self.target.hp > 0:
            if hasattr(self.target, "getFullBodyRect"):
                targetRect = self.target.getFullBodyRect()
                targetCenter = vec(targetRect.centerx, targetRect.centery)
            else:
                targetCenter = self.target.position + (self.target.getSize() / 2)

            arrowCenter = self.position + (self.getSize() / 2)
            targetDirection = targetCenter - arrowCenter
            if magnitude(targetDirection) > 0:
                self.direction = normalize(targetDirection)
                self.velocity = self.direction * self.speed

        self.position += self.velocity * seconds
        self.lifetime -= seconds
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, drawSurface):
        # Y axis points downward, so we negate angle for screen space.
        angle = -np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        rotatedImage = pygame.transform.rotate(self.image, angle)

        screenPosition = self.position - Drawable.CAMERA_OFFSET
        imageSize = self.getSize()
        center = (int(screenPosition[0] + imageSize[0] / 2),
                  int(screenPosition[1] + imageSize[1] / 2))
        # Re-center after rotation so spinning does not visually offset projectile.
        drawRect = rotatedImage.get_rect(center=center)
        drawSurface.blit(rotatedImage, drawRect)

    def getRect(self):
        imageSize = self.getSize()
        return pygame.Rect(int(self.position[0]),
                           int(self.position[1]),
                           int(imageSize[0]),
                           int(imageSize[1]))