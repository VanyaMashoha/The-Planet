from .weapon_inventory import *
from .constants import *
from .audio import sounds
import pygame
import math

from sprites import load_image


class Player(pygame.sprite.Sprite):
    def __init__(self, platforms, grounds, waters, walls, scorpions):
        '''
        Инициализация класса игрока

        :param platforms:
        :param grounds:
        :param waters:
        :param walls:

        :return: None
        '''
        super().__init__()
        self.score = 0
        self.wpn = inventory[1]
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
        self.scorpions = scorpions

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

        for water in self.waters:
            if future_rect.colliderect(water.rect) or future_rect.colliderect(water.rect):
                self.velocity_x = 0
            if future_rect.colliderect(water.rect) or future_rect.colliderect(water.rect):
                self.velocity_y = 0

        for wall in self.walls:
            if future_rect.colliderect(wall.rect) or future_rect.colliderect(wall.rect_right):
                self.velocity_x = 0
            if future_rect.colliderect(wall.rect) or future_rect.colliderect(wall.rect):
                self.velocity_y = 0
        
        # Проверка границ карты
        if 0 <= future_rect.x and future_rect.right <= SCREEN_WIDTH:
            self.rect.x += self.velocity_x

        if self.map == 'spawn' and future_rect.right >= SCREEN_WIDTH and len(self.scorpions) == 0:
            self.map = 'right_map'
            
        elif self.map == 'right_map' and future_rect.left <= SCREEN_WIDTH and len(self.scorpions) == 0:
            self.map = 'spawn'
            
        
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
        if keys[pygame.K_1] and self.wpn != inventory[1]:
            sounds['ui'].play()
            self.wpn = inventory[1]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_2] and self.wpn != inventory[2]:
            sounds['ui'].play()
            self.wpn = inventory[2]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_3] and self.wpn != inventory[3]:
            sounds['ui'].play()
            self.wpn = inventory[3]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_4] and self.wpn != inventory[4]:
            sounds['ui'].play()
            self.wpn = inventory[4]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_5] and self.wpn != inventory[5]:
            sounds['ui'].play()
            self.wpn = inventory[5]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_6] and self.wpn != inventory[6]:
            sounds['ui'].play()
            self.wpn = inventory[6]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_7] and self.wpn != inventory[7]:
            sounds['ui'].play()
            self.wpn = inventory[7]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_8] and self.wpn != inventory[8]:
            sounds['ui'].play()
            self.wpn = inventory[8]
            self.speed = self.wpn.plr_spd
        elif keys[pygame.K_9] and self.wpn != inventory[9]:
            sounds['ui'].play()
            self.wpn = inventory[9]
            self.speed = self.wpn.plr_spd