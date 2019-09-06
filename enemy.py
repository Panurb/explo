import bullet
import gameobject
import helpers
import creature

import tile
import math
import random


class Enemy(creature.Creature):
    def __init__(self, x, y, width, height, health, path,
                 group=gameobject.CollisionGroup.enemies):
        super().__init__(x, y, width, height, path, group)

        self.spawn_x = x
        self.spawn_y = y
        self.alive = True
        self.bullets = []
        for s in self.sprites:
            s.play('idle')
        self.max_health = health
        self.health = self.max_health
        self.sees_player = False
        self.vision = gameobject.GameObject(0, 0, 0, 0)

    def reset(self):
        super().reset()
        self.alive = True
        self.gibs.clear()
        self.bullets.clear()
        self.health = self.max_health
        if self.direction == gameobject.Direction.left:
            self.flip()

    def die(self):
        self.sounds.add('squish')
        self.alive = False

    def add_gib(self, x, y, dx, dy, part, path):
        x = self.x + x * helpers.SCALE
        y = self.y + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.append(creature.Gib(x, y, dx, dy, part, path))

    def on_edge(self, room):
        if not self.ground_collision:
            return False

        on_edge = True
        for row in room.walls:
            for w in row:
                if w is None:
                    continue
                if self.dx > 0:
                    if w.collider.collidepoint(self.collider.bottomright):
                        on_edge = False
                elif self.dx < 0:
                    if w.collider.collidepoint(self.collider.bottomleft):
                        on_edge = False
        return on_edge

    def see_player(self, room):
        player = room.level.player

        if not self.alive or not player.alive:
            self.sees_player = False
            return

        if abs(player.collider.y - self.collider.y) > 2 * helpers.TILE_SIZE:
            self.sees_player = False
            return

        if player.x > self.x:
            width = abs(self.collider.right - player.collider.left)
            collider = gameobject.GameObject(self.collider.right, self.collider.centery,
                                             width, helpers.TILE_SIZE)
        else:
            width = abs(self.collider.left - player.collider.right)
            collider = gameobject.GameObject(self.collider.left - width,
                                             self.collider.centery,
                                             width, helpers.TILE_SIZE)

        if collider.get_collisions(room):
            self.sees_player = False
        else:
            self.sees_player = True

    def update(self, room):
        super().update(room)

        if self.alive:
            for c in self.collisions:
                if type(c.obj) is tile.Spike:
                    self.damage(1, -self.dx, -self.dy)

                player = room.level.player
                if c.obj is player:
                    player.damage(1, 0, 0)

        for p in self.bullets:
            p.update(room)
            if helpers.outside_screen(p.collider):
                self.bullets.remove(p)

        self.animate()

    def animate(self):
        for s in self.sprites:
            s.animate()

    def apply_friction(self):
        pass

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        for p in self.bullets:
            p.draw(screen, img_hand)


class Crawler(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 8 * helpers.SCALE, 8 * helpers.SCALE, 2,
                         ['crawler'])

        self.speed = 0.25 * helpers.SCALE
        self.stun = 0

    def update(self, room):
        super().update(room)

        if self.alive:
            if self.stun == 0:
                self.dx = self.speed
            else:
                self.dx = 0
            if self.wall_collision or self.on_edge(room):
                self.speed = -self.speed
                self.dx = self.speed
            if self.stun > 0:
                self.stun -= 1

    def damage(self, amount, dx=0, dy=0):
        super().damage(amount, dx, dy)
        self.stun = 10

    def animate(self):
        super().animate()

        for s in self.sprites:
            if self.alive:
                if self.stun > 0:
                    s.play('damage')
                else:
                    s.play('idle')
            else:
                s.play_once('die')

    def die(self):
        if self.alive:
            self.add_gib(0, 0, -1.25, -3, 'shrapnel', 'crawler')
            self.add_gib(0, 0, 1.25, -3, 'shrapnel', 'crawler')

            self.dx = 0
            self.dy = 0
            super().die()

    def add_shrapnel(self, dx, dy):
        #dx = random.uniform(dx - 1, dx + 1) * helpers.SCALE
        dx = dx * helpers.SCALE
        dy = dy * helpers.SCALE
        self.bullets.append(Shrapnel(self.x, self.y, dx, dy))

    def reset(self):
        super().reset()
        self.speed = 0.25 * helpers.SCALE
        self.dx = self.speed


