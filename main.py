import pygame
import gameloop
import helpers
import imagehandler
import inputhandler


class Main:
    def __init__(self, width=160, height=120):
        pygame.init()
        size = (width, height)
        self.screen = pygame.display.set_mode(size)
        self.img_hand = imagehandler.ImageHandler()
        self.input_hand = inputhandler.InputHandler()
        self.loop = gameloop.GameLoop(self.screen, self.img_hand, self.input_hand)
        self.clock = pygame.time.Clock()
        self.fps = 60

    def main_loop(self):
        while self.loop.state != gameloop.State.quit:
            self.loop.update(self.clock)
            self.clock.tick(self.fps)

if __name__ == '__main__':
    main_window = Main(160 * helpers.SCALE, 120 * helpers.SCALE)
    main_window.main_loop()