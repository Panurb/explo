import pygame
import helpers
import level
import powerup
import textbox


OBJECTS = ['W', 'G', 'R', 'M', 'D', '#', '~', '=', 'C', '*', 'c', 'z', 'f', '0', '1', '2', '3', '4', '5']
OBJECT_NAMES = ['WALL', 'GROUND', 'ROCK', 'METAL', 'DESTROYABLE', 'LADDER', 'SURFACE', 'WATER', 'CHECKPOINT', 'THORNS',
                'CRAWLER', 'ZOMBIE', 'FLYER', 'RUN', 'DOUBLE JUMP', 'WALL JUMP', 'SWORD', 'GUN', 'REBREATHER']


class Editor:
    def __init__(self, x, y):
        self.room_x = x
        self.room_y = y
        self.object = 0

    def input(self, lvl, keys_pressed, keys_down, mouse_wheel, mouse_down, mouse_x, mouse_y):
        room = lvl.room(self.room_x, self.room_y)
        if mouse_down[0]:
            x, y = mouse_to_grid(mouse_x, mouse_y)

            room.remove_object(x, y)
            char = OBJECTS[self.object]

            room.add_object(x, y, char)
            room.update_visuals()

        if mouse_down[2]:
            x, y = mouse_to_grid(mouse_x, mouse_y)

            room.remove_object(x, y)
            room.update_visuals()

        if mouse_wheel[4]:
            if self.object > 0:
                self.object -= 1
            else:
                self.object = len(OBJECTS) - 1

        if mouse_wheel[5]:
            if self.object < len(OBJECTS) - 1:
                self.object += 1
            else:
                self.object = 0

        if keys_pressed[pygame.K_UP]:
            self.room_y -= 1
        if keys_pressed[pygame.K_DOWN]:
            self.room_y += 1
        if keys_pressed[pygame.K_RIGHT]:
            self.room_x += 1
        if keys_pressed[pygame.K_LEFT]:
            self.room_x -= 1
        if keys_down[pygame.K_c]:
            room.clear()
        if keys_down[pygame.K_s]:
            lvl.write()

    def draw(self, screen, img_hand):
        text = textbox.Textbox(OBJECT_NAMES[self.object])
        text.draw(screen, img_hand)


def mouse_to_grid(mouse_x, mouse_y):
    x = mouse_x - mouse_x % (8 * helpers.SCALE)
    y = mouse_y - mouse_y % (8 * helpers.SCALE)

    return x, y