from enum import Enum
import gameobject
import helpers


class Ability(Enum):
    run = 0
    double_jump = 1
    wall_jump = 2
    gun = 3
    rebreather = 4
    full_auto = 5
    spread = 6
    gravity = 7

TEXTS = {
    Ability.run: 'Hold shift to walk',
    Ability.double_jump: 'Press A in midair',
    Ability.wall_jump: 'Press A while against a wall',
    Ability.gun: 'Press S to shoot\\Press up to aim upwards',
    Ability.rebreather: 'Breathe underwater\\Press A to swim upwards'
}


class Powerup(gameobject.GameObject):
    def __init__(self, x, y, ability):
        super().__init__(x, y, 8 * helpers.SCALE, 8 * helpers.SCALE, ['powerup'])

        self.collider.x = x
        self.collider.y = y
        self.collision_enabled = False
        self.ability = ability
        self.visible = True

        try:
            self.text = TEXTS[self.ability]
        except KeyError:
            self.text = ''

        for s in self.sprites:
            s.play('idle')

    def update(self, room):
        self.animate()

        if room.level.player.abilities[self.ability]:
            self.visible = False
        else:
            self.visible = True

        player = room.level.player
        if self.collider.colliderect(player.collider):
            player.give_powerup(self)

    def animate(self):
        for s in self.sprites:
            s.animate()

    def draw(self, screen, img_hand):
        if self.visible:
            super().draw(screen, img_hand)

    def reset(self):
        self.visible = True
