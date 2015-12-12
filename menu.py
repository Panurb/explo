import enum
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


class Menu:
    def __init__(self):
        self.buttons = animatedsprite.Group()

    def add_button(self, x, y, button_type, text=''):
        self.buttons.add(Button(x * helpers.TILE_SIZE, y * helpers.TILE_SIZE, button_type, text))

    def draw(self, screen, img_hand):
        self.buttons.draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons.sprites():
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    return b.press()

        return self.state


class MainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.add_button(0, 2, ButtonType.play)
        self.add_button(0, 4, ButtonType.options)
        self.add_button(0, 6, ButtonType.quit)

        self.bg_sprite = animatedsprite.AnimatedSprite('bg')
        self.bg_sprite.play('sky')
        self.state = gameloop.State.menu

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        Menu.draw(self, screen, img_hand)


class PauseMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.add_button(0, 6, ButtonType.resume)
        self.add_button(0, 8, ButtonType.menu)
        self.state = gameloop.State.paused


class LevelSelectMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.add_button(0, 10, ButtonType.menu)
        dy = 2
        for filename in os.listdir('data/lvl'):
            self.add_button(0, 2 * dy, ButtonType.level, filename)
            self.add_button(5, 2 * dy, ButtonType.edit, filename)
            dy += 1

        self.bg_sprite = animatedsprite.AnimatedSprite('bg')
        self.bg_sprite.play('sky')
        self.state = gameloop.State.level_select
        self.level_name = ''

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        Menu.draw(self, screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons.sprites():
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    if b.type is ButtonType.level or b.type is ButtonType.edit:
                        self.level_name = b.txtbox.string
                    return b.press()

        return self.state


class OptionsMenu(Menu):
    pass


class Button(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, button_type, text=''):
        animatedsprite.AnimatedSprite.__init__(self, 'menu')
        self.rect.x = x + 0.5 * helpers.WIDTH - 16 * helpers.SCALE
        self.rect.y = y
        if text == '':
            text = button_type.name
        self.txtbox = textbox.Textbox(text, self.rect.centerx, self.rect.y)
        self.txtbox.y = y
        self.type = button_type

        self.play('button')

    def draw(self, screen, img_hand):
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)
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