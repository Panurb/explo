import math
import pygame
import animatedsprite
import helpers


class PhysicsObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.dx = 0
        self.dy = 0
        self.grounded = False
        self.walled = False
        self.ceilinged = False
        self.bounce = 0
        self.friction = 1 * helpers.SCALE
        self.collision = True
        self.gravity = True

    def update(self, room):
        self.move_x(room)
        self.move_y(room)
        self.apply_friction()
        self.apply_gravity()

    def move_x(self, room):
        self.rect.move_ip(self.dx, 0)

        if self.collision:
            collisions = pygame.sprite.spritecollide(self, room.walls, False)

            for c in collisions:
                if self.dx > 0:
                    self.rect.right = c.rect.left
                if self.dx < 0:
                    self.rect.left = c.rect.right

            if collisions:
                self.dx *= -self.bounce
                self.walled = True
            else:
                self.walled = False

    def move_y(self, room):
        self.rect.move_ip(0, self.dy)

        if self.collision:
            collisions = pygame.sprite.spritecollide(self, room.walls, False)

            for c in collisions:
                if self.dy > 0:
                    self.rect.bottom = c.rect.top
                    self.grounded = True

                if self.dy < 0:
                    self.rect.top = c.rect.bottom
                    self.ceilinged = True

            if collisions:
                self.dy *= -self.bounce
            else:
                self.grounded = False
                self.ceilinged = False

    def apply_friction(self):
        if self.collision and self.grounded:
            if self.dx > 0:
                self.dx = max(0, self.dx - self.friction)
            if self.dx < 0:
                self.dx = min(0, self.dx + self.friction)

    def apply_gravity(self):
        if self.gravity:
            self.dy += helpers.GRAVITY


class Debris(PhysicsObject, animatedsprite.AnimatedSprite):
    def __init__(self, x, y, dx, dy, part, path):
        animatedsprite.AnimatedSprite.__init__(self,  path)
        PhysicsObject.__init__(self, x, y, self.rect.width, self.rect.height)

        self.dx = dx
        self.dy = dy
        self.play(part, 0)
        self.bounce = 0.5
        self.friction = 0.5 * helpers.SCALE

    def update(self, room):
        PhysicsObject.update(self, room)
        self.animate()

    def animate(self):
        if helpers.speed(self.dx, self.dy) > 0.5 * helpers.SCALE:
            particle = animatedsprite.AnimatedSprite('particle')
            particle.set_position(self.rect.x, self.rect.y)
            animatedsprite.AnimatedSprite.animate(self)

    def draw(self, screen, img_hand):
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)


class Gib(PhysicsObject, animatedsprite.AnimatedSprite):
    def __init__(self, x, y, dx, dy, part, path):
        animatedsprite.AnimatedSprite.__init__(self,  path)
        PhysicsObject.__init__(self, x, y, self.rect.width, self.rect.height)

        self.dx = dx
        self.dy = dy
        self.play(part, 0)
        self.collision = True
        self.bounce = 0.5
        self.friction = 0.75 * helpers.SCALE
        self.trail = pygame.sprite.Group()

    def update(self, room):
        PhysicsObject.update(self, room)
        self.animate()

    def animate(self):
        if helpers.speed(self.dx, self.dy) > 0.5 * helpers.SCALE:
            particle = animatedsprite.AnimatedSprite('particle')
            particle.set_position(self.rect.x, self.rect.y)
            self.trail.add(particle)
            particle.play_once('blood')
            animatedsprite.AnimatedSprite.animate(self)

        for particle in self.trail:
            particle.animate()
            if particle.frame == 4:
                particle.kill()

    def draw(self, screen, img_hand):
        for blood in self.trail:
            blood.draw(screen, img_hand)
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)


class Particle(PhysicsObject, animatedsprite.AnimatedSprite):
    def __init__(self, x, y, dx, dy, type, path):
        animatedsprite.AnimatedSprite.__init__(self,  path)
        PhysicsObject.__init__(self, x, y, self.rect.width, self.rect.height)

        self.dx = dx
        self.dy = dy
        self.play_once(type)
        self.collision = False
        self.bounce = 0.5
        self.friction = 0

    def update(self, room):
        PhysicsObject.update(self, room)
        self.animate()

    def animate(self):
        particle = animatedsprite.AnimatedSprite('particle')
        particle.set_position(self.rect.x, self.rect.y)
        animatedsprite.AnimatedSprite.animate(self)
