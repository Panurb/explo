import enum
import pygame
import editor
import helpers
import level
import menu
import player
import textbox


class State(enum.Enum):
    menu = 1
    play = 2
    paused = 3
    editor = 4
    quit = 5


class GameLoop:
    def __init__(self, screen, img_hand, input_hand):
        self.screen = screen
        self.img_hand = img_hand
        self.input_hand = input_hand

        self.menu = menu.Menu()
        self.level = level.Level()
        self.player = player.Player(self.level.room(0, 0).player_x, self.level.room(0, 0).player_y, 0, 0, self.level)
        self.editor = editor.Editor(self.player.room_x, self.player.room_y)
        self.clock_text = textbox.Textbox('', helpers.WIDTH - 0.5 * helpers.TILE_SIZE, 0)

        self.state = State.menu

    def update(self, clock):
        self.input_hand.update()
        self.change_state()

        if self.state is State.menu:
            self.state = self.menu.input(self.input_hand)
            self.menu.draw(self.screen, self.img_hand)
        elif self.state is State.play:
            try:
                room = self.level.room(self.player.room_x, self.player.room_y)
            except KeyError:
                room = level.Room([], self.player.room_x, self.player.room_y, 'sky')
                self.level.rooms[(self.player.room_x, self.player.room_y)] = room

            self.player.input(self.input_hand, room)

            room.update()
            last_room = (self.player.room_x, self.player.room_y)
            self.player.update(room)

            room.draw(self.screen, self.img_hand)
            self.player.draw(self.screen, self.img_hand)

            # Done after drawing to avoid visual glitches on room change
            if (self.player.room_x, self.player.room_y) != last_room:
                self.level.rooms[last_room].reset()
        elif self.state is State.paused:
            pass
        elif self.state is State.editor:
            try:
                self.editor.input(self.level, self.input_hand)
                self.level.room(self.editor.room_x, self.editor.room_y).draw(self.screen, self.img_hand)
            except KeyError:
                room = level.Room([], self.editor.room_x, self.editor.room_y, 'sky')
                self.level.rooms[(self.editor.room_x, self.editor.room_y)] = room
            self.editor.draw(self.screen, self.img_hand)

        self.clock_text.set_string(str(int(clock.get_fps())))
        self.clock_text.draw(self.screen, self.img_hand)

        pygame.display.update()

    def change_state(self):
        if self.input_hand.keys_pressed[pygame.K_p]:
            if self.state is State.paused:
                self.state = State.play
            elif self.state is State.play:
                self.state = State.paused

        if self.state is not State.menu:
            if self.input_hand.keys_pressed[pygame.K_ESCAPE]:
                self.state = State.menu