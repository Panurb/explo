import pygame
import helpers
import textbox

OBJECTS = (('W', 'WALL'),
           ('G', 'GROUND'),
           ('R', 'ROCK'),
           ('M', 'METAL'),
           ('I', 'ICE'),
           ('P', 'PLATFORM'),
           ('V', 'VERTICAL PLATFORM'),
           ('F', 'FALLING PLATFORM'),
           ('D', 'DESTROYABLE'),
           ('#', 'LADDER'),
           ('~', 'SURFACE'),
           ('=', 'WATER'),
           ('C', 'CHECKPOINT'),
           ('E', 'END'),
           ('*', 'THORNS'),
           ('Z', 'SPRING'),
           ('N', 'CANNON'),
           ('c', 'CRAWLER'),
           ('z', 'ZOMBIE'),
           ('s', 'SPWANER'),
           ('f', 'FLYER'),
           ('h', 'CHARGER'),
           ('d', 'DROPPER'),
           ('0', 'RUN'),
           ('1', 'DOUBLE JUMP'),
           ('2', 'WALL JUMP'),
           ('3', 'GUN'),
           ('4', 'REBREATHER'),
           ('5', 'FULL AUTO'),
           ('6', 'SPREAD'),
           ('7', 'GRAVITY'))


class Editor:
    def __init__(self, x, y):
        self.room_x = x
        self.room_y = y
        self.object = 0
        self.text = textbox.Textbox(OBJECTS[self.object][1],
                                    0.5 * helpers.SCREEN_WIDTH, 0)

    def input(self, lvl, input_hand):
        room = lvl.room(self.room_x, self.room_y)
        if input_hand.mouse_down[0]:
            x, y = helpers.mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            # TODO: Remove objects according to object size
            room.remove_object(x, y)
            char = OBJECTS[self.object][0]

            room.add_object(x, y, char)
            room.update_visuals()

        if input_hand.mouse_down[2]:
            x, y = helpers.mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            room.remove_object(x, y)
            room.update_visuals()

        if input_hand.mouse_pressed[4] or input_hand.keys_pressed[
                pygame.K_COMMA]:
            if self.object > 0:
                self.object -= 1
            else:
                self.object = len(OBJECTS) - 1

        if input_hand.mouse_pressed[5] or input_hand.keys_pressed[
                pygame.K_PERIOD]:
            if self.object < len(OBJECTS) - 1:
                self.object += 1
            else:
                self.object = 0

        self.text.set_string(OBJECTS[self.object][1])

        if input_hand.keys_pressed[pygame.K_UP]:
            self.room_y -= 1
        if input_hand.keys_pressed[pygame.K_DOWN]:
            self.room_y += 1
        if input_hand.keys_pressed[pygame.K_RIGHT]:
            self.room_x += 1
        if input_hand.keys_pressed[pygame.K_LEFT]:
            self.room_x -= 1
        if input_hand.keys_down[pygame.K_c]:
            room.clear()
        if input_hand.keys_down[pygame.K_s]:
            lvl.write()

    def draw(self, screen, img_hand):
        self.text.draw(screen, img_hand)
