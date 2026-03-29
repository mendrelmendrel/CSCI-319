from . import Mobile
from FSMs import WalkingFSM, AttackFSM
from utils import vec, WORLD_SIZE, normalize, magnitude

import pygame

class PatrollingEnemy(Mobile):
    def __init__(self, position, minX, maxX, spriteName="Orc.png"):
        super().__init__(position, spriteName)

        self.maxHp = 2
        self.hp = self.maxHp
        
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
            "moving"   : 8,
            "standing" : 6,
            "hurting"     : 4
        }
        
        self.rowList = {
            "moving"   : 1,
            "standing" : 0,
            "hurting"     : 4
        }
        
        self.framesPerSecondList = {
            "moving"   : 12,
            "standing" : 8,
            "hurting"     : 4
        }
        
        self.frame = 0
        self.animationTimer = 0
        self.row = 0
        
        # Animation FSM
        self.FSManimated = AttackFSM(self)
    #returns the full sprite sized rect for collision with player attacks and colllisions
    def getFullBodyRect(self):

        return pygame.Rect(self.position[0], self.position[1],
                                    self.getSize()[0], self.getSize()[1])
    #returns a smaller rect in the center of the sprite for collision with other enemies                               
    def getCrowdRect(self):
        full_size = self.getSize()
        half_width = full_size[0] * 0.5
        half_height = full_size[1] * 0.5
        
        offset_x = (full_size[0] - half_width) / 2
        offset_y = (full_size[1] - half_height) / 2
        
        return pygame.Rect(int(self.position[0] + offset_x), int(self.position[1] + offset_y),
                          int(half_width), int(half_height))
    
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