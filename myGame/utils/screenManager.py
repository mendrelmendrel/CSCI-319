import pygame
from os.path import dirname, join


class ScreenManager:
    def __init__(self):
        self.titleFont = pygame.font.Font(None, 64)
        self.bodyFont = pygame.font.Font(None, 36)
        self.textColor = (255, 255, 255)
        self.backgroundColor = (0, 0, 0)
        self.startBackground = self._loadImage("start_screen.png") or self._loadImage("startScreen.jpg")
        self.gameOverBackground = self._loadImage("youDied.png") or self._loadImage("youDied.jpg")
        self.victoryBackground = self._loadImage("gameoverscreenpng") or self._loadImage("GameOverScreen.png")

    def _loadImage(self, fileName):
        imagePath = join(dirname(__file__), "..", "images", fileName)
        try:
            return pygame.image.load(imagePath)
        except (FileNotFoundError, pygame.error):
            return None

    def _drawCenteredText(self, screen, title, prompt, backgroundImage=None, textColor=None):
        if textColor is None:
            textColor = self.textColor

        if backgroundImage:
            scaledBackground = pygame.transform.scale(backgroundImage, screen.get_size())
            screen.blit(scaledBackground, (0, 0))
        else:
            screen.fill(self.backgroundColor)

        screenWidth, screenHeight = screen.get_size()

        titleSurface = self.titleFont.render(title, True, textColor)
        promptSurface = self.bodyFont.render(prompt, True, textColor)

        titleRect = titleSurface.get_rect(center=(screenWidth // 2, screenHeight // 2 - 30))
        promptRect = promptSurface.get_rect(center=(screenWidth // 2, screenHeight // 2 + 20))

        screen.blit(titleSurface, titleRect)
        screen.blit(promptSurface, promptRect)
        pygame.display.flip()

    def showStartScreen(self, screen):
        clock = pygame.time.Clock()

        while True:
            if self.startBackground:
                scaledBackground = pygame.transform.scale(self.startBackground,
                                                          screen.get_size())
                screen.blit(scaledBackground, (0, 0))
            else:
                screen.fill(self.backgroundColor)

            screenWidth, screenHeight = screen.get_size()
            titleSurface = self.titleFont.render("Select Difficulty", True,
                                                 self.textColor)
            easySurface = self.bodyFont.render("Press E for Easy", True,
                                               self.textColor)
            standardSurface = self.bodyFont.render("Press S for Standard", True,
                                                   self.textColor)
            quitSurface = self.bodyFont.render("Press Esc to Quit", True,
                                               self.textColor)

            screen.blit(titleSurface,
                        titleSurface.get_rect(center=(screenWidth // 2,
                                                      screenHeight // 2 - 60)))
            screen.blit(easySurface,
                        easySurface.get_rect(center=(screenWidth // 2,
                                                     screenHeight // 2 + 0)))
            screen.blit(standardSurface,
                        standardSurface.get_rect(center=(screenWidth // 2,
                                                         screenHeight // 2 + 40)))
            screen.blit(quitSurface,
                        quitSurface.get_rect(center=(screenWidth // 2,
                                                     screenHeight // 2 + 90)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        return "easy"
                    if event.key == pygame.K_s:
                        return "standard"
                    if event.key == pygame.K_ESCAPE:
                        return None

            clock.tick(60)

    def showGameOverScreen(self, screen, won=False):
        clock = pygame.time.Clock()
        gameOverTextColor = (0, 0, 0)
        title = "You Win!" if won else "Game Over"
        prompt = "Press R to restart or Esc to quit"
        background = self.victoryBackground if won else self.gameOverBackground

        while True:
            self._drawCenteredText(screen,
                                   title,
                                   prompt,
                                   background,
                                   gameOverTextColor)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "restart"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"

            clock.tick(60)
