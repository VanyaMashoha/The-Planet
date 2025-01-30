import pygame


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()

        self.surface = pygame.Surface((w, h))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
