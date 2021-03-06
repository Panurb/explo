import pygame
import gameloop
import helpers
import imagehandler
import inputhandler
import soundhandler


class Main:
    def __init__(self, width, height):
        # init mixer first to prevent audio delay
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        pygame.init()
        pygame.display.set_caption('EXPLO')

        self.info = pygame.display.Info()
        self.screen = pygame.display.set_mode((width, height))
        self.img_hand = imagehandler.ImageHandler(self.info)
        self.snd_hand = soundhandler.SoundHandler()
        self.inp_hand = inputhandler.InputHandler()
        self.loop = gameloop.GameLoop(self.screen, self.img_hand, self.snd_hand,
                                      self.inp_hand)
        self.clock = pygame.time.Clock()
        self.fps = helpers.FPS

        pygame.display.set_icon(self.img_hand.animations['icon']['idle'][0])

        self.snd_hand.set_music('menu')
        pygame.mixer.music.set_volume(1)
        self.snd_hand.set_volume(1)

    def main_loop(self):
        while self.loop.state != gameloop.State.quit:
            self.loop.update(self.clock)
            self.clock.tick(self.fps)


def main():
    main_window = Main(helpers.SCREEN_WIDTH, helpers.SCREEN_HEIGHT)
    main_window.main_loop()


if __name__ == '__main__':
    main()
