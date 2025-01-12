import pygame
import os
from constants import *
from sprites import Player, Bullet, Particle
from database import DatabaseManager
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap
from map_classes.ground import Ground
from map_classes.water import Water
from map_classes.mountain import Mountain
from crator import Crator


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Planet")
        self.clock = pygame.time.Clock()
        self.db = DatabaseManager()
        self._init_sprites()
        self.running = True
        self.tmx_data = load_pygame('data/maps/spawn.tmx')
        one, two = 0, 0
        for _ in range(30 * 17):
            if two == 0:
                self.mountain_group.add(Mountain(one, two))
            elif two == 16:
                self.water_group.add(Water(one, two))
            elif 0 < two < 16 and one == 29:
                self.crator_group.add(Crator(one, two, self.player, self.scarpion_group, self.mountain_group,
                                        self.water_group, self.bullets))
            else:
                self.ground_group.add(Ground(one, two))
            one += 1
            if one == 30:
                one, two = 0, two + 1

    # Отрисовка карты
    def draw_map(self, screen, tmx_data: TiledMap):
        for layer in tmx_data.visible_layers:
            for x, y, gid in layer:
                if gid != 0:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    # Инициализация групп спрайтов
    def _init_sprites(self):
        self.platforms = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.mountain_group = pygame.sprite.Group()
        self.crator_group = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.scarpion_group = pygame.sprite.Group()

        self.player = Player(self.platforms, self.ground_group, self.water_group, self.mountain_group)
        self.particles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.platforms, self.player,
                self.water_group, self.mountain_group, self.crator_group, self.scarpion_group
        )

    # Создание частиц при столкновении
    def create_impact_particles(self, x, y, color):
        for _ in range(PARTICLE_COUNT):
            particle = Particle(x, y, color)
            self.particles.add(particle)
            self.all_sprites.add(particle)

    # Обработка событий 
    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Если окно закрыто
                self.running = False # Остановить игру
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type == pygame.KEYUP and (event.key == pygame.K_a or event.key == pygame.K_d or event.key == pygame.K_s or event.key == pygame.K_w):
                self.player.time_num = 0
                self.player.time_old = 0
                keys = self.handle_events()
                self.update(keys)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Если нажата ЛКМ
                    self._create_bullet() # Создание пули

        return keys

    # Создание пули
    def _create_bullet(self):
        bullet = Bullet(
            self.player.rect.centerx, self.player.rect.centery, self.player.angle, self.mountain_group
        )
        self.bullets.add(bullet) # Добавление пули в группу
        self.all_sprites.add(bullet) # Добавление пули в общую группу

    # Обновление состояния игры
    def update(self, keys):
        self.player.update(keys)
        self.bullets.update()
        self.particles.update()
        self.crator_group.update()
        self.scarpion_group.update()

        self._handle_collisions()

    # Обработка столкновений
    def _handle_collisions(self):
        for bullet in self.bullets:
            if pygame.sprite.spritecollide(bullet, self.platforms, False):
                self.create_impact_particles(
                    bullet.rect.centerx, bullet.rect.centery, ORANGE
                )
                bullet.kill()
                continue

    def draw(self):
        self.draw_map(self.screen, self.tmx_data)
        self.all_sprites.draw(self.screen)

        # Отрисовка UI
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (10, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            keys = self.handle_events()
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)

        self.db.close()
        pygame.quit()
