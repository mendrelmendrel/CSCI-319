from . import Mobile
from .drawable import Drawable
from .arrow import Arrow
from FSMs import AttackFSM, AccelerationFSM
from utils import vec, RESOLUTION, magnitude

from pygame.locals import *

import pygame
import numpy as np


class Kirby(Mobile):
   def __init__(self, position):
      super().__init__(position, "Soldier.png")

      self.leftKeys = {K_a, K_LEFT}
      self.rightKeys = {K_d, K_RIGHT}
      self.upKeys = {K_w, K_UP}
      self.downKeys = {K_s, K_DOWN}
   
      
      self.nFramesList = {
         "moving"   : 8,
         "standing" : 6,
         "attacking" : 6,
         "shooting" : 9,
         "hurting" : 4
      }
      
      self.rowList = {
         "moving"   : 1,
         "standing" : 0,
         "attacking" : 2,
         "shooting" : 4,
         "hurting" : 5
      }
      
      self.framesPerSecondList = {
         "moving"   : 12,
         "standing" : 7,
         "attacking" :25,
         "shooting" : 14,
         "hurting" : 4
      }
            
      self.FSManimated = AttackFSM(self)
      self.LR = AccelerationFSM(self, axis=0)
      self.UD = AccelerationFSM(self, axis=1)

      # HP System
      self.maxHp = 45
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
      self.shootReleaseFrame = 8
      
      
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
            
         elif event.key == K_LSHIFT or event.key == K_RSHIFT:
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
         
         elif event.key == K_SPACE:
            # Trigger attack - FSM handles animation and timing
            self.FSManimated.startAttack()

         elif event.key == K_q:
            mousePosition = Drawable.translateMousePosition(pygame.mouse.get_pos())
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
      playerCenterX = self.position[0] + (self.getSize()[0] / 2)
      if mousePosition[0] < playerCenterX:
         self.flipped = True
      elif mousePosition[0] > playerCenterX:
         self.flipped = False
      
      # Handle dash
      if self.isDashing:
         self.dashTimer += seconds
         # Calculate velocity needed to travel dashDistance in dashDuration time
         self.velocity = self.dashDirection * (self.dashDistance / self.dashDuration)
         
         # End dash after duration
         if self.dashTimer >= self.dashDuration:
            self.isDashing = False
            
      
      super().update(seconds)

      if self.pendingShot and self.FSManimated.current_state.id != "shooting":
         self.pendingShot = False

      if self.pendingShot and self.FSManimated.current_state.id == "shooting":
         if self.frame >= self.shootReleaseFrame:
            playerCenter = self.position + (self.getSize() / 2)
            self.arrows.append(Arrow(playerCenter, self.pendingShotDirection))
            self.pendingShot = False

   def shootArrow(self, mousePosition):
      playerCenter = self.position + (self.getSize() / 2)
      shootDirection = mousePosition - playerCenter

      if magnitude(shootDirection) <= 0:
         shootDirection = vec(-1, 0) if self.flipped else vec(1, 0)

      self.pendingShotDirection = shootDirection
      self.pendingShot = True
      self.FSManimated.startShoot()
      
   def getAttackHitbox(self):
      """Returns a Rect for the weapon hitbox during attack, or None if not attacking.
      
      The hitbox represents the actual weapon portion of the sprite.
      Weapon dimensions: 24px wide (12 original × 2 scale), 44px tall
      """
      # Only create hitbox if currently in attacking state
      if self.FSManimated.current_state.id != "attacking":
         return None
      
      # Get player's current position and size
      playerSize = self.getSize()  # Returns vec(36, 44) after crop/scale
      playerX = self.position[0]
      playerY = self.position[1]
      
      # Weapon dimensions (from sprite measurements)
      weaponWidth = 24   # 12 pixels original × 2 scale
      weaponHeight = 44  # 22 pixels original × 2 scale (same height as player)
      
      # Calculate weapon hitbox position based on facing direction
      if self.flipped:  # Facing left
         # Weapon appears to the left of player
         weaponX = playerX - weaponWidth  # Weapon extends to the left
         weaponY = playerY                 # Aligned with player top
      else:  # Facing right
         # Weapon appears to the right of player
         weaponX = playerX + playerSize[0]  # Start at right edge of player
         weaponY = playerY                   # Aligned with player top
      
      # Create and return the weapon rectangle
      return pygame.Rect(weaponX, weaponY, weaponWidth, weaponHeight)
   
   def getDamageRect(self):
      full_size = self.getSize()
      damage_width = int(full_size[0] * 0.75)
      damage_height = int(full_size[1] * 0.75)

      offset_x = int((full_size[0] - damage_width) / 2)
      offset_y = int((full_size[1] - damage_height) / 2)

      return pygame.Rect(
         int(self.position[0] + offset_x),
         int(self.position[1] + offset_y),
         damage_width,
         damage_height
      )
   
   