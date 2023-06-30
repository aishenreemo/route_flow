from .vehicle import Vehicle, Road, VehicleLocation, offset_map
from .config import WINDOW_SIZE, COLORSCHEME, CELL_SIZE
from .utils import near_vehicles
from .light import TrafficLight 
from pygame.math import Vector2
from pygame.font import Font
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
    grid = {}

    spawn_timer = 0
    spawn_interval = 0

    max_vehicles = 200

    traffic_lights = {}

    total_travel_time = 0
    traveled_vehicle_count = 0

    total_delay = 0
    delayed_vehicle_count = 0

    font = Font(None, 16)

    for road in Road:
        traffic_lights[road] = TrafficLight(road)

    while running:
        update_grid(grid, vehicles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for traffic_light in traffic_lights.values():
                    if traffic_light.image.get_rect(center=tuple(traffic_light.position)).collidepoint(mouse_pos):
                        traffic_light.toggle()
                        break

                selected_vehicles = near_vehicles(grid, Vector2(*mouse_pos))

                for vehicle in selected_vehicles:
                    if vehicle.image.get_rect(center=tuple(vehicle.position)).collidepoint(mouse_pos):
                        vehicle.debug = not vehicle.debug
                        break

        vehicles_to_remove = []

        for vehicle in vehicles:
            vehicle_rect = vehicle.image.get_rect(center=vehicle.position)
            vehicle_is_inside = window.get_rect().colliderect(vehicle_rect)
            vehicle_passed = vehicle.location == VehicleLocation.ON_DESTINATION

            if not vehicle_is_inside and vehicle_passed:
                vehicles_to_remove.append(vehicle)
            else:
                vehicle.update(grid, traffic_lights)

            if vehicle_is_inside or not vehicle_passed:
                vehicle.travel_time += clock.get_time() / 1000

            if vehicle.is_stopped():
                vehicle.delay_time += clock.get_time() / 1000

        for vehicle in vehicles_to_remove:
            total_travel_time += vehicle.travel_time
            traveled_vehicle_count += 1
            total_delay += vehicle.delay_time
            delayed_vehicle_count += 1
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
            if not new_vehicle.is_safe_to_move(grid, traffic_lights):
                new_vehicle.position += Vector2(*offset_map[new_vehicle.src])

            vehicles.append(new_vehicle)

            spawn_timer = 0
            spawn_interval = random.randint(0, 1500) 

        seconds_since_awake = pygame.time.get_ticks() / 1000
        window.blit(font.render("seconds since awake: {:.2f}s".format(seconds_since_awake), True, COLORSCHEME["black"]), (10, 10))

        congestion_level = len(vehicles) / max_vehicles
        window.blit(font.render("congestion level: {:.2%}".format(congestion_level), True, COLORSCHEME["black"]), (10, 20))

        average_travel_time = total_travel_time / traveled_vehicle_count if traveled_vehicle_count > 0 else 0
        window.blit(font.render("avg travel time: {:.2f}s".format(average_travel_time), True, COLORSCHEME["black"]), (10, 30))

        average_delay = total_delay / delayed_vehicle_count if delayed_vehicle_count > 0 else 0
        window.blit(font.render("avg delay: {:.2f}s".format(average_delay), True, COLORSCHEME["black"]), (10, 40))

        window.blit(font.render("total vehicles: {}".format(len(vehicles)), True, COLORSCHEME["black"]), (10, 50))

        pygame.display.flip()

        clock.tick(30)

    pygame.quit()


def spawn_vehicle():
    roads = list(Road)
    colors = list(COLORSCHEME.values())[1:]

    src = random.choice(roads)
    dest = random.choice(roads)
    color = random.choice(colors)
    acceleration = random.uniform(1.3, 1.5)

    while src == dest:
        dest = random.choice(roads)

    return Vehicle(src, dest, color, acceleration)


def update_grid(grid, vehicles):
    grid.clear()

    for vehicle in vehicles:
        cell_x = int(vehicle.position.x / CELL_SIZE[0])
        cell_y = int(vehicle.position.y / CELL_SIZE[1])
        cell_key = (cell_x, cell_y)

        if cell_key in grid:
            grid[cell_key].append(vehicle)
        else:
            grid[cell_key] = [vehicle]


if __name__ == "__main__":
    main()
