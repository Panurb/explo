import enum
import random
import pygame
import animatedsprite
import gameloop
import helpers
import textbox
import os


class ButtonType(enum.Enum):
    play = 1
    options = 3
    quit = 4
    resume = 5
    menu = 6
    level = 7
    edit = 8
    new = 9
    editor = 10
    create = 11
    save = 12
    test = 13


class SliderType(enum.Enum):
    sound = 1
    music = 2
    scale = 3


class Menu:
    def __init__(self, state):
        self.state = state
        self.buttons = []

    def add_button(self, x, y, button_type, text=''):
        self.buttons.append(Button(x, y, button_type, text))

    def draw(self, screen, img_hand):
        for b in self.buttons:
            b.draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    return b.press()

        return self.state


class MainMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.menu)
        self.add_button(0, 7, ButtonType.play)
        self.add_button(0, 9, ButtonType.editor)
        self.add_button(0, 11, ButtonType.options)
        self.add_button(0, 13, ButtonType.quit)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')

        self.title_sprite = animatedsprite.AnimatedSprite('title')
        self.title_sprite.set_position(1.5 * helpers.TILE_SIZE, helpers.TILE_SIZE)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        self.title_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)


class PauseMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.paused)
        self.add_button(0, 6, ButtonType.resume)
        self.add_button(0, 8, ButtonType.menu)


class LevelSelectMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.level_select)

        dy = 4
        for filename in os.listdir('data/lvl'):
            self.add_button(0, dy, ButtonType.level,
                            filename.replace('.txt', ''))
            dy += 2
        self.add_button(-7, 13, ButtonType.menu)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.level_name = ''

    def update(self):
        self.buttons = []
        dy = 4
        for filename in os.listdir('data/lvl'):
            self.add_button(0, dy, ButtonType.level,
                            filename.replace('.txt', ''))
            dy += 2
        self.add_button(-7, 13, ButtonType.menu)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    if b.type is ButtonType.level:
                        self.level_name = b.txtbox.string
                    return b.press()

        return self.state


class EditorSelectMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.editor_select)
        self.add_button(-7, 13, ButtonType.menu)
        dy = 2
        for filename in os.listdir('data/lvl'):
            self.add_button(0, 2 * dy, ButtonType.edit,
                            filename.replace('.txt', ''))
            dy += 1

        self.add_button(7, 13, ButtonType.new)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.level_name = ''

    def update(self):
        self.buttons = []
        self.add_button(-7, 13, ButtonType.menu)
        dy = 2
        for filename in os.listdir('data/lvl'):
            self.add_button(0, 2 * dy, ButtonType.edit,
                            filename.replace('.txt', ''))
            dy += 1
        self.add_button(7, 13, ButtonType.new)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    if b.type is ButtonType.edit:
                        self.level_name = b.txtbox.string
                    return b.press()

        self.level_name = ''
        return self.state


class LevelCreationMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.level_creation)
        self.input_name = TextInput(0, 6)
        self.add_button(7, 13, ButtonType.create)
        self.add_button(-7, 13, ButtonType.editor, 'BACK')
        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        self.input_name.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        self.input_name.input(input_hand)
        return super().input(input_hand)


class EditorPauseMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.editor_paused)
        self.add_button(0, 4, ButtonType.edit)
        self.add_button(0, 6, ButtonType.test)
        self.add_button(0, 8, ButtonType.save)
        self.add_button(0, 10, ButtonType.menu)


class OptionsMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.options)
        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.sliders = [Slider(0, 5, SliderType.scale),
                        Slider(0, 8, SliderType.music),
                        Slider(0, 11, SliderType.sound)]
        self.add_button(-7, 13, ButtonType.menu)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)
        for s in self.sliders:
            s.draw(screen, img_hand)

    def input(self, hands):
        input_hand, snd_hand, img_hand = hands
        for s in self.sliders:
            s.input(input_hand, snd_hand, img_hand)
        return super().input(input_hand)


