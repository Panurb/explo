import helpers
import pygame
import imagehandler
from enum import Enum


class Direction(Enum):
    right = 1
    left = 2


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, path, offset_x=0, offset_y=0):
        if not path in imagehandler.ACTIONS:
            raise Exception('Invalid image path!')

        pygame.sprite.Sprite.__init__(self)
        self.sprite = pygame.sprite.RenderPlain(self)

        self.x = 0
        self.y = 0
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.name = path
        self.action = 'idle'
        self.image = None
        for action in imagehandler.ACTIONS[self.name]:
            if not self.action:
                self.action = action[0]

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.rect.width = imagehandler.SIZES[self.name][0] * helpers.SCALE
        self.rect.height = imagehandler.SIZES[self.name][1] * helpers.SCALE
        self.frame = 0

        self.playing = False
        self.delay = 5
        self.timer = self.delay
        self.loop = True
        self.dir = Direction.right
        self.flipped = False
        self.rotation = 0

        self.animation_finished = False

    def set_position(self, x, y):
        self.x = x + self.offset_x
        self.y = y + self.offset_y

    def animate(self):
        if self.playing:
            self.timer -= 1
            if self.timer <= 0:
                length = 0
                for action in imagehandler.ACTIONS[self.name]:
                    if action[0] == self.action:
                        length = action[1]
                        break
                if self.frame < length - 1:
                    self.frame += 1
                else:
                    if self.loop:
                        self.frame = 0
                    else:
                        self.animation_finished = True
                self.timer = self.delay

    def draw(self, screen, img_hand):
        self.image = img_hand.animations[self.name][self.action][self.frame]

        self.rect.x = int(self.x * img_hand.scale / helpers.SCALE)
        self.rect.y = int(self.y * img_hand.scale / helpers.SCALE)
        self.rect.width = imagehandler.SIZES[self.name][0] * img_hand.scale
        self.rect.height = imagehandler.SIZES[self.name][1] * img_hand.scale

        if self.rotation != 0:
            self.image = pygame.transform.rotate(self.image, self.rotation)
        if self.dir is Direction.left:
            self.image = pygame.transform.flip(self.image, True, False)

        self.sprite.draw(screen)

    def show_frame(self, name, index):
        self.playing = False
        self.action = name
        self.frame = index

    def play(self, name, index=0):
        self.playing = True
        self.loop = True
        if self.action != name:
            self.action = name
            self.frame = index
            self.timer = self.delay

    def play_once(self, name, index=0):
        self.playing = True
        self.loop = False
        if self.action != name:
            self.animation_finished = False
            self.action = name
            self.frame = index
            self.timer = self.delay

    def pause(self):
        self.playing = False

    def stop(self):
        self.playing = False
        self.frame = 0

    def flip(self):
        if self.dir is Direction.right:
            self.dir = Direction.left
        else:
            self.dir = Direction.right
