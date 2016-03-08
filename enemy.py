import animatedsprite
import bullet
import gameobject
import helpers
import livingobject
import physicsobject
import random

import tile
from player_old import Direction
import math


class Enemy(livingobject.LivingObject):
    def __init__(self, x, y, width, height, health, path):
        super().__init__(x, y, width, height, path)

        self.spawn_x = x
        self.spawn_y = y
        self.alive = True
        self.projectiles = []
        for s in self.sprites:
            s.play('idle')
        self.max_health = health
        self.health = self.max_health
        self.sees_player = False

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.dx = 0
        self.dy = 0
        self.alive = True
        self.gibs.clear()
        self.projectiles.clear()
        self.health = self.max_health

    def die(self):
        self.alive = False

    def add_gib(self, x, y, dx, dy, part, path):
        x = self.x + x * helpers.SCALE
        y = self.y + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.add(physicsobject.Gib(x, y, dx, dy, part, path))

    def on_edge(self, room):
        if not self.ground_collision:
            return False

        on_edge = True
        for wall in room.walls:
            if self.dx > 0:
                if wall.collider.collidepoint(self.collider.bottomright):
                    on_edge = False
            elif self.dx < 0:
                if wall.collider.collidepoint(self.collider.bottomleft):
                    on_edge = False
        return on_edge

    def see_player(self, room):
        player = room.level.player

        if self.alive and player.alive:
            width = abs(self.collider.x - player.collider.x)
            collider = gameobject.GameObject(self.collider.left,
                                             self.collider.centery,
                                             width + player.collider.width,
                                             helpers.TILE_SIZE)

            if player.collider.x < self.collider.x:
                collider.x = self.collider.x - width
                collider.collider.width = width

            for c in collider.get_collisions(room):
                if c.obj is not player:
                    self.sees_player = False
                    break
            else:
                self.sees_player = True

    def update(self, room):
        super().update(room)

        if self.alive:
            for c in self.collisions:
                if type(c.obj) is tile.Spike:
                    self.damage(-self.dx, -self.dy)

        for p in self.projectiles:
            p.update(room)

        self.animate()

    def animate(self):
        pass

    def apply_friction(self):
        pass

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        for p in self.projectiles:
            p.draw(screen, img_hand)


class Crawler(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 8 * helpers.SCALE, 8 * helpers.SCALE, 1,
                         ['crawler'])

        self.speed = 0.25 * helpers.SCALE

    def update(self, room):
        if self.alive:
            self.dx = self.speed

        super().update(room)

        if self.alive:
            if self.wall_collision or self.on_edge(room):
                self.speed = -self.speed
            for s in self.sprites:
                s.play('idle')
        else:
            for s in self.sprites:
                s.play_once('die')

    def die(self):
        if self.alive:
            self.add_shrapnel(-1.25, -3)
            self.add_shrapnel(-0.75, -3.5)
            self.add_shrapnel(0, -3.75)
            self.add_shrapnel(0.75, -3.5)
            self.add_shrapnel(1.25, -3)
            self.alive = False

    def add_shrapnel(self, dx, dy):
        dx = random.uniform(dx - 1, dx + 1) * helpers.SCALE
        dy = dy * helpers.SCALE
        self.projectiles.append(Shrapnel(self.x, self.y, dx, dy))

    def reset(self):
        super().reset()
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
        Enemy.__init__(self, x, y, 5, ['zombie'])

        self.rect.height = 16 * helpers.SCALE
        self.speed = 0.25 * helpers.SCALE
        self.gibs = animatedsprite.Group()
        self.cooldown = 0
        self.play('armored')
        self.bullet_speed = 2 * helpers.SCALE

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

    def see_player(self, player, room):
        Enemy.see_player(self, player, room)

        if self.sees_player and self.cooldown == 0:
            self.cooldown = 30
            if player.rect.x > self.rect.x:
                if self.dir is Direction.left:
                    self.flip()
                x = self.rect.x + 8 * helpers.SCALE
                y = self.rect.y + 2 * helpers.SCALE
                self.projectiles.add(bullet.Bullet(x, y, self.bullet_speed, 0))
            elif player.rect.x < self.rect.x:
                if self.dir is Direction.right:
                    self.flip()
                x = self.rect.x - 8 * helpers.SCALE
                y = self.rect.y + 2 * helpers.SCALE
                self.projectiles.add(
                        bullet.Bullet(x, y, -self.bullet_speed, 0))
        elif self.cooldown > 0:
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
        if self.dir is Direction.left:
            self.flip()


