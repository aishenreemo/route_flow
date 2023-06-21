from .vehicle import Vehicle, Road
from .config import WINDOW_SIZE, COLORSCHEME
from time import sleep
import pygame


def main():
    pygame.init()
    pygame.display.set_caption("Route Flow")

    window = pygame.display.set_mode(WINDOW_SIZE)
    running = True

    road_image = pygame.image.load("assets/roads/1.jpg")
    road_image = pygame.transform.scale(road_image, WINDOW_SIZE)

    vehicles = [
        Vehicle(Road.A, Road.B, COLORSCHEME["red"]),
        Vehicle(Road.A, Road.C, COLORSCHEME["red"]),
        Vehicle(Road.A, Road.D, COLORSCHEME["red"]),
        Vehicle(Road.B, Road.A, COLORSCHEME["yellow"]),
        Vehicle(Road.B, Road.C, COLORSCHEME["yellow"]),
        Vehicle(Road.B, Road.D, COLORSCHEME["yellow"]),
        Vehicle(Road.C, Road.A, COLORSCHEME["blue"]),
        Vehicle(Road.C, Road.B, COLORSCHEME["blue"]),
        Vehicle(Road.C, Road.D, COLORSCHEME["blue"]),
        Vehicle(Road.D, Road.A, COLORSCHEME["green"]),
        Vehicle(Road.D, Road.B, COLORSCHEME["green"]),
        Vehicle(Road.D, Road.C, COLORSCHEME["green"]),
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for vehicle in vehicles:
            vehicle.update()

        window.blit(road_image, (0, 0))

        for vehicle in vehicles:
            vehicle.render(window)

        pygame.display.flip()

        sleep(30 / 1000)


if __name__ == "__main__":
    main()
