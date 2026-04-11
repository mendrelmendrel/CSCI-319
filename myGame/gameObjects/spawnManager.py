"""
EnemySpawnManager - Handles dynamic enemy wave spawning and boss phase transitions.

The EnemySpawnManager orchestrates enemy spawning across game phases using scheduled
wave profiles. 

Spawn System:
- Scheduled Profiles: Each profile defines wave composition, enemy types, spawn intervals
- Wave Scheduling: Profiles activate based on elapsed time thresholds
- Easy Mode: 50% boss HP scaling + single-hit-death for standard enemies
- Standard Mode: Full difficulty with standard enemy HP values
- Boss Phase: 120-second timer triggers boss spawn and waves clear

Enemy Factory:
- Maps enemy type strings to actual enemy classes
- Creates enemies with randomized spawn positions (minimum radius from player)
- Applies difficulty scaling to newly created enemies
- Tracks isBoss flag for boss-phase identification

Difficulty Scaling:
- Easy Mode: Boss HP reduced to 50%, standard enemies reduced to 1 HP
- Standard Mode: Full HP values as defined in enemy classes
- Spawn Cooldown: Tracks individual cooldowns per enemy type
"""
import random
import math

from .orcEnemy import OrcEnemy
from .monsterSlime import MonsterSlime
from .humanSoldierEnemy import HumanSoldierEnemy
from .knightEnemy import KnightEnemy


