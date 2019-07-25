import pygame
import helpers
import textbox

WORLD_WIDTH = 18
WORLD_HEIGHT = 14
OBJECTS = {'WALLS': (('W', 'WALL'),
                     ('G', 'GROUND'),
                     ('R', 'ROCK'),
                     ('M', 'METAL'),
                     ('I', 'ICE')),
           'OBSTACLES': (('P', 'PLATFORM'),
                         ('V', 'VERTICAL PLATFORM'),
                         ('F', 'FALLING PLATFORM'),
                         ('D', 'DESTROYABLE'),
                         ('#', 'LADDER'),
                         ('Z', 'SPRING'),
                         ('B', 'BOSS WALL')),
           'HAZARDS': (('~', 'WATER SURFACE'),
                       ('=', 'WATER'),
                       ('-', 'LAVA SURFACE'),
                       ('_', 'LAVA'),
                       ('*', 'SPIKES'),
                       ('^', 'WATER SPIKES'),
                       ('N', 'CANNON')),
           'ENEMIES': (('c', 'CRAWLER'),
                       ('z', 'ZOMBIE'),
                       ('s', 'SPWANER'),
                       ('f', 'FLYER'),
                       ('h', 'CHARGER'),
                       ('d', 'DROPPER'),
                       ('b', 'BOSS')),
           'MISC': (('C', 'CHECKPOINT'),
                    ('E', 'END')),
           'POWERUPS': (('0', 'RUN'),
                        ('1', 'DOUBLE JUMP'),
                        ('2', 'WALL JUMP'),
                        ('3', 'GUN'),
                        ('4', 'REBREATHER'),
                        ('5', 'FULL AUTO'),
                        ('6', 'SPREAD'),
                        ('7', 'GRAVITY')),
           'MUSIC': (('m', 'TRACK 1'),
                     ('n', 'TRACK 2'))}


class Editor:
    def __init__(self, x, y):
        self.room_x = x
        self.room_y = y
        self.category = 'WALLS'
        self.object = 0
        self.category_text = textbox.Textbox(self.category,
                                             0.2 * helpers.SCREEN_WIDTH, 0)
        self.object_text = textbox.Textbox(OBJECTS[self.category][self.object][1],
                                           0.5 * helpers.SCREEN_WIDTH, 0)
        self.coord_text = textbox.Textbox('0 0',
                                          0.9 * helpers.SCREEN_WIDTH, 0)

    def change_category(self, category):
        self.category = category
        self.object = 0
        self.category_text.set_string(self.category)

    def input(self, lvl, input_hand):
        room = lvl.room(self.room_x, self.room_y)
        if input_hand.mouse_down[0]:
            x, y = helpers.mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            # TODO: Remove objects according to object size
            room.remove_object(x, y)
            char = OBJECTS[self.category][self.object][0]

            room.add_object(x, y, char)
            room.update_visuals()

        if input_hand.mouse_down[2]:
            x, y = helpers.mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            room.remove_object(x, y)
            room.update_visuals()

        if input_hand.keys_pressed[pygame.K_1]:
            self.change_category('WALLS')
        elif input_hand.keys_pressed[pygame.K_2]:
            self.change_category('OBSTACLES')
        elif input_hand.keys_pressed[pygame.K_3]:
            self.change_category('HAZARDS')
        elif input_hand.keys_pressed[pygame.K_4]:
            self.change_category('ENEMIES')
        elif input_hand.keys_pressed[pygame.K_5]:
            self.change_category('POWERUPS')
        elif input_hand.keys_pressed[pygame.K_6]:
            self.change_category('MISC')
        elif input_hand.keys_pressed[pygame.K_7]:
            self.change_category('MUSIC')

        if input_hand.mouse_pressed[4] or input_hand.keys_pressed[
                pygame.K_COMMA]:
            if self.object > 0:
                self.object -= 1
            else:
                self.object = len(OBJECTS[self.category]) - 1

        if input_hand.mouse_pressed[5] or input_hand.keys_pressed[
                pygame.K_PERIOD]:
            if self.object < len(OBJECTS[self.category]) - 1:
                self.object += 1
            else:
                self.object = 0

        self.object_text.set_string(OBJECTS[self.category][self.object][1])
        self.coord_text.set_string(str(self.room_x) + ' ' + str(self.room_y))

        if input_hand.keys_down[pygame.K_c]:
            room.clear()
        if input_hand.keys_down[pygame.K_s]:
            lvl.write()

        room.update_bg()

        if input_hand.keys_pressed[pygame.K_UP]:
            self.room_y = max(self.room_y - 1, -int(WORLD_HEIGHT / 2))
        if input_hand.keys_pressed[pygame.K_DOWN]:
            self.room_y = min(self.room_y + 1, int(WORLD_HEIGHT / 2))
        if input_hand.keys_pressed[pygame.K_RIGHT]:
            self.room_x = min(self.room_x + 1, int(WORLD_WIDTH / 2))
        if input_hand.keys_pressed[pygame.K_LEFT]:
            self.room_x = max(self.room_x - 1, -int(WORLD_WIDTH / 2))

    def setup_play(self, lvl):
        lvl.player.save.room_x = self.room_x
        lvl.player.save.room_y = self.room_y
        lvl.player.save.x = 0.5 * helpers.SCREEN_WIDTH
        lvl.player.save.y = 0.5 * helpers.SCREEN_HEIGHT
        room = lvl.room(self.room_x, self.room_y)
        for cp in room.checkpoints:
            cp.active = True
            lvl.player.save.x = cp.collider.x
            lvl.player.save.y = cp.collider.y

        room.reset()
        lvl.player.reset()

    def draw(self, screen, img_hand):
        self.category_text.draw(screen, img_hand)
        self.object_text.draw(screen, img_hand)
        self.coord_text.draw(screen, img_hand)

    def draw_grid(self, screen):
        color = (50, 50, 50)
        for i in range(helpers.ROOM_WIDTH):
            for j in range(helpers.ROOM_HEIGHT):
                start = (0, j * helpers.TILE_SIZE)
                end = (helpers.SCREEN_WIDTH, j * helpers.TILE_SIZE)
                pygame.draw.line(screen, color, start, end)
                start = (i * helpers.TILE_SIZE, 0)
                end = (i * helpers.TILE_SIZE, helpers.SCREEN_HEIGHT)
                pygame.draw.line(screen, color, start, end)
