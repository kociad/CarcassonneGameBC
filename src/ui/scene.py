import pygame

class Scene:
    def __init__(self, screen, switchSceneCallback):
        self.screen = screen
        self.switchScene = switchSceneCallback

    def handleEvents(self, events):
        raise NotImplementedError

    def update(self):
        pass

    def draw(self):
        raise NotImplementedError