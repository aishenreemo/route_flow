from .vehicle import Vehicle, Road, VehicleLocation, offset_map
from .config import WINDOW_SIZE, COLORSCHEME, CELL_SIZE
from .utils import near_vehicles
from .light import TrafficLight, traffic_light_position_map
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

    spawn = {
        Road.A: { "timer": 0, "interval": 0 },
        Road.B: { "timer": 0, "interval": 0 },
        Road.C: { "timer": 0, "interval": 0 },
        Road.D: { "timer": 0, "interval": 0 },
    }

    max_vehicles = 200

    traffic_lights = {}

    font = Font(None, 16)

    # create traffic lights
    for road in Road:
        traffic_lights[road] = TrafficLight(road)

    while running:
        # spatial partitioning
        update_grid(grid, vehicles)

        # listen for events
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
        total_travel_time = 0
        total_delay = 0
        queue_lengths = {
            Road.A: 0,
            Road.B: 0,
            Road.C: 0,
            Road.D: 0,
        }

        for vehicle in vehicles:
            vehicle_rect = vehicle.image.get_rect(center=vehicle.position)
            vehicle_is_inside = window.get_rect().colliderect(vehicle_rect)
            vehicle_passed = vehicle.location == VehicleLocation.ON_DESTINATION

            # mark this vehicle for removal
            if not vehicle_is_inside and vehicle_passed:
                vehicles_to_remove.append(vehicle)
                continue

            # accumulate travel time
            if vehicle_is_inside or not vehicle_passed:
                vehicle.travel_time += clock.get_time() / 1000

            # accumulate delay time
            if vehicle.is_stopped():
                vehicle.delay_time += clock.get_time() / 1000

            # accumulate queue length
            if vehicle.location == VehicleLocation.ON_SOURCE:
                queue_lengths[vehicle.src] += 1

            vehicle.update(grid, traffic_lights)

            total_travel_time += vehicle.travel_time
            total_delay += vehicle.delay_time

        # remove marked vehicles
        for vehicle in vehicles_to_remove:
            vehicles.remove(vehicle)

        # blit background image
        window.blit(road_image, (0, 0))

        # rendering vehicles
        for vehicle in vehicles:
            vehicle.render(window)

        # rendering traffic lights
        for traffic_light in traffic_lights.values():
            traffic_light.update(clock)
            traffic_light.render(window)

        # spawning a vehicle
        for road in Road:
            spawn[road]["timer"] += clock.get_time()

            if spawn[road]["timer"] >= spawn[road]["interval"] and len(vehicles) < max_vehicles:
                vehicles.append(spawn_vehicle(grid, traffic_lights, road))

                spawn[road]["interval"] = random.randint(1500, 7500)
                spawn[road]["timer"] = 0

        # statistics
        vehicles_length = len(vehicles)
        seconds_since_awake = pygame.time.get_ticks() / 1000
        congestion_level = len(vehicles) / max_vehicles
        average_travel_time = total_travel_time / vehicles_length if vehicles_length > 0 else 0
        average_delay = total_delay / vehicles_length if vehicles_length > 0 else 0

        window.blit(font.render("seconds since awake: {:.2f}s".format(seconds_since_awake), True, COLORSCHEME["black"]), (10, 10))
        window.blit(font.render("congestion level: {:.2%}".format(congestion_level), True, COLORSCHEME["black"]), (10, 20))
        window.blit(font.render("avg travel time: {:.2f}s".format(average_travel_time), True, COLORSCHEME["black"]), (10, 30))
        window.blit(font.render("avg delay: {:.2f}s".format(average_delay), True, COLORSCHEME["black"]), (10, 40))
        window.blit(font.render("total vehicles: {}".format(vehicles_length), True, COLORSCHEME["black"]), (10, 50))

        # queue lengths
        for road in Road:
            position = Vector2(*traffic_light_position_map[road])
            offsets = { Road.A: (-5, -50), Road.B: (-5, -50), Road.C: (-5, 40), Road.D: (-5, 40) }

            window.blit(font.render(str(queue_lengths[road]), True, COLORSCHEME["black"]), position + offsets[road])

        pygame.display.flip()

        clock.tick(30)

    pygame.quit()


def spawn_vehicle(grid, traffic_lights, src):
    roads = list(Road)
    colors = list(COLORSCHEME.values())[1:]

    dest = random.choice(roads)
    color = random.choice(colors)
    acceleration = random.uniform(1.3, 1.5)

    while src == dest:
        dest = random.choice(roads)

    new_vehicle = Vehicle(src, dest, color, acceleration)
    while not new_vehicle.is_safe_to_move(grid, traffic_lights):
        new_vehicle.position += Vector2(*offset_map[new_vehicle.src])

    return new_vehicle


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
