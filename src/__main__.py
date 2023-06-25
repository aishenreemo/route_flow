from .vehicle import Vehicle, Road, VehicleLocation
from .config import WINDOW_SIZE, COLORSCHEME
from .light import TrafficLight, TrafficLightVariant
import pygame
import random


def main():
    pygame.init()
    pygame.display.set_caption("Route Flow")

    window = pygame.display.set_mode(WINDOW_SIZE)
    running = True

    road_image = pygame.image.load("assets/roads/1.jpg")
    road_image = pygame.transform.scale(road_image, WINDOW_SIZE)

    clock = pygame.time.Clock()

    vehicles = []

    spawn_timer = 0
    spawn_interval = 0

    max_vehicles = 24

    traffic_lights = {}
    for road in Road:
        traffic_lights[road] = TrafficLight(road)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for traffic_light in traffic_lights.values():
                    if traffic_light.image.get_rect(center=tuple(traffic_light.position)).collidepoint(mouse_pos):
                        traffic_light.toggle()

        vehicles_to_remove = []

        for vehicle in vehicles:
            vehicle_rect = vehicle.image.get_rect(center=vehicle.position)
            vehicle_is_inside = window.get_rect().colliderect(vehicle_rect)
            vehicle_passed = vehicle.location == VehicleLocation.ON_DESTINATION

            if not vehicle_is_inside and vehicle_passed:
                vehicles_to_remove.append(vehicle)
            else:
                vehicle.update(vehicles, traffic_lights)

        for vehicle in vehicles_to_remove:
            vehicles.remove(vehicle)

        window.blit(road_image, (0, 0))

        for vehicle in vehicles:
            vehicle.render(window)

        for traffic_light in traffic_lights.values():
            traffic_light.update(clock)
            traffic_light.render(window)

        spawn_timer += clock.get_time()
        if spawn_timer >= spawn_interval and len(vehicles) < max_vehicles:
            new_vehicle = spawn_vehicle()
            if (new_vehicle.is_safe_to_move(vehicles, traffic_lights)):
                vehicles.append(new_vehicle)

            spawn_timer = 0
            spawn_interval = random.randint(200, 500) 

        pygame.display.flip()

        clock.tick(30)

    pygame.quit()


def spawn_vehicle():
    roads = list(Road)
    colors = list(COLORSCHEME.values())[1:]

    src = random.choice(roads)
    dest = random.choice(roads)
    color = random.choice(colors)
    acceleration = random.uniform(1.1, 1.4)

    while src == dest:
        dest = random.choice(roads)

    return Vehicle(src, dest, color, acceleration)


if __name__ == "__main__":
    main()
