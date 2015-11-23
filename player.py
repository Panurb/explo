import random
import pygame
import animatedsprite
import enemy
import helpers
import bullet
import imagehandler
import physicsobject
import save
import textbox


class Player:
    def __init__(self, x, y, room_x, room_y):
        self.room_x = room_x
        self.room_y = room_y

        self.sprite_body = animatedsprite.AnimatedSprite('player_body')
        self.sprite_legs = animatedsprite.AnimatedSprite('player_legs')

        self.abilities = {
            'run': False,
            'double jump': False,
            'slide': False,
            'wall jump': False,
            'sword': False,
            'gun': False,
            'rebreather': False,
            'full auto': True
        }

        self.weapon = ''
        self.weapon_cooldown = {'sword': 24, 'gun': 8}

        self.rect = pygame.Rect(x, y, 6 * helpers.SCALE, 16 * helpers.SCALE)
        self.dx = 0
        self.dy = 0

        self.speed = {'walk': 0.5 * helpers.SCALE,
                      'run': 1 * helpers.SCALE,
                      'wall': 0.25 * helpers.SCALE,
                      'ladder': 0.75 * helpers.SCALE,
                      'water': 0.5 * helpers.SCALE}
        self.acceleration = {'ground': 0.25 * helpers.SCALE,
                             'air': 0.125 * helpers.SCALE}
        self.friction = {'normal': 0.125 * helpers.SCALE,
                         'slide': 0.0125 * helpers.SCALE,
                         'water': 0.125 * helpers.SCALE}
        self.jump_height = {'normal': -2.25 * helpers.SCALE,
                            'double': -2.5 * helpers.SCALE,
                            'wall': -2.25 * helpers.SCALE}

        self.alive = True
        self.grounded = False
        self.walled = False
        self.laddered = False
        self.crouched = False
        self.watered = False
        self.moving = False
        self.climbing = False
        self.sliding = False

        self.dir = 'right'
        self.jump_count = 0
        self.jump_buffer = False
        self.walled_timer = 0
        self.fatal_speed = 8 * helpers.SCALE

        self.attack_buffer = True
        self.bullet_speed = 4
        self.spread = 0.5
        self.cooldown = 0

        self.bullets = animatedsprite.Group()
        self.gibs = animatedsprite.Group()

        self.save = save.Save(x, y, room_x, room_y, self.dir, self.abilities)

        self.text = textbox.Textbox('')

    def update(self, room):
        self.move_x(room)
        self.move_y(room)

        if self.abilities['wall jump']:
            collider = pygame.sprite.Sprite()
            collider.rect = pygame.Rect(self.rect.left - 1, self.rect.y, self.rect.width + 2, self.rect.height)
            if pygame.sprite.spritecollide(collider, room.walls, False):
                self.walled = True
            else:
                self.walled = False

        self.apply_damage(room)
        self.apply_saving(room)
        self.apply_powerups(room)
        self.apply_friction()
        self.apply_ladders(room)
        self.apply_water(room)

        if self.grounded:
            if self.dy <= 0:
                self.laddered = False
            self.jump_count = 0

        self.apply_gravity()
        self.animate()
        self.update_bullets(room)

        self.gibs.update(room)

        if self.cooldown > 0:
            self.cooldown -= 1

        self.text.update()

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
        for w in room.water:
            if self.rect.colliderect(w.rect):
                self.watered = True

                if not self.abilities['rebreather']:
                    self.die()
                if self.dx > self.speed['water']:
                    self.dx = max(self.speed['water'], self.dx - self.friction['water'])
                elif self.dx < -self.speed['water']:
                    self.dx = min(-self.speed['water'], self.dx + self.friction['water'])
                if self.dy > self.speed['water']:
                    self.dy = max(self.speed['water'], self.dy - self.friction['water'])

    def input(self, input_hand, room):
        self.moving = False
        self.climbing = False
        self.sliding = False

        keys_down = input_hand.keys_down

        if self.alive:
            if keys_down[pygame.K_d]:
                self.change_weapon(keys_down)
                return
            # TODO: use SHIFT modifier for running
            if keys_down[pygame.K_RIGHT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities['run'] and not keys_down[pygame.K_LSHIFT]:
                    self.move(self.speed['run'])
                else:
                    self.move(self.speed['walk'])
            if keys_down[pygame.K_LEFT]:
                self.moving = True
                self.uncrouch(room)
                if self.abilities['run'] and not keys_down[pygame.K_LSHIFT]:
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
            if self.weapon == '':
                if self.grounded:
                    if self.crouched:
                        self.sprite_body.play('crouch')
                    elif abs(self.dx) > self.speed['walk']:
                        self.sprite_body.play('run', self.sprite_body.frame)
                    elif abs(self.dx) > 0.1 * helpers.SCALE:
                        self.sprite_body.play('walk')
                    else:
                        self.sprite_body.play('idle')
                elif self.laddered:
                    if abs(self.dy) == self.speed['ladder']:
                        self.sprite_body.play('climb')
                    else:
                        self.sprite_body.pause()
                elif self.walled and self.abilities['wall jump']:
                    self.sprite_body.play('wall_hug')
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
                            self.sprite_body.play(self.weapon + '_crouch_attack')
                        else:
                            self.sprite_body.play(self.weapon + '_crouch')
                    elif self.climbing:
                        self.sprite_body.play(self.weapon + '_up')
                    else:
                        if self.cooldown > 0:
                            self.sprite_body.play(self.weapon + '_attack')
                        else:
                            if self.dx == 0:
                                self.sprite_body.play(self.weapon + '_idle')
                            else:
                                self.sprite_body.play(self.weapon + '_walk')
                else:
                    if self.cooldown > 0:
                        self.sprite_body.play(self.weapon + '_attack')
                    else:
                        if self.dy < 0:
                            self.sprite_body.play_once(self.weapon + '_jump', 0)
                        elif self.dy > 0:
                            self.sprite_body.play_once(self.weapon + '_jump', 2)
                        else:
                            self.sprite_body.play_once(self.weapon + '_jump', 1)

            # LEGS
            if self.grounded:
                if self.crouched:
                    self.sprite_legs.play('crouch')
                elif abs(self.dx) > self.speed['walk']:
                    self.sprite_legs.play('run', self.sprite_body.frame)
                elif abs(self.dx) > 0.1 * helpers.SCALE:
                    self.sprite_legs.play('walk', self.sprite_body.frame)
                else:
                    self.sprite_legs.play('idle')
            elif self.laddered:
                if abs(self.dy) == self.speed['ladder']:
                    self.sprite_legs.play('climb')
                else:
                    self.sprite_legs.pause()
            elif self.walled and self.abilities['wall jump']:
                self.sprite_legs.play('wall_hug')
            else:
                if self.dy < 0:
                    self.sprite_legs.play_once('jump', 0)
                elif self.dy > 0:
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

    def update_bullets(self, room):
        self.bullets.update(room)

    def apply_damage(self, room):
        for spike in room.spikes:
            if self.rect.colliderect(spike.rect):
                self.die()

        for e in room.enemies:
            if self.rect.colliderect(e.rect) and e.alive:
                self.die()

            for p in e.projectiles:
                if self.rect.colliderect(p.rect):
                    self.die()

            if type(e) is enemy.Zombie and e.alive:
                e.vision(self)

    def apply_saving(self, room):
        for cp in pygame.sprite.spritecollide(self, room.checkpoints, False):
            self.save.room_x = room.x
            self.save.room_y = room.y
            self.save.x = cp.rect.x
            self.save.y = cp.rect.y - helpers.TILE_SIZE
            self.save.dir = self.dir
            for ability in self.abilities:
                self.save.abilities[ability] = self.abilities[ability]

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
                self.text.set_string(p.ability + '\\' + p.text)
                self.text.time = 120
                if p.ability == 'sword' or p.ability == 'gun':
                    self.weapon = p.ability

    def change_room(self):
        window_rect = pygame.Rect(0, 0, helpers.WIDTH, helpers.HEIGHT)
        if not window_rect.collidepoint(self.rect.center):
            self.bullets.empty()

            if self.rect.centerx >= helpers.WIDTH:
                self.room_x += 1
                self.rect.centerx = 1 * helpers.SCALE
            if self.rect.centerx <= 0:
                self.room_x -= 1
                self.rect.centerx = helpers.WIDTH - 1 * helpers.SCALE
            if self.rect.centery >= helpers.HEIGHT:
                self.room_y += 1
                self.rect.centery = 1 * helpers.SCALE
            if self.rect.centery <= 0:
                self.room_y -= 1
                self.rect.centery = helpers.HEIGHT - 1 * helpers.SCALE

    def apply_friction(self):
        friction = self.friction['normal']

        if self.grounded:
            if not self.moving:
                if self.dx > 0:
                    self.dx = max(0, self.dx - friction)
                if self.dx < 0:
                    self.dx = min(0, self.dx + friction)

        if self.laddered:
            if not self.climbing and not self.sliding:
                self.dy = 0

    def apply_gravity(self):
        if self.alive and not self.laddered:
            if self.walled and self.abilities['wall jump'] and not self.sliding:
                self.dy += helpers.GRAVITY / 2
                self.dy = min(self.dy, self.speed['wall'])
            elif not self.jump_buffer and self.dy < 0:
                self.dy += helpers.GRAVITY / 2
            else:
                self.dy += helpers.GRAVITY

    def move(self, speed):
        if not self.laddered:
            if self.grounded:
                acceleration = self.acceleration['ground']
            else:
                acceleration = self.acceleration['air']
            if speed > 0:
                if not self.crouched:
                    self.dx = min(speed, self.dx + acceleration)
            elif speed < 0:
                if not self.crouched:
                    self.dx = max(speed, self.dx - acceleration)
        if speed > 0:
            if self.dir == 'left' and not self.walled:
                self.flip()
        elif speed < 0:
            if self.dir == 'right' and not self.walled:
                self.flip()

    def climb(self, speed, room):
        width = 2 * helpers.SCALE
        for l in room.ladders:
            if l.rect.colliderect(pygame.Rect(self.rect.centerx - width / 2, self.rect.top, width, self.rect.height)):
                self.laddered = True
                self.rect.centerx = l.rect.centerx
                self.dx = 0
        if self.laddered:
            self.dy = speed

    def flip(self):
        self.sprite_body.flip()
        self.sprite_legs.flip()
        if self.dir == 'right':
            self.dir = 'left'
        elif self.dir == 'left':
            self.dir = 'right'

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
        elif self.walled and self.abilities['wall jump']:
            self.flip()
            speed = self.speed['walk']
            if self.abilities['run']:
                speed = self.speed['run']
            if self.dir == 'left':
                self.dx = -speed
            elif self.dir == 'right':
                self.dx = speed
            self.dy = self.jump_height['wall']
            self.jump_buffer = False
        elif self.abilities['double jump'] and self.jump_count < 2:
            self.dy = self.jump_height['double']
            self.jump_count = 2
            self.jump_buffer = False

    def crouch(self):
        if self.grounded and not self.crouched:
            self.rect.height = helpers.TILE_SIZE
            self.rect.y += helpers.TILE_SIZE
            self.crouched = True

    def uncrouch(self, room):
        if self.crouched:
            self.rect.height = 16 * helpers.SCALE
            self.rect.y -= helpers.TILE_SIZE
            if pygame.sprite.spritecollide(self, room.walls, False):
                self.rect.height = helpers.TILE_SIZE
                self.rect.y += helpers.TILE_SIZE
                return
            self.crouched = False

    def attack(self, up=False):
        if self.weapon == '':
            return

        if self.attack_buffer and self.cooldown == 0:
            if self.weapon == 'sword':
                if self.dir == 'right':
                    self.bullets.add(bullet.Sword(self.rect.x + helpers.TILE_SIZE, self.rect.y))
                elif self.dir == 'left':
                    self.bullets.add(bullet.Sword(self.rect.x - helpers.TILE_SIZE, self.rect.y))
                self.attack_buffer = False
            elif self.weapon == 'gun':
                if self.crouched:
                    spread = random.uniform(-self.spread, 0)
                else:
                    spread = random.uniform(-self.spread, self.spread)
                if not up:
                    y = self.rect.y + 0.5 * imagehandler.SIZES['bullet'][1] * helpers.SCALE
                    if self.dir == 'right':
                        if self.walled and not self.grounded:
                            dx = -self.bullet_speed
                        else:
                            dx = self.bullet_speed
                        self.bullets.add(bullet.Bullet(self.rect.x, y, dx, spread))
                    elif self.dir == 'left':
                        if self.walled and not self.grounded:
                            dx = self.bullet_speed
                        else:
                            dx = -self.bullet_speed
                        self.bullets.add(bullet.Bullet(self.rect.x, y, dx, spread))
                else:
                    x = self.rect.x + 0.5 * imagehandler.SIZES['bullet'][1] * helpers.SCALE
                    self.bullets.add(bullet.Bullet(x, self.rect.y, spread, -self.bullet_speed))
                if not self.abilities['full auto']:
                    self.attack_buffer = False

            self.cooldown = self.weapon_cooldown[self.weapon]

    def change_weapon(self, keys):
        if keys[pygame.K_UP]:
            self.weapon = ''
        elif keys[pygame.K_DOWN]:
            self.weapon = ''
        elif keys[pygame.K_RIGHT]:
            if self.abilities['sword']:
                self.weapon = 'sword'
        elif keys[pygame.K_LEFT]:
            if self.abilities['gun']:
                self.weapon = 'gun'

    def move_x(self, room):
        self.rect.move_ip(self.dx, 0)

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))
        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if not c.destroyed:
                if self.dx > 0:
                    self.rect.right = c.rect.left
                if self.dx < 0:
                    self.rect.left = c.rect.right

        if collisions:
            self.dx = 0

    def move_y(self, room):
        self.rect.move_ip(0, self.dy)

        collisions = (pygame.sprite.spritecollide(self, room.walls, False) +
                      pygame.sprite.spritecollide(self, room.destroyables, False))
        collisions = [c for c in collisions if not c.destroyed]

        for c in collisions:
            if self.dy > 0:
                self.rect.bottom = c.rect.top
                self.grounded = True

            if self.dy < 0:
                self.rect.top = c.rect.bottom

            if abs(self.dy) > self.fatal_speed:
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
                    if not self.crouched:
                        self.rect.bottom = c.rect.top
                        self.grounded = True
                        self.dy = 0
                    elif not c.rect.colliderect(
                            pygame.Rect(self.rect.centerx - width / 2, self.rect.top, width, self.rect.height)):
                        self.rect.bottom = c.rect.top
                        self.grounded = True
                        self.dy = 0

    def reset(self, room):
        self.alive = True
        self.rect.x = self.save.x
        self.rect.y = self.save.y
        self.room_x = self.save.room_x
        self.room_y = self.save.room_y
        if self.dir is not self.save.dir:
            self.flip()
        for ability in self.save.abilities:
            self.abilities[ability] = self.save.abilities[ability]
        self.dx = 0
        self.dy = 0
        self.gibs.empty()
        room.reset()

    def die(self):
        if self.alive:
            self.add_gib(0, 0, 0, -2.5, 'head')
            self.add_gib(-0.5, 2, -1.25, -2.5, 'arm')
            self.add_gib(0.5, 2, 1.25, -2.5, 'arm')
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

        self.text.draw(screen, img_hand)
