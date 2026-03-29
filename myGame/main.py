import pygame
from gameObjects import GameEngine
from utils import RESOLUTION, UPSCALED, ScreenManager

def main():
    #Initialize the module
    pygame.init()
    
    pygame.font.init()
    
    
    #Get the screen
    screen = pygame.display.set_mode(list(map(int, UPSCALED)))
    drawSurface = pygame.Surface(list(map(int, RESOLUTION)))
    screenManager = ScreenManager()
    gameClock = pygame.time.Clock()

    if not screenManager.showStartScreen(screen):
        pygame.quit()
        return

    APP_RUNNING = True

    while APP_RUNNING:
        gameEngine = GameEngine()
        GAME_RUNNING = True

        while GAME_RUNNING:
            gameEngine.draw(drawSurface)

            pygame.transform.scale(drawSurface,
                                   list(map(int, UPSCALED)),
                                   screen)

            pygame.display.flip()

            # event handling, gets all event from the eventqueue
            for event in pygame.event.get():
                # only do something if the event is of type QUIT
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # change the value to False, to exit the main loop
                    GAME_RUNNING = False
                    APP_RUNNING = False
                else:
                    gameEngine.handleEvent(event)

            gameClock.tick(60)
            seconds = gameClock.get_time() / 1000
            gameEngine.update(seconds)

            # End round if Kirby runs out of HP
            if gameEngine.kirby.hp <= 0:
                GAME_RUNNING = False

        if not APP_RUNNING:
            break

        action = screenManager.showGameOverScreen(screen)
        if action == "quit":
            APP_RUNNING = False
     
    pygame.quit()


if __name__ == '__main__':
    main()