from settings import *


class Button(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf, type, scale_factor=1.2):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.type = type

        self.scale_factor = scale_factor

        self.pressed = False
        self.can_press = True
        self.press_cooldown = 300
        self.last_press_time = 0

    def check_pressed_cooldown(self):
        if pygame.time.get_ticks() - self.last_press_time >= self.press_cooldown:
            self.can_press = True

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and self.can_press:
            self.last_press_time = pygame.time.get_ticks()
            self.can_press = False
            self.pressed = True
        else:
            self.pressed = False

    def draw(self, surface):
        image = self.image
        rect = self.rect

        if isinstance(self, TextButton):
            text_surf = self.text_surf
            text_rect = self.text_rect

            if rect.collidepoint(pygame.mouse.get_pos()):
                image = pygame.transform.scale_by(image, self.scale_factor)
                text_surf = self.text_surf_scaled

                rect = pygame.FRect(0, 0, rect.width * self.scale_factor, rect.height * self.scale_factor)
                rect.center = self.rect.center
                text_rect = pygame.Rect(0, 0, text_rect.width * self.scale_factor, text_rect.height * self.scale_factor)
                text_rect.center = self.text_rect.center

            surface.blit(image, rect)
            surface.blit(text_surf, text_rect)
        else:
            if rect.collidepoint(pygame.mouse.get_pos()):
                image = pygame.transform.scale_by(image, self.scale_factor)

                rect = pygame.FRect(0, 0, rect.width * self.scale_factor, rect.height * self.scale_factor)
                rect.center = self.rect.center

            surface.blit(image, rect)

    def update(self, dt):
        self.check_pressed()
        self.check_pressed_cooldown()

class TextButton(Button):
    def __init__(self, groups, pos, surf, text, fonts):
        super().__init__(groups, pos, surf, text)
        # text
        self.text = text

        self.font = fonts[0]
        self.font_scaled = fonts[1]

        self.text_surf = self.font.render(self.text, True, (58, 58, 58))
        self.text_surf_scaled = self.font_scaled.render(self.text, True, (58, 58, 58))

        self.text_rect = self.text_surf.get_frect(center=self.rect.center)


class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # groups
        self.button_sprites = pygame.sprite.Group()

        # buttons
        self.create_buttons()

    def get_ore_values(self, ore_counts, coins):
        coal_text = FONT.render(f'Coal: {ore_counts[0]}', True, (240, 240, 240))
        iron_text = FONT.render(f'Iron: {ore_counts[1]}', True, (240, 240, 240))
        gold_text = FONT.render(f'Gold: {ore_counts[2]}', True, (240, 240, 240))
        coin_text = FONT.render(f'Coins: {coins}', True, (240, 240, 240))

        coal_rect = coal_text.get_frect(topleft=(10, WINDOW_HEIGHT - 50))
        iron_rect = iron_text.get_frect(topleft=(coal_rect.right + 20, WINDOW_HEIGHT - 50))
        gold_rect = gold_text.get_frect(topleft=(iron_rect.right + 20, WINDOW_HEIGHT - 50))
        coin_rect = coin_text.get_frect(topleft=(10, WINDOW_HEIGHT - 90))

        return [(coal_text, coal_rect), (iron_text, iron_rect), (gold_text, gold_rect), (coin_text, coin_rect)]

    def get_lives(self, player_lives):
        life_images = []
        life_image = pygame.image.load('../graphics/ui/match/life.png').convert_alpha()
        last_life_pos = (WINDOW_WIDTH - 70, WINDOW_HEIGHT - 70)

        for life in range(player_lives):
            life_images.append((life_image, last_life_pos))

            last_life_pos = (last_life_pos[0] - 70, last_life_pos[1])

        return life_images

    def create_buttons(self):
        surf = pygame.transform.scale_by(
            pygame.image.load('../graphics/ui/match/exit_button.png').convert_alpha(), 0.4)
        center = (surf.get_width() / 2 + 10, surf.get_height() / 2 + 10)

        Button((self.button_sprites), center, surf, 'exit')

    def draw(self, player_lives, ore_counts, coin_count):
        lives = self.get_lives(player_lives)

        for life in lives:
            self.display_surface.blit(life[0], life[1])

        ore_values = self.get_ore_values(ore_counts, coin_count)

        for text, rect in ore_values:
            self.display_surface.blit(text, rect.topleft)

        for button in self.button_sprites:
            button.draw(self.display_surface)

    def ui_loop(self, dt):
        for button in self.button_sprites:
            if button.pressed:
                if button.type == 'exit':
                    return False

        # update
        self.button_sprites.update(dt)

        return True