import pygame
from sprites import Scorpion
from random import randint

class Crator(pygame.sprite.Sprite):
    def __init__(self, x, y, player, scarpions, mountains, waters, bullets):
        super().__init__()

        self.rect = (x * 64, y * 64, 64, 64)
        self.rect_left = (x * 64, y * 64, 1, 64)
        self.rect_right = (x * 64 + 63, y * 64, 1, 64)
        self.rect_top = (x * 64, y * 64, 64, 1)
        self.rect_bottom = (x * 64, y * 64 + 63, 64, 1)
        self.player = player
        self.check = False
        self.mountain_group = mountains
        self.water_group = waters
        self.scarpion_group = scarpions
        self.bullets = bullets

    def update(self):
        if self.player.rect.colliderect(self.rect) and not self.check:
            if randint(1, 10) == 3 and not self.check:
                self.scarpion_group.add(Scorpion(self.rect[0] + 32, self.rect[1] + 32, self.player,
                                                  self.mountain_group, self.water_group, self.bullets))
            self.check = True
        if not self.player.rect.colliderect(self.rect):
            self.check = False