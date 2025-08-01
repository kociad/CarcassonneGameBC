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
    """A toast notification component."""

    def __init__(self,
                 message: str,
                 type: str = "info",
                 duration: float = 1.5) -> None:
        """
        Initialize the toast notification.
        
        Args:
            message: Message to display
            type: Type of toast (info, success, error, warning)
            duration: How long to display the toast at bottom position (default 1.5s)
        """
        self.message = message
        self.duration = duration
        self.startTime = None
        self.font = pygame.font.Font(None, 36)
        self.type = type if type in TOAST_COLORS else "info"
        self.active = False

        self.textColor, self.bgColor = TOAST_COLORS[self.type]

        self.animationDuration = 0.5
        self.currentY = 0
        self.targetY = 0
        self.isSliding = False
        self.slidingOut = False
        self.slideOutStartTime = None
        self.bottomStartTime = None
        self.baseY = 50
        self.manager = None

    def start(self, targetY: int = 0) -> None:
        """
        Start the toast animation.
        
        Args:
            targetY: Target Y position for the toast
        """
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

    def reposition(self, targetY: int) -> None:
        """
        Reposition the toast with animation from current position.
        
        Args:
            targetY: New target Y position for the toast
        """
        if self.targetY != targetY:
            self.targetY = targetY
            if not self.isSliding and not self.slidingOut:
                self.moveStartTime = time.time()
                self.moveStartY = self.currentY

    def startSlideOut(self) -> None:
        """Start the slide-out animation."""
        if not self.slidingOut:
            self.slidingOut = True
            self.slideOutStartTime = time.time()
            self._triggerPositionUpdate()

    def _triggerPositionUpdate(self) -> None:
        """Trigger immediate position update for all toasts."""
        if self.manager:
            self.manager._triggerImmediateUpdate()

    def _bounceEase(self, t: float) -> float:
        """
        Bounce easing function for smooth, bouncy animations.
        
        Args:
            t: Progress value between 0 and 1
            
        Returns:
            Eased progress value with bounce effect
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            t = 2 * t - 2
            return 0.5 * t * t * t + 1

    def isExpired(self) -> bool:
        """Check if the toast has expired."""
        if not self.active:
            return False

        if self.slidingOut and self.slideOutStartTime:
            elapsed = time.time() - self.slideOutStartTime
            return elapsed > self.animationDuration

        if self.isSliding:
            return False

        if not self.slidingOut and self.bottomStartTime is None:
            screen = pygame.display.get_surface()
            if screen:
                bottomY = screen.get_height() - self.baseY
                if abs(self.currentY - bottomY) < 5:
                    self.bottomStartTime = time.time()

        if self.bottomStartTime and not self.slidingOut:
            if time.time() - self.bottomStartTime > self.duration:
                self.startSlideOut()
                return False

        return False

    def update(self) -> None:
        """Update the toast animation."""
        if not self.active:
            return

        currentTime = time.time()

        if self.slidingOut and self.slideOutStartTime:
            elapsed = currentTime - self.slideOutStartTime
            progress = min(elapsed / self.animationDuration, 1.0)

            progress = 1 - self._bounceEase(1 - progress)

            startY = self.targetY
            screen = pygame.display.get_surface()
            endY = screen.get_height() + 60 if screen else self.targetY + 60
            self.currentY = startY + (endY - startY) * progress

        elif self.isSliding:
            elapsed = currentTime - self.startTime
            progress = min(elapsed / self.animationDuration, 1.0)

            if progress < 1.0:
                progress = self._bounceEase(progress)

            screen = pygame.display.get_surface()
            startY = screen.get_height() + 60 if screen else self.targetY + 60
            self.currentY = startY + (self.targetY - startY) * progress

            if progress >= 1.0:
                self.isSliding = False
                self.currentY = self.targetY

        else:
            if abs(self.currentY - self.targetY) > 1:
                if not hasattr(self, 'moveStartTime'):
                    self.moveStartTime = time.time()
                    self.moveStartY = self.currentY

                elapsed = currentTime - self.moveStartTime
                progress = min(elapsed / self.animationDuration, 1.0)

                if progress < 1.0:
                    progress = self._bounceEase(progress)
                    self.currentY = self.moveStartY + (
                        self.targetY - self.moveStartY) * progress
                else:
                    self.currentY = self.targetY
                    if hasattr(self, 'moveStartTime'):
                        delattr(self, 'moveStartTime')
                        delattr(self, 'moveStartY')

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the toast on the screen.
        
        Args:
            screen: Surface to draw on
        """
        if not self.active:
            return

        self.update()

        textSurf = self.font.render(self.message, True, self.textColor)
        textRect = textSurf.get_rect(center=(screen.get_width() // 2,
                                             self.currentY))

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
    """Manages multiple toast notifications."""

    def __init__(self,
                 maxToasts: int = 5,
                 delayBetweenToasts: float = 0.3) -> None:
        """
        Initialize the toast manager.
        
        Args:
            maxToasts: Maximum number of toasts to display simultaneously
            delayBetweenToasts: Delay in seconds between adding multiple toasts
        """
        self.maxToasts = maxToasts
        self.toasts = []
        self.toastQueue = []
        self.baseY = 50
        self.toastSpacing = 50
        self.delayBetweenToasts = delayBetweenToasts
        self.lastToastTime = 0
        self.processingQueue = False

    def addToast(self, toast: Toast) -> bool:
        """
        Add a toast to the manager with delay if multiple toasts are added quickly.
        
        Args:
            toast: Toast to add
            
        Returns:
            True if toast was added or queued, False if manager is full
        """
        currentTime = time.time()

        if self.toastQueue and (currentTime -
                                self.lastToastTime) >= self.delayBetweenToasts:
            self._processQueue()

        activeToasts = [
            t for t in self.toasts if not t.isExpired() and not t.slidingOut
        ]

        if len(activeToasts) >= self.maxToasts:
            self.toastQueue.append(toast)
            return True

        if not self.toasts or (currentTime -
                               self.lastToastTime) >= self.delayBetweenToasts:
            toast.manager = self
            self.toasts.append(toast)
            self.lastToastTime = currentTime
            self._updatePositions()
            return True
        else:
            self.toastQueue.append(toast)
            return True

    def _processQueue(self) -> None:
        """Process the toast queue and add toasts with proper timing."""
        if not self.toastQueue:
            return

        activeToasts = [
            t for t in self.toasts if not t.isExpired() and not t.slidingOut
        ]

        if self.toastQueue and len(activeToasts) < self.maxToasts:
            self.processingQueue = True
            toast = self.toastQueue.pop(0)
            toast.manager = self
            self.toasts.append(toast)
            self.lastToastTime = time.time()
            self._updatePositions()
            self.processingQueue = False

    def _updatePositions(self) -> None:
        """Update the positions of all active toasts."""
        screen = pygame.display.get_surface()
        if not screen:
            return

        screenHeight = screen.get_height()

        positionableToasts = [
            t for t in self.toasts if not t.isExpired() and not t.slidingOut
        ]

        for i, toast in enumerate(positionableToasts):
            targetY = screenHeight - self.baseY - (i * self.toastSpacing)

            if toast.startTime is None:
                toast.start(targetY)
            elif toast.targetY != targetY:
                toast.reposition(targetY)

    def _triggerImmediateUpdate(self) -> None:
        """Trigger immediate position update when a toast starts sliding out."""
        self._updatePositions()

    def update(self) -> None:
        """Update all toasts, remove expired ones, and process queue."""
        initialCount = len(self.toasts)
        self.toasts = [t for t in self.toasts if not t.isExpired()]

        if len(self.toasts) != initialCount:
            self._updatePositions()

        currentTime = time.time()
        if self.toastQueue and (currentTime -
                                self.lastToastTime) >= self.delayBetweenToasts:
            self._processQueue()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw all active toasts.
        
        Args:
            screen: Surface to draw on
        """
        self.update()

        for toast in self.toasts:
            if toast.active:
                toast.draw(screen)

    def clear(self) -> None:
        """Start slide-out animation for all toasts and clear queue."""
        for toast in self.toasts:
            toast.startSlideOut()
        self.toastQueue.clear()

    def getActiveCount(self) -> int:
        """Get the number of active toasts."""
        return len(
            [t for t in self.toasts if not t.isExpired() and not t.slidingOut])

    def isFull(self) -> bool:
        """Check if the manager is at maximum capacity."""
        return self.getActiveCount() >= self.maxToasts

    def getQueueSize(self) -> int:
        """Get the number of toasts waiting in the queue."""
        return len(self.toastQueue)
