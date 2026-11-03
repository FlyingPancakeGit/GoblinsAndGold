from settings import *

from game import *
from instructions import *
from ui import *


class MenuImage(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)


class Menu:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.running = True

        # groups
        self.menu_sprites = pygame.sprite.Group()
        self.button_sprites = pygame.sprite.Group()
        self.image_sprites = pygame.sprite.Group()

        # buttons
        self.create_buttons()

        # logo
        self.logo = pygame.image.load('../graphics/ui/menu/logo.png').convert_alpha()
        MenuImage((self.menu_sprites, self.image_sprites), (WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.25), self.logo)

    def create_buttons(self):
        center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        surf = pygame.image.load('../graphics/ui/menu/text_button.png').convert_alpha()
        fonts = (FONT, FONT_SCALED)

        TextButton((self.menu_sprites, self.button_sprites), center, surf,
                   'Play', fonts)
        TextButton((self.menu_sprites, self.button_sprites), (center[0], center[1] * 1.2), surf,
                   'Settings', fonts)
        TextButton((self.menu_sprites, self.button_sprites), (center[0], center[1] * 1.4), surf,
                   'Instructions', fonts)

    def menu_loop(self):
        while self.running:
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            # update
            self.menu_sprites.update(None)

            for button in self.button_sprites:
                if button.pressed:
                    if button.type == 'Play':
                        game = Game()
                        game.game_loop()
                    elif button.type == 'Settings':
                        print('WIP')
                    elif button.type == 'Instructions':
                        instructions = Instructions()
                        instructions.instruction_loop()

            # draw
            self.display_surface.fill((151, 151, 151))

            for button in self.button_sprites:
                button.draw(self.display_surface)

            self.image_sprites.draw(self.display_surface)

            pygame.display.update()
