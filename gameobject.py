from enum import Enum
import math

import pygame

import animatedsprite
import collision
import helpers
import platform

# COLLISION MATRIX
#
#           p   b   e   w   d   c   s   b   f   e
# player    -   -   X   X   -   X   X   X   X   -
# bullets   -   -   X   X   -   X   -   X   X   -
# enemies   -   X   -   X   -   -   X   X   -   -
# walls     -   -   -   X   -   -   -   -   -   -
# debris    -   -   -   -   -   -   -   -   -   -
# chaser    -   X   -   -   -   -   -   -   -   -
# springs   -   -   -   -   -   -   -   -   -   -
# boss      X   -   X   X   -   -   X   -   -   -
# flyer     X   -   -   X   -   -   -   -   -   -
# ebullets  X   -   X   X   -   X   X   -   X   -

COLLISION_MATRIX = [[False, False, True, True, False, True, True, True, True, False],
                    [False, False, True, True, False, True, False, True, True, False],
                    [False, True, False, True, False, False, True, True, False, False],
                    [False, False, False, True, False, False, False, False, False, False],
                    [False, False, False, False, False, False, False, False, False, False],
                    [False, True, False, False, False, False, False, False, False, False],
                    [False, False, False, False, False, False, False, False, False, False],
                    [True, False, True, True, False, False, True, False, False, False],
                    [True, False, False, True, False, False, False, False, False, False],
                    [True, False, True, True, False, True, True, False, True, False]]

# BOUNCE MATRIX
#
#           p   b   e   w   d   c   s   b   f   e
# player    0   0   0   0   0   0   1   0   0   0
# bullets   0   0  0.5 0.5  0  0.5  0   0   1   0
# enemies   0   0   0  0.5  0   0   1   1   0   0
# walls     0   0   0   1   0   0   0   1   0   0
# debris    0   0   0   0   0   0   0   0   0   0
# chaser    0   0   0   0   0   0   0   0   0   0
# springs   0   0   0   0   0   0   0   0   0   0
# boss      1   0   1   1   0   0   1   0   0   0
# flyer     0   0   0   1   0   0   0   0   0   0
# ebullets 0.5  0   0  0.5  0   0   0   0  0.5  0

