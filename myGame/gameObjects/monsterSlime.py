"""MonsterSlime Module - Weakest enemy type designed for early-game threat.

The MonsterSlime is the first enemy encountered and serves as an entry-level threat.
It's the slowest (60 px/s, 30% of player speed) and weakest (1 HP) enemy, ideal for
learning combat mechanics. Uses customized hitbox rects for both collision and crowd
separation to match its blobby body shape.

Stats:
- Speed: 60 px/s (30% of player speed)
- Health: 1 HP (one-shot by melee or arrow)
- Sprite: Monster_Slime-Sheet.png with custom hitboxes
- Special: Custom collision rects (55% width for body, 36% for crowd separation)
"""
from .patrollingEnemy import PatrollingEnemy

import pygame


class MonsterSlime(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Monster_Slime-Sheet.png")

        # Set speed to 30% of player speed (200 * 0.3 = 60)
        self.speed = 60
        # Set HP to 1
        self.maxHp = 1
        self.hp = self.maxHp

        self.nFramesList = {
            "moving": 8,
            "standing": 6,
            "hurting": 4,
            "attacking": 8
        }

        self.rowList = {
            "moving": 1,
            "standing": 0,
            "hurting": 6,
            "attacking": 4
        }

        self.framesPerSecondList = {
            "moving": 10,
            "standing": 6,
            "hurting": 8,
            "attacking": 12
        }

        self.FSManimated.on_enter_state()

    def getFullBodyRect(self):
        full_size = self.getSize()
        body_width = max(1, int(full_size[0] * 0.55))
        body_height = max(1, int(full_size[1] * 0.50))

        body_x = int(self.position[0] + ((full_size[0] - body_width) / 2))
        body_y = int(self.position[1] + ((full_size[1] - body_height) / 2))

        return pygame.Rect(body_x, body_y, body_width, body_height)

    def getCrowdRect(self):
        full_size = self.getSize()
        crowd_width = max(1, int(full_size[0] * 0.36))
        crowd_height = max(1, int(full_size[1] * 0.34))

        crowd_x = int(self.position[0] + ((full_size[0] - crowd_width) / 2))
        crowd_y = int(self.position[1] + ((full_size[1] - crowd_height) / 2))

        return pygame.Rect(crowd_x, crowd_y, crowd_width, crowd_height)