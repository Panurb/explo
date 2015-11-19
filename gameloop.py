import pygame
import editor
import level
import player
import hud
import textbox


class GameLoop:
    def __init__(self, screen, img_hand, input_hand):
        self.screen = screen
        self.img_hand = img_hand
        self.input_hand = input_hand
        self.level = level.Level()
        self.player = player.Player(self.level.room(0, 0).player_x, self.level.room(0, 0).player_y, 0, 0)

        self.map = hud.Map(self.level)
        self.paused = False
        self.editor_mode = False
        self.editor = editor.Editor(self.player.room_x, self.player.room_y)

    def update(self):
        self.input_hand.update()

        if self.input_hand.keys_pressed[pygame.K_p]:
            self.paused = not self.paused

        if self.input_hand.keys_pressed[pygame.K_SPACE]:
            self.editor_mode = not self.editor_mode
            self.level.room(self.editor.room_x, self.editor.room_y).reset()

        if self.editor_mode:
            try:
                self.editor.input(self.level, self.input_hand)

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

                self.player.input(self.input_hand, room)

                room.update()
                self.player.update(room)

                room.draw(self.screen, self.img_hand)
                self.player.draw(self.screen, self.img_hand)
            else:
                text = textbox.Textbox('PAUSED')
                text.draw(self.screen, self.img_hand)
                self.map.draw(self.screen, self.img_hand, self.player.room_x, self.player.room_y)

        pygame.display.update()