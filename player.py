import enum
import random

import pygame

import bullet
import enemy
import gameobject
import helpers
import hud
import imagehandler
import livingobject
import save
import textbox
import tile
from powerup import Ability

WIDTH = 6 * helpers.SCALE
HEIGHT = 15 * helpers.SCALE
CROUCHED_HEIGHT = 8 * helpers.SCALE

JUMP_HEIGHT = -2.25 * helpers.SCALE
WALK_SPEED = 0.5 * helpers.SCALE
RUN_SPEED = 1 * helpers.SCALE
LADDER_SPEED = 0.75 * helpers.SCALE
AIR_ACCELERATION = 0.125 * helpers.SCALE
WEAPON_COOLDOWN = 8
BULLET_SPEED = 4 * helpers.SCALE


class WeaponMod(enum.Enum):
    rapid = 1
    triple = 2
    gravity = 3


class Player(livingobject.LivingObject):
    def __init__(self, level):
        self.room_x = 0
        self.room_y = 0

        # Spawns in topleft if no checkpoint in room
        try:
            self.x = level.room(self.room_x, self.room_y).player_x
            self.y = level.room(self.room_x, self.room_y).player_y
        except KeyError:
            self.x = self.y = 0

        paths = ['player_body', 'player_legs']
        super().__init__(self.x, self.y, WIDTH, HEIGHT, paths)
        self.bounce_scale = 0

        self.alive = True
        self.moving = False
        self.looking_up = False
        self.sliding = False
        self.crouched = False
        self.climbing_ladder = False
        self.hugging_wall = False
        self.show_map = False

        self.jump_buffer = False
        self.jump_count = 0
        self.speed_wall = 0.25 * helpers.SCALE

        self.attack_buffer = True
        self.spread = 10
        self.cooldown = WEAPON_COOLDOWN
        self.weapon_mods = {}
        for w in WeaponMod:
            self.weapon_mods[w] = True

        self.bullets = []

        self.abilities = {}
        for a in Ability:
            self.abilities[a] = True

        self.save = save.Save(self.x, self.y, self.room_x, self.room_y,
                              self.direction, self.abilities)

        self.txtbox = textbox.Textbox('', 0.5 * helpers.SCREEN_WIDTH, 4 * helpers.SCALE)
        self.map = hud.Map(level)

    def update(self, room):
        super().update(room)

        self.apply_wall_hugging(room)

        self.cooldown = max(0, self.cooldown - 1)

        self.animate()

        for b in self.bullets:
            b.update(room)
            if not b.alive and not b.particles:
                self.bullets.remove(b)

        self.apply_room_change()

    def draw(self, screen, img_hand):
        for s in self.sprites:
            s.offset_x = -5 * helpers.SCALE
            if self.crouched:
                s.offset_y = -8 * helpers.SCALE
            else:
                s.offset_y = -1 * helpers.SCALE

        super().draw(screen, img_hand)

        for b in self.bullets:
            b.draw(screen, img_hand)

        if self.show_map:
            self.map.draw(screen, img_hand, self.room_x, self.room_y)

    def apply_wall_hugging(self, room):
        collider = pygame.Rect(self.collider.left - 1, self.collider.y,
                               self.collider.width + 2,
                               self.collider.height / 2)
        collisions = self.get_collisions(room, collider)

        for c in collisions:
            if type(c) is not enemy.Enemy:
                self.speed_wall = c.slide_speed

            if self.dy > 0:
                if self.speed_wall < helpers.TERMINAL_VELOCITY:
                    self.hugging_wall = True
            else:
                self.hugging_wall = False

        if not collisions or self.ground_collision:
            self.hugging_wall = False

    def input(self, input_hand, room):
        self.moving = False
        self.looking_up = False
        self.sliding = False

        keys_down = input_hand.keys_down

        if self.alive:
            if keys_down[pygame.K_d]:
                self.modify_weapon(input_hand.keys_pressed)
                return
            if keys_down[pygame.K_RIGHT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[
                        pygame.K_LSHIFT]:
                    self.move(RUN_SPEED)
                else:
                    self.move(WALK_SPEED)
            if keys_down[pygame.K_LEFT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[
                        pygame.K_LSHIFT]:
                    self.move(-RUN_SPEED)
                else:
                    self.move(-WALK_SPEED)
            if keys_down[pygame.K_UP]:
                self.looking_up = True
                # self.climb(-self.speed['ladder'], room)
            if keys_down[pygame.K_DOWN]:
                self.sliding = True
                if not keys_down[pygame.K_LEFT] and not keys_down[pygame.K_RIGHT]:
                    self.crouch()
                # self.climb(self.speed['ladder'], room)
            if keys_down[pygame.K_a]:
                self.jump()
            if not keys_down[pygame.K_a]:
                self.jump_buffer = True
            if keys_down[pygame.K_s]:
                if keys_down[pygame.K_UP]:
                    self.attack(True)
                else:
                    self.attack()

            self.show_map = keys_down[pygame.K_f]

            if not self.ground_collision or not keys_down[pygame.K_DOWN]:
                self.uncrouch(room)
            if not keys_down[pygame.K_s]:
                self.attack_buffer = True
        if input_hand.keys_pressed[pygame.K_r]:
            self.reset(room)

    def move(self, velocity):
        if not self.climbing_ladder:
            if self.ground_collision:
                acceleration = 4 * self.friction
            else:
                acceleration = AIR_ACCELERATION

            if velocity > 0:
                if not self.crouched:
                    self.dx = min(velocity, self.dx + acceleration)
            elif velocity < 0:
                if not self.crouched:
                    self.dx = max(velocity, self.dx - acceleration)
        if velocity > 0:
            if self.direction is gameobject.Direction.left:
                self.flip()
        elif velocity < 0:
            if self.direction is gameobject.Direction.right:
                self.flip()

    def jump(self):
        if not self.jump_buffer or self.crouched:
            return

        self.base_dx = 0
        self.base_dy = 0
        if self.ground_collision:
            self.dy = JUMP_HEIGHT
            self.jump_buffer = False
            self.jump_count = 1
        elif self.climbing_ladder:
            self.dy = JUMP_HEIGHT
            self.jump_buffer = False
            self.jump_count = 1
            self.climbing_ladder = False
        elif self.hugging_wall and self.abilities[Ability.wall_jump]:
            self.flip()
            speed = WALK_SPEED
            if self.abilities[Ability.run]:
                speed = RUN_SPEED
            if self.direction is gameobject.Direction.left:
                self.dx = -speed
            elif self.direction is gameobject.Direction.right:
                self.dx = speed
            self.dy = JUMP_HEIGHT
            self.jump_buffer = False
        elif self.abilities[Ability.double_jump] and self.jump_count < 2:
            self.dy = JUMP_HEIGHT
            self.jump_count = 2
            self.jump_buffer = False

    def reset(self, room):
        room.reset()
        self.base_dx = self.base_dy = 0
        self.x = self.save.x
        self.y = self.save.y
        self.room_x = self.save.room_x
        self.room_y = self.save.room_y
        if self.direction is not self.save.dir:
            self.flip()
        self.abilities = self.save.abilities.copy()
        self.dx = 0
        self.dy = 0
        self.bullets.clear()
        self.gibs.clear()
        self.alive = True

    def apply_gravity(self):
        if not self.alive or self.climbing_ladder:
            return

        if self.hugging_wall and self.abilities[Ability.wall_jump]:
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

    def die(self):
        path = 'player_gibs'
        if self.alive:
            self.add_gib(0, 0, 0, -2.5, path, 'head')
            self.add_gib(-0.5, 2, -1.25, -2.5, path, 'arm')
            self.add_gib(0.5, 2, 1.25, -2.5, path, 'arm')
            if not self.crouched:
                self.add_gib(-0.5, 4, -0.5, -1.25, path, 'leg')
                self.add_gib(0.5, 4, 0.5, -1.25, path, 'leg')
        super().die()

    def apply_room_change(self):
        window_rect = pygame.Rect(0, 0, helpers.SCREEN_WIDTH,
                                  helpers.SCREEN_HEIGHT)
        if not window_rect.collidepoint(self.collider.centerx,
                                        self.collider.centery):
            self.bullets.clear()

            if self.collider.centerx >= helpers.SCREEN_WIDTH:
                self.room_x += 1
                self.collider.centerx = helpers.SCALE
            if self.collider.centerx <= 0:
                self.room_x -= 1
                self.collider.centerx = helpers.SCREEN_WIDTH - helpers.SCALE
            if self.collider.centery >= helpers.SCREEN_HEIGHT:
                self.room_y += 1
                self.collider.centery = helpers.SCALE
            if self.collider.centery <= 0:
                self.room_y -= 1
                self.collider.centery = helpers.SCREEN_HEIGHT - helpers.SCALE

            self.x = self.collider.x
            self.y = self.collider.y

    def animate(self):
        sprite_body = self.sprites[0]
        sprite_legs = self.sprites[1]

        if self.alive:
            # BODY
            if not self.abilities[Ability.gun] or self.climbing_ladder:
                if self.ground_collision:
                    if self.crouched:
                        sprite_body.play('crouch')
                    elif self.moving and not self.wall_collision:
                        if abs(self.dx) > WALK_SPEED:
                            sprite_body.play('run', sprite_body.frame)
                        elif abs(self.dx) > 0:
                            sprite_body.play('walk')
                    else:
                        sprite_body.play('idle')
                elif self.climbing_ladder:
                    if abs(self.dy) == LADDER_SPEED:
                        sprite_body.play('climb')
                    else:
                        sprite_body.pause()
                elif self.hugging_wall and self.abilities[Ability.wall_jump]:
                    sprite_body.play_once('wall_hug')
                else:
                    if self.dy < 0:
                        sprite_body.play_once('jump', 0)
                    elif self.dy > 0:
                        sprite_body.play_once('jump', 2)
                    else:
                        sprite_body.play_once('jump', 1)
            else:
                if self.ground_collision:
                    if self.crouched:
                        if self.cooldown > 0:
                            sprite_body.play('gun_crouch_attack')
                        else:
                            sprite_body.play('gun_crouch')
                    elif self.looking_up:
                        sprite_body.play('gun_up')
                    else:
                        if self.cooldown > 0:
                            sprite_body.play('gun_attack')
                        else:
                            if self.dx == 0:
                                sprite_body.play('gun_idle')
                            else:
                                sprite_body.play('gun_walk')
                else:
                    if self.cooldown > 0:
                        sprite_body.play('gun_attack')
                    else:
                        if self.dy < 0:
                            sprite_body.play_once('gun_jump', 0)
                        elif self.dy > 0:
                            sprite_body.play_once('gun_jump', 2)
                        else:
                            sprite_body.play_once('gun_jump', 1)

            # LEGS
            if self.ground_collision:
                if self.crouched:
                    sprite_legs.play('crouch')
                elif self.moving and not self.wall_collision:
                    if abs(self.dx) > WALK_SPEED:
                        sprite_legs.play('run', sprite_body.frame)
                    elif abs(self.dx) > 0:
                        sprite_legs.play('walk', sprite_body.frame)
                else:
                    sprite_legs.play('idle')
            elif self.climbing_ladder:
                if abs(self.dy) == LADDER_SPEED:
                    sprite_legs.play('climb')
                else:
                    sprite_legs.pause()
            elif self.hugging_wall and self.abilities[Ability.wall_jump]:
                sprite_legs.play('wall_hug')
            else:
                if self.dy < -1 * helpers.SCALE:
                    sprite_legs.play_once('jump', 0)
                elif self.dy > 1 * helpers.SCALE:
                    sprite_legs.play_once('jump', 1)
                else:
                    sprite_legs.play_once('jump', 2)
        else:
            sprite_body.play_once('explode')
            sprite_legs.play_once('explode')

        x = self.collider.centerx - helpers.TILE_SIZE
        y = self.collider.y + self.collider.height - 16 * helpers.SCALE
        sprite_body.set_position(x, y)
        sprite_legs.set_position(x, y)
        sprite_body.animate()
        sprite_legs.animate()

    def attack(self, up=False):
        if not self.abilities[Ability.gun] or self.climbing_ladder:
            return

        if self.attack_buffer and self.cooldown == 0:
            if self.crouched:
                if self.direction is gameobject.Direction.right:
                    spread = random.uniform(-self.spread, 0)
                else:
                    spread = random.uniform(0, self.spread)
            else:
                spread = random.uniform(-self.spread, self.spread)

            x = self.x
            y = self.y
            angle = 0
            if up:
                x += 1.25 * helpers.SCALE
                angle = 270
            else:
                y += 0.5 * imagehandler.SIZES['bullet'][1] * helpers.SCALE
                if self.direction is gameobject.Direction.left:
                    if self.hugging_wall:
                        if self.ground_collision:
                            angle = 180
                    else:
                        angle = 180
                elif self.direction is gameobject.Direction.right:
                    if self.hugging_wall:
                        if not self.ground_collision:
                            angle = 180
                    else:
                        angle = 0

            grav = 0
            if self.weapon_mods[WeaponMod.gravity]:
                grav = 1
            self.bullets.append(
                bullet.Bullet(x, y, BULLET_SPEED, angle + spread, grav))
            if self.weapon_mods[WeaponMod.triple]:
                self.bullets.append(
                    bullet.Bullet(x, y, BULLET_SPEED, angle + 22.5 + spread,
                                  grav))
                self.bullets.append(
                    bullet.Bullet(x, y, BULLET_SPEED, angle - 22.5 + spread,
                                  grav))

            if not self.weapon_mods[WeaponMod.rapid]:
                self.attack_buffer = False

            self.cooldown = WEAPON_COOLDOWN

    def modify_weapon(self, keys):
        if keys[pygame.K_UP]:
            pass
        elif keys[pygame.K_DOWN]:
            if self.abilities[Ability.gravity]:
                self.weapon_mods[WeaponMod.gravity] = not self.weapon_mods[
                    WeaponMod.gravity]
        elif keys[pygame.K_RIGHT]:
            if self.abilities[Ability.full_auto]:
                self.weapon_mods[WeaponMod.rapid] = not self.weapon_mods[
                    WeaponMod.rapid]
        elif keys[pygame.K_LEFT]:
            if self.abilities[Ability.spread]:
                self.weapon_mods[WeaponMod.triple] = not self.weapon_mods[
                    WeaponMod.triple]

    def crouch(self):
        if self.ground_collision and not self.crouched:
            self.collider.height = CROUCHED_HEIGHT
            self.collider.y += 7 * helpers.SCALE
            self.y = self.collider.y
            self.crouched = True

    def uncrouch(self, room):
        if self.crouched:
            self.collider.height = HEIGHT
            self.collider.y -= 7 * helpers.SCALE
            self.y = self.collider.y
            if self.get_collisions(room):
                self.collider.height = helpers.TILE_SIZE
                self.collider.y += helpers.TILE_SIZE
                self.y = self.collider.y
                return
            self.crouched = False
