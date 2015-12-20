import math
import random
import pygame
import animatedsprite
import enemy
import helpers
import physicsobject
import tile


class Bullet(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, speed, angle):
        animatedsprite.AnimatedSprite.__init__(self, 'bullet')
        self.rect.x = x
        self.rect.y = y
        self.dx = speed * math.cos(math.radians(angle))
        self.dy = speed * math.sin(math.radians(angle))
        self.alive = True
        if self.dx < 0:
            self.flip()
        self.particles = animatedsprite.Group()

        self.play('idle', 0)

    def update(self, room):
        if self.alive:
            self.move_x(room)
            self.move_y(room)

            if helpers.outside_screen(self.rect):
                self.kill()
        else:
            if not self.particles:
                self.kill()

        self.particles.update(room)

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
            if type(c) is tile.Destroyable:
                c.destroy()

        if collisions:
            self.destroy('spark', False)

        enemy_collisions = pygame.sprite.spritecollide(self, room.enemies, False)
        enemy_collisions = [c for c in enemy_collisions if c.alive]

        for c in enemy_collisions:
            if self.dx > 0:
                self.rect.right = c.rect.left
            if self.dx < 0:
                self.rect.left = c.rect.right
            c.damage(0, 0)
            break

        if enemy_collisions:
            self.destroy('blood', False)

        for e in room.enemies:
            if type(e) is enemy.Spawner:
                for c in pygame.sprite.spritecollide(self, e.projectiles, False):
                    if c.alive:
                        c.die()
                        self.destroy('blood', False)
                        break

    def move_y(self, room):
        self.rect.move_ip(0, self.dy)

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))
        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if self.dy > 0:
                self.rect.bottom = c.rect.top
            if self.dy < 0:
                self.rect.top = c.rect.bottom
            if type(c) is tile.Destroyable:
                c.destroy()

        if collisions:
            self.destroy('spark', True)

        enemy_collisions = pygame.sprite.spritecollide(self, room.enemies, False)
        enemy_collisions = [c for c in enemy_collisions if c.alive]

        for c in enemy_collisions:
            if self.dy > 0:
                self.rect.bottom = c.rect.top
            if self.dy < 0:
                self.rect.top = c.rect.bottom
            c.damage(0, 0)
            break

        if enemy_collisions:
            self.destroy('blood', True)

    def destroy(self, particle_type, vertical):
        if self.alive:
            random.uniform(-2, 2) * helpers.SCALE, -0.2 * self.dy,
            self.add_particle(0, 0, -0.2, 2, particle_type, vertical)
            self.add_particle(0, 0, -0.2, 2, particle_type, vertical)
            self.alive = False

    def add_particle(self, x, y, speed, spread, particle_type, vertical):
        if vertical:
            dx = random.uniform(-spread, spread) * helpers.SCALE
            dy = speed * self.dy
        else:
            dx = speed * self.dx
            dy = random.uniform(-spread, spread) * helpers.SCALE
        particle = physicsobject.Particle(self.rect.x + x, self.rect.y + y, dx, dy, particle_type, True)

        self.particles.add(particle)

    def draw(self, screen, img_hand):
        if self.alive:
            animatedsprite.AnimatedSprite.draw(self, screen, img_hand)
        self.particles.draw(screen, img_hand)


class Sword(Bullet):
    def __init__(self, x, y):
        Bullet.__init__(self, x, y, 0, 0)
        self.rect.width = 24
        self.alive = False
        self.lifespan = 4

    def collide(self, room):
        if self.lifespan == 0:
            self.alive = False
        else:
            self.lifespan -= 1

        for e in room.enemies:
            for p in pygame.sprite.collidesprite(self, e.projectiles, False):
                p.dx = -p.dx

    def draw(self, screen, img_hand):
        pass