"""
GameEngine Module - Core game loop coordinator and collision manager.

This module contains the GameEngine class which serves as the central
coordinator between the player, enemies, level environment, and game state.

Key Responsibilities:
- Entity lifecycle management (spawning, updating, removal)
- Collision detection and resolution (player vs enemies, attacks, pickups, obstacles)
- Rendering and depth-based drawing (isometric-style Y-sorting)
- Camera system and world boundaries
- Boss progression tracking
"""
import pygame
import random

from .drawable import Drawable
from .user import User
from .orcEnemy import OrcEnemy
from .monsterSlime import MonsterSlime
from .humanSoldierEnemy import HumanSoldierEnemy
from .knightEnemy import KnightEnemy
from .boulder import Boulder
from .bush import Bush
from .heartPickup import HeartPickup
from .spawnManager import EnemySpawnManager
from .tree import Tree

from levels import get_level1_tree_positions, get_level1_boulder_specs, get_level1_bush_specs

from utils import SpriteManager, TILEMAP_COLOR2_FILE
from utils import vec, WORLD_SIZE, normalize, magnitude

class GameEngine(object):
    import pygame

    def __init__(self, difficulty="standard"):
        self.user = User((0, 0))
        self.kirby = self.user
        self.difficulty = (difficulty or "standard").lower()

        self.size = WORLD_SIZE
        self.user.position = vec(self.size[0] / 2 - self.user.getSize()[0] / 2,
                                 self.size[1] / 2 - self.user.getSize()[1] / 2)
        self.enemies = []
        self.user.enemyTargets = self.enemies
        self.background = Drawable((0,0))
        self.background.image = self._createGrassBackground()
        self.background.imageName = TILEMAP_COLOR2_FILE
        self.trees = self._generateForest()
        self.boulders = self._generateBoulders()
        self.bushes = self._generateBushes()
        self.heartFrames = SpriteManager.getInstance().getHeartRotateSprites()
        self.heartFrames = [pygame.transform.smoothscale(
                    heart,
                    (max(1, int(heart.get_width() * 0.6)),
                     max(1, int(heart.get_height() * 0.6))))
                    for heart in self.heartFrames]
        self.heartFrameIndex = 0
        self.heartAnimationTimer = 0
        self.heartFramesPerSecond = 10
        self.collisionCooldown = 0
        self.elapsedGameTime = 0
        self.showCollisionDebug = False
        self.heartPickups = []
        self.bossSeenAlive = False

        self.spawnManager = EnemySpawnManager(self.user,
                                              self.enemies,
                                              self.size,
                                              difficulty=self.difficulty)
        Drawable.updateOffset(self.user, self.size)
    
    def draw(self, drawSurface):        
        self.background.draw(drawSurface)
        drawQueue = []

        for tree in self.trees:
            drawQueue.append((tree.getDepthY(), 0, tree))

        for boulder in self.boulders:
            drawQueue.append((boulder.getDepthY(), 0, boulder))

        for bush in self.bushes:
            drawQueue.append((bush.getDepthY(), 0, bush))

        for enemy in self.enemies:
            enemyFootY = enemy.position[1] + enemy.getSize()[1]
            drawQueue.append((enemyFootY, 1, enemy))

        kirbyFootY = self.kirby.position[1] + self.kirby.getSize()[1]
        drawQueue.append((kirbyFootY, 2, self.kirby))

        # Primary sort by foot/depth Y, secondary sort by category to keep
        # deterministic layering when entities share the same Y value.
        drawQueue.sort(key=lambda item: (item[0], item[1]))

        for _, _, obj in drawQueue:
            obj.draw(drawSurface)

        for arrow in self.kirby.arrows:
            arrow.draw(drawSurface)

        for pickup in self.heartPickups:
            pickup.draw(drawSurface)

        if self.spawnManager is not None and self.spawnManager.bossStageBannerTimer > 0:
            bossFont = pygame.font.Font(None, 64)
            bossText = bossFont.render("Boss Stage!", True, (255, 80, 80))
            bossRect = bossText.get_rect(center=(drawSurface.get_width() // 2,
                                                 drawSurface.get_height() // 2))
            drawSurface.blit(bossText, bossRect)

        if self.showCollisionDebug:
            self._drawCollisionDebug(drawSurface)
        
    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.showCollisionDebug = not self.showCollisionDebug
            return
        self.kirby.handleEvent(event)

    def _clampEntityToWorldBounds(self, entity):
        if entity is None or not hasattr(entity, "position") or not hasattr(entity, "getSize"):
            return

        size = entity.getSize()

        if entity.position[0] < 0:
            entity.position[0] = 0
            if hasattr(entity, "velocity"):
                entity.velocity[0] = 0
        elif entity.position[0] + size[0] > self.size[0]:
            entity.position[0] = self.size[0] - size[0]
            if hasattr(entity, "velocity"):
                entity.velocity[0] = 0

        if entity.position[1] < 0:
            entity.position[1] = 0
            if hasattr(entity, "velocity"):
                entity.velocity[1] = 0
        elif entity.position[1] + size[1] > self.size[1]:
            entity.position[1] = self.size[1] - size[1]
            if hasattr(entity, "velocity"):
                entity.velocity[1] = 0

    def _drawCollisionDebug(self, drawSurface):
        offsetX = int(Drawable.CAMERA_OFFSET[0])
        offsetY = int(Drawable.CAMERA_OFFSET[1])

        def toScreenRect(worldRect):
            return pygame.Rect(int(worldRect.x - offsetX),
                               int(worldRect.y - offsetY),
                               int(worldRect.width),
                               int(worldRect.height))

        kirbyRect = self.kirby.getDamageRect()
        pygame.draw.rect(drawSurface, (0, 220, 0), toScreenRect(kirbyRect), 2)

        attackHitbox = self.kirby.getAttackHitbox()
        if attackHitbox is not None:
            pygame.draw.rect(drawSurface, (255, 220, 0),
                             toScreenRect(attackHitbox), 2)

        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue

            enemyRect = enemy.getFullBodyRect()
            color = (220, 40, 40)
            if attackHitbox is not None and attackHitbox.colliderect(enemyRect):
                color = (255, 120, 0)

            pygame.draw.rect(drawSurface, color, toScreenRect(enemyRect), 2)

            if isinstance(enemy, KnightEnemy):
                knightAttackRect = enemy.getAttackRect()
                attackColor = (80, 180, 255)
                if enemy.canDamagePlayer():
                    attackColor = (255, 80, 220)

                pygame.draw.rect(drawSurface,
                                 attackColor,
                                 toScreenRect(knightAttackRect),
                                 2)

    def _drawKnightHealthText(self, drawSurface):
        knight = None
        for enemy in self.enemies:
            if isinstance(enemy, KnightEnemy) and enemy.hp > 0:
                knight = enemy
                break

        if knight is None:
            return

        hpPercent = int(max(0, min(100,
                                    round((knight.hp / max(knight.maxHp, 1))
                                          * 100))))
        textSurface = pygame.font.Font(None, 38).render(
            f"Knight HP: {hpPercent}%", True, (255, 220, 120)
        )
        textRect = textSurface.get_rect(midtop=(drawSurface.get_width() // 2,
                                                12))
        drawSurface.blit(textSurface, textRect)

    def getKnightHealthPercent(self):
        for enemy in self.enemies:
            if isinstance(enemy, KnightEnemy) and enemy.hp > 0:
                return int(max(0, min(100,
                                       round((enemy.hp / max(enemy.maxHp, 1))
                                             * 100))))
        return None

    def isBossDefeated(self):
        if self.spawnManager is None:
            return False
        if not self.spawnManager.bossPhaseStarted:
            return False
        if not self.bossSeenAlive:
            return False

        for enemy in self.enemies:
            if getattr(enemy, "isBoss", False) and enemy.hp > 0:
                return False
        return True
    
    def checkCollisions(self):
        # Decrement 
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
                    # Per-attack latch: one melee swing can only damage each enemy once.
                    enemy._hitThisAttack = True  # Mark so we don't hit again this attack
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        self._maybeDropHeart(enemy)
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
                    if enemy.hp <= 0:
                        self._maybeDropHeart(enemy)
                    enemy.FSManimated.startHurt()
                    arrow.alive = False
                    break

        for pickup in self.heartPickups:
            if not pickup.alive:
                continue

            if pickup.getRect().colliderect(kirbyRect):
                if self.kirby.hp < self.kirby.maxHp:
                    self.kirby.hp = min(self.kirby.maxHp, self.kirby.hp + 1)
                pickup.alive = False

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
                # Approximate "desired" center distance as half-width sum; keeps
                # enemies from stacking while still allowing tight packs.
                touchDistance = (crowdA.width + crowdB.width) / 2
                overlap = touchDistance - centerDistance

                if overlap > 0:
                    # Split correction across both enemies so separation feels symmetric.
                    pushForce = pushDirection * (overlap / 2)
                    enemyA.position += pushForce
                    enemyB.position -= pushForce

        
    
    def update(self, seconds):
        self.elapsedGameTime += seconds
        if self.spawnManager is not None:
            self.spawnManager.update(seconds)
        self._updateHeartHud(seconds)
        
        for tree in self.trees:
            tree.update(seconds)

        for boulder in self.boulders:
            boulder.update(seconds)

        for bush in self.bushes:
            bush.update(seconds)

        self.kirby.update(seconds)
        self._clampEntityToWorldBounds(self.kirby)
        for arrow in self.kirby.arrows:
            arrow.update(seconds)

        for enemy in self.enemies:
            enemy.update(seconds)

        if not self.bossSeenAlive:
            for enemy in self.enemies:
                if getattr(enemy, "isBoss", False) and enemy.hp > 0:
                    self.bossSeenAlive = True
                    break

        for pickup in self.heartPickups:
            pickup.update(seconds)

        self._resolveEntityTreeCollisions(self.kirby,
                                          self.kirby.getDamageRect)
        for enemy in self.enemies:
            self._resolveEntityTreeCollisions(enemy,
                                              enemy.getFullBodyRect)

        self._resolveEntityTreeCollisions(self.kirby,
                                          self.kirby.getDamageRect,
                                          self.boulders)
        for enemy in self.enemies:
            self._resolveEntityTreeCollisions(enemy,
                                              enemy.getFullBodyRect,
                                              self.boulders)

        self.checkCollisions()

        # Kirby can be moved again by obstacle resolution, so enforce world bounds
        # after all collision position adjustments.
        self._clampEntityToWorldBounds(self.kirby)

        self.kirby.arrows = [
            arrow for arrow in self.kirby.arrows
            if arrow.alive
            and arrow.position[0] + arrow.getSize()[0] > 0
            and arrow.position[1] + arrow.getSize()[1] > 0
            and arrow.position[0] < WORLD_SIZE[0]
            and arrow.position[1] < WORLD_SIZE[1]
        ]

        self.heartPickups = [pickup for pickup in self.heartPickups if pickup.alive]
        
        # Remove dead enemies
        self.enemies[:] = [
            enemy for enemy in self.enemies 
            if enemy.hp > 0 or enemy.FSManimated.current_state.id == "hurting"            
            ]
        
        Drawable.updateOffset(self.kirby, self.size)

    def _generateForest(self):
        trees = []
        worldWidth = int(self.size[0])
        worldHeight = int(self.size[1])
        treeSize = Tree((0, 0), framesPerSecond=3).getSize()
        centerPosition = vec(worldWidth / 2, worldHeight / 2)
        safeRadius = 280

        for position in get_level1_tree_positions():
            x = max(20, min(float(position[0]), worldWidth - treeSize[0] - 20))
            y = max(20, min(float(position[1]), worldHeight - treeSize[1] - 20))

            treeCenter = vec(x + treeSize[0] / 2, y + treeSize[1] / 2)
            if magnitude(treeCenter - centerPosition) < safeRadius:
                continue

            tree = Tree((x, y), framesPerSecond=3)
            treeRect = tree.getCollisionRect()

            overlapping = False
            for existing in trees:
                if treeRect.colliderect(existing.getCollisionRect()):
                    overlapping = True
                    break

            if not overlapping:
                trees.append(tree)

        return trees

    def _generateBoulders(self):
        boulders = []
        for spec in get_level1_boulder_specs():
            position = spec["position"]
            fileName = spec.get("fileName", "Boulder.png")
            collisionSize = spec.get("collisionSize", (17, 14))
            collisionScale = spec.get("collisionScale", 0.75)
            drawSize = spec.get("drawSize", None)
            boulders.append(Boulder(position,
                                    fileName=fileName,
                                    collisionSize=collisionSize,
                                    collisionScale=collisionScale,
                                    drawSize=drawSize))
        return boulders

    def _generateBushes(self):
        bushes = []
        for spec in get_level1_bush_specs():
            position = spec["position"]
            fileName = spec.get("fileName", "bush_1.png")
            bushes.append(Bush(position, fileName=fileName))
        return bushes

    def _resolveEntityTreeCollisions(self, entity, getEntityRect, obstacleList=None):
        entityRect = getEntityRect()
        if obstacleList is None:
            obstacleList = self.trees

        for obstacle in obstacleList:
            obstacleRect = obstacle.getCollisionRect()
            if not entityRect.colliderect(obstacleRect):
                continue

            overlapLeft = entityRect.right - obstacleRect.left
            overlapRight = obstacleRect.right - entityRect.left
            overlapTop = entityRect.bottom - obstacleRect.top
            overlapBottom = obstacleRect.bottom - entityRect.top

            # Resolve along the shallowest penetration axis to avoid corner "teleporting".
            minOverlap = min(overlapLeft, overlapRight, overlapTop, overlapBottom)

            if minOverlap == overlapLeft:
                entity.position[0] -= overlapLeft
                entity.velocity[0] = min(0, entity.velocity[0])
            elif minOverlap == overlapRight:
                entity.position[0] += overlapRight
                entity.velocity[0] = max(0, entity.velocity[0])
            elif minOverlap == overlapTop:
                entity.position[1] -= overlapTop
                entity.velocity[1] = min(0, entity.velocity[1])
            else:
                entity.position[1] += overlapBottom
                entity.velocity[1] = max(0, entity.velocity[1])

            entityRect = getEntityRect()

    def _maybeDropHeart(self, enemy):
        if getattr(enemy, "hasDroppedHeart", False):
            return

        enemy.hasDroppedHeart = True

        dropChance = self._getHeartDropChance(enemy)
        if dropChance <= 0 or random.random() > dropChance:
            return

        if hasattr(enemy, "getFullBodyRect"):
            enemyRect = enemy.getFullBodyRect()
            dropPos = vec(enemyRect.centerx - 11, enemyRect.centery - 11)
        else:
            dropPos = vec(enemy.position[0], enemy.position[1])

        self.heartPickups.append(HeartPickup(dropPos))

    def _getHeartDropChance(self, enemy):
        if self.kirby.hp >= self.kirby.maxHp:
            return 0.0

        baseChance = 0.08

        if isinstance(enemy, OrcEnemy):
            baseChance = 0.10
        elif isinstance(enemy, HumanSoldierEnemy):
            baseChance = 0.10
        elif isinstance(enemy, MonsterSlime):
            baseChance = 0.08

        missingFraction = 1 - (self.kirby.hp / max(self.kirby.maxHp, 1))
        chance = baseChance + (0.10 * missingFraction)

        if self.kirby.hp <= 1:
            chance += 0.10

        return min(chance, 0.25)

    def _createGrassBackground(self):
        grassTile = SpriteManager.getInstance().getTilemapColor2Sprite("PLAIN_GRASS_BLOCK")
        background = pygame.Surface((int(self.size[0]), int(self.size[1])))
        centerPatch = self._getCenterPatch(grassTile, patchSize=64)
        # Pre-fill with an opaque sampled grass color so transparent tile edges
        # don't reveal black gaps between repeated blits.
        background.fill(self._getOpaqueBaseColor(centerPatch))
        tileWidth, tileHeight = centerPatch.get_size()

        for y in range(0, int(self.size[1]), tileHeight):
            for x in range(0, int(self.size[0]), tileWidth):
                background.blit(centerPatch, (x, y))

        return background

    def _getCenterPatch(self, tile, patchSize=64):
        tileWidth, tileHeight = tile.get_size()
        patchWidth = max(1, min(patchSize, tileWidth))
        patchHeight = max(1, min(patchSize, tileHeight))

        patchX = (tileWidth - patchWidth) // 2
        patchY = (tileHeight - patchHeight) // 2
        patchRect = pygame.Rect(patchX, patchY, patchWidth, patchHeight)

        patch = pygame.Surface((patchWidth, patchHeight), pygame.SRCALPHA, 32)
        patch.blit(tile, (0, 0), patchRect)
        return patch

    def _getOpaqueBaseColor(self, tile):
        width, height = tile.get_size()
        sample = tile.get_at((width // 2, height // 2))

        if sample.a > 0:
            return (sample.r, sample.g, sample.b)

        for y in range(height):
            for x in range(width):
                color = tile.get_at((x, y))
                if color.a > 0:
                    return (color.r, color.g, color.b)

        return (0, 0, 0)

    def _updateHeartHud(self, seconds):
        if len(self.heartFrames) == 0:
            return

        self.heartAnimationTimer += seconds
        frameDuration = 1 / self.heartFramesPerSecond

        while self.heartAnimationTimer >= frameDuration:
            self.heartAnimationTimer -= frameDuration
            self.heartFrameIndex = (self.heartFrameIndex + 1) % len(self.heartFrames)

    def _drawAnimatedHearts(self, drawSurface):
        if len(self.heartFrames) == 0:
            return

        currentHp = int(max(0, min(self.kirby.hp, self.kirby.maxHp)))
        heartWidth, heartHeight = self.heartFrames[0].get_size()
        spacing = 2
        startX = 10
        startY = 10

        for i in range(currentHp):
            frameIndex = (self.heartFrameIndex + i) % len(self.heartFrames)
            heartImage = self.heartFrames[frameIndex]
            drawSurface.blit(heartImage,
                             (startX + i * (heartWidth + spacing),
                              startY))
    