BOUNCE_MATRIX = [[0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0.5, 0.5, 0, 0.5, 0, 0, 1, 0],
                 [0, 0, 0, 0.5, 0, 0, 1, 1, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [1, 0, 1, 1, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                 [0.5, 0, 0, 0.5, 0, 0, 0, 0, 0.5, 0]]


class CollisionGroup:
    none = 1
    player = 2
    bullets = 3
    enemies = 4
    walls = 5
    debris = 6
    chaser = 7
    springs = 8
    boss = 9
    flyer = 10
    ebullets = 11


class Direction(Enum):
    right = 1
    left = 2


class GameObject:
    def __init__(self, x, y, width, height, sprite_paths=(),
                 group=CollisionGroup.none):
        self.x = x
        self.y = y
        self.collider = pygame.Rect(x, y, width, height)
        self.group = group
        self.direction = Direction.right
        self.sprites = []
        for path in sprite_paths:
            self.sprites.append(animatedsprite.AnimatedSprite(path))
        self.sounds = set()

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.collider.x = x
        self.collider.y = y

    def update(self, room):
        pass

    def animate(self):
        for s in self.sprites:
            s.animate()

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

        x1 = int(self.collider.left / helpers.TILE_SIZE)
        x2 = int(self.collider.right / helpers.TILE_SIZE)
        y1 = int(self.collider.top / helpers.TILE_SIZE)
        y2 = int(self.collider.bottom / helpers.TILE_SIZE)

        for x in range(x1 - 1, x2 + 1):
            for y in range(y1 - 1, y2 + 1):
                try:
                    w = room.walls[y][x]
                except IndexError:
                    continue

                if w is not None and w is not self:
                    if collider.colliderect(w.collider):
                        collisions.append(w)

        if not collisions:
            for s in room.spikes:
                if s is not self and collider.colliderect(s.collider):
                    collisions.append(s)

        for d in room.dynamic_objects:
            if collider.colliderect(d.collider):
                if d is not self and not d.destroyed:
                    collisions.append(d)

        for e in room.enemies:
            if collider.colliderect(e.collider):
                if e is not self and e.alive:
                    collisions.append(e)

            for b in e.bullets:
                if collider.colliderect(b.collider):
                    if b is not self and b.alive:
                        collisions.append(b)

        if room.boss:
            if collider.colliderect(room.boss.collider):
                if room.boss is not self and room.boss.alive:
                    collisions.append(room.boss)

        player = room.level.player
        if player is not self and collider.colliderect(player.collider):
            if player.alive:
                collisions.append(player)

        return collisions

    def play_sounds(self, snd_hand):
        for sound in self.sounds:
            snd_hand.sounds[sound].play()

        self.sounds.clear()


class PhysicsObject(GameObject):
    def __init__(self, x, y, width, height, dx, dy, sprite_paths, group=CollisionGroup.none):
        super().__init__(x, y, width, height, sprite_paths, group)
        self.base_dx = 0
        self.base_dy = 0
        self.dx = dx
        self.dy = dy
        self.collisions = []

        self.gravity_scale = 1.0
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
            if type(c.obj) is not platform.Platform:
                self.base_dx = 0
                self.base_dy = 0
            elif type(self) is not platform.Platform and c.direction is not collision.Direction.up:
                self.base_dx = c.obj.dx
                self.base_dy = c.obj.dy
                break

    def collides_with(self, obj):
        if self.group is CollisionGroup.none:
            return False
        else:
            # off by 2 because enums start at 1 and first is none
            return COLLISION_MATRIX[self.group - 2][obj.group - 2]

    def bounce_scale(self, obj):
        if self.group is CollisionGroup.none:
            return -1
        else:
            # off by 2 because enums start at 1 and first is none
            return BOUNCE_MATRIX[self.group - 2][obj.group - 2]

    def move_x(self, room):
        self.x += self.base_dx + self.dx
        self.collider.x = self.x

        collisions = self.get_collisions(room)
        collisions = [c for c in collisions if self.collides_with(c)]

        bounce_scale = 0

        for c in collisions:
            relative_vel = self.base_dx + self.dx
            if isinstance(c, PhysicsObject):
                relative_vel -= c.dx

            if relative_vel > 0:
                self.collider.right = c.collider.left
                self.x = self.collider.x
                self.collisions.append(collision.Collision(c, collision.Direction.right))
            elif relative_vel < 0:
                self.collider.left = c.collider.right
                self.x = self.collider.x
                self.collisions.append(collision.Collision(c, collision.Direction.left))

            if c.group is not CollisionGroup.springs:
                bounce_scale = self.bounce_scale(c)

            if abs(relative_vel) > helpers.SCALE:
                self.sounds.add('bump')
            elif abs(relative_vel) >= 0.5 * helpers.SCALE:
                if self is not room.level.player:
                    self.sounds.add('bump')

        if collisions:
            self.dx *= -bounce_scale
            self.wall_collision = True
        else:
            self.wall_collision = False

    def move_y(self, room):
        self.y += self.base_dy + self.dy
        self.collider.y = self.y

        collisions = self.get_collisions(room)
        collisions = [c for c in collisions if self.collides_with(c)]

        bounce_scale = 0

        for c in collisions:
            relative_vel = self.base_dy + self.dy
            if isinstance(c, PhysicsObject):
                relative_vel -= c.dy

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

            if c.group is CollisionGroup.springs:
                c.bounce()
                if self.dy != 0:
                    bounce_scale = 3 * helpers.SCALE / self.dy
            else:
                bounce_scale = self.bounce_scale(c)

            if abs(relative_vel) >= helpers.SCALE:
                if c.group is not CollisionGroup.springs:
                    self.sounds.add('bump')

        if collisions:
            self.dy *= -bounce_scale
        else:
            self.ground_collision = False
            self.ceiling_collision = False

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
        self.base_dx = 0
        self.base_dy = 0
        self.collider.x = self.x
        self.collider.y = self.y


class Debris(PhysicsObject):
    def __init__(self, x, y, dx, dy, part, path):
        super().__init__(x, y, 4 * helpers.SCALE, 4 * helpers.SCALE, 0, 0, path, CollisionGroup.debris)

        self.dx = dx
        self.dy = dy
        for s in self.sprites:
            s.play(part, 0)
        self.bounce = 0.5
        self.friction = 0.5 * helpers.SCALE

    def update(self, room):
        super().update(room)
        if math.hypot(self.dx, self.dy) > 0.5 * helpers.SCALE:
            for s in self.sprites:
                s.animate()
