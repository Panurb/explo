import player


class Save:
    def __init__(self, x, y, room_x, room_y, dir, abilities):
        self.x = x
        self.y = y
        self.room_x = room_x
        self.room_y = room_y
        self.dir = dir
        self.abilities = {}
        for ability in abilities:
            self.abilities[ability] = abilities[ability]
        self.weapon = player.Weapon.none