from .config import CAR_SIZE, COLORSCHEME, WINDOW_SIZE, CELL_SIZE
from .light import TrafficLightVariant
from .utils import near_vehicles, percent_val
from .road import Road

from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame.rect import Rect
import pygame
import math

from enum import Enum


class VehicleLocation(Enum):
    ON_SOURCE = 0
    ON_TURNING = 1
    ON_DESTINATION = 2


class VehicleDirection(Enum):
    LEFT = -1
    STRAIGHT = 0
    RIGHT = 1


control_zone = Rect(
    (int((40 / 100) * WINDOW_SIZE[0]), int((40 / 100) * WINDOW_SIZE[1])),
    (int((20 / 100) * WINDOW_SIZE[0]), int((20 / 100) * WINDOW_SIZE[1])),
)

danger_zone = control_zone.inflate(-25, -25)

# initial positions
offset_map = {
    Road.A: (0, -100),
    Road.B: (100, 0),
    Road.C: (0, 100),
    Road.D: (-100, 0),
}

source_position_map = {
    Road.A: ((45 / 100) * WINDOW_SIZE[0], -100),
    Road.B: (WINDOW_SIZE[0] + 100, (45 / 100) * WINDOW_SIZE[1]),
    Road.C: ((55 / 100) * WINDOW_SIZE[0], WINDOW_SIZE[1] + 100),
    Road.D: (-100, (55 / 100) * WINDOW_SIZE[1]),
}

turning_point_map = {
    Road.A: ((45 / 100) * WINDOW_SIZE[0], (40 / 100) * WINDOW_SIZE[1]),
    Road.B: ((60 / 100) * WINDOW_SIZE[0], (45 / 100) * WINDOW_SIZE[1]),
    Road.C: ((55 / 100) * WINDOW_SIZE[0], (60 / 100) * WINDOW_SIZE[1]),
    Road.D: ((40 / 100) * WINDOW_SIZE[0], (55 / 100) * WINDOW_SIZE[1]),
}

center_point_map = {
    Road.A: ((40 / 100) * WINDOW_SIZE[0], (40 / 100) * WINDOW_SIZE[1]),
    Road.B: ((60 / 100) * WINDOW_SIZE[0], (40 / 100) * WINDOW_SIZE[1]),
    Road.C: ((60 / 100) * WINDOW_SIZE[0], (60 / 100) * WINDOW_SIZE[1]),
    Road.D: ((40 / 100) * WINDOW_SIZE[0], (60 / 100) * WINDOW_SIZE[1]),
}

destination_map = {
    Road.A: ((55 / 100) * WINDOW_SIZE[0], (40 / 100) * WINDOW_SIZE[1]),
    Road.B: ((60 / 100) * WINDOW_SIZE[0], (55 / 100) * WINDOW_SIZE[1]),
    Road.C: ((45 / 100) * WINDOW_SIZE[0], (60 / 100) * WINDOW_SIZE[1]),
    Road.D: ((40 / 100) * WINDOW_SIZE[0], (45 / 100) * WINDOW_SIZE[1]),
}

# initial velocity
velocity_map = {
    Road.A: (0, 4),
    Road.B: (-4, 0),
    Road.C: (0, -4),
    Road.D: (4, 0),
}

# initial directions
degree_map = {
    Road.A: 270,
    Road.B: 180,
    Road.C: 90,
    Road.D: 0,
}

reverse_map = {
    Road.A: Road.C,
    Road.B: Road.D,
    Road.C: Road.A,
    Road.D: Road.B,
}

direction_map = {
    -1: VehicleDirection.LEFT,
    -2: VehicleDirection.STRAIGHT,
    -3: VehicleDirection.RIGHT,
    1: VehicleDirection.RIGHT,
    2: VehicleDirection.STRAIGHT,
    3: VehicleDirection.LEFT,
}


