import math
import random
import collision
import enemy
import gameobject
import helpers
import tile
import particle


class Bullet(gameobject.PhysicsObject):
    def __init__(self, x, y, speed, angle, gravity_scale=0):
        dx = speed * math.cos(math.radians(angle))
        dy = speed * math.sin(math.radians(angle))

        super().__init__(x, y, 4 * helpers.SCALE, 4 * helpers.SCALE, dx, dy,
                         ['bullet'])

        self.alive = True
        self.particles = []
        self.bounce_scale = 1
        self.gravity_scale = gravity_scale

        for s in self.sprites:
            s.play('idle', 0)

    def update(self, room):
        super().update(room)

        if self.alive:
            for c in self.collisions:
                if c.direction is collision.Direction.up or \
                        c.direction is collision.Direction.down:
                    vert = True
                else:
                    vert = False

                if type(c.obj) is tile.Destroyable:
                    c.destroy()

                if type(c.obj) is enemy.Enemy:
                    c.damage(1, 0, 0)
                    self.destroy('blood', vert)
                    for p in c.obj.projectiles:
                        if p.alive:
                            p.die()
                            self.destroy('blood', vert)
                else:
                    self.destroy('spark', vert)

            if helpers.outside_screen(self.collider):
                self.alive = False

        for p in self.particles:
            p.update(room)
            if not p.alive:
                self.particles.remove(p)

    def destroy(self, particle_type, vertical):
        if self.alive:
            self.add_particle(0, 0, 0.2, 2, particle_type, vertical)
            self.add_particle(0, 0, 0.2, 2, particle_type, vertical)
            self.alive = False

    def add_particle(self, x, y, speed, spread, particle_type, vertical):
        if vertical:
            dx = random.uniform(-spread, spread) * helpers.SCALE
            dy = speed * self.dy
        else:
            dx = speed * self.dx
            dy = random.uniform(-spread, spread) * helpers.SCALE

        p = particle.Particle(self.x + x, self.y + y, dx, dy, particle_type,
                              0.5)

        self.particles.append(p)

    def draw(self, screen, img_hand):
        if self.alive:
            super().draw(screen, img_hand)

        for p in self.particles:
            p.draw(screen, img_hand)
