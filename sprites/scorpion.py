import os
import sys
import pygame
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

class Scorpion(pygame.sprite.Sprite):
    def __init__(self, x, y, player, walls, waters, bullets):
        super().__init__()
        self.image = load_image("images\scorpion_walk_right_1.png")
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
        if self.time % 10 == 0:
            self.time_num += 1
        if self.player.rect.x > self.rect.x:
            self.pos = 'right'
            self.image = load_image(f"images\scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_x = self.speed
        else:
            self.pos = 'left'
            self.image = load_image(f"images\scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_x = -self.speed
        if self.player.rect.y > self.rect.y:
            self.image = load_image(f"images\scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_y = self.speed
        else:
            self.image = load_image(f"images\scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_y = -self.speed
        
        if self.atack_is:
            self.image = load_image(f"images\scorpion_atack_{self.pos}_{self.time_num % 3 + 1}.png")
        future_rect = self.rect.copy()
        future_rect.x += v_x
        future_rect.y += v_y

        for water in self.waters:
            if future_rect.colliderect(water.rect):
                v_x = 0
            if future_rect.colliderect(water.rect):
                v_y = 0

        for wall in self.walls:
            if future_rect.colliderect(wall.rect):
                v_x = 0
            if future_rect.colliderect(wall.rect):
                v_y = 0

        self.rect.x += v_x
        self.rect.y += v_y

        if self.rect.colliderect(self.player.rect) and not self.col_with_player:
            self.time_num = 0
            self.player.health -= 10
            self.col_with_player = True
            self.atack_is = True
        else:
            self.atack_is = False
        
        for bullet in self.bullets:
            if self.rect.colliderect(bullet.rect):
                self.health -= 10
                bullet.kill()

        if self.health < 0:
            self.kill()