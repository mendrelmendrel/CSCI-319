from .drawable import Drawable
from utils import vec, magnitude, normalize

import pygame
import numpy as np


class Arrow(Drawable):
    def __init__(self, position, direction, speed=500, lifetime=1.2):
        super().__init__(position, "Arrow01(32x32).png")

        if magnitude(direction) > 0:
            self.direction = normalize(direction)
        else:
            self.direction = vec(1, 0)

        self.velocity = self.direction * speed
        self.lifetime = lifetime
        self.alive = True
        self.damage = 1

        self.position -= self.getSize() / 2

    def update(self, seconds):
        self.position += self.velocity * seconds
        self.lifetime -= seconds
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, drawSurface):
        angle = -np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        rotatedImage = pygame.transform.rotate(self.image, angle)

        screenPosition = self.position - Drawable.CAMERA_OFFSET
        imageSize = self.getSize()
        center = (int(screenPosition[0] + imageSize[0] / 2),
                  int(screenPosition[1] + imageSize[1] / 2))
        drawRect = rotatedImage.get_rect(center=center)
        drawSurface.blit(rotatedImage, drawRect)

    def getRect(self):
        imageSize = self.getSize()
        return pygame.Rect(int(self.position[0]),
                           int(self.position[1]),
                           int(imageSize[0]),
                           int(imageSize[1]))