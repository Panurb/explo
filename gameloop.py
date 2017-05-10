import enum
import pygame
import editor
import helpers
import level
import menu
import textbox
import time


class State(enum.Enum):
    menu = 1
    play = 2
    paused = 3
    editor = 4
    quit = 5
    options = 6
    level_select = 7
    editor_select = 8
    level_creation = 9
    level_start = 10
    level_end = 11


class GameLoop:
    def __init__(self, screen, img_hand, snd_hand, input_hand):
        self.screen = screen
        self.img_hand = img_hand
        self.snd_hand = snd_hand
        self.input_hand = input_hand

        self.main_menu = menu.MainMenu()
        self.pause_menu = menu.PauseMenu()
        self.level_select_menu = menu.LevelSelectMenu()
        self.editor_select_menu = menu.EditorSelectMenu()
        self.options_menu = menu.OptionsMenu()
        self.level_creation_menu = menu.LevelCreationMenu()

        self.level_name = ''
        self.level = None
        self.editor = None
        self.clock_text = textbox.Textbox(
            '', helpers.SCREEN_WIDTH - 0.5 * helpers.TILE_SIZE, 0)

        self.state = State.menu

        self.debug_enabled = False

    def update(self, clock):
        self.input_hand.update()
        old_state = self.state
        self.change_state()
        if self.state is not old_state:
            self.level_select_menu.update()
            self.editor_select_menu.update()

        if self.state is State.menu:
            self.level = None
            self.state = self.main_menu.input(self.input_hand)
            self.main_menu.draw(self.screen, self.img_hand)
        elif self.state is State.paused:
            self.state = self.pause_menu.input(self.input_hand)
            self.pause_menu.draw(self.screen, self.img_hand)
        elif self.state is State.level_select:
            self.state = self.level_select_menu.input(self.input_hand)
            self.level_select_menu.draw(self.screen, self.img_hand)
        elif self.state is State.editor_select:
            self.state = self.editor_select_menu.input(self.input_hand)
            self.editor_select_menu.draw(self.screen, self.img_hand)
        elif self.state is State.options:
            self.state = self.options_menu.input(self.input_hand)
            self.options_menu.draw(self.screen, self.img_hand)
        elif self.state is State.level_creation:
            self.state = self.level_creation_menu.input(self.input_hand)
            self.level_creation_menu.draw(self.screen, self.img_hand)
        elif self.state is State.play:
            if self.level is None:
                self.level = level.Level(self.level_select_menu.level_name)

            last_room = (self.level.player.room_x, self.level.player.room_y)

            self.level.update(self.input_hand)
            self.level.play_sounds(self.snd_hand)

            if self.level.player.level_over:
                self.state = State.level_end

            self.level.draw(self.screen, self.img_hand)

            if self.debug_enabled:
                self.level.debug_draw(self.screen)

            # Done after drawing to avoid visual glitches on room change
            if (self.level.player.room_x,
                    self.level.player.room_y) != last_room:
                self.level.rooms[last_room].reset()
        elif self.state is State.editor:
            if self.level is None:
                if self.editor_select_menu.level_name:
                    name = self.editor_select_menu.level_name
                    self.level = level.Level(name)
                else:
                    name = self.level_creation_menu.input_name.txtbox.string
                    self.level = level.Level(name)
                self.editor = editor.Editor(self.level.player.room_x,
                                            self.level.player.room_y)
            try:
                self.editor.input(self.level, self.input_hand)
                room = self.level.room(self.editor.room_x, self.editor.room_y)
                room.draw(self.screen, self.img_hand)
            except KeyError:
                room = level.Room(self, [], self.editor.room_x,
                                  self.editor.room_y)
                self.level.rooms[(self.editor.room_x,
                                  self.editor.room_y)] = room

            self.editor.draw(self.screen, self.img_hand)
        elif self.state is State.level_end:
            text = textbox.Textbox('YOU WON', 0.5 * helpers.SCREEN_WIDTH,
                                   0.5 * helpers.SCREEN_HEIGHT)
            text.draw(self.screen, self.img_hand)

        if self.debug_enabled:
            self.clock_text.set_string(str(int(clock.get_fps())))
            self.clock_text.draw(self.screen, self.img_hand)

        pygame.display.update()

    def change_state(self):
        if self.input_hand.keys_pressed[pygame.K_ESCAPE]:
            if self.state is State.play:
                self.state = State.paused
            elif self.state is State.editor:
                self.state = State.menu
            elif self.state is State.options:
                self.state = State.menu
            elif self.state is State.level_select:
                self.state = State.menu
            elif self.state is State.paused:
                self.state = State.play
            elif self.state is State.editor_select:
                self.state = State.menu
            elif self.state is State.level_creation:
                self.state = State.editor_select
