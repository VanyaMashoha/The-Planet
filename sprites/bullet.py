import pygame
import math
from constants import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, walls, weapon_type):
        """
        Класс пули

        :param x:
        :param y:
        :param angle:
        :param walls:
        :param weapon_type:
        """
        super().__init__()
        self.image = pygame.Surface(weapon_type.blt_size)
        self.image.fill(weapon_type.blt_clr)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = math.radians(angle)
        self.speed = weapon_type.blt_spd
        self.position = pygame.math.Vector2(x, y)
        self.walls = walls
        self.damage = weapon_type.blt_dmg

    def update(self):
        """
        Обновление позиции пули
        """
        self.position.x += math.cos(self.angle) * self.speed
        self.position.y += math.sin(self.angle) * self.speed
        self.rect.center = self.position

        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()

        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                self.kill()
