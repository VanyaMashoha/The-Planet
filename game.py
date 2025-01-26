from stat import S_ISCHR

import pygame
import os
from constants import *
from database import DatabaseManager
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap
from sprites.bullet import Bullet
from sprites.player import Player
from sprites.scorpion import Scorpion
from map_classes.ground import Ground
from map_classes.water import Water
from map_classes.mountain import Mountain
from crator import Crator
from audio import sounds


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Planet")
        self.clock = pygame.time.Clock()
        self.db = DatabaseManager()
        self.sql_commands = DatabaseManager()
        self.map_prop = self.sql_commands.load_progress() # в tmx будет та карта которую вернула эта команда
        self._init_sprites()
        self.running = True
        self.name_map = self.map_prop[2]
        self.tmx_data = load_pygame(f'data/maps/{self.name_map}.tmx')
        self.check_map = False
        self.reset_map()

    def reset_map(self):
        for i in self.water_group:
            i.kill()
        for i in self.ground_group:
            i.kill()
        for i in self.mountain_group:
            i.kill()
        for object in self.tmx_data.objects:
            if object.type == 'ground':
                self.ground_group.add(Ground(object.x, object.y, object.width, object.height))
            elif object.type == 'water':
                self.water_group.add(Water(object.x, object.y, object.width, object.height))
            elif object.type == 'mountain':
                self.mountain_group.add(Mountain(object.x, object.y, object.width, object.height))
            elif object.type == 'crator':
                self.crator_group.add(Crator(object.x, object.y, object.width, object.height,
                                    self.player, self.scorpion_group, self.mountain_group,
                                    self.water_group, self.bullets))
                

    # Отрисовка карты
    def draw_map(self, screen, tmx_data):
        for layer in tmx_data.visible_layers:
            try:
                for x, y, gid in layer:
                    if gid != 0:
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
            except Exception:
                pass

    # Инициализация групп спрайтов
    def _init_sprites(self):
        self.platforms = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.mountain_group = pygame.sprite.Group()
        self.crator_group = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.scorpion_group = pygame.sprite.Group()

        self.player = Player(self.platforms, self.ground_group, self.water_group, self.mountain_group, self.scorpion_group)
        self.player.rect.x = self.map_prop[0]
        self.player.rect.y = self.map_prop[1]
        self.particles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.platforms, self.player,
                self.water_group, self.mountain_group, self.crator_group
        )

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
                if event.button == 1:
                    # Если нажата ЛКМ
                    for i in range(self.player.wpn.blt_n):
                        self._create_bullet() # Создание пули

        return keys

    # Создание пули
    def _create_bullet(self):
        bullet = Bullet(
            self.player.rect.centerx, self.player.rect.centery, self.player.angle, self.mountain_group, self.player.wpn
        )
        self.bullets.add(bullet) # Добавление пули в группу
        self.all_sprites.add(bullet) # Добавление пули в общую группу
        sounds['laser'].play()

    # Обновление состояния игры
    def update(self, keys):
        self.player.update(keys)
        map_prop = self.player.map_give()
        if map_prop[0]:
            self.name_map = map_prop[1]
        self.bullets.update()
        self.particles.update()
        self.crator_group.update()
        self.scorpion_group.update()
        if self.check_map:
            self.reset_map()
            self.check_map = False

        self._handle_collisions()

    # Обработка столкновений
    def _handle_collisions(self):
        for bullet in self.bullets:
            if pygame.sprite.spritecollide(bullet, self.platforms, False):
                self.create_impact_particles(
                    bullet.rect.centerx, bullet.rect.centery, bullet.weapon_type.blt_clr
                )
                bullet.kill()
                continue

    def draw(self):
        self.draw_map(self.screen, self.tmx_data)
        self.all_sprites.draw(self.screen)
        self.scorpion_group.draw(self.screen)

        # Отрисовка UI
        font = pygame.font.Font(None, 50)
        health_text = font.render(f"Health: {self.player.health}", True, WHITE)
        weapon_text = font.render(self.player.wpn.name, True, WHITE)
        self.screen.blit(health_text, health_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10)))
        self.screen.blit(weapon_text, weapon_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10 + 50)))

        pygame.display.flip()

    def run(self):
        while self.running:
            keys = self.handle_events()
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)

        self.sql_commands.save_progress(self.player.rect.x, self.player.rect.y, self.name_map)
        self.db.close()
        pygame.quit()
