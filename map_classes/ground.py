import pygame

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.rect = (x * 64, y * 64, 64, 64)