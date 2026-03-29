from .patrollingEnemy import PatrollingEnemy

import pygame


class MonsterSlime(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Monster_Slime-Sheet.png")

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
        body_width = full_size[0] * 0.5
        body_height = full_size[1] * 0.5

        offset_x = (full_size[0] - body_width) / 2
        offset_y = (full_size[1] - body_height) / 2

        return pygame.Rect(int(self.position[0] + offset_x), int(self.position[1] + offset_y),
                           int(body_width), int(body_height))

    def getCrowdRect(self):
        full_size = self.getSize()
        crowd_width = full_size[0] * 0.5
        crowd_height = full_size[1] * 0.5

        offset_x = (full_size[0] - crowd_width) / 2
        offset_y = (full_size[1] - crowd_height) / 2

        return pygame.Rect(int(self.position[0] + offset_x), int(self.position[1] + offset_y),
                           int(crowd_width), int(crowd_height))