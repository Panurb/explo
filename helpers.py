import os
import math
import pygame


SCALE = 5
WIDTH = 160 * SCALE
HEIGHT = 120 * SCALE
TILE_SIZE = 8 * SCALE
GRAVITY = 0.25 * SCALE
TERMINAL_VELOCITY = 8 * SCALE


def load_image(name):
    fullname = os.path.join('data', 'img', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    return image


def row_to_tiles(image, width, height, row, length):
    tiles = []
    i = 0
    while i < length * width:
        tiles.append(image.subsurface(pygame.Rect(i, row * height, width, height)))
        i += width

    return tiles


def outside_screen(rect):
    if rect.left > WIDTH or rect.right < 0 or rect.top > HEIGHT or rect.bottom < 0:
        return True
    else:
        return False


def rotation(dx, dy):
    rot = math.degrees(math.atan2(-dy, dx))
    if rot < 0:
        rot += 360

    return rot