class Slider():
    def __init__(self, x, y, slider_type):
        self.type = slider_type
        self.button_up = Button(x + 4, y, ButtonType.options, '+')
        self.button_down = Button(x - 4, y, ButtonType.options, '-')
        self.val = 0
        self.values = range(0, 110, 10)
        self.txtbox = TextInput(x, y, str(self.values[self.val]))

        if slider_type is SliderType.scale:
            self.values = [(helpers.ROOM_WIDTH * 8 * x, helpers.ROOM_HEIGHT * 8 * x) for x in range(4, 10)]
            val_str = str(self.values[self.val]).strip('()').replace(',', '*')
            self.txtbox = TextInput(x, y, val_str)

        self.title = TextInput(x, y - 1, slider_type.name)

    def draw(self, screen, img_hand):
        self.button_up.draw(screen, img_hand)
        self.button_down.draw(screen, img_hand)
        self.title.draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def input(self, input_hand, snd_hand, img_hand):
        changed = False

        if self.button_up.rect.collidepoint(input_hand.mouse_x,
                                            input_hand.mouse_y):
            if input_hand.mouse_released[1]:
                if self.val < len(self.values) - 1:
                    self.val += 1
                    changed = True
        if self.button_down.rect.collidepoint(input_hand.mouse_x,
                                              input_hand.mouse_y):
            if input_hand.mouse_released[1]:
                if self.val > 0:
                    self.val -= 1
                    changed = True

        if changed:
            if self.type is SliderType.music:
                pygame.mixer.music.set_volume(self.val / 100)
                self.txtbox.txtbox.set_string(str(self.values[self.val]))
            elif self.type is SliderType.sound:
                snd_hand.set_volume(self.val / 100)
                sound = random.choice(list(snd_hand.sounds.keys()))
                snd_hand.sounds[sound].play()
                self.txtbox.txtbox.set_string(str(self.values[self.val]))
            elif self.type is SliderType.scale:
                val_str = str(self.values[self.val]).strip('()').replace(',', '*')
                self.txtbox.txtbox.set_string(val_str)
                pygame.display.set_mode(self.values[self.val])
                img_hand.rescale(self.val + helpers.SCALE)


class Button(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, button_type, text=''):
        super().__init__('menu')
        self.x = x * helpers.TILE_SIZE + 0.5 * helpers.SCREEN_WIDTH - 16 * helpers.SCALE
        self.y = y * helpers.TILE_SIZE
        if text == '':
            text = button_type.name
        self.txtbox = textbox.Textbox(text, self.x + 16 * helpers.SCALE, self.y)
        self.txtbox.y = y
        self.type = button_type

        self.play('button')

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def press(self):
        if self.type is ButtonType.play:
            return gameloop.State.level_select
        elif self.type is ButtonType.options:
            return gameloop.State.options
        elif self.type is ButtonType.resume:
            return gameloop.State.play
        elif self.type is ButtonType.quit:
            return gameloop.State.quit
        elif self.type is ButtonType.menu:
            return gameloop.State.menu
        elif self.type is ButtonType.level:
            return gameloop.State.play
        elif self.type is ButtonType.edit:
            return gameloop.State.editor
        elif self.type is ButtonType.editor:
            return gameloop.State.editor_select
        elif self.type is ButtonType.new:
            return gameloop.State.level_creation
        elif self.type is ButtonType.create:
            return gameloop.State.editor
        elif self.type is ButtonType.save:
            return gameloop.State.save
        elif self.type is ButtonType.test:
            return gameloop.State.editor_play


class TextInput(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, text=''):
        super().__init__('menu')
        self.x = x + 0.5 * helpers.SCREEN_WIDTH - 16 * helpers.SCALE
        self.y = y * helpers.TILE_SIZE
        self.txtbox = textbox.Textbox(text, x + 0.5 * helpers.SCREEN_WIDTH, self.y)
        self.max_length = 7

        self.play('button')

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def input(self, input_hand):
        for key in input_hand.keys_pressed:
            if input_hand.keys_pressed[key]:
                if key == pygame.K_BACKSPACE:
                    self.txtbox.remove_char()
                else:
                    if len(self.txtbox.string) < self.max_length:
                        self.txtbox.add_char(chr(key))