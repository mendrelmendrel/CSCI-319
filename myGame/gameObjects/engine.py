import pygame
import random

from .drawable import Drawable
from .kirby import Kirby
from .orcEnemy import OrcEnemy
from .waddleDee import WaddleDee

from utils import vec, WORLD_SIZE, normalize, magnitude

class GameEngine(object):
    import pygame

    def __init__(self):       
        self.kirby = Kirby((0,0))   
        self.enemies = [
            # OrcEnemy((400,100), 300, 500),
            # WaddleDee((600, 300), 550, 750)
        ]
        # Set player reference so enemies can track the player
        # for enemy in self.enemies:
        #     enemy.player = self.kirby
        self.size = WORLD_SIZE
        self.background = Drawable((0,0), "background.png")
        self.collisionCooldown = 0
        
        # Enemy spawn system
        # self.spawnTimer = 0
        # self.spawnRate = 100  # Spawn new enemy every 2 seconds
    
    def draw(self, drawSurface):        
        self.background.draw(drawSurface)
        for enemy in self.enemies:
            enemy.draw(drawSurface)
        self.kirby.draw(drawSurface)

        # Draw HP counter
        font = pygame.font.Font(None, 36)
        hp_text = font.render(f"HP: {self.kirby.hp}/{self.kirby.maxHp}", True, (255, 0, 0))
        drawSurface.blit(hp_text, (10, 10))
        
    def handleEvent(self, event):
        self.kirby.handleEvent(event)
    
    def checkCollisions(self):
        # Decrement cooldown
        self.collisionCooldown -= 1
        
        # Get Kirby's body rect (for collision damage)
        kirbyRect = pygame.Rect(self.kirby.position[0], self.kirby.position[1], 
                                self.kirby.getSize()[0], self.kirby.getSize()[1])
        
        # Get attack hitbox (only exists when attacking, returns None otherwise)
        attackHitbox = self.kirby.getAttackHitbox()
        
        # Check if kirby is attacking
        isAttacking = self.kirby.FSManimated.current_state.id == "attacking"
        
        # If attack just ended, clear hit tracking flags on all enemies
        if not isAttacking:
            for enemy in self.enemies:
                if hasattr(enemy, '_hitThisAttack'):
                    delattr(enemy, '_hitThisAttack')
        
        # Check collision with each enemy
        for enemy in self.enemies:
            enemyRect = pygame.Rect(enemy.position[0], enemy.position[1],
                                    enemy.getSize()[0], enemy.getSize()[1])
            
            # Check if attack hitbox hits enemy
            if attackHitbox and attackHitbox.colliderect(enemyRect):
                # Damage from attack (hits enemy once per attack)
                if not hasattr(enemy, '_hitThisAttack'):
                    enemy._hitThisAttack = True  # Mark so we don't hit again this attack
                    # TODO: Add enemy.hp -= 1 when enemies have health system
            
            # Check if player body touches enemy (separate from attack)
            if kirbyRect.colliderect(enemyRect):
                # Damage player from collision (only when not attacking, with cooldown)
                if not isAttacking and self.collisionCooldown <= 0:
                    self.kirby.hp -= 1
                    self.collisionCooldown = 30
                
                # Calculate direction from enemy to player for knockback
                direction = self.kirby.position - enemy.position
                direction_length = magnitude(direction)
                
                if direction_length > 0:
                    direction = normalize(direction)
                
                # Knockback force
                knockback = 200
                
                # Apply opposite velocities (push player and enemy apart)
                self.kirby.velocity += direction * knockback
                enemy.velocity -= direction * knockback
    
    def update(self, seconds):
        # Update spawn timer and spawn new enemies
        # self.spawnTimer += seconds
        # if self.spawnTimer >= self.spawnRate:
        #     self.spawnTimer = 0
        #     self._spawnRandomEnemy()
        
        self.kirby.update(seconds)
        for enemy in self.enemies:
            enemy.update(seconds)
        self.checkCollisions()
        
        # Remove dead enemies
        
        Drawable.updateOffset(self.kirby, self.size)
    
    def _spawnRandomEnemy(self):
        """Spawn a new Orc enemy at a random location on the map."""
        # Random position with padding (50px from edges)
        x = random.uniform(50, WORLD_SIZE[0] - 100)
        y = random.uniform(50, WORLD_SIZE[1] - 100)
        
        # Create new OrcEnemy at random position
        enemy = OrcEnemy((x, y), 0, WORLD_SIZE[0])
        
        # Set player reference so enemy can track player
        enemy.player = self.kirby
        
        # Add to enemies list
        self.enemies.append(enemy)
    

