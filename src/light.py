from .config import TRAFFIC_LIGHT_SIZE, COLORSCHEME, WINDOW_SIZE
from .utils import percent_val
from .road import Road
from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame.rect import Rect
from enum import Enum
import pygame

traffic_light_position_map = {
    Road.A: ((35 / 100) * WINDOW_SIZE[0], (32.5 / 100) * WINDOW_SIZE[1]),
    Road.B: ((65 / 100) * WINDOW_SIZE[0], (32.5 / 100) * WINDOW_SIZE[1]),
    Road.C: ((65 / 100) * WINDOW_SIZE[0], (67.5 / 100) * WINDOW_SIZE[1]),
    Road.D: ((35 / 100) * WINDOW_SIZE[0], (67.5 / 100) * WINDOW_SIZE[1]),
}


class TrafficLightVariant(Enum):
    STOP = 0
    SLOW = 1
    GO = 2


class TrafficLight(Sprite):
    def __init__(self, src: Road):
        super().__init__()

        self.src = src
        self.variant = TrafficLightVariant.STOP
        self.position = Vector2(*traffic_light_position_map[src])
        self.draw()

    def draw(self):
        self.image = Surface(TRAFFIC_LIGHT_SIZE, pygame.SRCALPHA)

        positions = [
            percent_val((25, 12.5), TRAFFIC_LIGHT_SIZE),
            percent_val((25, 40), TRAFFIC_LIGHT_SIZE),
            percent_val((25, 67.5), TRAFFIC_LIGHT_SIZE),
        ]
        sizes = [
            percent_val((50, 22), TRAFFIC_LIGHT_SIZE),
            percent_val((50, 22), TRAFFIC_LIGHT_SIZE),
            percent_val((50, 22), TRAFFIC_LIGHT_SIZE),
        ]

        colors = [
            COLORSCHEME["red"],
            COLORSCHEME["yellow"],
            COLORSCHEME["green"],
        ]

        self.image.fill(COLORSCHEME["black"])

        for i in range(0, 3):
            rect = Rect(positions[i], sizes[i])
            width = 0 if self.variant.value == i else 1
            pygame.draw.rect(self.image, colors[i], rect, width)

    def render(self, screen):
        rect = self.image.get_rect(center=tuple(self.position))
        screen.blit(self.image, rect)
