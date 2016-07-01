class Save:
    def __init__(self, x, y, room_x, room_y, direction, abilities):
        self.x = x
        self.y = y
        self.room_x = room_x
        self.room_y = room_y
        self.direction = direction
        self.abilities = {}
        for ability in abilities:
            self.abilities[ability] = abilities[ability]