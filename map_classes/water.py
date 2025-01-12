import pygame


class Water(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.rect = (x * 64, y * 64, 64, 64)
        self.rect_left = (x * 64, y * 64, 1, 64)
        self.rect_right = (x * 64 + 63, y * 64, 1, 64)
        self.rect_top = (x * 64, y * 64, 64, 1)
        self.rect_bottom = (x * 64, y * 64 + 63, 64, 1)
