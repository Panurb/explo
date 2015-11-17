import animatedsprite


TEXTS = {'run': 'HOLD SHIFT TO WALK',
         'double jump': 'PRESS Z IN MIDAIR',
         'wall jump': 'PRESS Z WHILE HUGGING A WALL',
         'sword': 'PRESS X TO SWING',
         'gun': 'PRESS X TO SHOOT'}


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