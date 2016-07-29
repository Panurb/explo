class Save:
    def __init__(self, x, y, room_x, room_y, direction, abilities,
                 weapon_mods):
        self.x = x
        self.y = y
        self.room_x = room_x
        self.room_y = room_y
        self.direction = direction
        self.abilities = abilities.copy()
        self.weapon_mods = weapon_mods.copy()
