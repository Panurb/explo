import pygame

import helpers


SOUNDS = ['bump', 'hit', 'jump', 'powerup', 'save', 'shoot', 'splash', 'spring', 'squish']
MUSIC = ['menu']


class SoundHandler:
    def __init__(self):
        self.volume = 1
        self.sounds = {}
        self.current_track = ''

        for sound in SOUNDS:
            self.sounds[sound] = helpers.load_sound(sound + '.wav')

    def set_volume(self, vol):
        self.volume = vol
        for sound in self.sounds.values():
            sound.set_volume(0.5 * vol)

    def set_music(self, track):
        if self.current_track != track:
            if track == '':
                pygame.mixer.music.fadeout(1000)
            else:
                pygame.mixer.music.load('data/msc/' + track + '.mp3')
                pygame.mixer.music.play(-1)
            self.current_track = track
