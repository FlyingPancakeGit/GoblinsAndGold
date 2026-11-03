from settings import *

from game import *
from menu import *


class Main:
    def __init__(self):
        # setup
        pygame.mixer.set_num_channels(64)
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Goblins and Gold')
        pygame.display.set_icon(pygame.image.load('../graphics/ui/icon/icon.png').convert_alpha())
        pygame.mixer.music.load('../audio/background_music.mp3')
        pygame.mixer.music.play(-1)

    def main_loop(self):
        menu = Menu()
        menu.menu_loop()


if __name__ == "__main__":
    main = Main()
    main.main_loop()