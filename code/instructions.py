from settings import *


class Instructions:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.running = True

        # text
        self.instruction_font = pygame.font.Font('../graphics/fonts/comic_sans.ttf', 30)
        self.instruction_font_scaled = pygame.font.Font('../graphics/fonts/comic_sans.ttf', 60)

    def instruction_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            # draw
            self.display_surface.fill((151, 151, 151))

            pygame.display.update()

