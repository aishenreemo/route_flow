from .config import CAR_SIZE, COLORSCHEME, WINDOW_SIZE
from .light import TrafficLightVariant
from .utils import percent_val
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
    RIGHT = -1
    STRAIGHT = 0
    LEFT = 1


control_zone = Rect(
    (int((40 / 100) * WINDOW_SIZE[0]), int((40 / 100) * WINDOW_SIZE[1])),
    (int((20 / 100) * WINDOW_SIZE[0]), int((20 / 100) * WINDOW_SIZE[1])),
)

danger_zone = control_zone.inflate(-20, -20)

# initial positions
source_position_map = {
    Road.A: ((45 / 100) * WINDOW_SIZE[0], -500),
    Road.B: (WINDOW_SIZE[0] + 500, (45 / 100) * WINDOW_SIZE[1]),
    Road.C: ((55 / 100) * WINDOW_SIZE[0], WINDOW_SIZE[1] + 500),
    Road.D: (-500, (55 / 100) * WINDOW_SIZE[1]),
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
    -1: VehicleDirection.RIGHT,
    -2: VehicleDirection.STRAIGHT,
    -3: VehicleDirection.LEFT,
    1: VehicleDirection.LEFT,
    2: VehicleDirection.STRAIGHT,
    3: VehicleDirection.RIGHT,
}


class Vehicle(Sprite):
    def __init__(self, src: Road, dest: Road, color=COLORSCHEME["red"]):
        super().__init__()

        self.src = src
        self.dest = dest
        self.color = color

        self.position = Vector2(*source_position_map[src])
        self.velocity = Vector2(*velocity_map[src])
        self.degree = degree_map[src]

        self.location = VehicleLocation.ON_SOURCE
        self.direction = direction_map[self.src.value - self.dest.value]

        self.turning_point = Vector2(*turning_point_map[self.src])
        self.destination = Vector2(*destination_map[self.dest])
        self.center_point = Vector2(*center_point_map[self.src])

        if self.direction == VehicleDirection.RIGHT:
            next_enum = Road((self.src.value + 1) % 4)
            self.center_point = Vector2(*center_point_map[next_enum])

        self.stopped = False

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

        self.image = pygame.transform.rotate(self.image, self.degree)

    def update(self, vehicles, traffic_lights):
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
        max_speed = 4

        if not self.is_safe_to_move(vehicles, traffic_lights):
            if self.velocity.length() > min_speed:
                self.velocity *= 0.3
        else:
            if self.velocity.length() < max_speed:
                self.velocity *= 1.2

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        if self.velocity.length() > 0.02:
            self.position += self.velocity

    def render(self, screen):
        rect = self.image.get_rect(center=tuple(self.position))
        screen.blit(self.image, rect)

    def is_safe_to_move(self, vehicles, traffic_lights):
        is_stop = traffic_lights[self.src].variant != TrafficLightVariant.GO
        is_onsrc = self.location == VehicleLocation.ON_SOURCE
        is_close = self.image.get_rect(center=tuple(self.position)).colliderect(control_zone)
        is_danger = self.image.get_rect(center=tuple(self.position)).colliderect(danger_zone)

        if is_stop and is_onsrc and is_close and not is_danger:
            self.stopped = True
            return False

        for vehicle in vehicles[::-1]:
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
