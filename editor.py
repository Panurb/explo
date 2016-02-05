import pygame
import helpers
import textbox

OBJECTS = ['W', 'G', 'R', 'M', 'I', 'P', 'V', 'D', '#', '~', '=', 'C', '*', 'c', 'z', 's', 'f', 'h', '0', '1', '2', '3',
           '4', '5', '6', '7']
OBJECT_NAMES = ['WALL', 'GROUND', 'ROCK', 'METAL', 'ICE', 'PLATFORM', 'VERTICAL PLATFORM', 'DESTROYABLE', 'LADDER',
                'SURFACE', 'WATER', 'CHECKPOINT', 'THORNS', 'CRAWLER', 'ZOMBIE', 'SPAWNER', 'FLYER', 'CHARGER', 'RUN',
                'DOUBLE JUMP', 'WALL JUMP', 'GUN', 'REBREATHER', 'FULL AUTO', 'SPREAD', 'GRAVITY']


class Editor:
    def __init__(self, x, y):
        self.room_x = x
        self.room_y = y
        self.object = 0
        self.text = textbox.Textbox(OBJECT_NAMES[self.object], 0.5 * helpers.SCREEN_WIDTH, 0)

    def input(self, lvl, input_hand):
        room = lvl.room(self.room_x, self.room_y)
        if input_hand.mouse_down[0]:
            x, y = mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            # TODO: Remove objects according to object size
            room.remove_object(x, y)
            char = OBJECTS[self.object]

            room.add_object(x, y, char)
            room.update_visuals()

        if input_hand.mouse_down[2]:
            x, y = mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            room.remove_object(x, y)
            room.update_visuals()

        if input_hand.mouse_pressed[4] or input_hand.keys_pressed[pygame.K_COMMA]:
            if self.object > 0:
                self.object -= 1
            else:
                self.object = len(OBJECTS) - 1

        if input_hand.mouse_pressed[5] or input_hand.keys_pressed[pygame.K_PERIOD]:
            if self.object < len(OBJECTS) - 1:
                self.object += 1
            else:
                self.object = 0

        self.text.set_string(OBJECT_NAMES[self.object])

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


def mouse_to_grid(mouse_x, mouse_y):
    x = mouse_x - mouse_x % helpers.TILE_SIZE
    y = mouse_y - mouse_y % helpers.TILE_SIZE

    return x, y
