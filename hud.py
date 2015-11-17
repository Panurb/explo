import animatedsprite
import helpers


class Map():
    def __init__(self, level):
        self.sprite = animatedsprite.AnimatedSprite('map')
        self.rooms = level.rooms

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

        for key in self.rooms:
            room = self.rooms[key]
            self.sprite.rect.x = 0.5 * helpers.WIDTH - ((width / 2 - room.x + min_x) * 14) * helpers.SCALE
            self.sprite.rect.y = 0.5 * helpers.HEIGHT - ((height / 2 - room.y + min_y) * 12) * helpers.SCALE

            if room.x == x and room.y == y:
                self.sprite.play('active')
            else:
                self.sprite.play('idle')

            self.sprite.draw(screen, img_hand)