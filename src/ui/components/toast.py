import pygame
import time
import math
import logging
import typing

logger = logging.getLogger(__name__)

TOAST_COLORS = {
    "info": ((30, 30, 30), (255, 255, 255)),
    "success": ((255, 255, 255), (0, 128, 0)),
    "error": ((255, 255, 255), (128, 0, 0)),
    "warning": ((0, 0, 0), (255, 215, 0))
}

class Toast:
    """
    Represents a single toast notification with animation, message, and type.
    Handles its own timing, animation, and drawing.
    """
    def __init__(self, message: str, type: str = "info", duration: float = 2.0) -> None:
        """
        Initialize a Toast instance.
        :param message: The message to display.
        :param type: The type of toast ('info', 'success', 'error', 'warning').
        :param duration: Duration in seconds the toast is visible.
        """
        self.message = message
        self.duration = duration
        self.startTime = None
        self.font = pygame.font.Font(None, 36)
        self.type = type if type in TOAST_COLORS else "info"
        self.active = False
        self.textColor, self.bgColor = TOAST_COLORS[self.type]
        self.animationDuration = 0.3
        self.currentY = 0
        self.targetY = 0
        self.isSliding = False
        self.slidingOut = False
        self.slideOutStartTime = None

    def start(self, targetY: int = 0) -> None:
        """Activate the toast and start its slide-in animation."""
        self.startTime = time.time()
        self.active = True
        self.targetY = targetY
        screen = pygame.display.get_surface()
        if screen:
            self.currentY = screen.get_height() + 60
        else:
            self.currentY = targetY + 60
        self.isSliding = True
        self.slidingOut = False

    def startSlideOut(self) -> None:
        """Begin the slide-out animation for the toast."""
        if not self.slidingOut:
            self.slidingOut = True
            self.slideOutStartTime = time.time()

    def isExpired(self) -> bool:
        """Check if the toast has finished its display and animation."""
        if not self.active:
            return False
        if self.slidingOut and self.slideOutStartTime:
            expired = time.time() - self.slideOutStartTime > self.animationDuration
            return expired
        elapsed = time.time() - self.startTime
        if elapsed > self.duration and not self.slidingOut:
            self.startSlideOut()
            return False
        return False

    def update(self) -> None:
        """Update the toast's animation and position."""
        if not self.active:
            return
        currentTime = time.time()
        if self.slidingOut and self.slideOutStartTime:
            elapsed = currentTime - self.slideOutStartTime
            progress = min(elapsed / self.animationDuration, 1.0)
            progress = 1 - (1 - progress) ** 3
            startY = self.targetY
            screen = pygame.display.get_surface()
            endY = screen.get_height() + 60 if screen else self.targetY + 60
            self.currentY = startY + (endY - startY) * progress
        elif self.isSliding:
            elapsed = currentTime - self.startTime
            progress = min(elapsed / self.animationDuration, 1.0)
            if progress < 1.0:
                progress = progress * progress * (2.7 * progress - 1.7)
            screen = pygame.display.get_surface()
            startY = screen.get_height() + 60 if screen else self.targetY + 60
            self.currentY = startY + (self.targetY - startY) * progress
            if progress >= 1.0:
                self.isSliding = False
                self.currentY = self.targetY
        else:
            if abs(self.currentY - self.targetY) > 1:
                moveSpeed = 200
                maxMove = moveSpeed * (1/60)
                if self.currentY < self.targetY:
                    self.currentY = min(self.currentY + maxMove, self.targetY)
                else:
                    self.currentY = max(self.currentY - maxMove, self.targetY)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the toast on the given screen surface."""
        if not self.active:
            return
        self.update()
        textSurf = self.font.render(self.message, True, self.textColor)
        textRect = textSurf.get_rect(center=(screen.get_width() // 2, self.currentY))
        bgRect = textRect.inflate(20, 10)
        alpha = 255
        if self.isSliding or (self.slidingOut and self.slideOutStartTime):
            if self.slidingOut:
                elapsed = time.time() - self.slideOutStartTime
                progress = min(elapsed / self.animationDuration, 1.0)
                alpha = int(255 * (1 - progress))
            elif self.isSliding:
                elapsed = time.time() - self.startTime
                progress = min(elapsed / self.animationDuration, 1.0)
                alpha = int(255 * progress)
        bgSurf = pygame.Surface((bgRect.width, bgRect.height), pygame.SRCALPHA)
        bgColor = (*self.bgColor, alpha)
        pygame.draw.rect(bgSurf, bgColor, bgSurf.get_rect(), border_radius=8)
        screen.blit(bgSurf, bgRect.topleft)
        if alpha < 255:
            textSurf.set_alpha(alpha)
        screen.blit(textSurf, textRect)

class ToastManager:
    """
    Manages multiple Toast notifications, their stacking, display, and lifecycle.
    Handles adding, updating, drawing, and clearing toasts.
    """
    def __init__(self, maxToasts: int = 5) -> None:
        """Initialize a ToastManager instance."""
        self.maxToasts = maxToasts
        self.toasts = []
        self.baseY = 50
        self.toastSpacing = 50
    
    def addToast(self, toast: Toast) -> bool:
        """Add a toast to the manager if there is room."""
        activeToasts = [t for t in self.toasts if not t.isExpired() and not t.slidingOut]
        if len(activeToasts) >= self.maxToasts:
            return False
        self.toasts.append(toast)
        self._updatePositions()
        return True
    
    def _updatePositions(self) -> None:
        """Update the Y positions of all active toasts for stacking."""
        screen = pygame.display.get_surface()
        if not screen:
            return
        screenHeight = screen.get_height()
        positionableToasts = [t for t in self.toasts if not t.isExpired() and not t.slidingOut]
        for i, toast in enumerate(positionableToasts):
            targetY = screenHeight - self.baseY - (i * self.toastSpacing)
            if toast.startTime is None:
                toast.start(targetY)
            else:
                if toast.targetY != targetY:
                    toast.targetY = targetY
    
    def update(self) -> None:
        """Update the state of all toasts, removing expired ones and updating positions."""
        initialCount = len(self.toasts)
        self.toasts = [t for t in self.toasts if not t.isExpired()]
        if len(self.toasts) != initialCount:
            self._updatePositions()
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all active toasts on the given screen surface."""
        self.update()
        for toast in self.toasts:
            if toast.active:
                toast.draw(screen)
    
    def clear(self) -> None:
        """Start slide-out animation for all toasts, clearing them from the screen."""
        for toast in self.toasts:
            toast.startSlideOut()
    
    def getActiveCount(self) -> int:
        """Get the number of currently active (visible) toasts."""
        return len([t for t in self.toasts if not t.isExpired() and not t.slidingOut])
    
    def isFull(self) -> bool:
        """Check if the toast manager is at capacity."""
        return self.getActiveCount() >= self.maxToasts