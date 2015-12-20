import pygame
import animatedsprite
import helpers
import imagehandler
import math


class PhysicsObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
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
        self.x += self.dx
        self.rect.x = self.x

        if self.collision:
            collisions = pygame.sprite.spritecollide(self, room.walls, False)

            for c in collisions:
                if self.dx > 0:
                    self.rect.right = c.rect.left
                    self.x = self.rect.x
                if self.dx < 0:
                    self.rect.left = c.rect.right
                    self.x = self.rect.x

            if collisions:
                self.dx *= -self.bounce
                self.walled = True
            else:
                self.walled = False

    def move_y(self, room):
        self.y += self.dy
        self.rect.y = self.y

        if self.collision:
            collisions = pygame.sprite.spritecollide(self, room.walls, False)

            for c in collisions:
                if self.dy > 0:
                    self.rect.bottom = c.rect.top
                    self.y = self.rect.y
                    self.grounded = True

                if self.dy < 0:
                    self.rect.top = c.rect.bottom
                    self.y = self.rect.y
                    self.ceilinged = True

            if collisions:
                if self.dy > 1 * helpers.SCALE:
                    self.dy *= -self.bounce
                else:
                    self.dy = 0
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
        if self.gravity and not self.grounded:
            self.dy = min(self.dy + helpers.GRAVITY, helpers.TERMINAL_VELOCITY)


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
        if helpers.norm(self.dx, self.dy) > 0.5 * helpers.SCALE:
            self.animate()


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
        self.trail = animatedsprite.Group()

    def update(self, room):
        PhysicsObject.update(self, room)
        if not helpers.outside_screen(self.rect) and math.hypot(self.dx, self.dy) > 0.5 * helpers.SCALE:
            particle = Particle(self.rect.x, self.rect.y, 0, 0, 'blood', False)
            self.trail.add(particle)
            self.animate()
        self.trail.update(room)

    def draw(self, screen, img_hand):
        self.trail.draw(screen, img_hand)
        animatedsprite.AnimatedSprite.draw(self, screen, img_hand)


class Particle(PhysicsObject, animatedsprite.AnimatedSprite):
    def __init__(self, x, y, dx, dy, action, gravity):
        animatedsprite.AnimatedSprite.__init__(self,  'particle')
        PhysicsObject.__init__(self, x, y, self.rect.width, self.rect.height)

        self.dx = dx
        self.dy = dy
        self.play_once(action)
        self.collision = False
        self.gravity = gravity

    def update(self, room):
        PhysicsObject.update(self, room)
        self.animate()
        if self.frame == imagehandler.ACTIONS['particle'][0][1] - 1:
            self.kill()

    def animate(self):
        particle = animatedsprite.AnimatedSprite('particle')
        particle.set_position(self.rect.x, self.rect.y)
        animatedsprite.AnimatedSprite.animate(self)
