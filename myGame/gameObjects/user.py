"""
User (Player Character) - Controls the player avatar and all player mechanics.

The User class represents the playable character in the game. It inherits from Mobile
and handles all player-controlled actions including movement, attacks, shooting, and dash
mechanics. The character is animated with a finite state machine (FSM) that manages
transitions between standing, moving, attacking, shooting, and hurt states.

Player Mechanics:
- Movement: WASD or Arrow keys for 8-directional movement with acceleration/deceleration
- Melee Attack: Left-click to perform directional melee attack (LR/Up/Down)
- Ranged Attack: Right-click to shoot arrows with targeting/auto-aim toward enemies
- Dash: Hold movement key(s) to prepare, release to dash in that direction
- Health: 10 HP with heart pickup recovery, hurt animation on damage

Animation System:
- Separate sprite rows for each action (moving, standing, attacking, shooting, hurting)
- Attack animations split LR/Up/Down for directional variations (melee ranges differ by direction)  
- Shooting animations also directional (projectiles travel in aimed direction)
- FSM-driven state transitions with animation frame synchronization

Hitbox System:
- Melee attack hitbox only active during specific animation frames (2-4)
- Hitbox size and position varies by attack direction (vertical attacks are wider/chainer)
- Player collision box used for damage reception from enemies and boss attacks
- Body center defines ragdoll/knockback calculations and visual alignment
"""
from . import Mobile
from .drawable import Drawable
from .arrow import Arrow
from FSMs import AttackFSM, AccelerationFSM
from utils import vec, RESOLUTION, magnitude
from utils.soundManager import SoundManager

from pygame.locals import *

import pygame
import numpy as np


