import pygame
from os.path import dirname, join


class ScreenManager:
    def __init__(self):
        self.titleFont = pygame.font.Font(None, 64)
        self.bodyFont = pygame.font.Font(None, 36)
        self.textColor = (255, 255, 255)
        self.backgroundColor = (0, 0, 0)
        self.startBackground = self._loadImage("startScreen.jpg")
        self.gameOverBackground = self._loadImage("youDied.png") or self._loadImage("youDied.jpg")

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
            self._drawCenteredText(screen,
                                   "Untitled for now",
                                   "Press Enter to start",
                                   self.startBackground)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False

            clock.tick(60)

    def showGameOverScreen(self, screen):
        clock = pygame.time.Clock()
        gameOverTextColor = (0, 0, 0)

        while True:
            self._drawCenteredText(screen,
                                   "Game Over",
                                   "Press R to restart or Esc to quit",
                                   self.gameOverBackground,
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
