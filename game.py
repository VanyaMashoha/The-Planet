import pygame
from constants import *
from database import DatabaseManager
from pytmx.util_pygame import load_pygame
from sprites.bullet import Bullet
from sprites.player import Player
from map_classes.ground import Ground
from map_classes.water import Water
from map_classes.mountain import Mountain
from sprites.crator import Crator
from sprites.audio import sounds, player_dmg


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Planet")
        self.clock = pygame.time.Clock()
        self.state = 'menu'
        self.score_count = 0
        self.db = DatabaseManager()
        self.sql_commands = DatabaseManager()
        self.map_prop = self.sql_commands.load_progress() # в tmx будет та карта которую вернула эта команда
        self._init_sprites()
        self.running = True
        self.name_map = self.map_prop[2]
        self.tmx_data = load_pygame(f'data/maps/spawn.tmx')
        self.check_map = False
        self.reset_map()

    def reset_map(self):
        """
        Сброс всех групп спрайтов и создание новой карты
        """
        
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
                

    def draw_map(self, screen, tmx_data):
        """
        Отрисовка карты
        :param screen: экран для отрисовки
        :param tmx_data: объект карты
        """
        for layer in tmx_data.visible_layers:
            try:
                for x, y, gid in layer:
                    if gid != 0:
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
            except Exception:
                pass


    def _init_sprites(self):
        """
        Инициализация групп спрайтов
        """
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
        self.player.map = self.map_prop[2]
        self.particles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.platforms, self.player,
                self.water_group, self.mountain_group, self.crator_group
        )

    # Обработка событий 
    def handle_events(self):
        """
        Обработка нажатий клавиш
        """
        
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


    def _create_bullet(self):
        """
        Создание пули в зависимости от оружия игрока
        """
        
        bullet = Bullet(
            self.player.rect.centerx, self.player.rect.centery, self.player.angle, self.mountain_group, self.player.wpn
        )
        self.bullets.add(bullet) # Добавление пули в группу
        self.all_sprites.add(bullet) # Добавление пули в общую группу
        sounds['laser'].play()


    def update(self, keys):
        """
        Обновление состояния игры
        """
        self.player.update(keys)
        self.bullets.update()
        self.particles.update()
        self.crator_group.update()
        self.scorpion_group.update()
        if self.check_map:
            self.reset_map()
            self.check_map = False

        self._handle_collisions()
        self.name_map = self.player.map


    def _handle_collisions(self):
        """
        Обработка столкновений между спрайтами
        """
        for bullet in self.bullets:
            if pygame.sprite.spritecollide(bullet, self.platforms, False):
                self.create_impact_particles(
                    bullet.rect.centerx, bullet.rect.centery, bullet.weapon_type.blt_clr
                )
                bullet.kill()
                continue

    def draw(self):
        """
        Отрисовка UI, спрайтов и карты на экране
        """
        self.draw_map(self.screen, self.tmx_data)
        self.all_sprites.draw(self.screen)
        self.scorpion_group.draw(self.screen)

        # Отрисовка UI
        font = pygame.font.Font(None, 50)
        health_and_score_text = font.render(f"Health: {self.player.health} | Score: {self.player.score}", True, WHITE)
        weapon_text = font.render(self.player.wpn.name, True, WHITE)
        self.screen.blit(health_and_score_text, health_and_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10)))
        self.screen.blit(weapon_text, weapon_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10 + 50)))

        pygame.display.flip()

    def draw_menu(self):
        """
        Отрисовка меню в начале игры
        """
        self.screen.fill((2, 23, 51))
        font = pygame.font.Font(None, 100)
        font2 = pygame.font.Font(None, 50)
        title = font.render('THE PLANET', True, (252, 3, 248))
        play_btn = font2.render('Press space to play', True, "White")
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))
        self.screen.blit(play_btn, play_btn.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        pygame.display.flip()

    def draw_game_over(self):
        """
        Отрисовка экрана конца игры
        """
        self.screen.fill((2, 23, 51))
        font = pygame.font.Font(None, 90)
        game_over_text = font.render('GAME OVER', True, (252, 3, 248))
        font2 = pygame.font.Font(None, 70)
        score_text = font2.render(f'score: {self.score_count}', True, 'White')
        font3 = pygame.font.Font(None, 50)
        continue_btn = font3.render('Press m to get back to the menu', True, "White")
        self.screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        self.screen.blit(continue_btn, continue_btn.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        pygame.display.flip()


    def run(self):
        """
        Запуск игры
        """
        while self.running:
            keys = self.handle_events()
            if self.state == 'menu':
                self.player.score = 0
                self.draw_menu()
                if keys[pygame.K_SPACE]:
                    self.state = 'game'
            elif self.state == 'game_over':
                if self.score_count < self.player.score:
                    self.score_count += 1
                self.draw_game_over()
                if keys[pygame.K_m]:
                    self.state = 'menu'
                    self.player.health = 100
                    self.player.score = 0
                    self.reset_map()
            else:
                self.update(keys)
                self.draw()
                self.player.score += 1
                if keys[pygame.K_m]:
                    self.state = 'menu'
                    self.player.health = 100
                    self.player.score = 0
                    self.reset_map()
                if self.player.health <= 0:
                    self.state = 'game_over'
                    self.score_count = 0

            self.clock.tick(FPS)

        self.sql_commands.save_progress(self.player.rect.x, self.player.rect.y, self.name_map)
        self.db.close()
        pygame.quit()
