import enum
import animatedsprite
import gameloop
import helpers
import textbox


class ButtonType(enum.Enum):
    play = 1
    editor = 2
    options = 3
    quit = 4


class Menu:
    def __init__(self):
        self.buttons = animatedsprite.Group()
        dy = 0
        for b in ButtonType:
            self.buttons.add(Button(0, (2 + dy) * 2 * helpers.TILE_SIZE, b))
            dy += 1
        self.state = gameloop.State.menu
        self.bg_sprite = animatedsprite.AnimatedSprite('bg')
        self.bg_sprite.play('sky')

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        self.buttons.draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons.sprites():
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    return b.press()

        return gameloop.State.menu


class Button(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, button_type):
        animatedsprite.AnimatedSprite.__init__(self, 'menu')
        self.rect.x = x + 0.5 * helpers.WIDTH - 16 * helpers.SCALE
        self.rect.y = y
        self.txtbox = textbox.Textbox(button_type.name, 0.5 * helpers.WIDTH, self.rect.y)
        self.txtbox.y = y
        self.type = button_type

        self.play('button')

    def draw(self, screen, img_hand):
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def press(self):
        if self.type is ButtonType.play:
            return gameloop.State.play
        elif self.type is ButtonType.editor:
            return gameloop.State.editor
        elif self.type is ButtonType.options:
            return gameloop.State.menu
        else:
            return gameloop.State.quit