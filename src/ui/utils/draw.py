from __future__ import annotations

import pygame
import typing


def _split_color(color: tuple[int, ...]) -> tuple[tuple[int, int, int], int]:
    if len(color) == 4:
        return (color[0], color[1], color[2]), color[3]
    return (color[0], color[1], color[2]), 255


def draw_rect_alpha(
    surface: pygame.Surface,
    color: tuple[int, ...],
    rect: pygame.Rect | tuple[int, int, int, int],
    width: int = 0,
) -> None:
    rgb, alpha = _split_color(color)
    if alpha >= 255:
        pygame.draw.rect(surface, (*rgb, alpha), rect, width)
        return
    target_rect = pygame.Rect(rect)
    temp = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(temp, (*rgb, alpha), temp.get_rect(), width)
    surface.blit(temp, target_rect.topleft)


def draw_circle_alpha(
    surface: pygame.Surface,
    color: tuple[int, ...],
    center: tuple[int, int],
    radius: int,
    width: int = 0,
) -> None:
    rgb, alpha = _split_color(color)
    if alpha >= 255:
        pygame.draw.circle(surface, (*rgb, alpha), center, radius, width)
        return
    diameter = radius * 2 + max(2, width * 2)
    temp = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    temp_center = (diameter // 2, diameter // 2)
    pygame.draw.circle(temp, (*rgb, alpha), temp_center, radius, width)
    surface.blit(temp, (center[0] - temp_center[0], center[1] - temp_center[1]))
