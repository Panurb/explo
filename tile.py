import animatedsprite
import gameobject
import helpers
import physicsobject


class Wall(gameobject.GameObject):
    def __init__(self, x, y, path):
        super().__init__(x, y, helpers.TILE_SIZE, helpers.TILE_SIZE, [path],
                         gameobject.CollisionGroup.walls)
        self.index = 0
        for s in self.sprites:
            s.show_frame('idle', self.index)
        self.path = path
        self.destroyed = False
        self.friction = 0.125 * helpers.SCALE
        self.slide_speed = 0.25 * helpers.SCALE
        if self.path == 'ice':
            self.friction = 0.01 * helpers.SCALE
            self.slide_speed = helpers.TERMINAL_VELOCITY

    def update(self, room):
        up = right = down = left = 0
        for w in room.walls:
            if self.path != 'spike':
                if w.path != self.path:
                    continue

            if w.collider.x == self.collider.x:
                if w.collider.y == self.collider.y - helpers.TILE_SIZE:
                    up = 1
                if w.collider.y == self.collider.y + helpers.TILE_SIZE:
                    down = 1

            if w.collider.y == self.collider.y:
                if w.collider.x == self.collider.x + helpers.TILE_SIZE:
                    right = 1
                if w.collider.x == self.collider.x - helpers.TILE_SIZE:
                    left = 1

        if self.collider.y - helpers.TILE_SIZE < 0:
            up = 1
        elif self.collider.y + helpers.TILE_SIZE >= helpers.SCREEN_HEIGHT:
            down = 1

        if self.collider.x + helpers.TILE_SIZE >= helpers.SCREEN_WIDTH:
            right = 1
        elif self.collider.x - helpers.TILE_SIZE < 0:
            left = 1

        self.index = int(str(up) + str(right) + str(down) + str(left), 2)
        for s in self.sprites:
            s.show_frame('idle', self.index)


class Ladder(gameobject.GameObject):
    def __init__(self, x, y):
        gameobject.GameObject.__init__(self, x, y, helpers.TILE_SIZE,
                                       helpers.TILE_SIZE, ['ladder'])
        self.top = True
        self.destroyed = False

    def update(self, room):
        self.top = True
        if self.collider.y > 0:
            for l in room.ladders:
                if l.collider.x == self.collider.x and \
                        l.collider.y == self.collider.y - helpers.TILE_SIZE:
                    self.top = False
                    break


class Spike(Wall):
    def __init__(self, x, y, index):
        Wall.__init__(self, x, y, 'thorns')
        for s in self.sprites:
            s.show_frame('idle', index)
        self.path = 'spike'


class Checkpoint(gameobject.GameObject):
    def __init__(self, x, y):
        gameobject.GameObject.__init__(self, x, y, helpers.TILE_SIZE, 2 * helpers.TILE_SIZE, ['checkpoint'])
        for s in self.sprites:
            s.show_frame('idle', 0)

        self.active = False


class Water(gameobject.GameObject):
    def __init__(self, x, y, surface):
        gameobject.GameObject.__init__(self, x, y, helpers.TILE_SIZE,
                                       helpers.TILE_SIZE, ['water'])
        self.surface = surface

        if self.surface:
            for s in self.sprites:
                s.play('surface')
        else:
            for s in self.sprites:
                s.play('idle')

    def update(self, room):
        self.animate()


class Destroyable(Wall):
    def __init__(self, x, y):
        Wall.__init__(self, x, y, 'destroyable')
        self.destroyed = False
        self.debris = []

    def update(self, room):
        if not self.destroyed:
            self.play('idle')
        else:
            self.play('explode')
            self.debris.update(room)

    def animate(self):
        for s in self.sprites:
            if not self.destroyed:
                s.play('idle')
            else:
                s.play('explode')

    def destroy(self):
        self.debris.append(physicsobject.Debris(self.x, self.y, 5, 5, 'idle',
                                                'destroyable_debris'))
        self.debris.append(physicsobject.Debris(self.x, self.y, 5, -5, 'idle',
                                                'destroyable_debris'))
        self.debris.append(physicsobject.Debris(self.x, self.y, -5, 5, 'idle',
                                                'destroyable_debris'))
        self.debris.append(physicsobject.Debris(self.x, self.y, -5, -5, 'idle',
                                                'destroyable_debris'))
        self.destroyed = True

    def reset(self):
        self.destroyed = False
        self.debris.clear()

    def draw(self, screen, img_hand):
        Wall.draw(self, screen, img_hand)
        for d in self.debris:
            d.draw(screen, img_hand)
