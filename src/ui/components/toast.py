import pygame
import time
import math
import logging
import typing

from ui import theme

logger = logging.getLogger(__name__)

TOAST_COLORS = theme.THEME_TOAST_COLORS


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
        self.start_time = None
        self.font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.type = type if type in TOAST_COLORS else "info"
        self.active = False

        self.text_color, self.bg_color = TOAST_COLORS[self.type]

        self.animation_duration = 0.5
        self.current_y = 0
        self.target_y = 0
        self.is_sliding = False
        self.sliding_out = False
        self.slide_out_start_time = None
        self.bottom_start_time = None
        self.base_y = 50
        self.manager = None

    def start(self, target_y: int = 0) -> None:
        """
        Start the toast animation.
        
        Args:
            target_y: Target Y position for the toast
        """
        self.start_time = time.time()
        self.active = True
        self.target_y = target_y

        screen = pygame.display.get_surface()
        if screen:
            self.current_y = screen.get_height() + 60
        else:
            self.current_y = target_y + 60

        self.is_sliding = True
        self.sliding_out = False

    def reposition(self, target_y: int) -> None:
        """
        Reposition the toast with animation from current position.
        
        Args:
            target_y: New target Y position for the toast
        """
        if self.target_y != target_y:
            self.target_y = target_y
            if not self.is_sliding and not self.sliding_out:
                self.move_start_time = time.time()
                self.move_start_y = self.current_y

    def start_slide_out(self) -> None:
        """Start the slide-out animation."""
        if not self.sliding_out:
            self.sliding_out = True
            self.slide_out_start_time = time.time()
            self._trigger_position_update()

    def _trigger_position_update(self) -> None:
        """Trigger immediate position update for all toasts."""
        if self.manager:
            self.manager._trigger_immediate_update()

    def _bounce_ease(self, t: float) -> float:
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

    def is_expired(self) -> bool:
        """Check if the toast has expired."""
        if not self.active:
            return False

        if self.sliding_out and self.slide_out_start_time:
            elapsed = time.time() - self.slide_out_start_time
            return elapsed > self.animation_duration

        if self.is_sliding:
            return False

        if not self.sliding_out and self.bottom_start_time is None:
            screen = pygame.display.get_surface()
            if screen:
                bottom_y = screen.get_height() - self.base_y
                if abs(self.current_y - bottom_y) < 5:
                    self.bottom_start_time = time.time()

        if self.bottom_start_time and not self.sliding_out:
            if time.time() - self.bottom_start_time > self.duration:
                self.start_slide_out()
                return False

        return False

    def update(self) -> None:
        """Update the toast animation."""
        if not self.active:
            return

        current_time = time.time()

        if self.sliding_out and self.slide_out_start_time:
            elapsed = current_time - self.slide_out_start_time
            progress = min(elapsed / self.animation_duration, 1.0)

            progress = 1 - self._bounce_ease(1 - progress)

            start_y = self.target_y
            screen = pygame.display.get_surface()
            end_y = screen.get_height() + 60 if screen else self.target_y + 60
            self.current_y = start_y + (end_y - start_y) * progress

        elif self.is_sliding:
            elapsed = current_time - self.start_time
            progress = min(elapsed / self.animation_duration, 1.0)

            if progress < 1.0:
                progress = self._bounce_ease(progress)

            screen = pygame.display.get_surface()
            start_y = screen.get_height(
            ) + 60 if screen else self.target_y + 60
            self.current_y = start_y + (self.target_y - start_y) * progress

            if progress >= 1.0:
                self.is_sliding = False
                self.current_y = self.target_y

        else:
            if abs(self.current_y - self.target_y) > 1:
                if not hasattr(self, 'move_start_time'):
                    self.move_start_time = time.time()
                    self.move_start_y = self.current_y

                elapsed = current_time - self.move_start_time
                progress = min(elapsed / self.animation_duration, 1.0)

                if progress < 1.0:
                    progress = self._bounce_ease(progress)
                    self.current_y = self.move_start_y + (
                        self.target_y - self.move_start_y) * progress
                else:
                    self.current_y = self.target_y
                    if hasattr(self, 'move_start_time'):
                        delattr(self, 'move_start_time')
                        delattr(self, 'move_start_y')

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the toast on the screen.
        
        Args:
            screen: Surface to draw on
        """
        if not self.active:
            return

        self.update()

        text_surf = self.font.render(self.message, True, self.text_color)
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2,
                                               self.current_y))

        bg_rect = text_rect.inflate(20, 10)

        alpha = 255
        if self.is_sliding or (self.sliding_out and self.slide_out_start_time):
            if self.sliding_out:
                elapsed = time.time() - self.slide_out_start_time
                progress = min(elapsed / self.animation_duration, 1.0)
                alpha = int(255 * (1 - progress))
            elif self.is_sliding:
                elapsed = time.time() - self.start_time
                progress = min(elapsed / self.animation_duration, 1.0)
                alpha = int(255 * progress)

        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height),
                                 pygame.SRCALPHA)
        bg_color = (*self.bg_color, alpha)
        pygame.draw.rect(bg_surf,
                         bg_color,
                         bg_surf.get_rect(),
                         border_radius=8)
        screen.blit(bg_surf, bg_rect.topleft)

        if alpha < 255:
            text_surf.set_alpha(alpha)

        screen.blit(text_surf, text_rect)


class ToastManager:
    """Manages multiple toast notifications."""

    def __init__(self,
                 max_toasts: int = 5,
                 delay_between_toasts: float = 0.3) -> None:
        """
        Initialize the toast manager.
        
        Args:
            max_toasts: Maximum number of toasts to display simultaneously
            delay_between_toasts: Delay in seconds between adding multiple toasts
        """
        self.max_toasts = max_toasts
        self.toasts = []
        self.toast_queue = []
        self.base_y = 50
        self.toast_spacing = 50
        self.delay_between_toasts = delay_between_toasts
        self.last_toast_time = 0
        self.processing_queue = False

    def add_toast(self, toast: Toast) -> bool:
        """
        Add a toast to the manager with delay if multiple toasts are added quickly.
        
        Args:
            toast: Toast to add
            
        Returns:
            True if toast was added or queued, False if manager is full
        """
        current_time = time.time()

        if self.toast_queue and (current_time - self.last_toast_time
                                 ) >= self.delay_between_toasts:
            self._process_queue()

        active_toasts = [
            t for t in self.toasts if not t.is_expired() and not t.sliding_out
        ]

        if len(active_toasts) >= self.max_toasts:
            self.toast_queue.append(toast)
            return True

        if not self.toasts or (current_time - self.last_toast_time
                               ) >= self.delay_between_toasts:
            toast.manager = self
            self.toasts.append(toast)
            self.last_toast_time = current_time
            self._update_positions()
            return True
        else:
            self.toast_queue.append(toast)
            return True

    def _process_queue(self) -> None:
        """Process the toast queue and add toasts with proper timing."""
        if not self.toast_queue:
            return

        active_toasts = [
            t for t in self.toasts if not t.is_expired() and not t.sliding_out
        ]

        if self.toast_queue and len(active_toasts) < self.max_toasts:
            self.processing_queue = True
            toast = self.toast_queue.pop(0)
            toast.manager = self
            self.toasts.append(toast)
            self.last_toast_time = time.time()
            self._update_positions()
            self.processing_queue = False

    def _update_positions(self) -> None:
        """Update the positions of all active toasts."""
        screen = pygame.display.get_surface()
        if not screen:
            return

        screen_height = screen.get_height()

        positionable_toasts = [
            t for t in self.toasts if not t.is_expired() and not t.sliding_out
        ]

        for i, toast in enumerate(positionable_toasts):
            target_y = screen_height - self.base_y - (i * self.toast_spacing)

            if toast.start_time is None:
                toast.start(target_y)
            elif toast.target_y != target_y:
                toast.reposition(target_y)

    def _trigger_immediate_update(self) -> None:
        """Trigger immediate position update when a toast starts sliding out."""
        self._update_positions()

    def update(self) -> None:
        """Update all toasts, remove expired ones, and process queue."""
        initial_count = len(self.toasts)
        self.toasts = [t for t in self.toasts if not t.is_expired()]

        if len(self.toasts) != initial_count:
            self._update_positions()

        current_time = time.time()
        if self.toast_queue and (current_time - self.last_toast_time
                                 ) >= self.delay_between_toasts:
            self._process_queue()

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
            toast.start_slide_out()
        self.toast_queue.clear()

    def get_active_count(self) -> int:
        """Get the number of active toasts."""
        return len([
            t for t in self.toasts if not t.is_expired() and not t.sliding_out
        ])

    def is_full(self) -> bool:
        """Check if the manager is at maximum capacity."""
        return self.get_active_count() >= self.max_toasts

    def get_queue_size(self) -> int:
        """Get the number of toasts waiting in the queue."""
        return len(self.toast_queue)
