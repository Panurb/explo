from enum import Enum

import pygame
import animatedsprite
import collision
import helpers
import math
import platform


class Direction(Enum):
    right = 1
    left = 2


class GameObject:
    def __init__(self, x, y, width, height, sprite_paths=()):
        self.x = x
        self.y = y
        self.collider = pygame.rect.Rect(x, y, width, height)
        self.collision_enabled = True
        self.direction = Direction.right
        self.sprites = []
        for path in sprite_paths:
            self.sprites.append(animatedsprite.AnimatedSprite(path))

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.collider.x = x
        self.collider.y = y

    def update(self, room):
        pass

    def draw(self, screen, img_hand):
        for s in self.sprites:
            s.set_position(self.x, self.y)
            s.draw(screen, img_hand)

    def debug_draw(self, screen):
        color = (255, 0, 255)
        pygame.draw.rect(screen, color, self.collider, 1)

    def get_collisions(self, room, collider=None):
        if collider is None:
            collider = self.collider

        collisions = []

        for w in room.walls:
            if collider.colliderect(w.collider):
                if w is not self:
                    collisions.append(w)

        for d in room.dynamic_objects:
            if collider.colliderect(d.collider):
                if d is not self:
                    collisions.append(d)

        player = room.level.player

        # allow crushing enemies by platforms
        if type(self) is not platform.Platform and \
                self is not room.level.player:
            for e in room.enemies:
                if collider.colliderect(e.collider):
                    if e is not self and e.alive:
                        collisions.append(e)

                for b in e.bullets:
                    if collider.colliderect(b.collider):
                        if b is not self and b.alive:
                            collisions.append(b)

        if self is not player and collider.colliderect(player.collider):
            collisions.append(player)

        return collisions


class PhysicsObject(GameObject):
    def __init__(self, x, y, width, height, dx, dy, sprite_paths):
        GameObject.__init__(self, x, y, width, height, sprite_paths)
        self.base_dx = 0
        self.base_dy = 0
        self.dx = dx
        self.dy = dy
        self.collisions = []

        self.collision_enabled = True
        self.gravity_scale = 1.0
        self.bounce_scale = 0.5
        self.friction = 0

        self.wall_collision = False
        self.ground_collision = False
        self.ceiling_collision = False

        self.spawn_x = x
        self.spawn_y = y

    def update(self, room):
        self.collisions.clear()
        self.dx, self.dy = helpers.limit_speed(self.dx, self.dy)

        self.move_x(room)
        self.move_y(room)

        self.apply_friction()
        self.apply_gravity()

        for c in self.collisions:
            if type(c.obj) is platform.Platform:
                if c.direction is not collision.Direction.up:
                    self.base_dx = c.obj.dx
                    self.base_dy = c.obj.dy
                    break
            else:
                self.base_dx = 0
                self.base_dy = 0

    def move_x(self, room):
        self.x += self.base_dx + self.dx
        self.collider.x = self.x

        collisions = self.get_collisions(room)
        collisions = [c for c in collisions if c.collision_enabled]

        if self.collision_enabled:
            for c in collisions:
                if type(c) is PhysicsObject:
                    relative_vel = c.dx - self.base_dx - self.dx
                else:
                    relative_vel = self.base_dx + self.dx

                if relative_vel > 0:
                    self.collider.right = c.collider.left
                    self.x = self.collider.x
                    self.collisions.append(
                        collision.Collision(c, collision.Direction.right))
                elif relative_vel < 0:
                    self.collider.left = c.collider.right
                    self.x = self.collider.x
                    self.collisions.append(
                        collision.Collision(c, collision.Direction.left))

            if collisions:
                self.dx *= -self.bounce_scale
                self.wall_collision = True
            else:
                self.wall_collision = False

        player = room.level.player
        if type(self) is platform.Platform:
            if self.collider.colliderect(player.collider):
                if self.dx > 0:
                    player.dx = max(0, player.dx)
                elif self.dx < 0:
                    player.dx = min(0, player.dx)
                player.base_dx = self.dx

    def move_y(self, room):
        self.y += self.base_dy + self.dy
        self.collider.y = self.y

        collisions = self.get_collisions(room)
        collisions = [c for c in collisions if c.collision_enabled]

        if self.collision_enabled:
            for c in collisions:
                if type(c) is PhysicsObject:
                    relative_vel = c.dy - self.base_dy - self.dy
                else:
                    relative_vel = self.base_dy + self.dy

                if relative_vel > 0:
                    self.collider.bottom = c.collider.top
                    self.y = self.collider.y
                    self.ground_collision = True
                    self.friction = c.friction
                    self.collisions.append(
                        collision.Collision(c, collision.Direction.down))
                elif relative_vel < 0:
                    self.collider.top = c.collider.bottom
                    self.y = self.collider.y
                    self.ceiling_collision = True
                    self.collisions.append(
                        collision.Collision(c, collision.Direction.up))

            if collisions:
                self.dy *= -self.bounce_scale
            else:
                self.ground_collision = False
                self.ceiling_collision = False

        player = room.level.player
        if type(self) is platform.Platform:
            if self.collider.colliderect(player.collider):
                player.base_dy = self.dy

    def apply_friction(self):
        if self.ground_collision:
            if self.dx > 0:
                self.dx = max(0, self.dx - self.friction)
            if self.dx < 0:
                self.dx = min(0, self.dx + self.friction)

    def apply_gravity(self):
        self.dy += self.gravity_scale * helpers.GRAVITY

    def flip(self):
        for s in self.sprites:
            s.flip()
        if self.direction is Direction.right:
            self.direction = Direction.left
        elif self.direction is Direction.left:
            self.direction = Direction.right

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.dx = 0
        self.dy = 0


class Debris(PhysicsObject):
    def __init__(self, x, y, dx, dy, part, path):
        super().__init__(x, y, 4 * helpers.SCALE, 4 * helpers.SCALE, 0, 0,
                         path)

        self.dx = dx
        self.dy = dy
        for s in self.sprites:
            s.play(part, 0)
        self.bounce = 0.5
        self.friction = 0.5 * helpers.SCALE

    def update(self, room):
        PhysicsObject.update(self, room)
        if math.hypot(self.dx, self.dy) > 0.5 * helpers.SCALE:
            for s in self.sprites:
                s.animate()
