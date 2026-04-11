import pygame
from gameObjects import GameEngine
from gameObjects.drawable import Drawable
from utils import RESOLUTION, ScreenManager
from utils.soundManager import SoundManager


MENU_BGM = "Gwyn, Lord of Cinder.mp3"
GAME_BGM = "Golden Serpant Tavern (LOOP).mp3"
BOSS_BGM = "Vordt of the Boreal Valley.mp3"


def drawPauseOverlay(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    panelWidth = min(760, screen.get_width() - 80)
    panelHeight = min(620, screen.get_height() - 80)
    panelX = (screen.get_width() - panelWidth) // 2
    panelY = (screen.get_height() - panelHeight) // 2
    panelRect = pygame.Rect(panelX, panelY, panelWidth, panelHeight)

    panel = pygame.Surface((panelWidth, panelHeight), pygame.SRCALPHA)
    panel.fill((30, 30, 30, 230))
    screen.blit(panel, panelRect.topleft)
    pygame.draw.rect(screen, (240, 240, 240), panelRect, 2)

    titleFont = pygame.font.Font(None, 72)
    sectionFont = pygame.font.Font(None, 42)
    bodyFont = pygame.font.Font(None, 34)

    title = titleFont.render("Paused", True, (255, 255, 255))
    titleRect = title.get_rect(midtop=(screen.get_width() // 2, panelY + 18))
    screen.blit(title, titleRect)

    controls = [
        "Movement: WASD or Arrow Keys",
        "Dash: Space",
        "Melee Attack: Left Mouse Button",
        "Shoot Arrow: Right Mouse Button",
        "Toggle Collision Debug: F3",
        "Pause / Resume: P",
        "Quit Game: Esc",
        "Restart after death: R (on Game Over)",
    ]

    section = sectionFont.render("Controls", True, (255, 230, 150))
    screen.blit(section, (panelX + 28, panelY + 92))

    lineY = panelY + 132
    lineSpacing = 44
    for line in controls:
        lineSurface = bodyFont.render(line, True, (245, 245, 245))
        screen.blit(lineSurface, (panelX + 36, lineY))
        lineY += lineSpacing

def main():
    #Initialize the module
    pygame.init()
    
    pygame.font.init()
    
    
    #Get the screen
    screenInfo = pygame.display.Info()
    screen = pygame.display.set_mode((screenInfo.current_w,
                                      screenInfo.current_h),
                                     pygame.NOFRAME)
    drawSurface = pygame.Surface(list(map(int, RESOLUTION)))
    screenManager = ScreenManager()
    soundManager = SoundManager.getInstance()
    currentBgm = None

    soundManager.playBGM(MENU_BGM)
    currentBgm = MENU_BGM
    selectedMode = screenManager.showStartScreen(screen)

    if selectedMode is None:
        pygame.quit()
        return

    appRunning = True

    while appRunning:
        gameEngine = GameEngine(difficulty=selectedMode)
        if currentBgm != GAME_BGM:
            soundManager.playBGM(GAME_BGM)
            currentBgm = GAME_BGM

        bossMusicStarted = False
        # Reset frame timing per round so start/game-over screen time
        # doesn't leak into gameplay dt.
        gameClock = pygame.time.Clock()
        gameRunning = True
        isPaused = False
        roundResult = None

        while gameRunning:
            gameEngine.draw(drawSurface)

            screenWidth, screenHeight = screen.get_size()
            scaleFactor = max(screenWidth / RESOLUTION[0],
                              screenHeight / RESOLUTION[1])
            scaledSize = (int(RESOLUTION[0] * scaleFactor),
                          int(RESOLUTION[1] * scaleFactor))
            scaledSurface = pygame.transform.scale(drawSurface, scaledSize)
            drawX = (screenWidth - scaledSize[0]) // 2
            drawY = (screenHeight - scaledSize[1]) // 2
            Drawable.updateRenderTransform(scaleFactor, (drawX, drawY))
            screen.fill((0, 0, 0))
            screen.blit(scaledSurface, (drawX, drawY))

            hudFont = pygame.font.Font(None, 72)
            heartFrames = gameEngine.heartFrames
            
            if len(heartFrames) > 0:
                heartWidth, heartHeight = heartFrames[0].get_size()
                heartWidth = int(heartWidth * 2.0)
                heartHeight = int(heartHeight * 2.0)
                spacing = 2
                startX = 10
                startY = 10
                currentHp = int(max(0, min(gameEngine.user.hp, gameEngine.user.maxHp)))
                for i in range(currentHp):
                    frameIndex = (gameEngine.heartFrameIndex + i) % len(heartFrames)
                    heartImage = pygame.transform.smoothscale(heartFrames[frameIndex],
                                                              (heartWidth, heartHeight))
                    screen.blit(heartImage,
                                (startX + i * (heartWidth + spacing),
                                 startY))

            totalSeconds = int(gameEngine.elapsedGameTime)
            minutes = totalSeconds // 60
            seconds = totalSeconds % 60
            timerText = hudFont.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            screen.blit(timerText, timerText.get_rect(topright=(screenWidth - 10, 10)))

            knightHpPercent = gameEngine.getKnightHealthPercent()
            if knightHpPercent is not None:
                knightFont = pygame.font.Font(None, 44)
                knightText = knightFont.render(f"Knight HP: {knightHpPercent}%",
                                               True,
                                               (255, 220, 120))
                knightRect = knightText.get_rect(midtop=(screenWidth // 2, 12))
                screen.blit(knightText, knightRect)

            if isPaused:
                drawPauseOverlay(screen)

            pygame.display.flip()

            # event handling, gets all event from the eventqueue
            for event in pygame.event.get():
                # only do something if the event is of type QUIT
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # change the value to False, to exit the main loop
                    gameRunning = False
                    appRunning = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    isPaused = not isPaused
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    gameEngine.handleEvent(event)
                else:
                    if not isPaused:
                        gameEngine.handleEvent(event)

            # Clamp dt to prevent giant simulation jumps after hitches.
            seconds = min(gameClock.tick(60) / 1000, 0.05)
            if not isPaused:
                gameEngine.update(seconds)
                if (not bossMusicStarted
                        and gameEngine.spawnManager is not None
                        and gameEngine.spawnManager.bossPhaseStarted):
                    soundManager.playBGM(BOSS_BGM)
                    currentBgm = BOSS_BGM
                    bossMusicStarted = True

            # End round if Kirby runs out of HP
            if gameEngine.user.hp <= 0:
                roundResult = "defeat"
                gameRunning = False

            if gameEngine.isBossDefeated():
                roundResult = "victory"
                gameRunning = False

        if not appRunning:
            break

        action = screenManager.showGameOverScreen(screen,
                                                  won=(roundResult == "victory"))
        if action == "quit":
            appRunning = False
        elif action == "restart":
            if currentBgm != MENU_BGM:
                soundManager.playBGM(MENU_BGM)
                currentBgm = MENU_BGM
     
    pygame.quit()


if __name__ == '__main__':
    main()