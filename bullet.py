import math
import random
import collision
import enemy
import gameobject
import helpers
import tile
import particle


class Bullet(gameobject.PhysicsObject):
    def __init__(self, parent, x, y, speed, angle, gravity_scale=0, dist=-1, size=0):
        self.parent = parent

        dx = speed * math.cos(math.radians(angle))
        dy = speed * math.sin(math.radians(angle))

        super().__init__(x, y, 6 * helpers.SCALE, 6 * helpers.SCALE, dx, dy,
                         ['bullet'], gameobject.CollisionGroup.bullets)

        self.alive = True
        self.particles = []
        self.gravity_scale = gravity_scale
        self.dist = dist
        self.lifetime = 0

        for s in self.sprites:
            s.offset_x = -1 * helpers.SCALE
            s.offset_y = -1 * helpers.SCALE
            s.show_frame('idle', size)

    def get_collisions(self, room, collider=None):
        collisions = super().get_collisions(room)
        for c in collisions:
            if c is self.parent:
                collisions.remove(c)

        return collisions

    def update(self, room):
        super().update(room)

        if self.dist != -1:
            self.lifetime += 1

        if self.lifetime == self.dist:
            self.alive = False

        if self.alive:
            for c in self.collisions:
                if c.direction is collision.Direction.up or c.direction is collision.Direction.down:
                    vert = True
                else:
                    vert = False

                if c.obj.group is gameobject.CollisionGroup.player:
                    room.level.player.damage(1, 0, 0)

                if type(c.obj) is tile.Destroyable:
                    c.obj.destroy()

                if c.obj.group is gameobject.CollisionGroup.enemies or c.obj.group is gameobject.CollisionGroup.boss \
                        or c.obj.group is gameobject.CollisionGroup.chaser:
                    c.obj.damage(1, 0, 0)
                    self.destroy('blood', vert)
                    for p in c.obj.bullets:
                        if p.alive:
                            c.obj.bullets.remove(p)
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
            self.add_particle(0, 0, 1, 2, particle_type, vertical)
            self.add_particle(0, 0, 1, 2, particle_type, vertical)
            self.add_particle(0, 0, 1, 2, particle_type, vertical)
            self.alive = False
            self.parent.sounds.add('hit')

    def add_particle(self, x, y, speed, spread, particle_type, vertical):
        if vertical:
            dx = random.uniform(-spread, spread) * helpers.SCALE
            dy = math.copysign(helpers.SCALE * speed, self.dy)
        else:
            dx = math.copysign(helpers.SCALE * speed, self.dx)
            dy = random.uniform(-spread, spread) * helpers.SCALE

        p = particle.Particle(self.x + x, self.y + y, dx, dy, particle_type, 0.5)

        self.particles.append(p)

    def draw(self, screen, img_hand):
        if self.alive:
            super().draw(screen, img_hand)

        for p in self.particles:
            p.draw(screen, img_hand)
