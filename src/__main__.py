from .vehicle import Vehicle, Road
from .config import WINDOW_SIZE, COLORSCHEME
import pygame


def main():
    pygame.init()
    pygame.display.set_caption("Route Flow")

    window = pygame.display.set_mode(WINDOW_SIZE)
    running = True

    road_image = pygame.image.load("assets/roads/1.jpg")
    road_image = pygame.transform.scale(road_image, WINDOW_SIZE)

    test_vehicle_1 = Vehicle(Road.A, Road.B, COLORSCHEME["red"])
    test_vehicle_2 = Vehicle(Road.B, Road.A, COLORSCHEME["blue"])
    test_vehicle_3 = Vehicle(Road.C, Road.D, COLORSCHEME["green"])
    test_vehicle_4 = Vehicle(Road.D, Road.C, COLORSCHEME["yellow"])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        test_vehicle_1.update()
        test_vehicle_2.update()
        test_vehicle_3.update()
        test_vehicle_4.update()

        window.blit(road_image, (0, 0))
        test_vehicle_1.render(window)
        test_vehicle_2.render(window)
        test_vehicle_3.render(window)
        test_vehicle_4.render(window)
        pygame.display.flip()


if __name__ == "__main__":
    main()
