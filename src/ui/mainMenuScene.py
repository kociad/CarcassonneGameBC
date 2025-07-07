import pygame
from ui.scene import Scene
from gameState import GameState

class MainMenuScene(Scene):
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 100)
        self.buttonFont = pygame.font.Font(None, 48)
        self.buttonText = self.buttonFont.render("Start Game", True, (0, 0, 0))
        self.buttonRect = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2, 200, 60)

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttonRect.collidepoint(event.pos):
                    self.switchScene(GameState.GAME)

    def draw(self):
        self.screen.fill((30, 30, 30))
        titleText = self.font.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))
        self.screen.blit(titleText, titleRect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.buttonRect)
        textRect = self.buttonText.get_rect(center=self.buttonRect.center)
        self.screen.blit(self.buttonText, textRect)
        pygame.display.flip()
