from weapon_class import Weapon


# Типы оружия игрока:

# игрок не держит оружия, не стреляет т.к. кол-во пуль = 0
nothing = Weapon('Nothing',1,
                 0, (1, 1),0,
                 0, 'Black')

pistol = Weapon('Pistol', 1,
                2, (8, 4),40,
                1, 20, 'Orange')

rifle_semi = Weapon('Rifle (Semi)', 0.5,
               4, (10, 5), 80,
                1, 'Blue')

rifle_burst = Weapon('Rifle (Burst)', 0.5,
               4, (10, 5), 40,
                3, 'Purple')

# Инвентарь игрока:
inventory = [nothing,       # 0
             pistol,        # 1
             rifle_semi,    # 2
             rifle_burst,   # 3
             nothing,       # 4
             nothing,       # 5
             nothing,       # 6
             nothing,       # 7
             nothing,       # 8
             nothing]       # 9