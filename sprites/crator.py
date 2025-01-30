import pygame
from sprites.scorpion import Scorpion
from random import randint


class Crator(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, player, scarpions, mountains, waters, bullets):
        super().__init__()

        self.surface = pygame.Surface((w, h))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.check = False
        self.mountain_group = mountains
        self.water_group = waters
        self.scarpion_group = scarpions
        self.bullets = bullets

    def update(self):
        if self.player.rect.colliderect(self.rect) and not self.check:
            if randint(1, 10) == 3 and not self.check:
                self.scarpion_group.add(
                    Scorpion(
                        self.rect[0] + 32,
                        self.rect[1] + 32,
                        self.player,
                        self.mountain_group,
                        self.water_group,
                        self.bullets,
                    )
                )
            self.check = True
        if not self.player.rect.colliderect(self.rect):
            self.check = False