class EnemySpawnManager:
    def __init__(self, player, enemies, worldSize, difficulty="standard"):
        self.player = player
        self.enemies = enemies
        self.worldSize = worldSize
        self.elapsedGameTime = 0
        self.difficulty = (difficulty or "standard").lower()

        self.enemyFactories = {
            "orc": OrcEnemy,
            "slime": MonsterSlime,
            "human_soldier": HumanSoldierEnemy,
            "knight": KnightEnemy,
        }

        self.bossEnemyType = "knight"
        self.bossSpawnDelay = 2.5

        self.bossPhaseTime = 120
        self.bossPhaseStarted = False
        self.bossStageBannerTimer = 0

        self.standardSpawnSchedule = [
            {
                "until": 15,
                "waves": {
                    "slime": {"interval": 5.0, "count": 1},
                },
            },
            {
                "until": 30,
                "waves": {
                    "slime": {"interval": 7.0, "count": 2},
                },
            },
            {
                "until": 45,
                "waves": {
                    "slime": {"interval": 5.0, "count": 2},
                    "orc": {"interval": 5.0, "count": 1},
                },
            },
            {
                "until": 60,
                "waves": {
                    "slime": {"interval": 7.0, "count": 2},
                    "orc": {"interval": 7.0, "count": 1},
                    "human_soldier": {"interval": 7.0, "count": 1},
                },
            },
            {
                "until": 75,
                "waves": {
                    "slime": {"interval": 7.0, "count": 1},
                    "orc": {"interval": 7.0, "count": 2},
                    "human_soldier": {"interval": 7.0, "count": 1},
                },
            },
            {
                "until": 90,
                "waves": {
                    "slime": {"interval": 15.0, "count": 0},
                    "orc": {"interval": 7.0, "count": 2},
                    "human_soldier": {"interval": 7.0, "count": 1}
                },
            },
            {
                "until": 105,
                "waves": {
                    "slime": {"interval": 7.0, "count": 0},
                    "orc": {"interval": 7.0, "count": 2},
                    "human_soldier": {"interval": 7.0, "count": 2}
                },
            },
            {
                "until": 120,
                "waves": {
                    "slime": {"interval": 15.0, "count": 0},
                    "orc": {"interval": 15.0, "count": 2},
                    "human_soldier": {"interval": 15.0, "count": 3}
                },
            },
            {
                "until": None,
                "waves": {
                    self.bossEnemyType: {"interval": 9999.0, "count": 1},
                },
            },
        ]

        self.easySpawnSchedule = [
            {
                "until": 15,
                "waves": {
                    "slime": {"interval": 5.0, "count": 1},
                },
            },
            {
                "until": 30,
                "waves": {
                    "slime": {"interval": 7.0, "count": 2},
                },
            },
            {
                "until": 45,
                "waves": {
                    "slime": {"interval": 7.0, "count": 1},
                    "orc": {"interval": 10.0, "count": 1},
                },
            },
            {
                "until": 60,
                "waves": {
                    "slime": {"interval": 10.0, "count": 1},
                    "orc": {"interval": 10.0, "count": 1},
                    
                },
            },
            {
                "until": 75,
                "waves": {
                    "slime": {"interval": 15.0, "count": 1},
                    "orc": {"interval": 10.0, "count": 2},
                   
                },
            },
            {
                "until": 90,
                "waves": {
                    "slime": {"interval": 15.0, "count": 0},
                    "orc": {"interval": 15.0, "count": 3},
                    "human_soldier": {"interval": 15.0, "count": 1}
                },
            },
            {
                "until": 105,
                "waves": {
                    "slime": {"interval": 7.5, "count": 0},
                    "orc": {"interval": 7.0, "count": 1},
                    "human_soldier": {"interval": 7.0, "count": 1},
                },
            },
            {
                "until": 120,
                "waves": {
                    "slime": {"interval": 8.0, "count": 0},
                    "orc": {"interval": 7.0, "count": 1},
                    "human_soldier": {"interval": 6.0, "count": 1},
                },
            },
            {
                "until": None,
                "waves": {
                    self.bossEnemyType: {"interval": 9999.0, "count": 1},
                },
            },
        ]

        if self.difficulty == "easy":
            self.spawnSchedule = self.easySpawnSchedule
        else:
            self.spawnSchedule = self.standardSpawnSchedule

        # Start at zero so each active wave type can spawn immediately when its
        # profile first becomes active.
        self.spawnCooldowns = {
            enemyType: 0.0 for enemyType in self.enemyFactories
        }

    def update(self, seconds):
        self.elapsedGameTime += seconds

        if self.bossStageBannerTimer > 0:
            self.bossStageBannerTimer = max(0, self.bossStageBannerTimer - seconds)

        if not self.bossPhaseStarted and self.elapsedGameTime >= self.bossPhaseTime:
            self._enterBossPhase()

        self._updateEnemySpawning(seconds)

    def _enterBossPhase(self):
        self.bossPhaseStarted = True
        self.bossStageBannerTimer = 3.0

        #  clear regular mobs so boss phase is readable/focused.
        self.enemies[:] = [enemy for enemy in self.enemies if getattr(enemy, "isBoss", False)]

        # Freeze all normal spawns, then arm only the boss spawn timer.
        for enemyType in self.spawnCooldowns:
            self.spawnCooldowns[enemyType] = 9999.0
        self.spawnCooldowns[self.bossEnemyType] = self.bossSpawnDelay

    def _getCurrentSpawnProfile(self):
        for profile in self.spawnSchedule:
            if profile["until"] is None or self.elapsedGameTime < profile["until"]:
                return profile
        return self.spawnSchedule[-1]

    def _updateEnemySpawning(self, seconds):
        profile = self._getCurrentSpawnProfile()
        activeWaves = profile["waves"]

        for enemyType, waveConfig in activeWaves.items():
            interval = waveConfig["interval"]
            count = waveConfig["count"]

            self.spawnCooldowns[enemyType] -= seconds
            # Use while (not if) so long frames catch up missed intervals instead
            # of silently dropping scheduled waves.
            while self.spawnCooldowns[enemyType] <= 0:
                self._spawnEnemyWave(enemyType, count)
                self.spawnCooldowns[enemyType] += interval

    def _spawnEnemyWave(self, enemyType, count):
        for _ in range(count):
            enemy = self._createEnemy(enemyType)
            self.enemies.append(enemy)

    def _applyDifficultyToEnemy(self, enemy):
        if self.difficulty != "easy":
            return

        isBoss = getattr(enemy, "isBoss", False)
        if isBoss:
            standardHp = getattr(enemy, "maxHp", getattr(enemy, "hp", 1))
            scaledHp = max(1, math.ceil(standardHp * 0.5))
            if hasattr(enemy, "maxHp"):
                enemy.maxHp = scaledHp
            enemy.hp = scaledHp
            return

        if hasattr(enemy, "maxHp"):
            enemy.maxHp = 1
        enemy.hp = 1

    def _createEnemy(self, enemyType):
        padding = 50
        if self.player is not None:
            playerSize = self.player.getDamageRect()
            # Minimum spawn radius: double the player collision rect size
            minSpawnRadius = max(playerSize.width, playerSize.height) * 2
            
            # Spawn anywhere outside the safe zone using rejection sampling
            # Rejection-sample a spawn outside the player safe radius, bounded loop
            # prevents pathological infinite retries in crowded maps.
            for _ in range(10):  # Try up to 10 times to find valid spawn
                x = random.uniform(padding, self.worldSize[0] - 100)
                y = random.uniform(padding, self.worldSize[1] - 100)
                
                # Check if position is outside minimum radius
                dx = x - self.player.position[0]
                dy = y - self.player.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                if distance >= minSpawnRadius:  # Accept if far enough or last attempt
                    break
        else:
            x = random.uniform(padding, self.worldSize[0] - 100)
            y = random.uniform(padding, self.worldSize[1] - 100)

        enemyClass = self.enemyFactories[enemyType]
        enemy = enemyClass((x, y), 0, self.worldSize[0])

        if enemyType == self.bossEnemyType:
            enemy.isBoss = True

        enemy.player = self.player
        self._applyDifficultyToEnemy(enemy)
        return enemy