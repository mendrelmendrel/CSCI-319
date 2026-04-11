"""
KnightEnemy (Boss Enemy) - The primary boss enemy with kinda advanced combat AI.

The KnightEnemy class represents the main boss enemy encountered in the game's boss phase.
It inherits from PatrollingEnemy and adds complex behavior including directional attacks,
a dash-attack capability, health-based difficulty scaling.

Boss Mechanics:
- Health Scaling: 30 HP (3x standard enemies) with health-based AI logic
- Dual Attack Modes: Melee attack (2 damage) or dash-attack (3 damage) based on strategy
- Movement: Patrols patrol boundaries and actively pursues player when attacking
- Recovery: Attack and dash abilities have cooldowns (0.9s and 1.5s respectively)

AI Behavior:
- Low Health Strategy: When HP < 33%, increases aggression (shorter cooldowns, prefers dash)
- Attack Selection: Chooses directional melee (LR/Up/Down) based on player position
- Dash Logic: Targets player position when dashing; can travel ~270 pixels
- Knockback: Can be pushed by player melee, knockback affects dash targeting

Combat Timing:
- Attack animations: 8 frames at 24 FPS (~0.33s attack duration)
- Dash animations: 6 frames at 24 FPS (~0.25s dash duration)
- Attack cooldown: 0.9s between melee attacks
- Dash cooldown: 1.5s between dash-attacks

Hitbox System:
- Directional weapon hitboxes (34x74 LR, 74x34 Up/Down, 74x34 Down)
- Attack frames only active during specific animation windows
- Can damage player via melee attack or dash landing
- Boss status tracked via isBoss flag for phase transition logic
"""
from .patrollingEnemy import PatrollingEnemy
from utils import vec, WORLD_SIZE, normalize, magnitude
from utils.soundManager import SoundManager

import pygame


