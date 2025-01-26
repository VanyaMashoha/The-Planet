import math
import os
import random
import pygame
import sys

import weapon_inventory
from constants import *
from weapon_inventory import *
from audio import sounds


def load_image(name, colorkey=None):
    '''
    Загрузка изображения

    :param name: путь к изображению
    :param colorkey: цветовой ключ
    :return: image
    '''
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
        '''
        Инициализация класса частиц

        :param x: позиция по x
        :param y: позиция по y
        :param color: цвет

        :return: None
        '''
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
        '''
        Обновление позиции частицы

        :return: None
        '''
        self.velocity_y += GRAVITY * 0.1
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        '''
        Инициализация класса платформы

        :param x: позиция по x
        :param y: позиция по y
        :param width: ширина
        :param height: высота

        :return: None
        '''
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, platforms, grounds, waters, walls):
        '''
        Инициализация класса игрока

        :param platforms:
        :param grounds:
        :param waters:
        :param walls:

        :return: None
        '''
        super().__init__()
        self.wpn = weapon_inventory.inventory[1]
        self.point = "left"
        self.image = load_image("images/Main_hero_left_1.png")
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        self.speed = self.wpn.plr_spd
        self.health = PLAYER_HEALTH
        self.angle = 0

        self.velocity_y = 0
        self.velocity_x = 0
        self.number_of_pos = 1
        self.time = 0
        self.time_old = 0
        self.time_num = 0
        self.on_ground = False
        self.platforms = platforms
        self.grounds = grounds
        self.waters = waters
        self.walls = walls

    def update(self, keys):
        self.time += 1
        self._handle_horizontal_movement(keys)
        self._handle_vertical_movement()
        self._handle_rotation()
        self._handle_boundaries()
        self._animated_movement()
        self._handle_weapon_change(keys)

    def _animated_movement(self):
        number_of_pos = self.time_num % 3 + 1 
        if self.point == "left":
            self.image = load_image(f"images/Main_hero_left_{number_of_pos}.png")
        else:
            self.image = load_image(f"images/Main_hero_right_{number_of_pos}.png")

    def set_pos(self):
        if self.time_old == 0:
            self.time_old = self.time
        if (self.time - self.time_old) % 10 == 0:
            self.time_num += 1

    def _handle_horizontal_movement(self, keys):
        self.velocity_x = 0
        self.velocity_y = 0
        if keys[pygame.K_a]:
            self.velocity_x, self.point = -self.speed, "left"
            self.set_pos()
        if keys[pygame.K_d]:
            self.velocity_x, self.point = self.speed, "right"
            self.set_pos()
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.set_pos()
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.set_pos()

        future_rect = self.rect.copy()
        future_rect.x += self.velocity_x
        future_rect.y += self.velocity_y

        future_rect_x = self.rect.copy()
        future_rect_x.x += self.velocity_x

        future_rect_y = self.rect.copy()
        future_rect_y.y += self.velocity_y


        for water in self.waters:
            if future_rect_x.colliderect(water.rect_left) or future_rect.colliderect(water.rect_right):
                self.velocity_x = 0
            if future_rect_y.colliderect(water.rect_top) or future_rect.colliderect(water.rect_bottom):
                self.velocity_y = 0

        for wall in self.walls:
            if future_rect_x.colliderect(wall.rect_left) or future_rect.colliderect(wall.rect_right):
                self.velocity_x = 0
            if future_rect_y.colliderect(wall.rect_top) or future_rect.colliderect(wall.rect_bottom):
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

    def _handle_weapon_change(self, keys):
        if keys[pygame.K_1] and self.wpn != weapon_inventory.inventory[1]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[1]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_2] and self.wpn != weapon_inventory.inventory[2]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[2]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_3] and self.wpn != weapon_inventory.inventory[3]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[3]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_4] and self.wpn != weapon_inventory.inventory[4]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[4]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_5] and self.wpn != weapon_inventory.inventory[5]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[5]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_6] and self.wpn != weapon_inventory.inventory[6]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[6]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_7] and self.wpn != weapon_inventory.inventory[7]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[7]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_8] and self.wpn != weapon_inventory.inventory[8]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[8]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_9] and self.wpn != weapon_inventory.inventory[9]:
            sounds['ui'].play()
            self.wpn = weapon_inventory.inventory[9]
            self.speed = self.wpn.plr_spd

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, walls, weapon_type):
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
        self.position.x += math.cos(self.angle) * self.speed
        self.position.y += math.sin(self.angle) * self.speed
        self.rect.center = self.position

        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()

        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                self.kill()


class Scorpion(pygame.sprite.Sprite):
    def __init__(self, x, y, player, walls, waters, bullets):
        super().__init__()
        self.image = load_image("images/scorpion_walk_right_1.png")
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = SCORPION_SPEED
        self.health = SCORPION_HEALTH
        self.player = player
        self.walls = walls
        self.waters = waters
        self.bullets = bullets
        self.pos = 'right'
        self.time = 0
        self.time_num = 0
        self.col_with_player = False
        self.time_col_player = 0
        self.atack_is = False

    def update(self):
        v_x = 0
        v_y = 0
        self.time += 1
        if self.col_with_player:
            self.time_col_player += 1
        if self.time_col_player > 30:
            self.col_with_player = False
            self.time_col_player = 0
        if self.time % 30:
            self.time_num += 1
        if self.player.rect.x > self.rect.x:
            self.pos = 'left'
            self.image = load_image(f"images/scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_x = self.speed
        else:
            self.pos = 'right'
            self.image = load_image(f"images/scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_x = -self.speed
        if self.player.rect.y > self.rect.y:
            self.image = load_image(f"images/scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_y = self.speed
        else:
            self.image = load_image(f"images/scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_y = -self.speed
        
        if self.atack_is:
            self.image = load_image(f"images/scorpion_atack_{self.pos}_{self.time_num % 3 + 1}.png")
        print(self.image)
        future_rect_x = self.rect.copy()
        future_rect_x.x += v_x

        future_rect_y = self.rect.copy()
        future_rect_y.y += v_y

        for water in self.waters:
            if future_rect_x.colliderect(water.rect):
                v_x = 0
            if future_rect_y.colliderect(water.rect):
                v_y = 0

        for wall in self.walls:
            if future_rect_x.colliderect(wall.rect):
                v_x = 0
            if future_rect_y.colliderect(wall.rect):
                v_y = 0

        self.rect.x += v_x
        self.rect.y += v_y

        if self.rect.colliderect(self.player.rect) and not self.col_with_player:
            self.time_num = 0
            self.player.health -= 10
            self.col_with_player = True
            sounds['player_dmg'].play()
        
        for bullet in self.bullets:
            if self.rect.colliderect(bullet.rect):
                self.health -= 10
                bullet.kill()
                sounds['enemy_dmg'].play()

        if self.health < 0:
            self.kill()
