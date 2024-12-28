import pygame
from constants import *
from sprites import Platform, Player, NPC, Bullet, Particle
from database import DatabaseManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Planet")
        self.clock = pygame.time.Clock()
        self.db = DatabaseManager()

        self._init_sprites()
        self.running = True

    def _init_sprites(self):
        self.platforms = pygame.sprite.Group()
        self._create_platforms()

        self.player = Player(self.platforms)
        self.npcs = pygame.sprite.Group(
            NPC(200, 150, self.platforms), NPC(600, 450, self.platforms)
        )
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.platforms, self.player, *self.npcs)

    def _create_platforms(self):
        # Земля
        self.platforms.add(Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        
        # Платформы 
        self.platforms.add(Platform(300, 400, 200, 20))
        self.platforms.add(Platform(100, 300, 200, 20))
        self.platforms.add(Platform(500, 200, 200, 20))

    def create_impact_particles(self, x, y, color):
        for _ in range(PARTICLE_COUNT):
            particle = Particle(x, y, color)
            self.particles.add(particle)
            self.all_sprites.add(particle)

    def draw_gradient_background(self):
        for y in range(SCREEN_HEIGHT):
            color = (
                0,
                int(255 * y / SCREEN_HEIGHT),
                int(255 * (1 - y / SCREEN_HEIGHT)),
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._create_bullet()

        return keys

    def _create_bullet(self):
        bullet = Bullet(
            self.player.rect.centerx, self.player.rect.centery, self.player.angle
        )
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)

    def update(self, keys):
        self.player.update(keys)
        for npc in self.npcs:
            npc.update(self.player, self.npcs)
        self.bullets.update()
        self.particles.update()

        self._handle_collisions()

    def _handle_collisions(self):
        for bullet in self.bullets:
            if pygame.sprite.spritecollide(bullet, self.platforms, False):
                self.create_impact_particles(
                    bullet.rect.centerx, bullet.rect.centery, ORANGE
                )
                bullet.kill()
                continue

            hit_npcs = pygame.sprite.spritecollide(bullet, self.npcs, False)
            for npc in hit_npcs:
                npc.health -= 10
                self.create_impact_particles(
                    bullet.rect.centerx, bullet.rect.centery, RED
                )
                bullet.kill()
                if npc.health <= 0:
                    self.create_impact_particles(
                        npc.rect.centerx, npc.rect.centery, RED
                    )
                    npc.kill()

    def draw(self):
        self.draw_gradient_background()
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
