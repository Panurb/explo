import platform
import pygame
import animatedsprite
import enemy
import helpers
import player
import player_old
import powerup
import tile


class Level:
    def __init__(self, filename):
        self.path = 'data/lvl/' + filename + '.txt'
        file = open(self.path, 'a+')
        file.seek(0)
        lines = file.readlines()

        self.rooms = {}
        room = []
        coordinates = ()
        for line in lines:
            line = line.rstrip('\n')

            if line.find('(') == 0:
                line = line.replace('(', '').replace(')', '').split(',')
                coordinates = (int(line[0]), int(line[1]))
                continue

            if not line.rstrip():
                self.rooms[coordinates] = Room(self, room, coordinates[0],
                                               coordinates[1])
                room = []
                continue

            room.append(list(line))

        self.player = player.Player(self)

    def room(self, x, y):
        try:
            room = self.rooms[(x, y)]
        except KeyError:
            tilemap = 14 * [20 * "-"]
            self.rooms[(x, y)] = Room(self, tilemap, x, y)
            room = self.rooms[(x, y)]

        return room

    def write(self):
        f = open(self.path, 'w')

        for room in self.rooms.values():
            room.reset()
            tilemap = [['-' for _ in range(helpers.ROOM_WIDTH)] for _ in range(helpers.ROOM_HEIGHT)]

            for w in room.walls:
                char = ''
                if w.path == 'wall':
                    char = 'W'
                elif w.path == 'ground':
                    char = 'G'
                elif w.path == 'rock':
                    char = 'R'
                elif w.path == 'metal':
                    char = 'M'
                elif w.path == 'ice':
                    char = 'I'
                tilemap[w.y // helpers.TILE_SIZE][w.x // helpers.TILE_SIZE] = char
            for l in room.ladders:
                tilemap[l.y // helpers.TILE_SIZE][l.x // helpers.TILE_SIZE] = '#'
            for s in room.spikes:
                tilemap[s.y // helpers.TILE_SIZE][s.x // helpers.TILE_SIZE] = '*'
            for e in room.enemies:
                y = e.y // helpers.TILE_SIZE
                char = ''
                if type(e) is enemy.Crawler:
                    char = 'c'
                elif type(e) is enemy.Flyer:
                    char = 'f'
                elif type(e) is enemy.Zombie:
                    char = 'z'
                elif type(e) is enemy.Spawner:
                    char = 's'
                elif type(e) is enemy.Charger:
                    char = 'h'
                tilemap[y][e.x // helpers.TILE_SIZE] = char
            for c in room.checkpoints:
                tilemap[c.y // helpers.TILE_SIZE][c.x // helpers.TILE_SIZE] = 'C'
            for p in room.powerups:
                char = ''
                if p.ability == powerup.Ability.run:
                    char = '0'
                elif p.ability == powerup.Ability.double_jump:
                    char = '1'
                elif p.ability == powerup.Ability.wall_jump:
                    char = '2'
                elif p.ability == powerup.Ability.gun:
                    char = '3'
                elif p.ability == powerup.Ability.rebreather:
                    char = '4'
                elif p.ability == powerup.Ability.full_auto:
                    char = '5'
                elif p.ability == powerup.Ability.spread:
                    char = '6'
                elif p.ability == powerup.Ability.gravity:
                    char = '7'
                tilemap[p.y // helpers.TILE_SIZE][p.x // helpers.TILE_SIZE] = char
            for w in room.water:
                if w.surface:
                    tilemap[w.y // helpers.TILE_SIZE][w.x // helpers.TILE_SIZE] = '~'
                else:
                    tilemap[w.y // helpers.TILE_SIZE][w.x // helpers.TILE_SIZE] = '='
            for d in room.dynamic_objects:
                if type(d) is tile.Destroyable:
                    tilemap[d.y // helpers.TILE_SIZE][d.x // helpers.TILE_SIZE] = 'D'
                elif type(d) is platform.Platform:
                    if d.vertical:
                        tilemap[d.y // helpers.TILE_SIZE][d.x // helpers.TILE_SIZE] = 'V'
                    else:
                        tilemap[d.y // helpers.TILE_SIZE][d.x // helpers.TILE_SIZE] = 'P'
                elif type(d) is platform.FallingPlatform:
                    tilemap[d.y // helpers.TILE_SIZE][d.x // helpers.TILE_SIZE] = 'F'

            empty = True
            for row in tilemap:
                for char in row:
                    if char != '-':
                        empty = False
                        break

            if not empty:
                print('(' + str(room.x) + ', ' + str(room.y) + ')', file=f)
                for row in tilemap:
                    print(''.join(row), file=f)
                print('', file=f)

        f.close()

    def update(self, input_hand):
        try:
            room = self.room(self.player.room_x, self.player.room_y)
        except KeyError:
            room = Room(self, [], self.player.room_x, self.player.room_y)
            self.rooms[(self.player.room_x, self.player.room_y)] = room

        self.player.input(input_hand, room)

        room.update()
        self.player.update(room)

    def draw(self, screen, img_hand):
        room = self.room(self.player.room_x, self.player.room_y)
        room.draw(screen, img_hand)
        self.player.draw(screen, img_hand)

    def debug_draw(self, screen):
        room = self.room(self.player.room_x, self.player.room_y)
        room.debug_draw(screen)
        self.player.debug_draw(screen)


class Room:
    def __init__(self, level, tilemap, x, y):
        self.level = level

        self.bg = 'sky'
        self.bg_sprite = animatedsprite.AnimatedSprite('bg')
        self.bg_sprite.play(self.bg)

        self.walls = list()
        self.ladders = list()
        self.spikes = list()
        self.enemies = list()
        self.checkpoints = list()
        self.powerups = list()
        self.water = list()
        self.dynamic_objects = list()
        self.x = x
        self.y = y
        self.player_x = 0
        self.player_y = 0
        self.read_tilemap(tilemap)
        self.update_visuals()

    def read_tilemap(self, tilemap):
        for j in range(len(tilemap)):
            row = tilemap[j]
            for i in range(len(row)):
                char = row[i]
                x = i * helpers.TILE_SIZE
                y = j * helpers.TILE_SIZE

                self.add_object(x, y, char)

                if char == 'C':
                    if self.x == 0 and self.y == 0:
                        self.player_x = x
                        self.player_y = y

    def update(self):
        for e in self.enemies:
            e.update(self)
        for c in self.checkpoints:
            c.update(self)
        for p in self.powerups:
            p.update(self)
        for d in self.dynamic_objects:
            d.update(self)
        for w in self.water:
            w.update(self)

    def update_visuals(self):
        for w in self.walls:
            w.update(self)
        for s in self.spikes:
            s.update(self)
        for l in self.ladders:
            l.update(self)

    def reset(self):
        for e in self.enemies:
            e.reset()
        for d in self.dynamic_objects:
            d.reset()

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)

        for c in self.checkpoints:
            c.draw(screen, img_hand)
        for w in self.walls:
            w.draw(screen, img_hand)
        for l in self.ladders:
            l.draw(screen, img_hand)
        for s in self.spikes:
            s.draw(screen, img_hand)
        for e in self.enemies:
            e.draw(screen, img_hand)
        for p in self.powerups:
            p.draw(screen, img_hand)
        for w in self.water:
            w.draw(screen, img_hand)
        for d in self.dynamic_objects:
            d.draw(screen, img_hand)

    def debug_draw(self, screen):
        for c in self.checkpoints:
            c.debug_draw(screen)
        for w in self.walls:
            w.debug_draw(screen)
        for l in self.ladders:
            l.debug_draw(screen)
        for s in self.spikes:
            s.debug_draw(screen)
        for e in self.enemies:
            e.debug_draw(screen)
        for p in self.powerups:
            p.debug_draw(screen)
        for w in self.water:
            w.debug_draw(screen)
        for d in self.dynamic_objects:
            d.debug_draw(screen)

    def add_object(self, x, y, char):
        if char == 'W':
            self.walls.append(tile.Wall(x, y, 'wall'))
        elif char == 'G':
            self.walls.append(tile.Wall(x, y, 'ground'))
        elif char == 'R':
            self.walls.append(tile.Wall(x, y, 'rock'))
        elif char == 'M':
            self.walls.append(tile.Wall(x, y, 'metal'))
        elif char == 'I':
            self.walls.append(tile.Wall(x, y, 'ice'))
        elif char == 'P':
            self.dynamic_objects.append(platform.Platform(x, y))
        elif char == 'V':
            self.dynamic_objects.append(platform.Platform(x, y, True))
        elif char == 'F':
            self.dynamic_objects.append(platform.FallingPlatform(x, y))
        elif char == '#':
            self.ladders.append(tile.Ladder(x, y))
        elif char == '~':
            self.water.append(tile.Water(x, y, True))
        elif char == '=':
            self.water.append(tile.Water(x, y, False))
        elif char == 'C':
            self.checkpoints.append(tile.Checkpoint(x, y))
        elif char == '*':
            self.spikes.append(tile.Spike(x, y, 0))
        elif char == 'D':
            self.dynamic_objects.append(tile.Destroyable(x, y))
        elif char == 'c':
            self.enemies.append(enemy.Crawler(x, y))
        elif char == 'z':
            self.enemies.append(enemy.Zombie(x, y))
        elif char == 'f':
            self.enemies.append(enemy.Flyer(x, y))
        elif char == 's':
            self.enemies.append(enemy.Spawner(x, y))
        elif char == 'h':
            self.enemies.append(enemy.Charger(x, y))
        elif char == '0':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.run))
        elif char == '1':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.double_jump))
        elif char == '2':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.wall_jump))
        elif char == '3':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.gun))
        elif char == '4':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.rebreather))
        elif char == '5':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.full_auto))
        elif char == '6':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.spread))
        elif char == '7':
            self.powerups.append(powerup.Powerup(x, y, player_old.Ability.gravity))

    def remove_object(self, x, y):
        collider = pygame.Rect(x, y, helpers.TILE_SIZE, helpers.TILE_SIZE)

        self.walls[:] = [w for w in self.walls if not collider.colliderect(w.collider)]
        self.ladders[:] = [x for x in self.ladders if not collider.colliderect(x.collider)]
        self.spikes[:] = [x for x in self.spikes if not collider.colliderect(x.collider)]
        self.enemies[:] = [x for x in self.enemies if not collider.colliderect(x.collider)]
        self.checkpoints[:] = [x for x in self.checkpoints if not collider.colliderect(x.collider)]
        self.powerups[:] = [x for x in self.powerups if not collider.colliderect(x.collider)]
        self.water[:] = [x for x in self.water if not collider.colliderect(x.collider)]
        self.dynamic_objects[:] = [x for x in self.dynamic_objects if not collider.colliderect(x.collider)]

    def clear(self):
        self.walls.clear()
        self.ladders.clear()
        self.spikes.clear()
        self.spikes.clear()
        self.enemies.clear()
        self.checkpoints.clear()
        self.powerups.clear()
        self.water.clear()
        self.dynamic_objects.clear()
