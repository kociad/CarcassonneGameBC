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


def draw_line_alpha(
    surface: pygame.Surface,
    color: tuple[int, ...],
    start_pos: tuple[int, int],
    end_pos: tuple[int, int],
    width: int = 1,
) -> None:
    rgb, alpha = _split_color(color)
    if alpha >= 255:
        pygame.draw.line(surface, (*rgb, alpha), start_pos, end_pos, width)
        return
    min_x = min(start_pos[0], end_pos[0])
    min_y = min(start_pos[1], end_pos[1])
    max_x = max(start_pos[0], end_pos[0])
    max_y = max(start_pos[1], end_pos[1])
    pad = max(1, width)
    temp_width = max(1, max_x - min_x + pad * 2)
    temp_height = max(1, max_y - min_y + pad * 2)
    temp = pygame.Surface((temp_width, temp_height), pygame.SRCALPHA)
    local_start = (start_pos[0] - min_x + pad, start_pos[1] - min_y + pad)
    local_end = (end_pos[0] - min_x + pad, end_pos[1] - min_y + pad)
    pygame.draw.line(temp, (*rgb, alpha), local_start, local_end, width)
    surface.blit(temp, (min_x - pad, min_y - pad))
