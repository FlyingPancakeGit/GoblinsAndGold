from settings import *


class SoundEffect:
    def __init__(self, file_name, volume, player):
        self.sound = pygame.mixer.Sound(f'../audio/{file_name}')
        self.sound.set_volume(volume)

        self.default_volume = volume

        self.file_name = file_name
        self.player = player

    def play(self, channel, pos):
        self.calculate_volume(pos)
        channel.play(self.sound)

    def calculate_volume(self, pos):
        difference = (self.player.rect.centerx - pos[0], self.player.rect.centery - pos[1])
        difference = math.sqrt(difference[0] ** 2 + difference[1] ** 2)
        if abs(difference) < TILE_SIZE * 8:
            lerp_factor = 1 - (abs(difference) / (TILE_SIZE * 8))
            self.sound.set_volume(pygame.math.lerp(0, self.default_volume, lerp_factor))
        else:
            self.sound.set_volume(0)

class AudioManager:
    def __init__(self, player):
        self.walking_sound = SoundEffect('walking_sound.wav', 0.3, player)
        self.mining_sound = SoundEffect('mining_sound.ogg', 0.6, player)
        self.breaking_sound = SoundEffect('rock_breaking_sound.wav', 0.5, player)
        self.selling_sound = SoundEffect('selling_sound.wav', 1, player)