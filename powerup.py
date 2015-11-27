from enum import Enum
import animatedsprite


class Ability(Enum):
    run = 0
    double_jump = 1
    wall_jump = 2
    sword = 3
    gun = 4
    rebreather = 5
    full_auto = 6

TEXTS = {
    Ability.run: 'Hold shift to walk',
    Ability.double_jump: 'Press A in midair',
    Ability.wall_jump: 'Press A while hugging a wall',
    Ability.sword: 'Press S to swing',
    Ability.gun: 'Press S to shoot'
}


class Powerup(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, ability):
        animatedsprite.AnimatedSprite.__init__(self, 'powerup')

        self.rect.x = x
        self.rect.y = y
        self.ability = ability
        self.visible = True
        self.play('idle')

        try:
            self.text = TEXTS[self.ability]
        except KeyError:
            self.text = ''

    def draw(self, screen, img_hand):
        if self.visible:
            animatedsprite.AnimatedSprite.draw(self, screen, img_hand)

    def reset(self):
        self.visible = True