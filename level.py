import pygame
import animatedsprite
import enemy
import helpers
import player
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
                self.rooms[coordinates] = Room(room, coordinates[0], coordinates[1])
                room = []
                continue

            room.append(list(line))

    def room(self, x, y):
        return self.rooms[(x, y)]

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
                tilemap[w.rect.y // helpers.TILE_SIZE][w.rect.x // helpers.TILE_SIZE] = char
            for l in room.ladders:
                tilemap[l.rect.y // helpers.TILE_SIZE][l.rect.x // helpers.TILE_SIZE] = '#'
            for s in room.spikes:
                tilemap[s.rect.y // helpers.TILE_SIZE][s.rect.x // helpers.TILE_SIZE] = '*'
            for e in room.enemies:
                y = e.rect.y // helpers.TILE_SIZE
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
                tilemap[y][e.rect.x // helpers.TILE_SIZE] = char
            for c in room.checkpoints:
                tilemap[c.rect.y // helpers.TILE_SIZE][c.rect.x // helpers.TILE_SIZE] = 'C'
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
                tilemap[p.rect.y // helpers.TILE_SIZE][p.rect.x // helpers.TILE_SIZE] = char
            for w in room.water:
                if w.surface:
                    tilemap[w.rect.y // helpers.TILE_SIZE][w.rect.x // helpers.TILE_SIZE] = '~'
                else:
                    tilemap[w.rect.y // helpers.TILE_SIZE][w.rect.x // helpers.TILE_SIZE] = '='
            for d in room.destroyables:
                tilemap[d.rect.y // helpers.TILE_SIZE][d.rect.x // helpers.TILE_SIZE] = 'D'

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


class Room:
    def __init__(self, tilemap, x, y):
        self.bg = 'sky'
        self.bg_sprite = animatedsprite.AnimatedSprite('bg')
        self.bg_sprite.play(self.bg)

        self.walls = animatedsprite.Group()
        self.ladders = animatedsprite.Group()
        self.spikes = animatedsprite.Group()
        self.enemies = animatedsprite.Group()
        self.checkpoints = animatedsprite.Group()
        self.powerups = animatedsprite.Group()
        self.water = animatedsprite.Group()
        self.destroyables = animatedsprite.Group()
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
        self.enemies.update(self)
        self.checkpoints.update(self)
        self.powerups.update(self)
        self.destroyables.update(self)

        self.water.animate()
        self.powerups.animate()

    def update_visuals(self):
        self.walls.update(self)
        self.spikes.update(self)
        self.ladders.update(self)

    def reset(self):
        self.enemies.reset()
        self.destroyables.reset()

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)

        self.checkpoints.draw(screen, img_hand)
        self.walls.draw(screen, img_hand)
        self.ladders.draw(screen, img_hand)
        self.spikes.draw(screen, img_hand)
        self.enemies.draw(screen, img_hand)
        self.powerups.draw(screen, img_hand)
        self.water.draw(screen, img_hand)
        self.destroyables.draw(screen, img_hand)

    def add_object(self, x, y, char):
        if char == 'W':
            self.walls.add(tile.Wall(x, y, 'wall'))
        elif char == 'G':
            self.walls.add(tile.Wall(x, y, 'ground'))
        elif char == 'R':
            self.walls.add(tile.Wall(x, y, 'rock'))
        elif char == 'M':
            self.walls.add(tile.Wall(x, y, 'metal'))
        elif char == 'I':
            self.walls.add(tile.Wall(x, y, 'ice'))
        elif char == '#':
            self.ladders.add(tile.Ladder(x, y))
        elif char == '~':
            self.water.add(tile.Water(x, y, True))
        elif char == '=':
            self.water.add(tile.Water(x, y, False))
        elif char == 'C':
            self.checkpoints.add(tile.Checkpoint(x, y))
        elif char == '*':
            self.spikes.add(tile.Spike(x, y, 0))
        elif char == 'D':
            self.destroyables.add(tile.Destroyable(x, y))
        elif char == 'c':
            self.enemies.add(enemy.Crawler(x, y))
        elif char == 'z':
            self.enemies.add(enemy.Zombie(x, y))
        elif char == 'f':
            self.enemies.add(enemy.Flyer(x, y))
        elif char == 's':
            self.enemies.add(enemy.Spawner(x, y))
        elif char == 'h':
            self.enemies.add(enemy.Charger(x, y))
        elif char == '0':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.run))
        elif char == '1':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.double_jump))
        elif char == '2':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.wall_jump))
        elif char == '3':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.gun))
        elif char == '4':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.rebreather))
        elif char == '5':
            self.powerups.add(powerup.Powerup(x, y, player.Ability.full_auto))

    def remove_object(self, x, y):
        collider = pygame.sprite.Sprite()
        collider.rect = pygame.Rect(x, y, helpers.TILE_SIZE, helpers.TILE_SIZE)

        pygame.sprite.spritecollide(collider, self.walls, True)
        pygame.sprite.spritecollide(collider, self.ladders, True)
        pygame.sprite.spritecollide(collider, self.spikes, True)
        pygame.sprite.spritecollide(collider, self.enemies, True)
        pygame.sprite.spritecollide(collider, self.checkpoints, True)
        pygame.sprite.spritecollide(collider, self.powerups, True)
        pygame.sprite.spritecollide(collider, self.water, True)
        pygame.sprite.spritecollide(collider, self.destroyables, True)

    def clear(self):
        self.walls.empty()
        self.ladders.empty()
        self.spikes.empty()
        self.spikes.empty()
        self.enemies.empty()
        self.checkpoints.empty()
        self.powerups.empty()
        self.water.empty()
        self.destroyables.empty()