class KnightEnemy(PatrollingEnemy):
    def __init__(self, position, minX, maxX):
        super().__init__(position, minX, maxX, spriteName="Knight.png")

        self.speed = 140
        self.dashSpeed = 320
        self.maxHp = 30
        self.hp = self.maxHp

        self.lowHealthThreshold = 0.33
        self.attackRange = 64
        self.attackCooldown = 0.9
        self.attackCooldownTimer = 0.0

        self.dashCooldown = 1.5
        self.dashCooldownTimer = 0.0
        self.dashDistance = 270
        self.dashDistanceTraveled = 0.0
        self.dashStopDistance = 10
        self.isDashing = False
        self.dashTargetPos = None

        self.attackDamage = 2
        self.dashDamage = 3
        self.currentDamageMode = None
        self.attackHasHit = False

        self.weaponHitboxSizeLR = (34, 74)
        self.weaponHitboxSizeUp = (74, 34)
        self.weaponHitboxSizeDown = (74, 34)
         
        self.defaultAttackAnimationKey = "attackingLR"
        self.upAttackAnimationKey = "attackingUp"
        self.downAttackAnimationKey = "attackingDown"
        self.lastAttackAnimationKey = self.defaultAttackAnimationKey
        self.currentAttackAnimationKey = self.defaultAttackAnimationKey

        self.attackVerticalEnterRatio = 1.2
        self.attackSideEnterRatio = 1.2

        self.nFramesList = {
            "moving": 6,
            "standing": 6,
            "hurting": 4,
            "attackingLR": 8,
            "attackingUp": 8,
            "attackingDown": 8,
            "attacking": 8,
            "dashing": 6,
        }

        self.rowList = {
            "moving": 0,
            "standing": 0,
            "hurting": 3,
            "attackingLR": 2,
            "attackingUp": 2,
            "attackingDown": 2,
            "attacking": 2,
            "dashing": 1,
        }

        self.framesPerSecondList = {
            "moving": 24,
            "standing":10,
            "hurting": 24,
            "attackingLR": 24,
            "attackingUp": 24,
            "attackingDown": 24,
            "attacking": 24,
            "dashing": 24,
        }

        self.bodyWidthRatio = 0.28
        self.bodyHeightRatio = 0.80
        self.crowdWidthRatio = 0.40
        self.crowdHeightRatio = 0.42
        self.centerXOffset = -20
        self.flipDeadzoneX = 10

        self._setAttackAnimation(self.defaultAttackAnimationKey)

        self.FSManimated.on_enter_state()

    def getAnimationStateKey(self, state):
        if getattr(self, "isDashing", False) and state in ["moving", "standing"]:
            return "dashing"
        return state

    def _getBodyCenter(self):
        bodyRect = self.getFullBodyRect()
        return vec(bodyRect.centerx, bodyRect.centery)

    def _getVisualCenter(self):
        size = self.getSize()
        return vec(self.position[0] + (size[0] / 2),
                   self.position[1] + (size[1] / 2))

    def _getPlayerCenter(self):
        if self.player is None:
            return None

        if hasattr(self.player, "getDamageRect"):
            playerRect = self.player.getDamageRect()
            return vec(playerRect.centerx, playerRect.centery)

        return self.player.position + (self.player.getSize() / 2)

    def _isLowHealthPhase(self):
        return (self.hp / max(self.maxHp, 1)) <= self.lowHealthThreshold

    def _setAttackAnimation(self, animationKey):
        self.rowList["attacking"] = self.rowList[animationKey]
        self.nFramesList["attacking"] = self.nFramesList[animationKey]
        self.framesPerSecondList["attacking"] = self.framesPerSecondList[animationKey]
        self.currentAttackAnimationKey = animationKey

    def _selectAttackAnimation(self, attackDirection):
        if magnitude(attackDirection) <= 0:
            attackDirection = vec(-1, 0) if self.flipped else vec(1, 0)

        absX = abs(attackDirection[0])
        absY = abs(attackDirection[1])

        if absY > (absX * self.attackVerticalEnterRatio):
            if attackDirection[1] < 0:
                selectedAttackAnimation = self.upAttackAnimationKey
            else:
                selectedAttackAnimation = self.downAttackAnimationKey
        elif absX > (absY * self.attackSideEnterRatio):
            selectedAttackAnimation = self.defaultAttackAnimationKey
        else:
            selectedAttackAnimation = self.lastAttackAnimationKey

        self._setAttackAnimation(selectedAttackAnimation)
        self.lastAttackAnimationKey = selectedAttackAnimation

    def _startAttack(self, attackDirection):
        self.velocity = vec(0, 0)
        self._selectAttackAnimation(attackDirection)
        self.attackDamage = 2
        self.currentDamageMode = "attack"
        self.attackHasHit = False
        self.FSManimated.startAttack()
        SoundManager.getInstance().playSFX("bossSlash.mp3")
        self.attackCooldownTimer = self.attackCooldown

    def _startDash(self, targetPos):
        if targetPos is None:
            return

        knightCenter = self._getBodyCenter()
        dashDirection = targetPos - knightCenter
        if magnitude(dashDirection) <= 0:
            dashDirection = vec(-1, 0) if self.flipped else vec(1, 0)

        self.isDashing = True
        self.dashDistanceTraveled = 0.0
        # Snapshot target at dash start so dash is committed, not fully homing.
        self.dashTargetPos = vec(targetPos[0], targetPos[1])
        self.velocity = normalize(dashDirection) * self.dashSpeed
        self.attackDamage = self.dashDamage
        self.currentDamageMode = "dash"
        self.attackHasHit = False
        SoundManager.getInstance().playSFX("bossSlash.mp3")
        self.dashCooldownTimer = self.dashCooldown

    def _endDash(self):
        self.isDashing = False
        self.dashDistanceTraveled = 0.0
        self.dashTargetPos = None
        self.velocity = vec(0, 0)
        self.currentDamageMode = None
        self.attackHasHit = False

    def update(self, seconds):
        if self.attackCooldownTimer > 0:
            self.attackCooldownTimer -= seconds
        if self.dashCooldownTimer > 0:
            self.dashCooldownTimer -= seconds

        state = self.FSManimated.current_state.id
        playerCenter = self._getPlayerCenter()
        knightCenter = self._getBodyCenter()
        visualCenter = self._getVisualCenter()

        if playerCenter is not None:
            deltaX = playerCenter[0] - visualCenter[0]
            if deltaX < -self.flipDeadzoneX:
                self.flipped = True
            elif deltaX > self.flipDeadzoneX:
                self.flipped = False

        if state == "hurting":
            self._endDash()

        if self.isDashing:
            self.dashDistanceTraveled += magnitude(self.velocity) * seconds

            if self.dashTargetPos is not None:
                toTarget = self.dashTargetPos - knightCenter
                if magnitude(toTarget) <= self.dashStopDistance:
                    self._endDash()

            # Secondary fail-safe so dash always terminates even if target keeps moving.
            if self.isDashing and self.dashDistanceTraveled >= self.dashDistance:
                self._endDash()

        elif state not in ["attacking", "hurting"]:
            self.velocity = vec(0, 0)

            if playerCenter is not None:
                toPlayer = playerCenter - knightCenter
                distanceToPlayer = magnitude(toPlayer)
                inAttackRange = distanceToPlayer <= self.attackRange

                if not self._isLowHealthPhase():
                    if inAttackRange:
                        if self.attackCooldownTimer <= 0:
                            self._startAttack(toPlayer)
                    elif distanceToPlayer > 0:
                        self.velocity = normalize(toPlayer) * self.speed
                else:
                    if inAttackRange and self.attackCooldownTimer <= 0:
                        self._startAttack(toPlayer)
                    elif (not inAttackRange) and self.dashCooldownTimer <= 0:
                        self._startDash(playerCenter)

        currentState = self.FSManimated.current_state.id
        if self.currentDamageMode == "attack" and currentState != "attacking":
            self.currentDamageMode = None
            self.attackHasHit = False

        # Intentionally call Mobile.update (skipping PatrollingEnemy.update) to avoid
        # re-running base chase AI after boss-specific velocity decisions above.
        super(PatrollingEnemy, self).update(seconds)
        self._clampToWorldBounds()

    def canDamagePlayer(self):
        if self.attackHasHit:
            return False

        if self.currentDamageMode == "dash":
            return self.isDashing

        if self.currentDamageMode == "attack" and self.FSManimated.current_state.id == "attacking":
            if self.FSManimated.attackDuration <= 0:
                return False

            # Damage only during middle of swing. Startup and recovery frames are safe.
            progress = 1 - max(self.FSManimated.attackTimer, 0) / self.FSManimated.attackDuration
            return 0.35 <= progress <= 0.85

        return False

    def getAttackRect(self):
        if self.currentDamageMode == "dash" and self.isDashing:
            bodyRect = self.getFullBodyRect()
            return pygame.Rect(int(bodyRect.x), int(bodyRect.y),
                               int(bodyRect.width), int(bodyRect.height))

        bodyRect = self.getFullBodyRect()
        if self.currentAttackAnimationKey == self.upAttackAnimationKey:
            width, height = self.weaponHitboxSizeUp
            weaponX = bodyRect.centerx - (width // 2)
            weaponY = bodyRect.top - height
        elif self.currentAttackAnimationKey == self.downAttackAnimationKey:
            width, height = self.weaponHitboxSizeDown
            weaponX = bodyRect.centerx - (width // 2)
            weaponY = bodyRect.bottom
        else:
            width, height = self.weaponHitboxSizeLR
            weaponY = bodyRect.centery - (height // 2)
            if self.flipped:
                weaponX = bodyRect.left - width
            else:
                weaponX = bodyRect.right

        return pygame.Rect(int(weaponX), int(weaponY),
                           int(width), int(height))

    def markAttackHit(self):
        self.attackHasHit = True

    def getFullBodyRect(self):
        full_size = self.getSize()
        body_width = max(1, int(full_size[0] * self.bodyWidthRatio))
        body_height = max(1, int(full_size[1] * self.bodyHeightRatio))
        centerXShift = -self.centerXOffset if self.flipped else self.centerXOffset

        body_x = int(self.position[0] + ((full_size[0] - body_width) / 2)
             + centerXShift)
        body_y = int(self.position[1] + ((full_size[1] - body_height) / 2))

        return pygame.Rect(body_x, body_y, body_width, body_height)

    def getCrowdRect(self):
        full_size = self.getSize()
        crowd_width = max(1, int(full_size[0] * self.crowdWidthRatio))
        crowd_height = max(1, int(full_size[1] * self.crowdHeightRatio))
        centerXShift = -self.centerXOffset if self.flipped else self.centerXOffset

        crowd_x = int(self.position[0] + ((full_size[0] - crowd_width) / 2)
              + centerXShift)
        crowd_y = int(self.position[1] + ((full_size[1] - crowd_height) / 2))

        return pygame.Rect(crowd_x, crowd_y, crowd_width, crowd_height)