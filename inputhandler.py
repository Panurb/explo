import pygame
import sys


class InputHandler:
    def __init__(self):
        self.keys_down = {}
        self.keys_pressed = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = []
        self.mouse_wheel = {}

    def update(self):
        self.keys_pressed = {pygame.K_UP: False,
                             pygame.K_DOWN: False,
                             pygame.K_RIGHT: False,
                             pygame.K_LEFT: False,
                             pygame.K_p: False,
                             pygame.K_SPACE: False,
                             pygame.K_r: False}
        self.mouse_wheel = {4: False,
                            5: False}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            else:
                if event.type == pygame.KEYDOWN:
                    self.keys_pressed[event.key] = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_wheel[event.button] = True
                self.keys_down = pygame.key.get_pressed()
                self.mouse_x = pygame.mouse.get_pos()[0]
                self.mouse_y = pygame.mouse.get_pos()[1]
                self.mouse_down = pygame.mouse.get_pressed()
