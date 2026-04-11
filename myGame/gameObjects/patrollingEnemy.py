"""PatrollingEnemy - Base class for all standard enemies with patrol/pursuit AI.

The PatrollingEnemy class is the foundation for all non-boss enemy types (Orc, Slime,
Human Soldier). It provides patrol behavior between min/max bounds, player tracking,
and basic FSM-driven animation. Subclasses override speed/HP for balance tuning.

Enemy Behavior:
- Patrol: Moves left/right between minX/maxX bounds at constant speed
- Boundary Wrapping: Reverses direction on world edge or path limit collision
- Player Reference: Stores reference to player for combat system integration
- Animation FSM: Drives state transitions (standing/moving/hurting/attacking)

Hitbox System:
- getFullBodyRect(): Full sprite collision used for damageable hitbox
- getCrowdRect(): Smaller centered box for enemy-to-enemy separation only
"""
from . import Mobile
from FSMs import AttackFSM
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

    # Full sprite collision used for player attacks and direct body contact.
    def getFullBodyRect(self):

        return pygame.Rect(self.position[0], self.position[1],
                                    self.getSize()[0], self.getSize()[1])
    # Smaller center rect used only for enemy crowd-separation pushes.
    def getCrowdRect(self):
        full_size = self.getSize()
        half_width = full_size[0] * 0.5
        half_height = full_size[1] * 0.5
        
        offset_x = (full_size[0] - half_width) / 2
        offset_y = (full_size[1] - half_height) / 2
        
        return pygame.Rect(int(self.position[0] + offset_x), int(self.position[1] + offset_y),
                          int(half_width), int(half_height))

    def _clampToWorldBounds(self):
        clamped = False

        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
            clamped = True
        elif self.position[0] + self.getSize()[0] > WORLD_SIZE[0]:
            self.position[0] = WORLD_SIZE[0] - self.getSize()[0]
            self.velocity[0] = 0
            clamped = True

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0
            clamped = True
        elif self.position[1] + self.getSize()[1] > WORLD_SIZE[1]:
            self.position[1] = WORLD_SIZE[1] - self.getSize()[1]
            self.velocity[1] = 0
            clamped = True

        # Returned for callers that may want to react to boundary contact.
        return clamped
    
    def update(self, seconds):
        # Simple chase AI: steer directly toward player's current position.
        # (Uses player's position vector, not damage-rect center.)
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
        
        # Mobile.update handles animation tick + velocity integration.
        super().update(seconds)
        self._clampToWorldBounds()