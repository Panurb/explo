import os
import math
import pygame


SCALE = 4
WIDTH = 160 * SCALE
HEIGHT = 120 * SCALE
TILE_SIZE = 8 * SCALE
GRAVITY = 0.25 * SCALE


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


def speed(dx, dy):
    return math.sqrt(dx**2 + dy**2)
