from .patrollingEnemy import PatrollingEnemy

from utils import magnitude

import pygame


class SickleBoss(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="sickle_sheet.png")

        self.isBoss = True
        self.maxHp = 30
        self.hp = self.maxHp

        self.attackRange = 150
        self.attackCooldown = 2.0
        self.attackCooldownTimer = 0.6
        self.attackDamage = 1
        self.attackHasHit = False

        self.nFramesList = {
            "moving": 5,
            "standing": 1,
            "hurting": 4,
            "attacking": 7,
        }

        self.rowList = {
            "moving": 1,
            "standing": 0,
            "hurting": 4,
            "attacking": 3,
        }

        self.framesPerSecondList = {
            "moving": 8,
            "standing": 6,
            "hurting": 8,
            "attacking": 10,
        }

        self.FSManimated.on_enter_state()

    def update(self, seconds):
        if self.attackCooldownTimer > 0:
            self.attackCooldownTimer -= seconds

        if self == "attacking":
            if self.FSManimated.attackTimer <= 0:
                self.attackHasHit = False
        else:
            self.attackHasHit = False

            if self.player and self.attackCooldownTimer <= 0:
                toPlayer = self.player.position - self.position
                if magnitude(toPlayer) <= self.attackRange:
                    self.FSManimated.startAttack()
                    self.attackCooldownTimer = self.attackCooldown

        super().update(seconds)

    def canDamagePlayer(self):
        if self != "attacking" or self.attackHasHit:
            return False

        if self.FSManimated.attackDuration <= 0:
            return False

        progress = 1 - max(self.FSManimated.attackTimer, 0) / self.FSManimated.attackDuration
        return 0.35 <= progress <= 0.85

    def getAttackRect(self):
        size = self.getSize()
        return pygame.Rect(int(self.position[0] - size[0] * 0.25),
                           int(self.position[1] - size[1] * 0.25),
                           int(size[0] * 1.5),
                           int(size[1] * 1.5))

    def markAttackHit(self):
        self.attackHasHit = True