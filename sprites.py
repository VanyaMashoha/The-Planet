import math
import os
import random
import pygame
import sys
from constants import *


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
    return image


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(2, 4)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, PARTICLE_SPEED)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed

        self.lifetime = PARTICLE_LIFETIME

    def update(self):
        self.velocity_y += GRAVITY * 0.1
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, platforms, grounds, waters):
        super().__init__()
        self.point = "left"
        self.image = load_image("images/Main_hero_left_1.png")
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.angle = 0

        self.velocity_y = 0
        self.velocity_x = 0
        self.number_of_pos = 1
        self.time_num = 0
        self.time_of_animation = 0
        self.on_ground = False
        self.platforms = platforms
        self.grounds = grounds
        self.waters = waters

    def update(self, keys, time):
        self._handle_horizontal_movement(keys, time)
        self._handle_vertical_movement()
        self._handle_rotation()
        self._handle_boundaries()
        self._animated_movement()

    def _animated_movement(self):
        self.number_of_pos = self.time_num % 3 + 1
        if self.point == "left":
            self.image = load_image(f"images/Main_hero_left_{self.number_of_pos}.png")
        else:
            self.image = load_image(f"images/Main_hero_right_{self.number_of_pos}.png")

    def set_pos(self, time):
        if self.time_of_animation == 0:
            self.time_of_animation = time
        if (time - self.time_of_animation) % 20 == 0:
            self.time_num += 1

    def _handle_horizontal_movement(self, keys, time):
        self.velocity_x = 0
        self.velocity_y = 0
        if keys[pygame.K_a]:
            self.velocity_x, self.point = -self.speed, "left"
            self.set_pos(time)
        if keys[pygame.K_d]:
            self.velocity_x, self.point = self.speed, "right"
            self.set_pos(time)
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.set_pos(time)
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.set_pos(time)

        future_rect = self.rect.copy()
        future_rect.x += self.velocity_x
        future_rect.y += self.velocity_y

        for water in self.waters:
            if future_rect.colliderect(water.rect_left) or future_rect.colliderect(
                water.rect_right
            ):
                self.velocity_x = 0
            if future_rect.colliderect(water.rect_top) or future_rect.colliderect(
                water.rect_bottom
            ):
                self.velocity_y = 0

        # Проверка границ карты
        if 0 <= future_rect.x and future_rect.right <= SCREEN_WIDTH:
            self.rect.x += self.velocity_x

        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

    def _handle_vertical_movement(self):
        future_rect = self.rect.copy()
        future_rect.y += self.velocity_y

        # Проверка верхней границы
        if future_rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        else:
            self.rect.y += self.velocity_y

        self.on_ground = False
        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        # Проверка нижней границы
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True

    def _handle_rotation(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.degrees(
            math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)
        )

    def _handle_boundaries(self):
        # Финальная проверка границ
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = math.radians(angle)
        self.speed = BULLET_SPEED
        self.position = pygame.math.Vector2(x, y)

    def update(self):
        self.position.x += math.cos(self.angle) * self.speed
        self.position.y += math.sin(self.angle) * self.speed
        self.rect.center = self.position

        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()
