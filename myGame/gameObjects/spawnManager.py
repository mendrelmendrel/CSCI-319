import random

from .orcEnemy import OrcEnemy
from .monsterSlime import MonsterSlime
from .humanSoldierEnemy import HumanSoldierEnemy
from .sickleBoss import SickleBoss


class EnemySpawnManager:
    def __init__(self, player, enemies, worldSize):
        self.player = player
        self.enemies = enemies
        self.worldSize = worldSize
        self.elapsedGameTime = 0

        self.enemyFactories = {
            "orc": OrcEnemy,
            "slime": MonsterSlime,
            "human_soldier": HumanSoldierEnemy,
            "sickle_boss": SickleBoss,
        }

        self.bossPhaseTime = 90
        self.bossPhaseStarted = False
        self.bossStageBannerTimer = 0

        self.spawnSchedule = [
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
                    "slime": {"interval": 8.0, "count": 2},
                    "orc": {"interval": 8.0, "count": 2},
                    "human_soldier": {"interval": 8.0, "count": 1},
                },
            },
            {
                "until": 75,
                "waves": {
                    "slime": {"interval": 8.0, "count": 3},
                    "orc": {"interval": 9.0, "count": 3},
                    "human_soldier": {"interval": 8.0, "count": 1},
                },
            },
            {
                "until": 90,
                "waves": {
                    "slime": {"interval": 6.0, "count": 1},
                    "orc": {"interval": 4.0, "count": 4},
                    "human_soldier": {"interval": 3.0, "count": 2},
                },
            },
            {
                "until": None,
                "waves": {
                    "sickle_boss": {"interval": 9999.0, "count": 1},
                },
            },
        ]

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

        self.enemies[:] = [enemy for enemy in self.enemies if getattr(enemy, "isBoss", False)]

        for enemyType in self.spawnCooldowns:
            self.spawnCooldowns[enemyType] = 9999.0
        self.spawnCooldowns["sickle_boss"] = 0.0

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
            while self.spawnCooldowns[enemyType] <= 0:
                self._spawnEnemyWave(enemyType, count)
                self.spawnCooldowns[enemyType] += interval

    def _spawnEnemyWave(self, enemyType, count):
        for _ in range(count):
            enemy = self._createEnemy(enemyType)
            self.enemies.append(enemy)

    def _createEnemy(self, enemyType):
        padding = 50
        if self.player is not None:
            spawnRadius = 180
            x = self.player.position[0] + random.uniform(-spawnRadius, spawnRadius)
            y = self.player.position[1] + random.uniform(-spawnRadius, spawnRadius)
            x = max(padding, min(x, self.worldSize[0] - 100))
            y = max(padding, min(y, self.worldSize[1] - 100))
        else:
            x = random.uniform(padding, self.worldSize[0] - 100)
            y = random.uniform(padding, self.worldSize[1] - 100)

        enemyClass = self.enemyFactories[enemyType]
        enemy = enemyClass((x, y), 0, self.worldSize[0])
        enemy.player = self.player
        return enemy