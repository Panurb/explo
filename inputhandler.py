import pygame
import sys


class InputHandler:
    def __init__(self):
        self.keys_down = {}
        self.keys_pressed = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = []
        self.mouse_pressed = []
        self.mouse_released = []

    def update(self):
        self.keys_pressed = {pygame.K_UP: False,
                             pygame.K_DOWN: False,
                             pygame.K_RIGHT: False,
                             pygame.K_LEFT: False,
                             pygame.K_p: False,
                             pygame.K_SPACE: False,
                             pygame.K_r: False,
                             pygame.K_ESCAPE: False,
                             pygame.K_PERIOD: False,
                             pygame.K_COMMA: False}
        self.mouse_pressed = [False] * 6
        self.mouse_released = [False] * 6

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            else:
                if event.type == pygame.KEYDOWN:
                    self.keys_pressed[event.key] = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pressed[event.button] = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_released[event.button] = True

                self.mouse_x = pygame.mouse.get_pos()[0]
                self.mouse_y = pygame.mouse.get_pos()[1]

        self.keys_down = pygame.key.get_pressed()
        self.mouse_down = pygame.mouse.get_pressed()