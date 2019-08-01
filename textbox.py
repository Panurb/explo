import pygame
import animatedsprite
import helpers

UPPER_CASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER_CASE = 'abcdefghijklmnopqrstuvwxyz'
NUMBERS = '1234567890-+*:'


class Textbox:
    def __init__(self, string, x=0.5*helpers.SCREEN_WIDTH, y=0.5*helpers.SCREEN_HEIGHT, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.chars = []
        self.time = -1
        self.string = string
        self.set_string(string)

        self.sprites = []
        self.update_sprites()

    def update_sprites(self):
        if self.width:
            width = self.width
        else:
            rows = self.string.split('\\')
            width = 0
            for row in rows:
                width = max(width, len(row))
            width = int(width / 2 + 2)
        if self.height:
            height = self.height
        else:
            height = len(rows)

        self.sprites = []
        for i in range(width):
            for j in range(height):
                s = animatedsprite.AnimatedSprite('menu')
                s.set_position(self.x - (width * 4) * helpers.SCALE + i * helpers.TILE_SIZE, self.y + j * helpers.TILE_SIZE)
                frame = 1
                action = 'middle'
                if i == 0:
                    frame = 0
                elif i == width - 1:
                    frame = 2
                if j == 0:
                    action = 'top'
                elif j == height - 1:
                    action = 'bottom'
                s.show_frame(action, frame)
                self.sprites.append(s)

        if height == 1:
            if len(self.sprites) == 1:
                self.sprites[0].show_frame('button', 3)
            else:
                for s in self.sprites:
                    s.show_frame('button', 1)
                self.sprites[0].show_frame('button', 0)
                self.sprites[-1].show_frame('button', 2)

    def clear(self):
        self.set_string('')

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.set_string(self.string)
        self.update_sprites()

    def set_string(self, string):
        self.string = string
        strings = string.split('\\')
        self.chars = []

        for j, string in enumerate(strings):
            string = string.upper()
            x = self.x - (0.5 * len(string) * 4) * helpers.SCALE
            y = self.y + 0.5 * 4 * helpers.SCALE

            for i, char in enumerate(list(string)):
                sprite = animatedsprite.AnimatedSprite('chars')
                try:
                    index = int(char)
                    sprite.show_frame('numbers', index)
                except ValueError:
                    if char.isupper():
                        index = UPPER_CASE.find(char)
                        sprite.show_frame('upper_case', index)
                    elif char.islower():
                        index = LOWER_CASE.find(char)
                        sprite.show_frame('lower_case', index)
                    else:
                        index = NUMBERS.find(char)
                        sprite.show_frame('numbers', index)

                    if index == -1:
                        continue

                sprite.set_position(x + i * 4 * helpers.SCALE, y + j * helpers.TILE_SIZE)
                self.chars.append(sprite)

        self.update_sprites()

    def add_char(self, char):
        if LOWER_CASE.find(char) != -1:
            self.set_string(self.string + char)

    def remove_char(self):
        if len(self.string) > 0:
            self.set_string(self.string[:-1])

    def update(self):
        if self.time == -1:
            return

        if self.time > 0:
            self.time -= 1
        else:
            self.set_string('')

    def draw(self, screen, img_hand):
        if self.string or (self.width and self.height):
            for s in self.sprites:
                s.draw(screen, img_hand)
        for char in self.chars:
            char.draw(screen, img_hand)