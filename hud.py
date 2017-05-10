import animatedsprite
import helpers
import player


class Map():
    def __init__(self, level):
        self.sprite = animatedsprite.AnimatedSprite('map')
        self.rooms = level.rooms
        self.rooms_visited = {}
        for key in self.rooms:
            self.rooms_visited[key] = False

    def draw(self, screen, img_hand, x, y):
        max_x = 0
        min_x = 0
        max_y = 0
        min_y = 0
        for key in self.rooms:
            room = self.rooms[key]
            max_x = max(room.x, max_x)
            min_x = min(room.x, min_x)
            max_y = max(room.y, max_y)
            min_y = min(room.y, min_y)

        width = abs(max_x - min_x) + 1
        height = abs(max_y - min_y) + 1

        for key, room in self.rooms.items():
            self.sprite.rect.x = 0.5 * helpers.SCREEN_WIDTH - ((width / 2 - room.x + min_x) * 7) * helpers.SCALE
            self.sprite.rect.y = 0.5 * helpers.SCREEN_HEIGHT - ((height / 2 - room.y + min_y) * 6) * helpers.SCALE

            if room.x == x and room.y == y:
                self.sprite.play('active')
            else:
                self.sprite.play('idle')

            if self.rooms_visited[key]:
                self.sprite.draw(screen, img_hand)


class Mods():
    def __init__(self):
        size = 48
        self.x = (helpers.SCREEN_WIDTH - size * helpers.SCALE) / 2
        self.y = (helpers.SCREEN_HEIGHT - size * helpers.SCALE) / 2

        self.up = animatedsprite.AnimatedSprite('mods')
        self.right = animatedsprite.AnimatedSprite('mods')
        self.down = animatedsprite.AnimatedSprite('mods')
        self.left = animatedsprite.AnimatedSprite('mods')

        self.up.set_position(self.x, self.y)
        self.right.set_position(self.x, self.y)
        self.down.set_position(self.x, self.y)
        self.left.set_position(self.x, self.y)

    def draw(self, screen, img_hand, weapon_mods):
        self.up.show_frame('up', 0)

        if weapon_mods[player.WeaponMod.gravity]:
            self.down.show_frame('down', 1)
        else:
            self.down.show_frame('down', 0)

        if weapon_mods[player.WeaponMod.rapid]:
            self.right.show_frame('right', 1)
        else:
            self.right.show_frame('right', 0)

        if weapon_mods[player.WeaponMod.triple]:
            self.left.show_frame('left', 1)
        else:
            self.left.show_frame('left', 0)

        self.up.draw(screen, img_hand)
        self.right.draw(screen, img_hand)
        self.down.draw(screen, img_hand)
        self.left.draw(screen, img_hand)