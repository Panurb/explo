import helpers


SIZES = {
    'bg': (160, 120),
    'bullet': (4, 4),
    'chars': (4, 4),
    'checkpoint': (8, 8),
    'crawler': (8, 8),
    'destroyable': (8, 8),
    'destroyable_debris': (4, 4),
    'flyer': (8, 8),
    'ground': (8, 8),
    'ice': (8, 8),
    'ladder': (8, 8),
    'map': (14, 12),
    'menu': (32, 8),
    'metal': (8, 8),
    'particle': (4, 4),
    'player_body': (16, 16),
    'player_gibs': (4, 4),
    'player_legs': (16, 16),
    'powerup': (8, 8),
    'rock': (8, 8),
    'thorns': (8, 8),
    'wall': (8, 8),
    'water': (8, 8),
    'zombie': (8, 16),
    'zombie_gibs': (4, 4)
}

ACTIONS = {
    'bg': [
        ['sky', 1],
        ['cave', 1]
    ],
    'bullet': [
        ['idle', 1]
    ],
    'chars': [
        ['upper_case', 26],
        ['lower_case', 26],
        ['numbers', 10]
    ],
    'checkpoint': [
        ['idle', 2]
    ],
    'crawler': [
        ['idle', 4],
        ['die', 4],
        ['shrapnel', 1]
    ],
    'destroyable': [
        ['idle', 1],
        ['explode', 4]
    ],
    'destroyable_debris': [
        ['idle', 4]
    ],
    'flyer': [
        ['idle', 5]
    ],
    'ground': [
        ['idle', 16]
    ],
    'ice': [
        ['idle', 16]
    ],
    'ladder': [
        ['idle', 1]
    ],
    'map': [
        ['idle', 1],
        ['active', 1]
    ],
    'metal': [
        ['idle', 16]
    ],
    'menu': [
        ['button', 1]
    ],
    'particle': [
        ['blood', 4],
        ['spark', 4]
    ],
    'player_body': [
        ['idle', 8],
        ['walk', 12],
        ['run', 12],
        ['crouch', 8],
        ['jump', 3],
        ['climb', 6],
        ['wall_hug', 1],
        ['explode', 5],
        ['gun_idle', 8],
        ['gun_walk', 12],
        ['gun_jump', 3],
        ['gun_attack', 3],
        ['gun_up', 8],
        ['gun_crouch', 1],
        ['gun_crouch_attack', 3],
        ['gun_wall_hug', 1]
    ],
    'player_gibs': [
        ['head', 1],
        ['arm', 4],
        ['leg', 4]
    ],
    'player_legs': [
        ['idle', 1],
        ['walk', 12],
        ['run', 12],
        ['crouch', 1],
        ['jump', 3],
        ['climb', 6],
        ['wall_hug', 1],
        ['explode', 1]
    ],
    'powerup': [
        ['idle', 8]
    ],
    'rock': [
        ['idle', 16]
    ],
    'thorns': [
        ['idle', 16]
    ],
    'wall': [
        ['idle', 16]
    ],
    'water': [
        ['surface', 8],
        ['idle', 8]
    ],
    'zombie': [
        ['armored', 12],
        ['nude', 12],
        ['die', 10]
    ],
    'zombie_gibs': [
        ['head', 4],
        ['arm', 4],
        ['armor', 4]
    ]
}


class ImageHandler:
    def __init__(self):
        self.animations = {}
        self.load()

    def load(self):
        for name in ACTIONS.keys():
            image = helpers.load_image(name + '.png')
            animations = {}
            row = 0
            for animation in ACTIONS[name]:
                length = animation[1]
                animations[animation[0]] = helpers.row_to_tiles(image, SIZES[name][0], SIZES[name][1], row, length)
                row += 1

            self.animations[name] = animations