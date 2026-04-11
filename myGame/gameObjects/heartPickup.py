"""HeartPickup Module - Consumable health item dropped by defeated enemies.

The HeartPickup class represents one-hit-point recovery items dropped by enemies when
killed. Hearts float with animated sprite rotation for 8 seconds before disappearing.
Collision with player automatically restores 1 HP (up to max), and heart is then removed.
Drop chance increases when player is low on health to prevent softlock scenarios.

Features:
- Animation: Rotates through heart frame animation at 10 FPS
- Lifetime: 8 second despawn timer (matches typical drop visibility)
- Auto-Pickup: Automatic on collision; healing only if below max HP
- Visual Polish: Scaled to 22x22 pixels with smooth scaling
- Scaling: 60% of full sprite size for prominent visibility
"""
from .drawable import Drawable
from utils import SpriteManager

import pygame


class HeartPickup(Drawable):
    def __init__(self, position):
        super().__init__(position, "")

        self.frames = SpriteManager.getInstance().getHeartRotateSprites()
        self.frames = [pygame.transform.smoothscale(frame, (22, 22))
                       for frame in self.frames]

        self.frameIndex = 0
        self.animationTimer = 0.0
        self.framesPerSecond = 10
        self.lifeTimer = 8.0
        self.alive = True

        self.image = self.frames[0] if len(self.frames) > 0 else pygame.Surface((22, 22), pygame.SRCALPHA, 32)
        self.imageName = "heart.rotate.png"

    def update(self, seconds):
        if not self.alive:
            return

        self.lifeTimer -= seconds
        if self.lifeTimer <= 0:
            self.alive = False
            return

        if len(self.frames) == 0:
            return

        self.animationTimer += seconds
        frameDuration = 1 / self.framesPerSecond

        while self.animationTimer >= frameDuration:
            self.animationTimer -= frameDuration
            self.frameIndex = (self.frameIndex + 1) % len(self.frames)

        self.image = self.frames[self.frameIndex]

    def draw(self, drawSurface):
        if not self.alive:
            return

        drawSurface.blit(self.frames[self.frameIndex],
                         list(map(int, self.position - Drawable.CAMERA_OFFSET)))

    def getRect(self):
        return pygame.Rect(int(self.position[0]),
                           int(self.position[1]),
                           int(self.getSize()[0]),
                           int(self.getSize()[1]))