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
        for key, room in self.rooms.items():
            self.sprite.set_position(0.5 * helpers.SCREEN_WIDTH + (room.x - 0.5) * self.sprite.rect.width,
                                     0.5 * helpers.SCREEN_HEIGHT + (room.y - 0.5) * self.sprite.rect.height)

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
