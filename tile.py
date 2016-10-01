import gameobject
import helpers


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

        x = int(self.x / helpers.TILE_SIZE)
        y = int(self.y / helpers.TILE_SIZE)

        try:
            if room.walls[y - 1][x].path == self.path:
                up = 1
        except (IndexError, AttributeError):
            pass

        try:
            if room.walls[y + 1][x].path == self.path:
                down = 1
        except (IndexError, AttributeError):
            pass

        try:
            if room.walls[y][x + 1].path == self.path:
                right = 1
        except (IndexError, AttributeError):
            pass

        try:
            if room.walls[y][x - 1].path == self.path:
                left = 1
        except (IndexError, AttributeError):
            pass

        if self.y - helpers.TILE_SIZE < 0:
            up = 1
        elif self.y + helpers.TILE_SIZE >= helpers.SCREEN_HEIGHT:
            down = 1

        if self.x + helpers.TILE_SIZE >= helpers.SCREEN_WIDTH:
            right = 1
        elif self.x - helpers.TILE_SIZE < 0:
            left = 1

        self.index = int(str(up) + str(right) + str(down) + str(left), 2)
        for s in self.sprites:
            s.show_frame('idle', self.index)


class Ladder(gameobject.GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, helpers.TILE_SIZE, helpers.TILE_SIZE,
                         ['ladder'])
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
        super().__init__(x, y, 'thorns')
        self.collider.x = x + helpers.SCALE
        self.collider.y = y + helpers.SCALE
        self.collider.width = 6 * helpers.SCALE
        self.collider.height = 6 * helpers.SCALE
        for s in self.sprites:
            s.show_frame('idle', index)
        self.path = 'spike'


class Checkpoint(gameobject.GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, helpers.TILE_SIZE, 2 * helpers.TILE_SIZE,
                         ['checkpoint'])
        for s in self.sprites:
            s.show_frame('idle', 0)

        self.active = False


class Water(gameobject.GameObject):
    def __init__(self, x, y, surface):
        super().__init__(x, y, helpers.TILE_SIZE, helpers.TILE_SIZE, ['water'])
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
        super().__init__(x, y, 'destroyable')
        self.destroyed = False
        self.debris = []

    def update(self, room):
        if not self.destroyed:
            for s in self.sprites:
                s.play('idle')
        else:
            for s in self.sprites:
                s.play('explode')
            for d in self.debris:
                d.update(room)

    def animate(self):
        for s in self.sprites:
            if not self.destroyed:
                s.play('idle')
            else:
                s.play('explode')

    def destroy(self):
        self.add_debris(5, 5)
        self.add_debris(5, -5)
        self.add_debris(-5, 5)
        self.add_debris(-5, -5)

        self.destroyed = True

    def add_debris(self, dx, dy):
        debris = gameobject.Debris(self.x, self.y, dx, dy, 'idle',
                                   'destroyable_debris')
        self.debris.append(debris)

    def reset(self):
        self.destroyed = False
        self.debris.clear()

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        for d in self.debris:
            d.draw(screen, img_hand)


class Spring(Wall):
    def __init__(self, x, y):
        super().__init__(x, y, 'spring')
        for s in self.sprites:
            s.offset_y = -8 * helpers.SCALE
        self.group = gameobject.CollisionGroup.springs
        self.bounce_scale = 1

    def update(self, room):
        self.animate()

    def bounce(self):
        for s in self.sprites:
            s.frame = 0
            s.play_once('bounce')

    def reset(self):
        pass
