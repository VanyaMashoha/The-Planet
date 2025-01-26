from constants import *


# Класс оружия, позволяющий создавать объекты, хранящие в себе характеристики оружия
class Weapon:
    def __init__(self, name, player_speed_mul=1, cooldown_ticks=None,
                 bullet_speed_mul=1, blt_size=(10,5), bullet_dmg=100, bullet_number=1, crit_chance=20, bullet_clr='Blue'):
        self.name = name
        self.plr_spd = player_speed_mul * PLAYER_SPEED
        self.cooldown = cooldown_ticks
        self.blt_spd = bullet_speed_mul * BULLET_SPEED
        self.blt_size = blt_size
        self.blt_dmg = bullet_dmg
        self.blt_n = bullet_number
        self.crit_chance = crit_chance
        self.blt_clr = bullet_clr