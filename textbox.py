import pygame
import animatedsprite
import helpers

CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class Textbox:
    def __init__(self, string, time=-1):
        self.y = 1 * 4 * helpers.SCALE
        self.chars = pygame.sprite.Group()
        self.time = time
        self.set_string(string)

    def set_string(self, string):
        string = string.upper()
        strings = string.split('\\')
        self.chars = pygame.sprite.Group()

        for j, string in enumerate(strings):
            x = 0.5 * helpers.WIDTH - (0.5 * len(string) * 4) * helpers.SCALE
            for i, char in enumerate(list(string)):
                sprite = animatedsprite.AnimatedSprite('chars')
                index = CHARS.find(char)
                if index == -1:
                    continue
                sprite.show_frame('idle', index)
                sprite.set_position(x + i * 4 * helpers.SCALE, self.y + j * 5 * helpers.SCALE)
                self.chars.add(sprite)

    def update(self):
        if self.time == -1:
            return

        if self.time > 0:
            self.time -= 1
        else:
            self.set_string('')

    def draw(self, screen, img_hand):
        for char in self.chars:
            char.draw(screen, img_hand)