class Flyer(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, -1, 'flyer')
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
    def __init__(self, x, y):
        super().__init__(x, y, 16 * helpers.SCALE, 16 * helpers.SCALE, 5,
                         ['spawner'])
        self.gravity_scale = 0
        self.cooldown = 0

    def update(self, room):
        Enemy.update(self, room)
        if self.alive and len(self.projectiles) < 3 and self.cooldown == 60:
            self.projectiles.append(
                    Chaser(self.collider.x + 0.25 * self.collider.width,
                           self.collider.y + 0.25 * self.collider.height))
            self.cooldown = 0

        if self.cooldown < 60:
            self.cooldown += 1

    def chase(self, player):
        for c in self.projectiles.sprites():
            c.chase(player)

    def die(self):
        super().die()
        for s in self.sprites:
            s.play_once('die')

    def reset(self):
        Enemy.reset(self)
        for s in self.sprites:
            s.play('idle')
        self.cooldown = 0


class Chaser(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 8 * helpers.SCALE, 8 * helpers.SCALE, 1,
                         ['chaser'])
        self.gravity_scale = 0
        self.collision = False
        self.speed = 0.25 * helpers.SCALE
        for s in self.sprites:
            s.show_frame('idle', 0)

    def update(self, room):
        super().update(room)
        if self.collisions:
            self.speed = 0.1 * helpers.SCALE
        else:
            self.speed = 0.25 * helpers.SCALE

        rotation = helpers.rotation(self.dx, self.dy)
        if self.alive:
            self.chase(room)
            for s in self.sprites:
                s.show_frame('idle', int((rotation / 360) * 8))
        elif self.sprites[0].animation_finished:
            pass

    def chase(self, room):
        player = room.level.player

        if self.alive and player.alive:
            x = player.x - self.x
            y = player.y - self.y
            distance = math.hypot(x, y)
            if distance > 0:
                self.dx = (x / distance) * self.speed
                self.dy = (y / distance) * self.speed
            else:
                self.dx = 0
                self.dy = 0
        else:
            self.dx = 0
            self.dy = 0

    def reset(self):
        Enemy.reset(self)

    def die(self):
        Enemy.die(self)
        for s in self.sprites:
            s.play_once('die')
        self.dx = 0
        self.dy = 0


class Charger(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 16 * helpers.SCALE, 16 * helpers.SCALE, 6,
                         ['charger'])
        for s in self.sprites:
            s.play('idle')
        self.speed = 1 * helpers.SCALE
        self.goal_dx = 0

    def update(self, room):
        super().update(room)

        if self.alive:
            self.see_player(room)

            if self.wall_collision:
                self.goal_dx = 0

            if self.goal_dx != 0:
                acceleration = self.friction
                if self.goal_dx < self.dx:
                    self.dx -= acceleration
                elif self.goal_dx > self.dx:
                    self.dx += acceleration
                for s in self.sprites:
                    s.play('charge')
            else:
                for s in self.sprites:
                    s.play('idle')

    def die(self):
        super().die()
        self.add_gib(0, 0, -1, -2, 'left', 'charger_gibs')
        self.add_gib(0, 0, 1, -2, 'right', 'charger_gibs')
        for s in self.sprites:
            s.play_once('die')

    def see_player(self, room):
        super().see_player(room)

        player = room.level.player

        if self.sees_player:
            if player.x > self.x:
                if self.direction is Direction.left:
                    self.flip()
                self.goal_dx = self.speed
            elif player.x < self.x:
                if self.direction is Direction.right:
                    self.flip()
                self.goal_dx = -self.speed

    def reset(self):
        super().reset()
        self.goal_dx = 0
