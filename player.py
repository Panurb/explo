from enum import Enum
import random
import pygame
import animatedsprite
from animatedsprite import Direction
import enemy
import helpers
import bullet
import hud
import imagehandler
import physicsobject
from powerup import Ability
import save
import textbox


class Weapon(Enum):
    none = 1
    gun = 2
    sword = 3


class Player:
    def __init__(self, level):
        try:
            self.x = level.room(0, 0).player_x
            self.y = level.room(0, 0).player_y
        except KeyError:
            self.x = self.y = 0
        self.room_x = 0
        self.room_y = 0

        self.sprite_body = animatedsprite.AnimatedSprite('player_body')
        self.sprite_legs = animatedsprite.AnimatedSprite('player_legs')

        self.abilities = {}
        for a in Ability:
            self.abilities[a] = False

        self.weapon = Weapon.none
        self.weapon_cooldown = {Weapon.sword: 24, Weapon.gun: 8}

        self.rect = pygame.Rect(self.x, self.y, 6 * helpers.SCALE, 15 * helpers.SCALE)
        self.dx = 0
        self.dy = 0

        self.speed = {'walk': 0.5 * helpers.SCALE,
                      'run': 1 * helpers.SCALE,
                      'ladder': 0.75 * helpers.SCALE,
                      'water': 0.5 * helpers.SCALE}
        self.speed_wall = 0.25 * helpers.SCALE
        self.acceleration = {'ground': 0.25 * helpers.SCALE,
                             'air': 0.125 * helpers.SCALE}
        self.friction = 0.125 * helpers.SCALE
        self.friction_water = 0.125 * helpers.SCALE
        self.jump_height = {'normal': -2.25 * helpers.SCALE,
                            'double': -2.5 * helpers.SCALE,
                            'wall': -2.25 * helpers.SCALE}

        self.alive = True
        self.grounded = False
        self.walled = False
        self.laddered = False
        self.crouched = False
        self.moving = False
        self.climbing = False
        self.sliding = False
        self.hugging = False
        self.show_map = False

        self.dir = Direction.right
        self.jump_count = 0
        self.jump_buffer = False

        self.attack_buffer = True
        self.bullet_speed = 4 * helpers.SCALE
        self.spread = 0
        self.cooldown = 0

        self.bullets = animatedsprite.Group()
        self.gibs = animatedsprite.Group()

        self.save = save.Save(self.rect.x, self.rect.y, self.room_x, self.room_y, self.dir, self.abilities)

        self.txtbox = textbox.Textbox('', 0.5 * helpers.SCREEN_WIDTH, 4 * helpers.SCALE)
        self.map = hud.Map(level)

    def update(self, room):
        self.move_x(room)
        self.move_y(room)

        self.apply_damage(room)
        self.apply_saving(room)
        self.apply_powerups(room)
        self.apply_friction()
        self.apply_ladders(room)
        self.apply_water(room)

        if self.grounded:
            self.jump_count = 0
            if self.dy <= 0:
                self.laddered = False

        self.apply_gravity()
        self.animate()
        self.bullets.update(room)
        self.gibs.update(room)

        self.cooldown = max(0, self.cooldown - 1)

        self.txtbox.update()

        self.change_room()

    def apply_ladders(self, room):
        collided = False
        for l in room.ladders:
            width = 2 * helpers.SCALE
            if l.rect.colliderect(pygame.Rect(self.rect.centerx - width / 2, self.rect.top, width, self.rect.height)):
                collided = True
        if not collided:
            self.laddered = False

    def apply_water(self, room):
        if pygame.sprite.spritecollide(self, room.water, False):
            if not self.abilities[Ability.rebreather]:
                self.die()
            if self.dx > self.speed['water']:
                self.dx = max(self.speed['water'], self.dx - self.friction_water)
            elif self.dx < -self.speed['water']:
                self.dx = min(-self.speed['water'], self.dx + self.friction_water)
            if self.dy > self.speed['water']:
                self.dy = max(self.speed['water'], self.dy - self.friction_water)

    def input(self, input_hand, room):
        self.moving = False
        self.climbing = False
        self.sliding = False

        keys_down = input_hand.keys_down

        if self.alive:
            if keys_down[pygame.K_d]:
                self.change_weapon(keys_down)
                return
            if keys_down[pygame.K_RIGHT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[pygame.K_LSHIFT]:
                    self.move(self.speed['run'])
                else:
                    self.move(self.speed['walk'])
            if keys_down[pygame.K_LEFT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[pygame.K_LSHIFT]:
                    self.move(-self.speed['run'])
                else:
                    self.move(-self.speed['walk'])
            if keys_down[pygame.K_UP]:
                self.climbing = True
                self.climb(-self.speed['ladder'], room)
            if keys_down[pygame.K_DOWN]:
                self.sliding = True
                if not keys_down[pygame.K_LEFT] and not keys_down[pygame.K_RIGHT]:
                    self.crouch()
                self.climb(self.speed['ladder'], room)
            if keys_down[pygame.K_a]:
                self.jump()
            if keys_down[pygame.K_s]:
                if keys_down[pygame.K_UP]:
                    self.attack(True)
                else:
                    self.attack()

            self.show_map = keys_down[pygame.K_f]

            if not self.grounded or not keys_down[pygame.K_DOWN]:
                self.uncrouch(room)
            if not keys_down[pygame.K_a]:
                self.jump_buffer = True
            if not keys_down[pygame.K_s]:
                self.attack_buffer = True
        if input_hand.keys_pressed[pygame.K_r]:
            self.reset(room)

    def animate(self):
        if self.alive:
            # BODY
            if self.weapon is Weapon.none or self.laddered:
                if self.grounded:
                    if self.crouched:
                        self.sprite_body.play('crouch')
                    elif self.moving and not self.walled:
                        if abs(self.dx) > self.speed['walk']:
                            self.sprite_body.play('run', self.sprite_body.frame)
                        elif abs(self.dx) > 0:
                            self.sprite_body.play('walk')
                    else:
                        self.sprite_body.play('idle')
                elif self.laddered:
                    if abs(self.dy) == self.speed['ladder']:
                        self.sprite_body.play('climb')
                    else:
                        self.sprite_body.pause()
                elif self.hugging and self.abilities[Ability.wall_jump]:
                    self.sprite_body.play_once('wall_hug')
                else:
                    if self.dy < 0:
                        self.sprite_body.play_once('jump', 0)
                    elif self.dy > 0:
                        self.sprite_body.play_once('jump', 2)
                    else:
                        self.sprite_body.play_once('jump', 1)
            else:
                if self.grounded:
                    if self.crouched:
                        if self.cooldown > 0:
                            self.sprite_body.play(self.weapon.name + '_crouch_attack')
                        else:
                            self.sprite_body.play(self.weapon.name + '_crouch')
                    elif self.climbing:
                        self.sprite_body.play(self.weapon.name + '_up')
                    else:
                        if self.cooldown > 0:
                            self.sprite_body.play(self.weapon.name + '_attack')
                        else:
                            if self.dx == 0:
                                self.sprite_body.play(self.weapon.name + '_idle')
                            else:
                                self.sprite_body.play(self.weapon.name + '_walk')
                else:
                    if self.cooldown > 0:
                        self.sprite_body.play(self.weapon.name + '_attack')
                    else:
                        if self.dy < 0:
                            self.sprite_body.play_once(self.weapon.name + '_jump', 0)
                        elif self.dy > 0:
                            self.sprite_body.play_once(self.weapon.name + '_jump', 2)
                        else:
                            self.sprite_body.play_once(self.weapon.name + '_jump', 1)

            # LEGS
            if self.grounded:
                if self.crouched:
                    self.sprite_legs.play('crouch')
                elif self.moving and not self.walled:
                    if abs(self.dx) > self.speed['walk']:
                        self.sprite_legs.play('run', self.sprite_body.frame)
                    elif abs(self.dx) > 0:
                        self.sprite_legs.play('walk', self.sprite_body.frame)
                else:
                    self.sprite_legs.play('idle')
            elif self.laddered:
                if abs(self.dy) == self.speed['ladder']:
                    self.sprite_legs.play('climb')
                else:
                    self.sprite_legs.pause()
            elif self.hugging and self.abilities[Ability.wall_jump]:
                self.sprite_legs.play('wall_hug')
            else:
                if self.dy < -1 * helpers.SCALE:
                    self.sprite_legs.play_once('jump', 0)
                elif self.dy > 1 * helpers.SCALE:
                    self.sprite_legs.play_once('jump', 1)
                else:
                    self.sprite_legs.play_once('jump', 2)
        else:
            self.sprite_body.play_once('explode')
            self.sprite_legs.play_once('explode')

        x = self.rect.centerx - helpers.TILE_SIZE
        y = self.rect.y + self.rect.height - 16 * helpers.SCALE
        self.sprite_body.set_position(x, y)
        self.sprite_legs.set_position(x, y)
        self.sprite_body.animate()
        self.sprite_legs.animate()

    def apply_damage(self, room):
        if pygame.sprite.spritecollide(self, room.spikes, False):
            self.die()

        for e in room.enemies:
            if self.rect.colliderect(e.rect) and e.alive:
                self.die()

            for p in e.projectiles:
                if p.alive and self.rect.colliderect(p.rect):
                    self.die()

            if e.alive:
                if type(e) is enemy.Zombie:
                    e.see_player(self, room)
                elif type(e) is enemy.Charger:
                    e.see_player(self, room)
            if type(e)is enemy.Spawner:
                    e.chase(self)

    def apply_saving(self, room):
        for cp in pygame.sprite.spritecollide(self, room.checkpoints, False):
            self.save.room_x = room.x
            self.save.room_y = room.y
            self.save.x = cp.rect.x
            self.save.y = cp.rect.y
            self.save.dir = self.dir
            self.save.abilities = self.abilities.copy()
            self.save.weapon = self.weapon

            cp.active = True

    def apply_powerups(self, room):
        for p in room.powerups:
            if not self.abilities[p.ability]:
                p.visible = True
            else:
                p.visible = False
        for p in pygame.sprite.spritecollide(self, room.powerups, False):
            if self.abilities[p.ability] is False:
                self.abilities[p.ability] = True
                self.txtbox.set_string(p.ability.name.upper() + '\\' + p.text)
                self.txtbox.time = 120
                if p.ability is Ability.gun:
                    self.weapon = Weapon.gun

    def change_room(self):
        window_rect = pygame.Rect(0, 0, helpers.SCREEN_WIDTH, helpers.SCREEN_HEIGHT)
        if not window_rect.collidepoint(self.rect.center):
            self.bullets.empty()

            if self.rect.centerx >= helpers.SCREEN_WIDTH:
                self.room_x += 1
                self.rect.centerx = 1 * helpers.SCALE
            if self.rect.centerx <= 0:
                self.room_x -= 1
                self.rect.centerx = helpers.SCREEN_WIDTH - 1 * helpers.SCALE
            if self.rect.centery >= helpers.SCREEN_HEIGHT:
                self.room_y += 1
                self.rect.centery = 1 * helpers.SCALE
            if self.rect.centery <= 0:
                self.room_y -= 1
                self.rect.centery = helpers.SCREEN_HEIGHT - 1 * helpers.SCALE

            self.x = self.rect.x
            self.y = self.rect.y

    def apply_friction(self):
        if self.grounded and not self.moving:
            if self.dx > 0:
                self.dx = max(0, self.dx - self.friction)
            if self.dx < 0:
                self.dx = min(0, self.dx + self.friction)

        if self.laddered:
            if not self.climbing and not self.sliding:
                self.dy = 0

    def apply_gravity(self):
        if self.alive and not self.laddered:
            if self.hugging and self.abilities[Ability.wall_jump]:
                if not self.sliding:
                    self.dy += helpers.GRAVITY / 2
                    self.dy = min(self.dy, self.speed_wall)
                else:
                    self.dy += helpers.GRAVITY
                    self.dy = min(self.dy, helpers.TERMINAL_VELOCITY)
            elif not self.jump_buffer and self.dy < 0:
                self.dy += helpers.GRAVITY / 2
            else:
                self.dy += helpers.GRAVITY

    def move(self, speed):
        if not self.laddered:
            if self.grounded:
                acceleration = 4 * self.friction
            else:
                acceleration = self.acceleration['air']
            if speed > 0:
                if not self.crouched:
                    self.dx = min(speed, self.dx + acceleration)
            elif speed < 0:
                if not self.crouched:
                    self.dx = max(speed, self.dx - acceleration)
        if speed > 0:
            if self.dir is Direction.left:
                self.flip()
        elif speed < 0:
            if self.dir is Direction.right:
                self.flip()

    def climb(self, speed, room):
        collider = pygame.sprite.Sprite()
        width = 2 * helpers.SCALE
        collider.rect = pygame.Rect(self.rect.centerx - width / 2, self.rect.top, width, self.rect.height)

        for l in pygame.sprite.spritecollide(collider, room.ladders, False):
            self.laddered = True
            self.rect.centerx = l.rect.centerx
            self.x = self.rect.x
            self.dx = 0
        if self.laddered:
            self.dy = speed

    def flip(self):
        self.sprite_body.flip()
        self.sprite_legs.flip()
        if self.dir is Direction.right:
            self.dir = Direction.left
        elif self.dir is Direction.left:
            self.dir = Direction.right

    def jump(self):
        if not self.jump_buffer or self.crouched:
            return

        if self.grounded:
            self.dy = self.jump_height['normal']
            self.jump_buffer = False
            self.jump_count = 1
        elif self.laddered:
            self.dy = self.jump_height['normal']
            self.jump_buffer = False
            self.jump_count = 1
            self.laddered = False
        elif self.hugging and self.abilities[Ability.wall_jump]:
            self.flip()
            speed = self.speed['walk']
            if self.abilities[Ability.run]:
                speed = self.speed['run']
            if self.dir is Direction.left:
                self.dx = -speed
            elif self.dir is Direction.right:
                self.dx = speed
            self.dy = self.jump_height['wall']
            self.jump_buffer = False
        elif self.abilities[Ability.double_jump] and self.jump_count < 2:
            self.dy = self.jump_height['double']
            self.jump_count = 2
            self.jump_buffer = False

    def crouch(self):
        if self.grounded and not self.crouched:
            self.rect.height = 8 * helpers.SCALE
            self.rect.y += 7 * helpers.SCALE
            self.y = self.rect.y
            self.crouched = True

    def uncrouch(self, room):
        if self.crouched:
            self.rect.height = 15 * helpers.SCALE
            self.rect.y -= 7 * helpers.SCALE
            self.y = self.rect.y
            if pygame.sprite.spritecollide(self, room.walls, False):
                self.rect.height = helpers.TILE_SIZE
                self.rect.y += helpers.TILE_SIZE
                self.y = self.rect.y
                return
            self.crouched = False

    def attack(self, up=False):
        if self.weapon is Weapon.none or self.laddered:
            return

        if self.attack_buffer and self.cooldown == 0:
            if self.weapon is Weapon.sword:
                if self.dir is Direction.right:
                    self.bullets.add(bullet.Sword(self.rect.x + helpers.TILE_SIZE, self.rect.y))
                else:
                    self.bullets.add(bullet.Sword(self.rect.x - helpers.TILE_SIZE, self.rect.y))
                self.attack_buffer = False
            elif self.weapon is Weapon.gun:
                if self.crouched:
                    if self.dir is Direction.right:
                        spread = random.uniform(-self.spread, 0)
                    else:
                        spread = random.uniform(0, self.spread)
                else:
                    spread = random.uniform(-self.spread, self.spread)

                x = y = angle = 0
                if up:
                    x = 1.25 * helpers.SCALE
                    angle = 270
                else:
                    y = 0.5 * imagehandler.SIZES['bullet'][1] * helpers.SCALE
                    if self.dir is Direction.left:
                        if self.walled:
                            if self.grounded:
                                angle = 180
                        else:
                            angle = 180
                    elif self.dir is Direction.right:
                        if self.walled:
                            if not self.grounded:
                                angle = 180
                        else:
                            angle = 0

                self.bullets.add(bullet.Bullet(self.rect.x + x, self.rect.y + y, self.bullet_speed, angle + spread))

                if not self.abilities[Ability.full_auto]:
                    self.attack_buffer = False

            self.cooldown = self.weapon_cooldown[self.weapon]

    def change_weapon(self, keys):
        if keys[pygame.K_UP]:
            self.weapon = Weapon.none
        elif keys[pygame.K_DOWN]:
            self.weapon = Weapon.none
        elif keys[pygame.K_RIGHT]:
            if self.abilities[Ability.sword]:
                self.weapon = Weapon.sword
        elif keys[pygame.K_LEFT]:
            if self.abilities[Ability.gun]:
                self.weapon = Weapon.gun

    def move_x(self, room):
        self.x += self.dx
        self.rect.x = self.x

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))
        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if not c.destroyed:
                self.speed_wall = c.slide_speed
                if self.dx > 0:
                    self.rect.right = c.rect.left
                    self.x = self.rect.x
                if self.dx < 0:
                    self.rect.left = c.rect.right
                    self.x = self.rect.x

        if collisions:
            self.dx = 0

        if self.abilities[Ability.wall_jump]:
            collider = pygame.sprite.Sprite()
            collider.rect = pygame.Rect(self.rect.left - 1, self.rect.y, self.rect.width + 2, self.rect.height / 2)
            # TODO: check for destroyables
            collisions = pygame.sprite.spritecollide(collider, room.walls, False)
            for c in collisions:
                self.speed_wall = c.slide_speed
            if collisions and self.dy > 0:
                self.walled = True
                if self.speed_wall < helpers.TERMINAL_VELOCITY:
                    self.hugging = True
            else:
                self.walled = False
                self.hugging = False

    def move_y(self, room):
        self.y += self.dy
        self.rect.y = self.y

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))
        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if self.dy > 0:
                self.rect.bottom = c.rect.top
                self.y = self.rect.y
                self.grounded = True
                self.friction = c.friction

            if self.dy < 0:
                self.rect.top = c.rect.bottom
                self.y = self.rect.y

            if abs(self.dy) >= helpers.TERMINAL_VELOCITY:
                self.die()

        if collisions:
            self.dy = helpers.GRAVITY
        else:
            self.grounded = False

        if not self.laddered:
            ladder_collisions = pygame.sprite.spritecollide(self, room.ladders, False)
            ladder_collisions = [c for c in ladder_collisions if c.top]

            for c in ladder_collisions:
                if self.dy > 0 and self.rect.bottom - self.dy <= c.rect.top:
                    width = 2 * helpers.SCALE
                    self.friction = 0.125 * helpers.SCALE
                    if not self.crouched:
                        self.rect.bottom = c.rect.top
                        self.y = self.rect.y
                        self.grounded = True
                        self.dy = 0
                    elif not c.rect.colliderect(
                            pygame.Rect(self.rect.centerx - width / 2, self.rect.top, width, self.rect.height)):
                        self.rect.bottom = c.rect.top
                        self.y = self.rect.y
                        self.grounded = True
                        self.dy = 0

    def reset(self, room):
        room.reset()
        self.x = self.save.x
        self.y = self.save.y
        self.room_x = self.save.room_x
        self.room_y = self.save.room_y
        if self.dir is not self.save.dir:
            self.flip()
        self.abilities = self.save.abilities.copy()
        self.dx = 0
        self.dy = 0
        self.gibs.empty()
        self.weapon = self.save.weapon
        self.alive = True

    def die(self):
        if self.alive:
            self.add_gib(0, 0, 0, -2.5, 'head')
            self.add_gib(-0.5, 2, -1.25, -2.5, 'arm')
            self.add_gib(0.5, 2, 1.25, -2.5, 'arm')
            if not self.crouched:
                self.add_gib(-0.5, 4, -0.5, -1.25, 'leg')
                self.add_gib(0.5, 4, 0.5, -1.25, 'leg')
            self.alive = False
        self.dx = 0
        self.dy = 0

    def add_gib(self, x, y, dx, dy, part):
        path = 'player_gibs'
        x = self.rect.centerx + x * helpers.SCALE
        y = self.rect.centery + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.add(physicsobject.Gib(x, y, dx, dy, part, path))

    def draw(self, screen, img_hand):
        self.sprite_legs.draw(screen, img_hand)
        self.sprite_body.draw(screen, img_hand)

        self.bullets.draw(screen, img_hand)
        self.gibs.draw(screen, img_hand)

        self.txtbox.draw(screen, img_hand)
        if self.show_map:
            self.map.draw(screen, img_hand, self.room_x, self.room_y)
