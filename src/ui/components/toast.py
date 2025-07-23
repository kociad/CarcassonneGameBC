import pygame
import time

TOAST_COLORS = {
    "info": ((30, 30, 30), (255, 255, 255)),
    "success": ((255, 255, 255), (0, 128, 0)),
    "error": ((255, 255, 255), (128, 0, 0)),
    "warning": ((0, 0, 0), (255, 215, 0))
}

class Toast:
    def __init__(self, message, duration=2, font=None, type="info"):
        self.message = message
        self.duration = duration
        self.startTime = None  # Not started yet
        self.font = font or pygame.font.Font(None, 36)
        self.type = type if type in TOAST_COLORS else "info"
        self.active = False

        self.textColor, self.bgColor = TOAST_COLORS[self.type]

    def start(self):
        self.startTime = time.time()
        self.active = True

    def isExpired(self):
        return self.active and (time.time() - self.startTime > self.duration)

    def draw(self, screen):
        if not self.active:
            return

        textSurf = self.font.render(self.message, True, self.textColor)
        textRect = textSurf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))

        bgRect = textRect.inflate(20, 10)
        pygame.draw.rect(screen, self.bgColor, bgRect, border_radius=8)
        screen.blit(textSurf, textRect)
