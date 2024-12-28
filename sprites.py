import math
import random
import pygame
from constants import *


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
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
        self.velocity_y += GRAVITY * 0.1
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, platforms):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.angle = 0

        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.platforms = platforms

    def update(self, keys):
        self._handle_horizontal_movement(keys)
        self._handle_vertical_movement(keys)
        self._handle_rotation()
        self._handle_boundaries()

    def _handle_horizontal_movement(self, keys):
        self.velocity_x = 0
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        future_rect = self.rect.copy()
        future_rect.x += self.velocity_x

        # Проверка границ карты
        if 0 <= future_rect.x and future_rect.right <= SCREEN_WIDTH:
            self.rect.x += self.velocity_x

        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

    def _handle_vertical_movement(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = PLAYER_JUMP_SPEED
            self.on_ground = False

        self.velocity_y += GRAVITY
        future_rect = self.rect.copy()
        future_rect.y += self.velocity_y

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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = math.radians(angle)
        self.speed = BULLET_SPEED
        self.position = pygame.math.Vector2(x, y)

    def update(self):
        self.position.x += math.cos(self.angle) * self.speed
        self.position.y += math.sin(self.angle) * self.speed
        self.rect.center = self.position

        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = NPC_SPEED
        self.health = NPC_HEALTH
        self.damage_timer = 0
        self.platforms = platforms
        self.velocity_y = 0

    def update(self, player, npcs):
        self._apply_gravity()
        self._handle_movement(player)
        self._handle_player_collision(player)
        self._handle_boundaries()

    def _apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0

    def _handle_movement(self, player):
        if abs(player.rect.x - self.rect.x) > 10:
            future_rect = self.rect.copy()

            if player.rect.x > self.rect.x:
                future_rect.x += self.speed
            else:
                future_rect.x -= self.speed

            # Проверка границ перед движением
            if 0 <= future_rect.x and future_rect.right <= SCREEN_WIDTH:
                self.rect.x = future_rect.x

    def _handle_player_collision(self, player):
        if self.rect.colliderect(player.rect):
            if pygame.time.get_ticks() - self.damage_timer > 1000:
                player.health -= 10
                self.damage_timer = pygame.time.get_ticks()

    def _handle_boundaries(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
