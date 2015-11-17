import pygame
import animatedsprite
import enemy
import helpers
import physicsobject
import powerup


class Level:
    def __init__(self):
        path = 'data/lvl/level.txt'
        with open(path) as f:
            lines = f.readlines()

        self.rooms = {}
        room = []
        coordinates = ()
        bg = ''
        for line in lines:
            line = line.rstrip('\n')

            if line.find('(') == 0:
                line = line.replace('(', '').replace(')', '').split(',')
                coordinates = (int(line[0]), int(line[1]))
                try:
                    bg = line[2].replace(' ', '')
                except IndexError:
                    bg = 'sky'
                continue

            if not line.rstrip():
                self.rooms[coordinates] = Room(room, coordinates[0], coordinates[1], bg)
                room = []
                coordinates = ()
                continue

            room.append(list(line))

    def room(self, x, y):
        return self.rooms[(x, y)]

    def write(self):
        f = open('data/lvl/level.txt', 'w')

        for key in self.rooms:
            room = self.rooms[key]
            room.reset()
            tilemap = [['-' for _ in range(20)] for _ in range(15)]

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
                tilemap[w.rect.y // helpers.TILE_SIZE][w.rect.x // helpers.TILE_SIZE] = char
            for l in room.ladders:
                tilemap[l.rect.y // helpers.TILE_SIZE][l.rect.x // helpers.TILE_SIZE] = '#'
            for s in room.spikes:
                tilemap[s.rect.y // helpers.TILE_SIZE][s.rect.x // helpers.TILE_SIZE] = '*'
            for e in room.enemies:
                char = ''
                if type(e) is enemy.Crawler:
                    char = 'c'
                elif type(e) is enemy.Flyer:
                    char = 'f'
                elif type(e) is enemy.Zombie:
                    char = 'z'
                tilemap[e.rect.y // helpers.TILE_SIZE][e.rect.x // helpers.TILE_SIZE] = char
            for c in room.checkpoints:
                tilemap[c.rect.y // helpers.TILE_SIZE][c.rect.x // helpers.TILE_SIZE] = 'C'
            for p in room.powerups:
                char = ''
                if p.ability == 'run':
                    char = '0'
                elif p.ability == 'double jump':
                    char = '1'
                elif p.ability == 'wall jump':
                    char = '2'
                elif p.ability == 'sword':
                    char = '3'
                elif p.ability == 'gun':
                    char = '4'
                elif p.ability == 'rebreather':
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
                print('(' + str(room.x) + ', ' + str(room.y) + ', ' + room.bg + ')', file=f)
                for row in tilemap:
                    print(''.join(row), file=f)
                print('', file=f)

        f.close()


class Room:
    def __init__(self, tilemap, x, y, bg):
        self.bg = bg
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
                        self.player_y = y - helpers.TILE_SIZE

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
        self.powerups.reset()
        self.destroyables.reset()

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)

        self.walls.draw(screen, img_hand)
        self.ladders.draw(screen, img_hand)
        self.spikes.draw(screen, img_hand)
        self.enemies.draw(screen, img_hand)
        self.checkpoints.draw(screen, img_hand)
        self.powerups.draw(screen, img_hand)
        self.water.draw(screen, img_hand)
        self.destroyables.draw(screen, img_hand)

    def add_object(self, x, y, char):
        if char == 'W':
            self.walls.add(Wall(x, y, 'wall'))
        elif char == 'G':
            self.walls.add(Wall(x, y, 'ground'))
        elif char == 'R':
            self.walls.add(Wall(x, y, 'rock'))
        elif char == 'M':
            self.walls.add(Wall(x, y, 'metal'))
        elif char == '#':
            self.ladders.add(Ladder(x, y))
        elif char == '~':
            self.water.add(Water(x, y, True))
        elif char == '=':
            self.water.add(Water(x, y, False))
        elif char == 'C':
            self.checkpoints.add(Checkpoint(x, y))
        elif char == '*':
            self.spikes.add(Spike(x, y, 0))
        elif char == 'c':
            self.enemies.add(enemy.Crawler(x, y))
        elif char == 'z':
            self.enemies.add(enemy.Zombie(x, y))
        elif char == 'f':
            self.enemies.add(enemy.Flyer(x, y))
        elif char == '0':
            self.powerups.add(powerup.Powerup(x, y, 'run'))
        elif char == '1':
            self.powerups.add(powerup.Powerup(x, y, 'double jump'))
        elif char == '2':
            self.powerups.add(powerup.Powerup(x, y, 'wall jump'))
        elif char == '3':
            self.powerups.add(powerup.Powerup(x, y, 'sword'))
        elif char == '4':
            self.powerups.add(powerup.Powerup(x, y, 'gun'))
        elif char == '5':
            self.powerups.add(powerup.Powerup(x, y, 'rebreather'))
        elif char == 'D':
            self.destroyables.add(Destroyable(x, y))

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


class Tile(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, path):
        animatedsprite.AnimatedSprite.__init__(self, path)

        self.rect.x = x
        self.rect.y = y


class Wall(Tile):
    def __init__(self, x, y, path):
        Tile.__init__(self, x, y, path)
        self.index = 0
        self.show_frame('idle', self.index)
        self.path = path
        self.destroyed = False

    def update(self, room):
        up = right = down = left = '0'
        for w in room.walls:
            if self.path != 'spike':
                if w.path != self.path:
                    continue

            if w.rect.x == self.rect.x:
                if w.rect.y == self.rect.y - helpers.TILE_SIZE:
                    up = '1'
                if w.rect.y == self.rect.y + helpers.TILE_SIZE:
                    down = '1'

            if w.rect.y == self.rect.y:
                if w.rect.x == self.rect.x + helpers.TILE_SIZE:
                    right = '1'
                if w.rect.x == self.rect.x - helpers.TILE_SIZE:
                    left = '1'

        if self.rect.y - helpers.TILE_SIZE < 0:
            up = '1'
        if self.rect.x + helpers.TILE_SIZE >= helpers.WIDTH:
            right = '1'
        if self.rect.y + helpers.TILE_SIZE >= helpers.HEIGHT:
            down = '1'
        if self.rect.x - helpers.TILE_SIZE < 0:
            left = '1'

        self.index = int(up + right + down + left, 2)
        self.show_frame('idle', self.index)


class Ladder(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'ladder')
        self.top = True
        self.destroyed = False

    def update(self, room):
        self.top = True
        if self.rect.y > 0:
            for l in room.ladders:
                if l.rect.x == self.rect.x and l.rect.y == self.rect.y - helpers.TILE_SIZE:
                    self.top = False
                    break


class Spike(Wall):
    def __init__(self, x, y, index):
        Tile.__init__(self, x, y, 'thorns')
        self.show_frame('idle', index)
        self.path = 'spike'


class Checkpoint(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'checkpoint')
        self.show_frame('idle', 0)

        self.active = False

    def update(self, room):
        if self.active:
            self.show_frame('idle', 1)
        else:
            self.show_frame('idle', 0)


class Water(Tile):
    def __init__(self, x, y, surface):
        Tile.__init__(self, x, y, 'water')
        self.surface = surface

        if self.surface:
            self.play('surface')
        else:
            self.play('idle')


class Destroyable(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'destroyable')
        self.destroyed = False
        self.debris = animatedsprite.Group()

    def update(self, room):
        if not self.destroyed:
            self.play('idle')
        else:
            self.play('explode')
            self.debris.update(room)

    def destroy(self):
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, 5, 5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, 5, -5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, -5, 5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, -5, -5, 'idle', 'destroyable_debris'))
        self.destroyed = True

    def reset(self):
        self.destroyed = False
        self.debris.empty()

    def draw(self, screen, img_hand):
        Tile.draw(self, screen, img_hand)
        self.debris.draw(screen, img_hand)
