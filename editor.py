import pygame
import helpers
import textbox


OBJECTS = ['W', 'G', 'R', 'M', 'D', '#', '~', '=', 'C', '*', 'c', 'z', 'f', '0', '1', '2', '3', '4', '5']
OBJECT_NAMES = ['WALL', 'GROUND', 'ROCK', 'METAL', 'DESTROYABLE', 'LADDER', 'SURFACE', 'WATER', 'CHECKPOINT', 'THORNS',
                'CRAWLER', 'ZOMBIE', 'FLYER', 'RUN', 'DOUBLE JUMP', 'WALL JUMP', 'SWORD', 'GUN', 'REBREATHER']


class Editor:
    def __init__(self, x, y):
        self.room_x = x
        self.room_y = y
        self.object = 0
        self.text = textbox.Textbox(OBJECT_NAMES[self.object])

    def input(self, lvl, input_hand):
        room = lvl.room(self.room_x, self.room_y)
        if input_hand.mouse_down[0]:
            x, y = mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            room.remove_object(x, y)
            char = OBJECTS[self.object]

            room.add_object(x, y, char)
            room.update_visuals()

        if input_hand.mouse_down[2]:
            x, y = mouse_to_grid(input_hand.mouse_x, input_hand.mouse_y)

            room.remove_object(x, y)
            room.update_visuals()

        if input_hand.mouse_wheel[4]:
            if self.object > 0:
                self.object -= 1
            else:
                self.object = len(OBJECTS) - 1

        if input_hand.mouse_wheel[5]:
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
    x = mouse_x - mouse_x % (8 * helpers.SCALE)
    y = mouse_y - mouse_y % (8 * helpers.SCALE)

    return x, y