class Vehicle(Sprite):
    def __init__(self, src: Road, dest: Road, color=COLORSCHEME["red"], acceleration=1.2):
        super().__init__()

        self.src = src
        self.dest = dest
        self.color = color
        self.acceleration = acceleration
        self.travel_time = 0
        self.delay_time = 0

        self.position = Vector2(*source_position_map[src])
        self.velocity = Vector2(*velocity_map[src])
        self.degree = degree_map[src]

        self.location = VehicleLocation.ON_SOURCE
        self.direction = direction_map[self.src.value - self.dest.value]

        self.turning_point = Vector2(*turning_point_map[self.src])
        self.destination = Vector2(*destination_map[self.dest])
        self.center_point = Vector2(*center_point_map[self.src])

        if self.direction == VehicleDirection.LEFT:
            next_enum = Road((self.src.value + 1) % 4)
            self.center_point = Vector2(*center_point_map[next_enum])

        self.stopped = False
        self.debug = False

        self.draw()

    def draw(self):
        self.image = Surface(CAR_SIZE, pygame.SRCALPHA)
        positions = [percent_val((15, 15), CAR_SIZE), percent_val((70, 15), CAR_SIZE)]
        sizes = [percent_val((70, 70), CAR_SIZE), percent_val((15, 70), CAR_SIZE)]
        colors = [self.color, COLORSCHEME["white"]]

        self.image.fill((0, 0, 0, 0))

        for i in range(0, 2):
            rect = Rect(positions[i], sizes[i])
            pygame.draw.rect(self.image, colors[i], rect)

        if self.direction != VehicleDirection.STRAIGHT:
            position = percent_val((74, 20 if self.direction == VehicleDirection.LEFT else 63), CAR_SIZE)
            size = percent_val((7, 10), CAR_SIZE)
            rect = Rect(position, size)
            pygame.draw.rect(self.image, COLORSCHEME["yellow"], rect)

        self.image = pygame.transform.rotate(self.image, self.degree)

    def update(self, grid, traffic_lights):
        if self.location == VehicleLocation.ON_SOURCE:
            distance = self.position.distance_to(self.turning_point)
            if distance <= 4:
                self.location = VehicleLocation.ON_TURNING

        elif self.location == VehicleLocation.ON_TURNING:
            if self.direction != VehicleDirection.STRAIGHT:
                direction = self.center_point - self.turning_point
                radius = direction.length()
                angular_velocity = self.velocity.length() / radius
                angle_change = math.degrees(angular_velocity) * self.direction.value
                self.degree = (self.degree - angle_change) % 360
                self.velocity = self.velocity.rotate(angle_change) * radius
                self.draw()

            distance = self.position.distance_to(self.destination)
            if distance <= 4:
                reverse_road = reverse_map[self.dest]
                self.location = VehicleLocation.ON_DESTINATION
                self.velocity = Vector2(*velocity_map[reverse_road])
                self.degree = round(self.degree / 90) * 90
                self.draw()

        min_speed = 0.01
        max_speed = 3.5

        if not self.is_safe_to_move(grid, traffic_lights):
            if self.velocity.length() > min_speed:
                self.velocity *= 0.65
        else:
            if self.velocity.length() < max_speed:
                self.velocity *= self.acceleration

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        if not self.is_stopped():
            self.position += self.velocity

    def render(self, screen):
        rect = self.image.get_rect(center=tuple(self.position))
        screen.blit(self.image, rect)

        if not self.debug:
            return

        if self.location == VehicleLocation.ON_DESTINATION:
            return

        pygame.draw.rect(screen, COLORSCHEME["red"], self.image.get_rect(center=tuple(self.position)), 1)
        pygame.draw.circle(screen, COLORSCHEME["red"], self.turning_point, 2)
        pygame.draw.circle(screen, COLORSCHEME["red"], self.destination, 2)

        if self.direction != VehicleDirection.STRAIGHT:
            radius = (self.center_point - self.turning_point).length()
            pygame.draw.circle(screen, COLORSCHEME["red"], self.center_point, radius, 1)
            pygame.draw.circle(screen, COLORSCHEME["red"], self.center_point, 2)
            pygame.draw.line(screen, COLORSCHEME["red"], self.position, self.turning_point)
        else:
            pygame.draw.line(screen, COLORSCHEME["red"], self.position, self.destination)

    def is_stopped(self):
        return self.velocity.length() <= 0.02

    def is_safe_to_move(self, grid, traffic_lights):
        is_stop = traffic_lights[self.src].variant != TrafficLightVariant.GO
        is_onsrc = self.location == VehicleLocation.ON_SOURCE
        is_close = self.image.get_rect(center=tuple(self.position)).colliderect(control_zone)
        is_danger = self.image.get_rect(center=tuple(self.position)).colliderect(danger_zone)

        if is_stop and is_onsrc and is_close and not is_danger:
            self.stopped = True
            return False

        vehicles = near_vehicles(grid, self.position)

        for vehicle in vehicles:
            if vehicle is self:
                continue

            distance_a = vehicle.position.distance_to(self.position)
            distance_b = vehicle.position.distance_to(self.position + self.velocity)
            distance_c = self.position.distance_to(vehicle.position + vehicle.velocity)

            if distance_b > distance_a:
                continue

            if distance_c < distance_a and vehicle.stopped:
                continue

            if self.is_colliding(vehicle):
                self.stopped = True
                return False

        self.stopped = False
        return True

    def is_colliding(self, vehicle):
        image_a = Surface(CAR_SIZE, pygame.SRCALPHA)
        image_b = Surface(CAR_SIZE, pygame.SRCALPHA)

        image_a.fill((0, 0, 0))
        image_b.fill((0, 0, 0))

        # Scale up the surfaces for inflation
        scaled_surface_a = pygame.transform.rotate(image_a, self.degree)
        scaled_surface_b = pygame.transform.rotate(image_b, vehicle.degree)

        # Create masks from the scaled surfaces
        scaled_mask_a = pygame.mask.from_surface(scaled_surface_a)
        scaled_mask_b = pygame.mask.from_surface(scaled_surface_b)

        # Calculate the offset between the positions of the two vehicles
        offset = (
            int(vehicle.position.x - self.position.x),
            int(vehicle.position.y - self.position.y)
        )

        # Calculate the overlap between the inflated collision masks
        overlap = scaled_mask_a.overlap(scaled_mask_b, offset)

        return bool(overlap)
