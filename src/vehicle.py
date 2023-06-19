from .config import CAR_SIZE, COLORSCHEME, WINDOW_SIZE
from .utils import percent_val

from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.rect import Rect
import pygame


class Vehicle(Sprite):
    def __init__(self):
        super().__init__()

        self.image = Surface(CAR_SIZE, pygame.SRCALPHA)
        self.speed = 0.4
        self.x = -100
        self.y = self.x + (50 / 100) * WINDOW_SIZE[1]
        self.rect = Rect((self.x, self.y), CAR_SIZE)

        self.draw()

    def draw(self):
        position = percent_val((10, 10), CAR_SIZE)
        size = percent_val((80, 80), CAR_SIZE)

        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.image,
            COLORSCHEME["red"],
            Rect(position, size),
            0
        )
        pygame.draw.rect(
            self.image,
            COLORSCHEME["black"],
            Rect((0, 0), CAR_SIZE),
            1
        )

    def update(self):
        # y = mx + b
        self.x += self.speed
        self.y = (0 * self.x) + (50 / 100) * WINDOW_SIZE[1]

        self.rect = Rect((self.x, self.y), CAR_SIZE)

    def render(self, screen):
        screen.blit(self.image, self.rect)
