import sys
import pygame
import editor
import helpers
import level
import player
import hud
import textbox


class GameLoop:
    def __init__(self, screen, img_hand):
        self.screen = screen
        self.img_hand = img_hand
        self.level = level.Level()
        self.player = player.Player(self.level.room(0, 0).player_x, self.level.room(0, 0).player_y, 0, 0)

        # Input
        self.keys_down = {}
        self.keys_pressed = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = []
        self.mouse_wheel = {}

        self.map = hud.Map(self.level)
        self.paused = False
        self.editor_mode = False
        self.editor = editor.Editor(self.player.room_x, self.player.room_y)

    def update(self):
        self.keys_pressed = {pygame.K_UP: False,
                             pygame.K_DOWN: False,
                             pygame.K_RIGHT: False,
                             pygame.K_LEFT: False,
                             pygame.K_p: False,
                             pygame.K_SPACE: False}
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

        if self.keys_pressed[pygame.K_p]:
            self.paused = not self.paused

        if self.keys_pressed[pygame.K_SPACE]:
            self.editor_mode = not self.editor_mode
            self.level.room(self.editor.room_x, self.editor.room_y).reset()

        if self.editor_mode:
            try:
                self.editor.input(self.level, self.keys_pressed,
                                  self.keys_down, self.mouse_wheel, self.mouse_down, self.mouse_x, self.mouse_y)

                self.level.room(self.editor.room_x, self.editor.room_y).draw(self.screen, self.img_hand)
            except KeyError:
                self.level.rooms[(self.editor.room_x, self.editor.room_y)] = level.Room(
                    [], self.editor.room_x, self.editor.room_y, 'sky')
            self.editor.draw(self.screen, self.img_hand)
        else:
            if not self.paused:
                try:
                    room = self.level.room(self.player.room_x, self.player.room_y)
                except KeyError:
                    room = level.Room([], self.player.room_x, self.player.room_y, 'sky')
                    self.level.rooms[(self.player.room_x, self.player.room_y)] = room

                self.player.input(self.keys_down, room)

                room.draw(self.screen, self.img_hand)
                self.player.draw(self.screen, self.img_hand)

                room.update()
                self.player.update(room)
            else:
                text = textbox.Textbox('PAUSED')
                text.draw(self.screen, self.img_hand)
                self.map.draw(self.screen, self.img_hand, self.player.room_x, self.player.room_y)

        pygame.display.update()