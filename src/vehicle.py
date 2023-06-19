from .config import CAR_SIZE, COLORSCHEME, WINDOW_SIZE
from .utils import percent_val

from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.rect import Rect
import pygame

from enum import Enum


class Road(Enum):
    A = 0
    B = 1
    C = 2
    D = 3


class Vehicle(Sprite):
    def __init__(self, src: Road, dest: Road, color=COLORSCHEME["red"]):
        super().__init__()

        self.src = src
        self.dest = dest
        self.color = color

        if self.src == Road.A:
            self.x = (45 / 100) * WINDOW_SIZE[0]
            self.y = (0 / 100) * WINDOW_SIZE[1] - 100
            self.velocity = (0.0, 0.4)
            self.degree = 90
        elif self.src == Road.B:
            self.x = (100 / 100) * WINDOW_SIZE[0] + 100
            self.y = (45 / 100) * WINDOW_SIZE[1]
            self.velocity = (-0.4, 0.0)
            self.degree = 180
        elif self.src == Road.C:
            self.x = (55 / 100) * WINDOW_SIZE[0]
            self.y = (100 / 100) * WINDOW_SIZE[1] + 100
            self.velocity = (0.0, -0.4)
            self.degree = 270
        elif self.src == Road.D:
            self.x = (0 / 100) * WINDOW_SIZE[0] - 100
            self.y = (55 / 100) * WINDOW_SIZE[1]
            self.velocity = (0.4, 0.0)
            self.degree = 0

        self.image = Surface(CAR_SIZE, pygame.SRCALPHA)
        self.turning = True

        self.draw()

    def draw(self):
        position = percent_val((10, 10), CAR_SIZE)
        size = percent_val((80, 80), CAR_SIZE)

        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.image,
            self.color,
            Rect(position, size),
            0
        )
        # pygame.draw.rect(
        #     self.image,
        #     COLORSCHEME["black"],
        #     Rect((0, 0), CAR_SIZE),
        #     1
        # )

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def render(self, screen):
        if self.turning:
            self.image = pygame.transform.rotate(self.image, self.degree)
            self.turning = False

        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)