class Shrapnel(creature.Gib):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy, 'idle', 'crawler')
        for s in self.sprites:
            s.play_once('shrapnel')

        self.dx = dx
        self.dy = dy
        self.collision = False


class Zombie(Enemy):
    def __init__(self, x, y):
        width = helpers.TILE_SIZE
        height = 2 * helpers.TILE_SIZE
        super().__init__(x, y, width, height, 5, ['zombie'])

        self.collider.height = 16 * helpers.SCALE
        self.speed = 0.25 * helpers.SCALE
        self.cooldown = 0
        for s in self.sprites:
            s.play('armored')
        self.bullet_speed = 2 * helpers.SCALE

    def update(self, room):
        if self.alive and self.ground_collision and not self.bullets:
            self.dx = self.speed
        else:
            self.dx = 0

        super().update(room)

        if self.alive:
            if self.wall_collision or self.on_edge(room):
                self.speed = -self.speed
                self.flip()

        self.animate()

    def animate(self):
        for s in self.sprites:
            if self.alive:
                if self.dx == 0:
                    s.pause()
                else:
                    s.play('armored')
            else:
                s.play_once('die')

    def see_player(self, room):
        super().see_player(room)
        player = room.level.player

        if self.sees_player and self.cooldown == 0:
            self.cooldown = 30
            if player.collider.x > self.collider.x:
                if self.direction is gameobject.Direction.left:
                    self.flip()
                x = self.collider.x + 8 * helpers.SCALE
                y = self.collider.y + 2 * helpers.SCALE
                self.bullets.append(
                    bullet.Bullet(x, y, self.bullet_speed, 0))
            elif player.rect.x < self.collider.x:
                if self.direction is gameobject.Direction.right:
                    self.flip()
                x = self.collider.x - 8 * helpers.SCALE
                y = self.collider.y + 2 * helpers.SCALE
                self.bullets.append(
                    bullet.Bullet(x, y, -self.bullet_speed, 0))
        elif self.cooldown > 0:
            self.cooldown -= 1

    def damage(self, amt, dx=0, dy=0):
        super().damage(amt, dx, dy)
        # path = 'zombie_gibs'
        # if self.armored:
        # self.armored = False
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
        if self.direction is gameobject.Direction.right:
            self.add_gib(0, -4, 0.5, -2.5, 'head', path)
        else:
            self.add_gib(0, -4, 0.5, -2.5, 'head', path)
        self.add_gib(-0.5, 4, -1.25, -2.5, 'arm', path)
        self.add_gib(0.5, 2, 1.25, -2.5, 'arm', path)

    def reset(self):
        Enemy.reset(self)
        self.speed = 0.25 * helpers.SCALE
        if self.direction is gameobject.Direction.left:
            self.flip()


class Flyer(Enemy):
    def __init__(self, x, y):
        width = 8 * helpers.SCALE
        height = 8 * helpers.SCALE
        super().__init__(x, y, width, height, 1, ['flyer'])
        self.group = gameobject.CollisionGroup.flyer
        self.speed = 1 * helpers.SCALE
        self.dx = self.speed
        self.gravity_scale = 0

    def update(self, room):
        super().update(room)

        if self.wall_collision:
            self.dy = self.dx
            self.dx = 0
        if self.ground_collision:
            self.dx = -self.dy
            self.dy = 0
        if self.ceiling_collision:
            self.dx = -self.dy
            self.dy = 0

    def damage(self, amount, dx=0, dy=0):
        pass

    def reset(self):
        super().reset()
        self.dx = self.speed
        self.dy = 0


