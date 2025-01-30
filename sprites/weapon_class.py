from constants import *


# Класс оружия, позволяющий создавать объекты, хранящие в себе характеристики оружия
class Weapon:
    def __init__(
        self,
        name,
        player_speed_mul=1,
        bullet_speed_mul=1,
        blt_size=(10, 5),
        bullet_dmg=100,
        bullet_number=1,
        bullet_clr="Blue",
    ):
        """
        Инициализация класса оружия

        :param name -- название оружия:
        :param player_speed_mul: -- коэффицент, с которым оружие увеличивает или уменьшает начальную скорость игрока
        :param bullet_speed_mul: -- коэффицент, увеличиваюзий или уменьшающий скорость пули оружия
        :param blt_size: -- кортеж с размером пули (x, y)
        :param bullet_dmg: -- урон, который пуля оружия наносит вргагм
        :param bullet_number: -- количество пуль, появляющихся после одного выстрела
        :param bullet_clr: -- цвет пуль оружия

        :return: None
        """

        self.name = name
        self.plr_spd = player_speed_mul * PLAYER_SPEED
        self.blt_spd = bullet_speed_mul * BULLET_SPEED
        self.blt_size = blt_size
        self.blt_dmg = bullet_dmg
        self.blt_n = bullet_number
        self.blt_clr = bullet_clr
