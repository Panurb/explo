import enum


class Direction(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4


class Collision:
    def __init__(self, obj, direction):
        self.obj = obj
        self.direction = direction
