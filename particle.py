import animatedsprite
import gameobject
import helpers


class Particle(gameobject.PhysicsObject):
    def __init__(self, x, y, dx, dy, action, gravity_scale):
        super().__init__(x, y, 0.5 * helpers.TILE_SIZE, 0.5 * helpers.TILE_SIZE, dx, dy, ['particle'])

        self.alive = True
        self.dx = dx
        self.dy = dy
        for s in self.sprites:
            s.play_once(action)
        self.collision_enabled = False
        self.gravity_scale = gravity_scale

    def update(self, room):
        super().update(room)
        self.animate()
        for s in self.sprites:
            if s.frame == 3:
                self.alive = False

    def animate(self):
        particle = animatedsprite.AnimatedSprite('particle')
        particle.set_position(self.x, self.y)
        for s in self.sprites:
            s.animate()
