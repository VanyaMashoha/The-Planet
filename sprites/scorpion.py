import os
import sys
import pygame
from constants import *
from sprites import load_image


class Scorpion(pygame.sprite.Sprite):
    def __init__(self, x, y, player, walls, waters, bullets):
        """
        Класс скорпиона

        :param x:
        :param y:
        :param player:
        :param walls:
        :param waters:
        :param bullets:
        :param bullets:
        """
        super().__init__()
        self.image = load_image("images/scorpion_walk_right_1.png")
        
        # Вектор от игрока к (x, y)
        dx = x - player.rect.x
        dy = y - player.rect.y

        # Переносим спрайт на противоположную сторону со сдвигом
        scorpion_x = x + dx + (1 if dx != 0 else 0)  # Сдвиг по X
        scorpion_y = y + dy + (1 if dy != 0 else 0)  # Сдвиг по Y
        
        self.rect = self.image.get_rect(center=(scorpion_x, scorpion_y))
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
        """
        Обновление скорпиона
        """
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
            self.image = load_image(f"images/scorpion_walk_{self.pos}_{self.time_num % 3 + 1}.png")
            v_x = self.speed
        else:
            self.pos = 'left'
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