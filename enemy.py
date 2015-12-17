import pygame
import animatedsprite
import bullet
import helpers
import physicsobject
import random
from player import Direction


class Enemy(animatedsprite.AnimatedSprite, physicsobject.PhysicsObject):
    def __init__(self, x, y, path):
        animatedsprite.AnimatedSprite.__init__(self, path)
        physicsobject.PhysicsObject.__init__(self, x, y, self.rect.width, self.rect.height)

        self.spawn_x = x
        self.spawn_y = y
        self.alive = True
        self.gibs = animatedsprite.Group()
        self.projectiles = animatedsprite.Group()
        self.play('idle')
        self.max_health = 1
        self.health = self.max_health

    def reset(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.alive = True
        self.gibs.empty()
        self.frame = 0
        self.projectiles.empty()
        self.health = self.max_health

    def damage(self, dx, dy):
        self.dx = dx
        self.dy = dy

        self.health -= 1

        if self.health <= 0:
            self.die()

    def die(self):
        self.alive = False

    def add_gib(self, x, y, dx, dy, part, path):
        x = self.rect.x + x * helpers.SCALE
        y = self.rect.y + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.add(physicsobject.Gib(x, y, dx, dy, part, path))

    def on_edge(self, room):
        if not self.grounded:
            return False

        on_edge = True
        for wall in room.walls:
            if self.speed > 0:
                if wall.rect.collidepoint(self.rect.bottomright):
                    on_edge = False
            elif self.speed < 0:
                if wall.rect.collidepoint(self.rect.bottomleft):
                    on_edge = False
        return on_edge

    def update(self, room):
        physicsobject.PhysicsObject.update(self, room)

        if self.alive:
            if pygame.sprite.spritecollide(self, room.spikes, False):
                self.damage(-self.dx, -self.dy)

        self.gibs.update(room)
        self.projectiles.update(room)

        self.animate()

    def draw(self, screen, img_hand):
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)
        self.gibs.draw(screen, img_hand)
        self.projectiles.draw(screen, img_hand)


class Crawler(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, 'crawler')

        self.speed = 0.25 * helpers.SCALE

        self.max_health = self.health = 5

    def update(self, room):
        if self.alive:
            self.dx = self.speed

        Enemy.update(self, room)

        if self.alive:
            if self.walled or self.on_edge(room):
                self.speed = -self.speed
            self.play('idle')
        else:
            self.play_once('die')

    def die(self):
        Enemy.die(self)
        self.add_shrapnel(-1.25, -3)
        self.add_shrapnel(-0.75, -3.5)
        self.add_shrapnel(0, -3.75)
        self.add_shrapnel(0.75, -3.5)
        self.add_shrapnel(1.25, -3)

    def add_shrapnel(self, dx, dy):
        dx = random.uniform(dx - 1, dx + 1) * helpers.SCALE
        dy = dy * helpers.SCALE
        self.projectiles.add(Shrapnel(self.rect.x, self.rect.y, dx, dy))

    def reset(self):
        Enemy.reset(self)
        self.speed = 0.25 * helpers.SCALE


class Shrapnel(physicsobject.Gib):
    def __init__(self, x, y, dx, dy):
        physicsobject.Gib.__init__(self, x, y, dx, dy, 'idle', 'crawler')
        self.play_once('shrapnel')
        self.animate()

        self.rect.width = 8 * helpers.SCALE
        self.rect.height = 8 * helpers.SCALE
        self.dx = dx
        self.dy = dy
        self.collision = False

    def update(self, room):
        physicsobject.Gib.update(self, room)
        if helpers.outside_screen(self.rect) and not self.trail:
            self.kill()


class Zombie(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y - 8 * helpers.SCALE, 'zombie')

        self.rect.height = 16 * helpers.SCALE
        self.speed = 0.25 * helpers.SCALE
        self.gibs = animatedsprite.Group()
        self.cooldown = 0
        self.play('armored')
        self.bullet_speed = 2 * helpers.SCALE
        self.health = self.max_health = 5

    def update(self, room):
        if self.alive and self.grounded and not self.projectiles:
            self.dx = self.speed
        else:
            self.dx = 0

        Enemy.update(self, room)

        if self.alive:
            if self.walled or self.on_edge(room):
                self.speed = -self.speed
                self.flip()

        self.animate()

    def animate(self):
        if self.alive:
            if self.dx == 0:
                self.pause()
            else:
                self.play('armored')
        else:
            self.play_once('die')

    def vision(self, player, room):
        if self.cooldown == 0:
            self.cooldown = 30
            if self.speed > 0:
                #collider = pygame.sprite.Sprite()
                #collider.rect = pygame.Rect(self.rect.left - 1, self.rect.y, self.rect.width + 2, self.rect.height / 2)
                for i in range(40 * helpers.SCALE):
                    if player.rect.collidepoint(self.rect.x + i * helpers.SCALE, self.rect.y):
                        x = self.rect.x + 8 * helpers.SCALE
                        y = self.rect.y + 2 * helpers.SCALE
                        self.projectiles.add(bullet.Bullet(x, y, self.bullet_speed, 0))
                        return
            elif self.speed < 0:
                for i in range(40 * helpers.SCALE):
                    if player.rect.collidepoint(self.rect.x - i * helpers.SCALE, self.rect.y):
                        x = self.rect.x - 8 * helpers.SCALE
                        y = self.rect.y + 2 * helpers.SCALE
                        self.projectiles.add(bullet.Bullet(x, y, -self.bullet_speed, 0))
                        return
        else:
            self.cooldown -= 1

    def damage(self, dx, dy):
        Enemy.damage(self, dx, dy)
        # path = 'zombie_gibs'
        # if self.armored:
        #     self.armored = False
        #     self.add_gib(0, 4, 0.5, -2.5, 'armor', path)
        #     self.add_gib(0, 0, -0.5, -2.5, 'armor', path)
        #     self.add_gib(0, 6, -0.25, -2.5, 'armor', path)
        #     self.dx = dx
        #     self.dy = dy
        #     self.grounded = False
        # else:
        #     self.die()

    def die(self):
        Enemy.die(self)
        path = 'zombie_gibs'
        if self.dir is Direction.right:
            self.add_gib(0, -4, 0.5, -2.5, 'head', path)
        else:
            self.add_gib(0, -4, 0.5, -2.5, 'head', path)
        self.add_gib(-0.5, 4, -1.25, -2.5, 'arm', path)
        self.add_gib(0.5, 2, 1.25, -2.5, 'arm', path)

    def reset(self):
        Enemy.reset(self)
        self.speed = 0.25 * helpers.SCALE
        self.dx = self.speed
        self.dy = 0
        if self.dir is Direction.left:
            self.flip()


class Flyer(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, 'flyer')
        self.speed = 0.5 * helpers.SCALE
        self.dx = self.speed
        self.gravity = False
        self.bounce = 1

    def update(self, room):
        Enemy.update(self, room)

        if self.walled:
            self.dy = self.dx
            self.dx = 0
        if self.grounded:
            self.dx = -self.dy
            self.dy = 0
        if self.ceilinged:
            self.dx = -self.dy
            self.dy = 0

    def damage(self, dx, dy):
        pass

    def reset(self):
        Enemy.reset(self)
        self.dx = self.speed
        self.dy = 0


class Spawner(Enemy):
    pass


class Chaser(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, 'chaser')
        self.gravity = False
        self.speed = 1 * helpers.SCALE

    def update(self, room):
        Enemy.update(self, room)

    def chase(self, player):
        pass