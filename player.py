import pygame

import gameobject
import helpers
import save
from powerup import Ability

JUMP_HEIGHT = -2.25 * helpers.SCALE
WALK_SPEED = 0.5 * helpers.SCALE
RUN_SPEED = 1 * helpers.SCALE
AIR_ACCELERATION = 0.125 * helpers.SCALE


class Player(gameobject.PhysicsObject):
    def __init__(self, level):
        self.room_x = 0
        self.room_y = 0

        # Spawns in topleft if no checkpoint in room
        try:
            self.x = level.room(self.room_x, self.room_y).player_x
            self.y = level.room(self.room_x, self.room_y).player_y
        except KeyError:
            self.x = self.y = 0

        width = 6 * helpers.SCALE
        height = 16 * helpers.SCALE
        paths = ['player_body', 'player_legs']
        gameobject.PhysicsObject.__init__(self, self.x, self.y, width, height, 0, 0, paths)
        self.bounce_scale = 0

        self.alive = True
        self.moving = False
        self.climbing = False
        self.sliding = False
        self.crouched = False
        self.laddered = False
        self.hugging_wall = False

        self.jump_buffer = False
        self.jump_count = 0
        self.speed_wall = 0.25 * helpers.SCALE

        self.gibs = []
        self.abilities = {}
        for a in Ability:
            self.abilities[a] = True

        self.save = save.Save(self.x, self.y, self.room_x, self.room_y, self.direction, self.abilities)

    def update(self, room):
        gameobject.PhysicsObject.update(self, room)

        self.apply_room_change()

    def input(self, input_hand, room):
        self.moving = False
        self.climbing = False
        self.sliding = False

        keys_down = input_hand.keys_down

        if self.alive:
            if keys_down[pygame.K_d]:
                # self.change_mods(input_hand.keys_pressed)
                return
            if keys_down[pygame.K_RIGHT]:
                self.moving = True
                # self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[pygame.K_LSHIFT]:
                    self.move(RUN_SPEED)
                else:
                    self.move(WALK_SPEED)
            if keys_down[pygame.K_LEFT]:
                self.moving = True
                # self.uncrouch(room)
                if self.abilities[Ability.run] and not keys_down[pygame.K_LSHIFT]:
                    self.move(-RUN_SPEED)
                else:
                    self.move(-WALK_SPEED)
            if keys_down[pygame.K_UP]:
                pass
                # self.climbing = True
                # self.climb(-self.speed['ladder'], room)
            if keys_down[pygame.K_DOWN]:
                self.sliding = True
                # if not keys_down[pygame.K_LEFT] and not keys_down[pygame.K_RIGHT]:
                # self.crouch()
                # self.climb(self.speed['ladder'], room)
            if keys_down[pygame.K_a]:
                self.jump()
            if not keys_down[pygame.K_a]:
                self.jump_buffer = True
            if keys_down[pygame.K_s]:
                pass
                # if keys_down[pygame.K_UP]:
                # self.attack(True)
                # else:
                # self.attack()

            # self.show_map = keys_down[pygame.K_f]

            if not self.ground_collision or not keys_down[pygame.K_DOWN]:
                pass
                # self.uncrouch(room)
            if not keys_down[pygame.K_s]:
                pass
                # self.attack_buffer = True
        if input_hand.keys_pressed[pygame.K_r]:
            self.reset(room)

    def move(self, velocity):
        if not self.laddered:
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
        elif self.laddered:
            self.dy = JUMP_HEIGHT
            self.jump_buffer = False
            self.jump_count = 1
            self.laddered = False
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
        self.gibs.clear()
        self.alive = True

    def apply_gravity(self):
        if not self.alive or self.laddered or self.ground_collision:
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
        print('DIED')
        path = 'player_gibs'
        x = self.collider.centerx + x * helpers.SCALE
        y = self.collider.centery + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.append(gameobject.Gib(x, y, dx, dy, part, path))

    def apply_room_change(self):
        window_rect = pygame.Rect(0, 0, helpers.SCREEN_WIDTH, helpers.SCREEN_HEIGHT)
        if not window_rect.collidepoint(self.collider.centerx, self.collider.centery):
            # self.bullets.empty()

            if self.collider.centerx >= helpers.SCREEN_WIDTH:
                self.room_x += 1
                self.collider.centerx = 1 * helpers.SCALE
            if self.collider.centerx <= 0:
                self.room_x -= 1
                self.collider.centerx = helpers.SCREEN_WIDTH - 1 * helpers.SCALE
            if self.collider.centery >= helpers.SCREEN_HEIGHT:
                self.room_y += 1
                self.collider.centery = 1 * helpers.SCALE
            if self.collider.centery <= 0:
                self.room_y -= 1
                self.collider.centery = helpers.SCREEN_HEIGHT - 1 * helpers.SCALE

            self.x = self.collider.x
            self.y = self.collider.y
