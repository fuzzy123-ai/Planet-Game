import pygame
import math
import os
from random import randrange
from dataclasses import dataclass

FPS = 1000

window = pygame.display.set_mode()
pygame.display.set_caption("My first Game!")
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)
script_path = os.path.dirname(__file__)
planet_path = os.path.join(script_path, 'Assets', 'Planets')

# TODO add some scale factor so planet image size matches planet.radius for hitbox calculations
planet_images = [
    pygame.image.load(os.path.join(planet_path, 'cheese.png')),
    pygame.image.load(os.path.join(planet_path, 'earth.png')),
    pygame.image.load(os.path.join(planet_path, 'luna.png')),
    pygame.image.load(os.path.join(planet_path, 'magma.png')),
    pygame.image.load(os.path.join(planet_path, 'saturn.png')),
    pygame.image.load(os.path.join(planet_path, 'venus.png')),
]
sun_image = pygame.image.load(os.path.join(planet_path, 'sun.png'))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

universe = []
player_planet_index = 0


class Node:
    def draw(self, elapsed):
        pass

    def update(self, delta):
        pass


class Planet(Node):
    def __init__(self, radius, color, orbit_radius, orbit_speed, orbit_offset, mass):
        self.position = [0, 0]
        self.speed = [0, 0]
        self.radius = radius
        self.color = color
        self.orbit_radius = orbit_radius
        self.orbit_speed = math.radians(orbit_speed)
        self.orbit_offset = math.radians(orbit_offset)
        self.player = 0
        self.targeting_angle = 0
        self.mass = mass

        planet_index = randrange(0, len(planet_images) - 1)
        self.image = planet_images[planet_index]

    def draw(self, elapsed):
        if self.player != 0:
            # Show pulsing marker for player planet
            pulsing_speed = 4
            pygame.draw.circle(window, (0, 220, 0), self.position, self.radius + 3 + math.sin(elapsed * pulsing_speed) * 2)

            targeting_marker_distance = self.radius + 10
            vec = self.get_targeting_vector()
            targeting_position = [vec[0] * targeting_marker_distance + self.position[0],
                                  vec[1] * targeting_marker_distance + self.position[1]]
            pygame.draw.circle(window, WHITE, targeting_position, 5)

        # pygame.draw.circle(window, self.color, self.position, self.radius)  # Plain circle for debugging

        planet_size = self.radius * 2, self.radius * 2
        image_scaled = pygame.transform.scale(self.image, planet_size)
        window.blit(image_scaled, [elem - self.radius for elem in self.position])
    def update(self, delta):
        self.orbit_offset = math.fmod(self.orbit_offset + self.orbit_speed * delta, math.pi * 2)
        new_position = [math.sin(self.orbit_offset) * self.orbit_radius + window.get_width() / 2,
                        math.cos(self.orbit_offset) * self.orbit_radius + window.get_height() / 2]

        self.speed = [new_position[i] - self.position[i] for i in range(2)]
        self.position = new_position

    def get_targeting_vector(self):
        return [math.sin(self.targeting_angle), math.cos(self.targeting_angle)]


class Vec2:
    def __init__(self, x=0, y=None):
        self.x = x
        self.y = x if y is None else y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        else:
            return Vec2(self.x * other, self.y * other)

    def normalized(self):
        length = self.length()
        return Vec2(self.x / length, self.y / length)

    def length(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))


def distance_squared(pos1, pos2):
    return math.pow(pos2.x - pos1.x, 2) + math.pow(pos2.y - pos1.y, 2)


class GravitationAffected(Node):
    def __init__(self, position, speed, mass):
        self.position = position
        self.speed = speed
        self.mass = mass

    def update(self, delta):
        speed = Vec2(*self.speed)
        for planet in universe:
            # G = 6.674e-11
            G = 30
            planet_pos = Vec2(*planet.position)
            self_pos = Vec2(*self.position)
            distance = distance_squared(planet_pos, self_pos)
            if distance > 1:
                force = G * ((self.mass * planet.mass) / distance)
                direction = (self_pos - planet_pos).normalized()

                speed = speed + direction * force

        self.position[0] += speed.x * delta
        self.position[1] += speed.y * delta


class Garbage(GravitationAffected):
    def __init__(self, position, speed, mass, radius):
        super().__init__(position, speed, mass)
        self.radius = radius

    def draw(self, elapsed):
        pygame.draw.circle(window, RED, self.position, self.radius)


def draw_window():
    window.fill(BLACK)
    # pygame.display.update()


def draw(elapsed):
    # print("draw")
    draw_window()

    for node in universe:
        node.draw(elapsed)


def update(delta):
    # print("update")
    TARGETING_SPEED = 5

    # Handle events
    for event in pygame.event.get():
        pressed_keys = pygame.key.get_pressed()

        if event.type == pygame.QUIT or pressed_keys[pygame.K_ESCAPE]:
            quit()

        if pressed_keys[pygame.K_SPACE]:
            planet = universe[player_planet_index]
            speed = [elem * 50 for elem in planet.get_targeting_vector()]
            speed = [speed[i] + planet.speed[i] for i in range(2)]
            mass = 10
            universe.append(Garbage(planet.position.copy(), speed, mass, 10))

        if pressed_keys[pygame.K_d]:
            planet = universe[player_planet_index]
            planet.targeting_angle += math.radians(TARGETING_SPEED)

        if pressed_keys[pygame.K_a]:
            planet = universe[player_planet_index]
            planet.targeting_angle -= math.radians(TARGETING_SPEED)

    # Update the universe
    for node in universe:
        node.update(delta)


def main():
    pygame.init()
    clock = pygame.time.Clock()

    sun_radius = 50
    max_orbit_radius = min(window.get_width(), window.get_height()) / 2 * 0.9
    orbit_radius = sun_radius
    planet_count = 5
    orbit_radius_step = max_orbit_radius / planet_count
    planet_radius_max = int(orbit_radius_step / 2)
    planet_radius_min = int(planet_radius_max * 0.8)

    for i in range(planet_count):
        radius = randrange(planet_radius_min, planet_radius_max)
        orbit_radius += orbit_radius_step

        color = [randrange(0, 255), randrange(0, 255), randrange(0, 255)]
        # Prevent planets being too dark
        if max(color) < 50:
            color[randrange(0, 2)] = 255

        universe.append(Planet(radius,
                               color,
                               orbit_radius,
                               orbit_speed=randrange(5, 20),
                               orbit_offset=randrange(0, 360),
                               mass=radius))

    global player_planet_index
    player_planet_index = randrange(0, len(universe) - 1)
    universe[player_planet_index].player = 1

    sun = Planet(sun_radius, (255, 255, 0), 0, 0, 0, sun_radius)
    sun.image = sun_image
    universe.append(sun)

    while True:
        delta = clock.tick(FPS) / 1000
        update(delta)
        elapsed = pygame.time.get_ticks() / 1000
        draw(elapsed)

        # textsurface = myfont.render(str(clock.get_fps()), False, RED)
        # window.blit(textsurface, (5, 5))

        pygame.display.flip()


if __name__ == '__main__':
    main()
