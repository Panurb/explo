import helpers


SOUNDS = ['bump', 'hit', 'jump', 'powerup', 'save', 'shoot', 'splash', 'spring', 'squish']
MUSIC = ['menu']


class SoundHandler():
    def __init__(self):
        self.sounds = {}

        for sound in SOUNDS:
            self.sounds[sound] = helpers.load_sound(sound + '.wav')

    def set_volume(self, vol):
        for sound in self.sounds.values():
            sound.set_volume(vol)
        self.sounds['bump'].set_volume(0.75 * vol)
