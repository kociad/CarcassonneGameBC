import pygame

class Scene:
    def __init__(self, screen, switchSceneCallback):
        self.screen = screen
        self.switchScene = switchSceneCallback
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

    def handleEvents(self, events):
        raise NotImplementedError

    def update(self):
        pass

    def draw(self):
        raise NotImplementedError

    def applyScroll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scrollOffset += event.y * self.scrollSpeed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.scrollOffset -= self.scrollSpeed
                elif event.key == pygame.K_UP:
                    self.scrollOffset += self.scrollSpeed

        self.scrollOffset = max(
            min(0, self.scrollOffset),
            min(0, self.screen.get_height() - self.maxScroll)
        )

    def getScrollOffset(self):
        return self.scrollOffset