class Spawner(Enemy):
    def __init__(self, x, y):
        width = 16 * helpers.SCALE
        height = 16 * helpers.SCALE
        super().__init__(x, y, width, height, 5, ['spawner'])
        self.gravity_scale = 0
        self.cooldown = 120
        self.timer = self.cooldown

    def update(self, room):
        super().update(room)

        for b in self.bullets:
            if not b.alive:
                for s in b.sprites:
                    if s.animation_finished:
                        self.bullets.remove(b)
                        break

        if self.alive:
            if len(self.bullets) < 3 and self.timer == self.cooldown:
                self.bullets.append(
                    Chaser(self.collider.x + 0.25 * self.collider.width,
                           self.collider.y + 0.25 * self.collider.height))
                self.timer = 0

        if self.timer < self.cooldown:
            self.timer += 1

    def chase(self, player):
        for c in self.bullets:
            c.chase(player)

    def die(self):
        super().die()
        for s in self.sprites:
            s.play_once('die')

    def reset(self):
        super().reset()
        for s in self.sprites:
            s.play('idle')
        self.timer = self.cooldown


class Chaser(Enemy):
    def __init__(self, x, y):
        width = 8 * helpers.SCALE
        height = 8 * helpers.SCALE
        super().__init__(x, y, width, height, 1, ['chaser'],
                         gameobject.CollisionGroup.chaser)
        self.gravity_scale = 0
        self.collision_enabled = False
        self.speed = 0.25 * helpers.SCALE

    def update(self, room):
        super().update(room)

        if self.collisions:
            self.speed = 0.1 * helpers.SCALE
        else:
            self.speed = 0.25 * helpers.SCALE

        if self.alive:
            self.chase(room)
        elif self.sprites[0].animation_finished:
            pass

    def animate(self):
        super().animate()

        if self.alive:
            rotation = helpers.rotation(self.dx, self.dy)
            for s in self.sprites:
                s.show_frame('idle', int((rotation / 360) * 8))
        else:
            for s in self.sprites:
                s.play_once('die')

    def chase(self, room):
        player = room.level.player

        if self.alive and player.alive:
            if self.collider.colliderect(player.collider):
                player.damage(1, 0, 0)

            x = player.x - self.x
            y = player.y - self.y
            distance = math.hypot(x, y)
            if distance > 1 * helpers.SCALE:
                self.dx = (x / distance) * self.speed
                self.dy = (y / distance) * self.speed
            else:
                self.dx = 0
                self.dy = 0

        else:
            self.dx = 0
            self.dy = 0

    def die(self):
        super().die()
        self.dx = 0
        self.dy = 0


class Charger(Enemy):
    def __init__(self, x, y):
        width = 16 * helpers.SCALE
        height = 16 * helpers.SCALE
        super().__init__(x, y, width, height, 6, ['charger'])
        self.speed = 0.5 * helpers.SCALE
        self.goal_dx = 0

    def update(self, room):
        super().update(room)

        if self.alive:
            super().update(room)
            self.see_player(room)

            if self.wall_collision:
                self.goal_dx = 0

            acceleration = self.friction
            if self.goal_dx < self.dx:
                self.dx -= acceleration
            elif self.goal_dx > self.dx:
                self.dx += acceleration

    def animate(self):
        super().animate()
        for s in self.sprites:
            if self.alive:
                if self.goal_dx != 0:
                    s.play('charge')
                else:
                    s.play('idle')
            else:
                s.play_once('die')

    def die(self):
        if self.alive:
            self.add_gib(0, 0, -1, -2, 'left', 'charger_gibs')
            self.add_gib(0, 0, 1, -2, 'right', 'charger_gibs')
        self.goal_dx = 0
        # FIXME: purk fix
        self.group = gameobject.CollisionGroup.none
        self.dy = -2 * helpers.SCALE
        super().die()

    def see_player(self, room):
        super().see_player(room)

        player = room.level.player

        if self.sees_player:
            if player.x > self.x:
                if self.direction is gameobject.Direction.left:
                    self.flip()
                self.goal_dx = self.speed
            elif player.x < self.x:
                if self.direction is gameobject.Direction.right:
                    self.flip()
                self.goal_dx = -self.speed

    def reset(self):
        super().reset()
        self.goal_dx = 0
        self.group = gameobject.CollisionGroup.enemies


