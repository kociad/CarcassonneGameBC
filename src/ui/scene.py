import os
import pygame
import typing
import settings
from ui.components.toast import Toast


class Scene:
    """Base class for all scenes in the UI."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        self.screen = screen
        self.switch_scene = switch_scene_callback
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self._background_cache: dict[tuple, pygame.Surface] = {}

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the scene."""
        raise NotImplementedError

    def update(self) -> None:
        """Update the scene state."""
        pass

    def draw(self) -> None:
        """Draw the scene."""
        raise NotImplementedError

    def show_notification(self, notification_type: str, message: str) -> None:
        """
        Show notification toast - available to all scenes that have a toast_manager
        """
        if hasattr(self, 'toast_manager'):
            toast_type_map = {
                "error": "error",
                "warning": "warning",
                "info": "info",
                "success": "success"
            }

            toast_type = toast_type_map.get(notification_type, "info")
            toast = Toast(message, type=toast_type, duration=3)

            self.toast_manager.add_toast(toast)

    def _apply_scroll(self, events: list[pygame.event.Event]) -> None:
        """Apply scroll events to the scene."""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset += event.y * self.scroll_speed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.scroll_offset -= self.scroll_speed
                elif event.key == pygame.K_UP:
                    self.scroll_offset += self.scroll_speed
        self.scroll_offset = max(
            min(0, self.scroll_offset),
            min(0,
                self.screen.get_height() - self.max_scroll))

    def _get_scroll_offset(self) -> int:
        """Return the current scroll offset."""
        return self.scroll_offset

    def _draw_background(
        self,
        background_color: tuple[int, int, int] | None,
        image_name: str | None,
        scale_mode: str | None,
        tint_color: tuple[int, int, int, int] | None,
        blur_radius: float | int | None,
        surface: pygame.Surface | None = None,
    ) -> None:
        """Draw the background on the provided surface or the scene screen."""
        target_surface = surface or self.screen
        if background_color is not None:
            target_surface.fill(background_color)

        image_surface = self._get_background_surface(
            image_name=image_name,
            target_size=target_surface.get_size(),
            scale_mode=scale_mode,
            blur_radius=blur_radius,
        )
        if image_surface is not None:
            target_surface.blit(image_surface, (0, 0))

        if tint_color is not None:
            overlay = pygame.Surface(target_surface.get_size(),
                                     pygame.SRCALPHA)
            overlay.fill(tint_color)
            target_surface.blit(overlay, (0, 0))

    def _get_background_surface(
        self,
        image_name: str | None,
        target_size: tuple[int, int],
        scale_mode: str | None,
        blur_radius: float | int | None,
    ) -> pygame.Surface | None:
        if not image_name:
            return None

        image_path = os.path.join(settings.BACKGROUND_IMAGE_PATH, image_name)
        cache_key = (image_path, target_size, scale_mode, blur_radius)
        cached = self._background_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            image = pygame.image.load(image_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

        scaled = self._scale_background_image(image, target_size, scale_mode)
        blurred = self._apply_background_blur(scaled, blur_radius)
        self._background_cache[cache_key] = blurred
        return blurred

    def _scale_background_image(
        self,
        image: pygame.Surface,
        target_size: tuple[int, int],
        scale_mode: str | None,
    ) -> pygame.Surface:
        mode = (scale_mode or "fill").lower()
        target_width, target_height = target_size
        image_width, image_height = image.get_size()
        if image_width == 0 or image_height == 0:
            return pygame.transform.smoothscale(image, target_size)

        if mode == "stretch":
            return pygame.transform.smoothscale(image, target_size)

        if mode == "fit":
            scale = min(target_width / image_width,
                        target_height / image_height)
        else:
            scale = max(target_width / image_width,
                        target_height / image_height)

        scaled_size = (
            max(1, int(image_width * scale)),
            max(1, int(image_height * scale)),
        )
        scaled = pygame.transform.smoothscale(image, scaled_size)
        result = pygame.Surface(target_size, pygame.SRCALPHA)
        offset_x = (target_width - scaled_size[0]) // 2
        offset_y = (target_height - scaled_size[1]) // 2
        result.blit(scaled, (offset_x, offset_y))
        return result

    def _apply_background_blur(
        self,
        image: pygame.Surface,
        blur_radius: float | int | None,
    ) -> pygame.Surface:
        if not blur_radius or blur_radius <= 0:
            return image

        width, height = image.get_size()
        strength = max(1.0, float(blur_radius))
        divisor = max(1, int(strength * 2))
        downscaled = pygame.transform.smoothscale(
            image,
            (max(1, width // divisor), max(1, height // divisor)),
        )
        return pygame.transform.smoothscale(downscaled, (width, height))
