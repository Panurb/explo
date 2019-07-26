import pygame
import helpers


SIZES = {
    'bg': (8, 8),
    'boss': (24, 24),
    'bosswall': (8, 8),
    'bullet': (8, 8),
    'cannon': (8, 8),
    'charger': (16, 16),
    'charger_gibs': (8, 8),
    'chars': (4, 4),
    'chaser': (8, 8),
    'checkpoint': (8, 16),
    'crawler': (8, 8),
    'destroyable': (8, 8),
    'destroyable_debris': (4, 4),
    'end': (16, 32),
    'flyer': (8, 8),
    'ground': (8, 8),
    'ice': (8, 8),
    'image': (160, 120),
    'ladder': (8, 8),
    'lava': (8, 8),
    'map': (7, 6),
    'menu': (32, 8),
    'metal': (8, 8),
    'mods': (48, 48),
    'music': (8, 8),
    'particle': (4, 4),
    'platform': (24, 8),
    'player_body': (16, 16),
    'player_gibs': (4, 4),
    'player_legs': (16, 16),
    'powerup': (8, 8),
    'rock': (8, 8),
    'spawner': (16, 16),
    'spike': (8, 8),
    'spring': (8, 16),
    'thorns': (8, 8),
    'title': (136, 32),
    'wall': (8, 8),
    'water': (8, 8),
    'zombie': (8, 16),
    'zombie_gibs': (4, 4)
}

ACTIONS = {
    'bg': [
        ['sky', 1],
        ['ground', 16],
        ['rock', 16],
        ['ice', 16],
        ['water', 16]
    ],
    'boss': [
        ['idle', 1],
        ['die', 1]
    ],
    'bosswall': [
        ['idle', 1]
    ],
    'bullet': [
        ['idle', 3]
    ],
    'cannon': [
        ['idle', 1]
    ],
    'charger': [
        ['idle', 4],
        ['charge', 4],
        ['die', 4]
    ],
    'charger_gibs': [
        ['left', 4],
        ['right', 4]
    ],
    'chars': [
        ['upper_case', 26],
        ['lower_case', 26],
        ['numbers', 13]
    ],
    'chaser': [
        ['idle', 8],
        ['die', 6]
    ],
    'checkpoint': [
        ['idle', 1]
    ],
    'crawler': [
        ['idle', 4],
        ['die', 4],
        ['shrapnel', 1],
        ['damage', 1]
    ],
    'destroyable': [
        ['idle', 1],
        ['explode', 4]
    ],
    'destroyable_debris': [
        ['idle', 4]
    ],
    'end': [
        ['idle', 1]
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
    'image': [
        ['menu', 1]
    ],
    'ladder': [
        ['idle', 1]
    ],
    'lava': [
        ['surface', 8],
        ['idle', 8]
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
    'mods': [
        ['up', 2],
        ['right', 2],
        ['down', 2],
        ['left', 2],
    ],
    'music': [
        ['idle', 1]
    ],
    'particle': [
        ['blood', 4],
        ['spark', 4]
    ],
    'platform': [
        ['idle', 1]
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
    'spawner': [
        ['idle', 1],
        ['die', 2]
    ],
    'spike': [
        ['idle', 16],
        ['water', 16]
    ],
    'spring': [
        ['idle', 1],
        ['bounce', 5]
    ],
    'thorns': [
        ['idle', 16]
    ],
    'title': [
        ['idle', 1]
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
        self.scale = helpers.SCALE
        self.rescale(self.scale)

    def rescale(self, scale):
        self.scale = scale

        for name in self.animations.keys():
            for action in self.animations[name]:
                for i, image in enumerate(self.animations[name][action]):
                    width = SIZES[name][0] * self.scale
                    height = SIZES[name][1] * self.scale
                    self.animations[name][action][i] = pygame.transform.scale(image, (width, height))

    def load(self):
        for name in ACTIONS.keys():
            image = helpers.load_image(name + '.png')
            animations = {}
            row = 0
            for animation in ACTIONS[name]:
                length = animation[1]
                tiles = helpers.row_to_tiles(image, SIZES[name][0],
                                             SIZES[name][1], row, length)
                animations[animation[0]] = tiles
                row += 1

            self.animations[name] = animations