class Dropper(Enemy):
    def __init__(self, x, y):
        width = helpers.TILE_SIZE
        height = helpers.TILE_SIZE
        super().__init__(x, y, width, height, 5, ['crawler'])
        self.gravity_scale = 0

    def update(self, room):
        super().update(room)
        player = room.level.player

        height = abs(self.collider.y - player.collider.y)
        collider = gameobject.GameObject(self.collider.bottom,
                                         self.collider.left,
                                         self.collider.width,
                                         height)

        for c in collider.get_collisions(room):
            if c is not player and c is not self:
                self.sees_player = False
                break
        else:
            self.sees_player = True
            self.gravity_scale = 1

    def reset(self):
        self.gravity_scale = 0


class Boss(Enemy):
    def __init__(self, x, y):
        width = 24 * helpers.SCALE
        height = 24 * helpers.SCALE
        super().__init__(x, y, width, height, 30, ['boss'])
        self.gravity_scale = 0
        self.group = gameobject.CollisionGroup.boss
        self.speed = 2 * helpers.SCALE
        self.active = False
        self.timer = 0
        self.time = 4 * helpers.FPS
        self.pause_time = 1 * helpers.FPS

    def animate(self):
        super().animate()
        for s in self.sprites:
            if not self.active:
                s.show_frame('idle', 0)
            else:
                if self.alive:
                    if self.time < self.timer < self.time + self.pause_time:
                        s.show_frame('idle', 0)
                    else:
                        s.play('idle')
                else:
                    s.play_once('die')

    def random_direction(self):
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        self.dx = dx * self.speed / math.sqrt(dx**2 + dy**2)
        self.dy = dy * self.speed / math.sqrt(dx**2 + dy**2)

    def damage(self, amount, dx=0, dy=0):
        super().damage(amount, dx, dy)

        if not self.active:
            self.active = True

    def update(self, room):
        super().update(room)

        if not self.active and abs(self.collider.centerx - room.level.player.x) < 2.5 * helpers.TILE_SIZE:
            self.active = True
            self.random_direction()

        if self.alive and self.active:
            if self.time < self.timer < self.time + self.pause_time:
                self.dx = 0
                self.dy = 0
            elif self.timer == self.time + self.pause_time:
                self.random_direction()
                self.timer = 0

            self.timer += 1

    def reset(self):
        super().reset()
        self.gravity_scale = 0
        self.group = gameobject.CollisionGroup.boss
        self.active = False
        self.timer = 0

    def apply_friction(self):
        if not self.alive and self.ground_collision:
            if self.dx > 0:
                self.dx = max(0, self.dx - self.friction)
            if self.dx < 0:
                self.dx = min(0, self.dx + self.friction)

    def die(self):
        super().die()
        self.dx = 0
        self.dy = 0
        self.group = gameobject.CollisionGroup.enemies
        self.add_gib(-2, 8, -1, -2, 'eye', 'boss_gibs')
        self.add_gib(18, 8, 1, -2, 'eye', 'boss_gibs')
        self.add_gib(-2, 0, -1, -1, 'left', 'boss_gibs')
        self.add_gib(18, 0, 1, -1, 'right', 'boss_gibs')
        self.add_gib(4, 12, -0.5, -1, 'tooth', 'boss_gibs')
        self.add_gib(12, 12, 0.5, -1, 'tooth', 'boss_gibs')
        self.gravity_scale = 1
