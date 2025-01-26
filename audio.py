import pygame

pygame.mixer.init()


ui_sound = pygame.mixer.Sound('data/sounds/ui.wav')
laser = pygame.mixer.Sound('data/sounds/laser.wav')
enemy_dmg = pygame.mixer.Sound('data/sounds/enemy_dmg.wav')
player_dmg = pygame.mixer.Sound('data/sounds/player_dmg.wav')

sounds = {
    'ui': ui_sound,
    'laser': laser,
    'enemy_dmg': enemy_dmg,
    'player_dmg': player_dmg
}
