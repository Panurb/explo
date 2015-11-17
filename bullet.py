import math
import random
import pygame
import animatedsprite
import helpers
import level
import physicsobject
import enemy


class Bullet(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, dx, dy):
        animatedsprite.AnimatedSprite.__init__(self, 'bullet')
        self.set_position(x, y)
        self.dx = dx * helpers.SCALE
        self.dy = dy * helpers.SCALE
        if dx != 0:
            self.rotation = math.degrees(math.atan(-self.dy / abs(self.dx)))
        self.alive = True
        if self.dx < 0:
            self.flip()
        self.particles = pygame.sprite.Group()

        self.play('idle', 0)

    def update(self, room):
        if self.alive:
            self.move_x(room)
            # self.move_y(room)

            if (self.rect.left > helpers.WIDTH or self.rect.right < 0 or
                    self.rect.top > helpers.HEIGHT or self.rect.bottom < 0):
                self.kill()
        else:
            done = True
            for p in self.particles:
                p.update(room)
                if not p.animation_finished:
                    done = False

            if done:
                self.kill()

    def move_x(self, room):
        self.rect.move_ip(self.dx, 0)

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))

        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if self.dx > 0:
                self.rect.right = c.rect.left
            if self.dx < 0:
                self.rect.left = c.rect.right
            if type(c) is level.Destroyable:
                c.destroy()

        enemy_collisions = pygame.sprite.spritecollide(self, room.enemies, False)

        enemy_collisions = [c for c in enemy_collisions if c.alive]

        for c in enemy_collisions:
            if self.dx > 0:
                self.rect.right = c.rect.left
            if self.dx < 0:
                self.rect.left = c.rect.right
            c.damage(0, 0)

        if collisions or enemy_collisions:
            self.destroy()

    def move_y(self, room):
        self.rect.move_ip(0, self.dy)

        collisions = pygame.sprite.spritecollide(self, room.walls, False)
        for c in collisions:
            if self.dy > 0:
                self.rect.bottom = c.rect.top

            if self.dy < 0:
                self.rect.top = c.rect.bottom

        if collisions:
            self.destroy()

    def destroy(self):
        if self.alive:
            self.add_particle(0, 0, -0.2 * self.dx, random.uniform(-2, 2) * helpers.SCALE)
            self.add_particle(0, 0, -0.2 * self.dx, random.uniform(-2, 2) * helpers.SCALE)
            self.alive = False

    def add_particle(self, x, y, dx, dy):
        particle = physicsobject.Particle(self.rect.x + x, self.rect.y + y, dx, dy, 'spark', 'particle')
        if self.dx > 0:
            particle.rect.right = self.rect.right
        elif self.dx < 0:
            particle.rect.left = self.rect.left
        self.particles.add(particle)

    def draw(self, screen, img_hand):
        if self.alive:
            animatedsprite.AnimatedSprite.draw(self, screen, img_hand)
        for p in self.particles:
            p.draw(screen, img_hand)


class Sword(Bullet):
    def __init__(self, x, y):
        Bullet.__init__(self, x, y, 0, 0)
        self.rect.width = 24
        self.alive = False
        self.lifespan = 4

    def collide(self, room):
        Bullet.collide(self, room)
        if self.lifespan == 0:
            self.alive = False
        else:
            self.lifespan -= 1

    def draw(self, screen, img_hand):
        pass
