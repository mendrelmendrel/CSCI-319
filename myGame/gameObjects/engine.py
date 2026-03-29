import pygame

from .drawable import Drawable
from .kirby import Kirby
from .orcEnemy import OrcEnemy
from .monsterSlime import MonsterSlime
from .humanSoldierEnemy import HumanSoldierEnemy
from .sickleBoss import SickleBoss
from .spawnManager import EnemySpawnManager

from utils import vec, WORLD_SIZE, normalize, magnitude

class GameEngine(object):
    import pygame

    def __init__(self):       
        self.kirby = Kirby((0,0))
        self.enemies = [
        #     OrcEnemy((140, 140), 0, WORLD_SIZE[0]),
        # MonsterSlime((260, 180), 0, WORLD_SIZE[0]),
        # HumanSoldierEnemy((360, 220), 0, WORLD_SIZE[0]),
            # SickleBoss((120, 120), 0, WORLD_SIZE[0]),
        ]
        # Set player reference so enemies can track the player
        for enemy in self.enemies:
            enemy.player = self.kirby
            enemy.player = None #
            enemy.speed = 0
            enemy.velocity = vec(0, 0)
            enemy.maxVelocity = 0 #
        self.size = WORLD_SIZE
        self.background = Drawable((0,0), "background.png")
        self.collisionCooldown = 0
        self.elapsedGameTime = 0

        self.spawnManager = EnemySpawnManager(self.kirby, self.enemies, self.size)
    
    def draw(self, drawSurface):        
        self.background.draw(drawSurface)
        for arrow in self.kirby.arrows:
            arrow.draw(drawSurface)
        for enemy in self.enemies:
            enemy.draw(drawSurface)
        self.kirby.draw(drawSurface)

        # Draw HP counter
        font = pygame.font.Font(None, 36)
        hp_text = font.render(f"HP: {self.kirby.hp}/{self.kirby.maxHp}", True, (255, 0, 0))
        drawSurface.blit(hp_text, (10, 10))

        enemy_count_text = font.render(f"Enemies: {len(self.enemies)}", True, (255, 255, 255))
        drawSurface.blit(enemy_count_text, (10, 42))

        totalSeconds = int(self.elapsedGameTime)
        minutes = totalSeconds // 60
        seconds = totalSeconds % 60
        timerText = font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        timerRect = timerText.get_rect(topright=(drawSurface.get_width() - 10, 10))
        drawSurface.blit(timerText, timerRect)

        if self.spawnManager.bossStageBannerTimer > 0:
            bossFont = pygame.font.Font(None, 64)
            bossText = bossFont.render("Boss Stage!", True, (255, 80, 80))
            bossRect = bossText.get_rect(center=(drawSurface.get_width() // 2,
                                                 drawSurface.get_height() // 2))
            drawSurface.blit(bossText, bossRect)
        
    def handleEvent(self, event):
        self.kirby.handleEvent(event)
    
    def checkCollisions(self):
        # Decrement cooldown
        self.collisionCooldown -= 1
        
        # Get Kirby's body rect (for collision damage)
        kirbyRect = self.kirby.getDamageRect()
        
        # Get attack hitbox (only exists when attacking, returns None otherwise)
        attackHitbox = self.kirby.getAttackHitbox()
        
        # Check if kirby is attacking
        isAttacking = self.kirby.FSManimated.current_state.id == "attacking"
        
        # If attack just ended, clear hit tracking flags on all enemies
        if not isAttacking:
            for enemy in self.enemies:
                if hasattr(enemy, '_hitThisAttack'):
                    delattr(enemy, '_hitThisAttack')
        
        # Check player collision with each enemy
        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue

            enemyRect = enemy.getFullBodyRect()  # Get enemmies full body rect for collision with player and attacks 

            # Check if attack hitbox hits enemy
            if attackHitbox and attackHitbox.colliderect(enemyRect):
                # Damage from attack (hits enemy once per attack)
                if not hasattr(enemy, '_hitThisAttack'):
                    enemy._hitThisAttack = True  # Mark so we don't hit again this attack
                    enemy.hp -= 1
                    enemy.FSManimated.startHurt()  # Trigger hurt animation
            
            # Check if player body touches enemy (separate from attack)
            if kirbyRect.colliderect(enemyRect):
                # Damage player from collision (only when not attacking, with cooldown, i -frames for player while hurt)
                if not getattr(enemy, "isBoss", False) and not isAttacking and self.collisionCooldown <= 0 and not self.kirby.FSManimated.current_state.id == "hurting":
                    self.kirby.hp -= 1
                    self.collisionCooldown = 30
                    self.kirby.FSManimated.startHurt()  # Trigger hurt animation
                
                # Calculate direction from enemy to player for knockback
                direction = self.kirby.position - enemy.position
                direction_length = magnitude(direction)
                
                if direction_length > 0:
                    direction = normalize(direction)
                
                # Knockback force
                knockback = 25
                
                # Apply opposite velocities (push player and enemy apart)
                self.kirby.velocity += direction * knockback
                enemy.velocity -= direction * knockback

            if hasattr(enemy, "canDamagePlayer") and enemy.canDamagePlayer():
                bossAttackRect = enemy.getAttackRect()
                if bossAttackRect.colliderect(kirbyRect) and self.collisionCooldown <= 0 and self.kirby.FSManimated.current_state.id != "hurting":
                    self.kirby.hp -= getattr(enemy, "attackDamage", 1)
                    self.collisionCooldown = 30
                    self.kirby.FSManimated.startHurt()
                    enemy.markAttackHit()

        for arrow in self.kirby.arrows:
            if not arrow.alive:
                continue

            arrowRect = arrow.getRect()
            for enemy in self.enemies:
                if enemy.hp <= 0:
                    continue

                enemyRect = enemy.getFullBodyRect()
                if arrowRect.colliderect(enemyRect):
                    enemy.hp -= arrow.damage
                    enemy.FSManimated.startHurt()
                    arrow.alive = False
                    break

        # Enemy-to-enemy crowd separation using smaller centered crowd rects
        for i in range(len(self.enemies)):
            enemyA = self.enemies[i]
            if enemyA.hp <= 0:
                continue

            crowdA = enemyA.getCrowdRect()
            centerA_pos = vec(crowdA.centerx, crowdA.centery)

            for j in range(i + 1, len(self.enemies)):
                enemyB = self.enemies[j]
                if enemyB.hp <= 0:
                    continue

                crowdB = enemyB.getCrowdRect()
                if not crowdA.colliderect(crowdB):
                    continue

                centerB_pos = vec(crowdB.centerx, crowdB.centery)
                separationVector = centerA_pos - centerB_pos
                centerDistance = magnitude(separationVector)

                if centerDistance == 0:
                    separationVector = vec(1, 0)
                    centerDistance = 1

                pushDirection = normalize(separationVector)
                touchDistance = (crowdA.width + crowdB.width) / 2
                overlap = touchDistance - centerDistance

                if overlap > 0:
                    pushForce = pushDirection * (overlap / 2)
                    enemyA.position += pushForce
                    enemyB.position -= pushForce

        
    
    def update(self, seconds):
        self.elapsedGameTime += seconds
        self.spawnManager.update(seconds)
        
        self.kirby.update(seconds)
        for arrow in self.kirby.arrows:
            arrow.update(seconds)

        for enemy in self.enemies:
            enemy.update(seconds)
        self.checkCollisions()

        self.kirby.arrows = [
            arrow for arrow in self.kirby.arrows
            if arrow.alive
            and arrow.position[0] + arrow.getSize()[0] > 0
            and arrow.position[1] + arrow.getSize()[1] > 0
            and arrow.position[0] < WORLD_SIZE[0]
            and arrow.position[1] < WORLD_SIZE[1]
        ]
        
        # Remove dead enemies
        self.enemies[:] = [
            enemy for enemy in self.enemies 
            if enemy.hp > 0 or enemy.FSManimated.current_state.id == "hurting"            
            ]
        
        Drawable.updateOffset(self.kirby, self.size)
    

