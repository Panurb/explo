import pygame
import gameloop
import helpers
import imagehandler
import inputhandler


class Main:
    def __init__(self, width, height):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((width, height))
        self.img_hand = imagehandler.ImageHandler()
        self.input_hand = inputhandler.InputHandler()
        self.loop = gameloop.GameLoop(self.screen, self.img_hand, self.input_hand)
        self.clock = pygame.time.Clock()
        self.fps = 60

        pygame.mixer.music.load('data/music/gaym.wav')
        #pygame.mixer.music.play(-1)

    def main_loop(self):
        while self.loop.state != gameloop.State.quit:
            self.loop.update(self.clock)
            self.clock.tick(self.fps)

if __name__ == '__main__':
    main_window = Main(helpers.SCREEN_WIDTH, helpers.SCREEN_HEIGHT)
    main_window.main_loop()