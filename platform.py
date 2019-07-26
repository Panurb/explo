import gameobject
import helpers
import collision


class Platform(gameobject.PhysicsObject):
    def __init__(self, x, y, vertical=False):
        super().__init__(x, y, 3 * helpers.TILE_SIZE, helpers.TILE_SIZE, 0, 0,
                         ['platform'], gameobject.CollisionGroup.walls)
        self.gravity_scale = 0
        self.vertical = vertical
        self.friction = 0.125 * helpers.SCALE
        self.slide_speed = 0.25 * helpers.SCALE
        if self.vertical:
            self.dy = 0.5 * helpers.SCALE
        else:
            self.dx = 0.5 * helpers.SCALE
        self.spawn_x = x
        self.spawn_y = y
        self.destroyed = False

    def move_x(self, room):
        super().move_x(room)
        player = room.level.player
        if self.collider.colliderect(player.collider):
            if self.dx > 0:
                player.dx = max(0, player.dx)
            elif self.dx < 0:
                player.dx = min(0, player.dx)
            player.base_dx = self.dx

    def move_y(self, room):
        super().move_y(room)
        player = room.level.player
        if self.collider.colliderect(player.collider):
            player.base_dy = self.dy

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        if self.vertical:
            self.dy = 0.5 * helpers.SCALE
        else:
            self.dx = 0.5 * helpers.SCALE


class FallingPlatform(gameobject.PhysicsObject):
    def __init__(self, x, y):
        super().__init__(x, y, 3 * helpers.TILE_SIZE, helpers.TILE_SIZE, 0, 0,
                         ['platform'])
        self.gravity_scale = 0
        self.bounce_scale = 0
        self.friction = 0.125 * helpers.SCALE
        self.slide_speed = 0.25 * helpers.SCALE
        self.spawn_y = y
        self.speed = 2 * helpers.SCALE
        self.timer = 0
        self.delay = 30

    def update(self, room):
        super().update(room)
        for c in room.level.player.collisions:
            if c.obj is self and c.direction is collision.Direction.down:
                self.dy = self.speed
                # For smooth elevator rides
                room.level.player.base_dy = self.dy
                self.timer = self.delay
                break

        for c in self.collisions:
            if c.direction is collision.Direction.down:
                self.timer = self.delay
                break

        if self.timer == 0:
            self.dy = -self.speed
        else:
            self.timer -= 1

        if self.dy < 0:
            if self.y < self.spawn_y:
                self.dy = 0
                self.y = self.spawn_y
                self.collider.y = self.y

    def reset(self):
        self.y = self.spawn_y
        self.dy = 0
        self.gravity_scale = 0