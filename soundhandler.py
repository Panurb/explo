import pygame


SOUNDS = []


class Soundhandler():
    def __init__(self):
        for sound in SOUNDS:
            pygame.mixer.Sound('data/sfx/' + sound)