class User(Mobile):
   def __init__(self, position):
      super().__init__(position, "soldiersprite.png")

      self.leftKeys = {K_a, K_LEFT}
      self.rightKeys = {K_d, K_RIGHT}
      self.upKeys = {K_w, K_UP}
      self.downKeys = {K_s, K_DOWN}

      self.nFramesList = {
         "moving"   : 8,
         "standing" : 6,
         "attackingLR" : 6,
         "attackingUp" : 6,
         "attackingDown" : 6,
         "attacking" : 6,
         "shootingLR" : 9,
         "shooting" : 9,
         "shootingUp" : 9,
         "shootingDown" : 9,
         "hurting" : 4
      }

      self.rowList = {
         "moving"   : 1,
         "standing" : 0,
         "attackingLR" : 2,
         "attackingUp" : 10,
         "attackingDown" : 9,
         "attacking" : 2,
         "shootingLR" : 4,
         "shooting" : 4,
         "shootingUp" : 7,
         "shootingDown" : 8,
         "hurting" : 5
      }

      self.framesPerSecondList = {
         "moving"   : 12,
         "standing" : 7,
         "attackingLR" :25,
         "attackingUp" :25,
         "attackingDown" :25,
         "attacking" :25,
         "shootingLR" : 14,
         "shooting" : 14,
         "shootingUp" : 14,
         "shootingDown" : 14,
         "hurting" : 4
      }

      self.attackAnimationFileByKey = {
         "attackingLR" : "soldiersprite.png",
         "attackingUp" : "soldiersprite.png",
         "attackingDown" : "soldiersprite.png"
      }

      self.defaultAttackAnimationKey = "attackingLR"
      self.upAttackAnimationKey = "attackingUp"
      self.downAttackAnimationKey = "attackingDown"
      self.lastAttackAnimationKey = self.defaultAttackAnimationKey
      self.currentAttackAnimationKey = self.defaultAttackAnimationKey

      # Inclusive active frame windows where melee collision is enabled.
      # Tune these values per attack animation.
      self.attackActiveFrames = {
         "attackingLR": (2, 4),
         "attackingUp": (2, 4),
         "attackingDown": (2, 4)
      }

      self.attackHitboxSizes = {
         "attackingLR": (32, 60),
         "attackingUp": (60, 32),
         "attackingDown": (60, 32)
      }

      self.attackVerticalEnterRatio = 1.2
      self.attackSideEnterRatio = 1.2

      self.defaultShootAnimationKey = "shootingLR"
      self.upShootAnimationKey = "shootingUp"
      self.downShootAnimationKey = "shootingDown"
      self.lastShootAnimationKey = self.defaultShootAnimationKey

      # Hysteresis around the diagonal boundary to prevent flicker.
      # Vertical activates only when |dy| is this much larger than |dx|,
      # and side activates only when |dx| is this much larger than |dy|.
      self.shootVerticalEnterRatio = 1.2
      self.shootSideEnterRatio = 1.2

      self.FSManimated = AttackFSM(self)
      self.LR = AccelerationFSM(self, axis=0)
      self.UD = AccelerationFSM(self, axis=1)

      # HP System
      self.maxHp = 10
      self.hp = self.maxHp

      # Dash System
      self.isDashing = False
      self.dashTimer = 0
      self.dashDistance = 100  # Pixels to travel during dash
      self.dashDuration = 0.3 # How long dash takes in seconds
      self.dashDirection = vec(1, 0)  # Direction to dash

      # Track held keys for dash direction
      self.keysHeld = {
         'left': False,
         'right': False,
         'up': False,
         'down': False
      }

      self.arrows = []
      self.pendingShot = False
      self.pendingShotDirection = vec(1, 0)
      self.pendingShotTarget = None
      self.shootReleaseFrame = 8
      self.enemyTargets = []
      self.arrowLockRadius = 26

      # Body center is based on sprite dimensions so debug/collision stays aligned
      # even when animation crops change.
      self.bodyCenterRatio = vec(0.50, 0.62)
      self.bodyCenterNudge = vec(0, 0)

      self._setAttackAnimation(self.defaultAttackAnimationKey)
      
      
   def handleEvent(self, event):
      if event.type == KEYDOWN:
         if event.key in self.upKeys:
            self.UD.decrease()
            self.keysHeld['up'] = True
             
         elif event.key in self.downKeys:
            self.UD.increase()
            self.keysHeld['down'] = True
            
         elif event.key in self.leftKeys:
            self.LR.decrease()
            self.keysHeld['left'] = True
            
         elif event.key in self.rightKeys:
            self.LR.increase()
            self.keysHeld['right'] = True
            
         elif event.key == K_SPACE:
            # Start dash based on held direction keys
            if not self.isDashing:
               self.isDashing = True
               self.dashTimer = 0
               
               # Determine dash direction from held keys
               dashDir = vec(0, 0)
               if self.keysHeld['right']:
                  dashDir[0] = 1
               elif self.keysHeld['left']:
                  dashDir[0] = -1
               
               if self.keysHeld['down']:
                  dashDir[1] = 1
               elif self.keysHeld['up']:
                  dashDir[1] = -1
               
               # If no direction held, dash in the direction Kirby is facing
               if dashDir[0] == 0 and dashDir[1] == 0:
                  dashDir[0] = -1 if self.flipped else 1
               
               self.dashDirection = dashDir
         
      elif event.type == MOUSEBUTTONDOWN:
         mousePosition = Drawable.translateMousePosition(pygame.mouse.get_pos())

         if event.button == 1:  # Left click: melee attack
            self._selectAttackAnimation(mousePosition - self.getBodyCenter())
            self.FSManimated.startAttack()
            SoundManager.getInstance().playSFX("playerSlash.wav")

         elif event.button == 3:  # Right click: shoot
            self.shootArrow(mousePosition)
            
      elif event.type == KEYUP:
         if event.key in self.upKeys:
            self.UD.stop_decrease()
            self.keysHeld['up'] = False
             
         elif event.key in self.downKeys:
            self.UD.stop_increase()
            self.keysHeld['down'] = False
             
         elif event.key in self.leftKeys:
            self.LR.stop_decrease()
            self.keysHeld['left'] = False
            
         elif event.key in self.rightKeys:
            self.LR.stop_increase()
            self.keysHeld['right'] = False
   
   def update(self, seconds): 
      self.LR.update(seconds)
      self.UD.update(seconds)

      mousePosition = Drawable.translateMousePosition(pygame.mouse.get_pos())
      playerCenterX = self.getBodyCenter()[0]
      if mousePosition[0] < playerCenterX:
         self.flipped = True
      elif mousePosition[0] > playerCenterX:
         self.flipped = False
      
      # Handle dash
      if self.isDashing:
         self.dashTimer += seconds
         # Constant-speed dash: choose velocity so distance ~= speed * duration.
         self.velocity = self.dashDirection * (self.dashDistance / self.dashDuration)
         
         # End dash after duration
         if self.dashTimer >= self.dashDuration:
            self.isDashing = False
            
      
      super().update(seconds)

      if self.pendingShot and self.FSManimated.current_state.id != "shooting":
         self.pendingShot = False
         self.pendingShotTarget = None

      if self.pendingShot and self.FSManimated.current_state.id == "shooting":
         # Spawn projectile on a specific animation frame so visual release
         # and hit timing stay synced to the bow/shoot motion.
         if self.frame >= self.shootReleaseFrame:
            playerCenter = self.getBodyCenter()
            self.arrows.append(Arrow(playerCenter,
                                     self.pendingShotDirection,
                                     target=self.pendingShotTarget))
            self.pendingShot = False
            self.pendingShotTarget = None

   def shootArrow(self, mousePosition):
      playerCenter = self.getBodyCenter()
      shootTarget = mousePosition
      lockRadius = max(self.arrowLockRadius,
                       int(max(self.getDamageRect().width,
                               self.getDamageRect().height)))

      bestTarget = None
      bestHealthPercent = None
      bestDistance = None

      for enemy in self.enemyTargets:
         if not hasattr(enemy, "hp") or enemy.hp <= 0:
            continue

         if hasattr(enemy, "getFullBodyRect"):
            enemyRect = enemy.getFullBodyRect()
         else:
            enemySize = enemy.getSize() 
            enemyRect = pygame.Rect(int(enemy.position[0]),
                                    int(enemy.position[1]),
                                    int(enemySize[0]),
                                    int(enemySize[1]))

         enemyCenter = vec(enemyRect.centerx, enemyRect.centery)
         mouseToEnemy = enemyCenter - mousePosition
         distanceToMouse = magnitude(mouseToEnemy)

         # Only soft-lock targets near cursor; preserves player aim intent.
         if distanceToMouse > lockRadius:
            continue

         maxHp = getattr(enemy, "maxHp", enemy.hp if enemy.hp > 0 else 1)
         healthPercent = enemy.hp /maxHp

         # Priority: lowest HP% target first, then nearest-to-cursor as tie-break.
         if bestTarget is None or healthPercent < bestHealthPercent or \
            (healthPercent == bestHealthPercent and distanceToMouse < bestDistance):
            bestTarget = enemy
            bestHealthPercent = healthPercent
            bestDistance = distanceToMouse

      if bestTarget is not None:
         targetRect = bestTarget.getFullBodyRect() 
         shootTarget = vec(targetRect.centerx, targetRect.centery)

      shootDirection = shootTarget - playerCenter

      if magnitude(shootDirection) <= 0:
         shootDirection = vec(-1, 0) if self.flipped else vec(1, 0)

      absX = abs(shootDirection[0])
      absY = abs(shootDirection[1])

      # Ratio-based hysteresis prevents diagonal flicker between vertical/horizontal
      # animation choices when aim is near 45 degrees.
      if absY > (absX * self.shootVerticalEnterRatio):
         if shootDirection[1] < 0:
            selectedShootAnimation = self.upShootAnimationKey
         else:
            selectedShootAnimation = self.downShootAnimationKey
      elif absX > (absY * self.shootSideEnterRatio):
         selectedShootAnimation = self.defaultShootAnimationKey
      else:
         selectedShootAnimation = self.lastShootAnimationKey

      self._setShootAnimation(selectedShootAnimation)
      self.lastShootAnimationKey = selectedShootAnimation

      # Calculate and store the shooting angle
      self.shootingAngle = -np.degrees(np.arctan2(shootDirection[1], shootDirection[0]))
      
      # Store direction/target now; actual Arrow object is created later on the
      # configured release frame inside update().
      self.pendingShotDirection = shootDirection
      self.pendingShotTarget = bestTarget
      self.pendingShot = True
      self.FSManimated.startShoot()
      SoundManager.getInstance().playSFX("shoot.mp3")

   def _setShootAnimation(self, animationKey):
      self.rowList["shooting"] = self.rowList[animationKey]
      self.nFramesList["shooting"] = self.nFramesList[animationKey]
      self.framesPerSecondList["shooting"] = self.framesPerSecondList[animationKey]

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

   def _setAttackAnimation(self, animationKey):
      self.rowList["attacking"] = self.rowList[animationKey]
      self.nFramesList["attacking"] = self.nFramesList[animationKey]
      self.framesPerSecondList["attacking"] = self.framesPerSecondList[animationKey]
      self.currentAttackAnimationKey = animationKey

      self.attackAnimationSheet = self.attackAnimationFileByKey.get(
         animationKey,
         self.imageName
      )

   def getAnimationSheet(self, state):
      if state == "attacking":
         return self.attackAnimationSheet

      return self.imageName

   def getBodyCenter(self):
      spriteSize = self.getSize()
      return vec(self.position[0] + (spriteSize[0] * self.bodyCenterRatio[0])
              + self.bodyCenterNudge[0],
              self.position[1] + (spriteSize[1] * self.bodyCenterRatio[1])
              + self.bodyCenterNudge[1])
      
   def getAttackHitbox(self):
      """Returns a Rect for the weapon hitbox during attack, or None if not attacking."""
      
      #The hitbox represents the actual weapon portion of the sprite.
      if self.FSManimated.current_state.id != "attacking":
         return None

      activeWindow = self.attackActiveFrames.get(self.currentAttackAnimationKey)
      if activeWindow is not None:
         activeStart, activeEnd = activeWindow
         if self.frame < activeStart or self.frame > activeEnd:
            return None

      # Anchor sword hitbox to the player's body rect so it matches visuals.
      playerRect = self.getDamageRect()

      weaponWidth, weaponHeight = self.attackHitboxSizes.get(
         self.currentAttackAnimationKey,
         self.attackHitboxSizes["attackingLR"]
      )

      if self.currentAttackAnimationKey == self.upAttackAnimationKey:
         weaponX = playerRect.centerx - (weaponWidth // 2)
         weaponY = playerRect.top - weaponHeight
      elif self.currentAttackAnimationKey == self.downAttackAnimationKey:
         weaponX = playerRect.centerx - (weaponWidth // 2)
         weaponY = playerRect.bottom
      else:
         weaponY = playerRect.centery - (weaponHeight // 2)
         if self.flipped:  # Facing left
            weaponX = playerRect.left - weaponWidth
         else:  # Facing right
            weaponX = playerRect.right

      return pygame.Rect(int(weaponX), int(weaponY),
                         int(weaponWidth), int(weaponHeight))
   
   def getDamageRect(self):
      # Keep the collision box as a small centered body box so visuals can be wider
      # without making hits register far away.
      damage_width = 14
      damage_height = 18
      bodyCenter = self.getBodyCenter()

      return pygame.Rect(
         int(bodyCenter[0] - (damage_width / 2)),
         int(bodyCenter[1] - (damage_height / 2)),
         damage_width,
         damage_height
      )


# Backward-compatible alias while code is migrating from Kirby -> User.
Kirby = User
   

