import pygame
import typing

from ui import theme
from ui.components.toast import Toast


class Scene:
    """Base class for all scenes in the UI."""

    _background_cache: dict[tuple[
        str,
        tuple[int, int],
        str,
        float
    ], tuple[pygame.Surface, tuple[int, int]] | None] = {}

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        self.screen = screen
        self.switch_scene = switch_scene_callback
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the scene."""
        raise NotImplementedError

    def update(self) -> None:
        """Update the scene state."""
        pass

    def draw(self) -> None:
        """Draw the scene."""
        raise NotImplementedError

    def _draw_background(
        self,
        image_path: str | None = None,
        scale_mode_override: str | None = None,
        tint_color_override: theme.ColorA | None = None,
        blur_radius_override: float | None = None
    ) -> None:
        """Draw shared scene background with optional image, blur, and tint."""
        self.screen.fill(theme.THEME_SCENE_BG_COLOR)
        resolved_image_path = (
            image_path
            if image_path is not None
            else theme.THEME_BACKGROUND_IMAGE
        )
        image_path = resolved_image_path
        if not image_path:
            return

        screen_size = self.screen.get_size()
        scale_mode_value = (
            scale_mode_override
            if scale_mode_override is not None
            else theme.THEME_BACKGROUND_SCALE_MODE
        )
        scale_mode = (
            str(scale_mode_value).lower().strip()
            if scale_mode_value
            else "fill"
        )
        blur_value = (
            blur_radius_override
            if blur_radius_override is not None
            else theme.THEME_BACKGROUND_BLUR_RADIUS
        )
        blur_strength = float(blur_value) if blur_value else 0.0
        cache_key = (image_path, screen_size, scale_mode, blur_strength)

        cached = self._background_cache.get(cache_key)
        if cached is None and cache_key in self._background_cache:
            return

        if cached is None:
            try:
                source_image = pygame.image.load(image_path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self._background_cache[cache_key] = None
                return

            scaled_image, position = self._scale_background(
                source_image,
                screen_size,
                scale_mode
            )
            if blur_strength > 0:
                scaled_image = self._blur_surface(
                    scaled_image,
                    blur_strength
                )
            cached = (scaled_image, position)
            self._background_cache[cache_key] = cached

        background_image, position = cached
        self.screen.blit(background_image, position)

        tint_color = (
            tint_color_override
            if tint_color_override is not None
            else theme.THEME_BACKGROUND_TINT_COLOR
        )
        if tint_color is not None and tint_color[3] > 0:
            overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
            overlay.fill(tint_color)
            self.screen.blit(overlay, (0, 0))

    def _scale_background(
        self,
        image: pygame.Surface,
        screen_size: tuple[int, int],
        scale_mode: str
    ) -> tuple[pygame.Surface, tuple[int, int]]:
        """Scale and position background image based on mode."""
        screen_width, screen_height = screen_size
        image_width, image_height = image.get_size()

        if scale_mode == "stretch":
            scaled = pygame.transform.smoothscale(
                image,
                (screen_width, screen_height)
            )
            return scaled, (0, 0)

        if scale_mode == "fit":
            ratio = min(
                screen_width / image_width,
                screen_height / image_height
            )
        else:
            ratio = max(
                screen_width / image_width,
                screen_height / image_height
            )

        scaled_width = max(1, int(image_width * ratio))
        scaled_height = max(1, int(image_height * ratio))
        scaled = pygame.transform.smoothscale(
            image,
            (scaled_width, scaled_height)
        )
        position = (
            (screen_width - scaled_width) // 2,
            (screen_height - scaled_height) // 2
        )
        return scaled, position

    def _blur_surface(
        self,
        surface: pygame.Surface,
        blur_strength: float
    ) -> pygame.Surface:
        """Apply a lightweight blur via downscale/upscale."""
        if blur_strength <= 1:
            return surface

        scale_factor = max(2, int(round(blur_strength)))
        width, height = surface.get_size()
        small_size = (max(1, width // scale_factor),
                      max(1, height // scale_factor))
        downscaled = pygame.transform.smoothscale(surface, small_size)
        return pygame.transform.smoothscale(downscaled, (width, height))

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
