import os
import math
import pygame

SCALE = 4
ROOM_WIDTH = 20
ROOM_HEIGHT = 15
TILE_SIZE = 8 * SCALE
SCREEN_WIDTH = ROOM_WIDTH * TILE_SIZE
SCREEN_HEIGHT = ROOM_HEIGHT * TILE_SIZE
GRAVITY = 0.25 * SCALE
TERMINAL_VELOCITY = 7 * SCALE


def load_image(name):
    fullname = os.path.join('data', 'img', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        raise SystemExit(message)
    image = image.convert_alpha()

    return image


def load_sound(name):
    path = os.path.join('data', 'snd', name)
    try:
        sound = pygame.mixer.Sound(path)
    except pygame.error as message:
        raise SystemExit(message)

    return sound


def row_to_tiles(image, width, height, row, length):
    tiles = []
    i = 0
    while i < length * width:
        tiles.append(image.subsurface(pygame.Rect(i, row * height, width, height)))
        i += width

    return tiles


def outside_screen(rect):
    if rect.left > SCREEN_WIDTH or rect.right < 0 or rect.top > SCREEN_HEIGHT or rect.bottom < 0:
        return True
    else:
        return False


def rotation(dx, dy):
    rot = math.degrees(math.atan2(-dy, dx))
    if rot < 0:
        rot += 360

    return rot


def limit_speed(dx, dy):
    speed = math.hypot(dx, dy)
    if speed > TERMINAL_VELOCITY:
        dx *= (TERMINAL_VELOCITY / speed)
        dy *= (TERMINAL_VELOCITY / speed)
    return dx, dy


def mouse_to_grid(mouse_x, mouse_y):
    x = mouse_x - mouse_x % TILE_SIZE
    y = mouse_y - mouse_y % TILE_SIZE

    return x, y
