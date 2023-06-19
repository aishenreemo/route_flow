from .vehicle import Vehicle
from .config import WINDOW_SIZE
import pygame


def main():
    pygame.init()
    pygame.display.set_caption("Route Flow")

    window = pygame.display.set_mode(WINDOW_SIZE)
    running = True

    road_image = pygame.image.load("assets/roads/1.jpg")
    road_image = pygame.transform.scale(road_image, WINDOW_SIZE)

    test_vehicle = Vehicle()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        test_vehicle.update()

        window.blit(road_image, (0, 0))
        test_vehicle.render(window)
        pygame.display.flip()


if __name__ == "__main__":
    main()
