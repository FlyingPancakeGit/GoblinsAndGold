import pygame

from settings import *


class GameOver:
    def __init__(self, ore_counts, coins):
        self.display_surface = pygame.display.get_surface()
        self.running = True

        self.ore_values = self.get_ore_values(ore_counts, coins)

    def get_ore_values(self, ore_counts, coins):
        coin_text = FONT_SCALED.render(f'Coins: {coins}', True, (240, 240, 240))
        coal_text = FONT_SCALED.render(f'Coal: {ore_counts[0]}', True, (240, 240, 240))
        iron_text = FONT_SCALED.render(f'Iron: {ore_counts[1]}', True, (240, 240, 240))
        gold_text = FONT_SCALED.render(f'Gold: {ore_counts[2]}', True, (240, 240, 240))

        coin_rect = coin_text.get_frect(center=(WINDOW_WIDTH / 2, (WINDOW_HEIGHT / 2) - 60))
        coal_rect = coal_text.get_frect(center=(coin_rect.centerx - 140, WINDOW_HEIGHT / 2))
        iron_rect = iron_text.get_frect(center=(coin_rect.centerx, WINDOW_HEIGHT / 2))
        gold_rect = gold_text.get_frect(center=(coin_rect.centerx + 140, WINDOW_HEIGHT / 2))

        return [(coal_text, coal_rect), (iron_text, iron_rect), (gold_text, gold_rect), (coin_text, coin_rect)]

    def draw(self):
        game_over_text = FONT_HEADER.render('Game Over!', True, (240, 240, 240))
        game_over_rect = game_over_text.get_frect(center = (WINDOW_WIDTH / 2, (WINDOW_HEIGHT / 2) - 180))

        return_text = FONT_SCALED.render('Press "x" to return to Main Menu.', True, (240, 240, 240))
        return_rect = return_text.get_frect(center = (WINDOW_WIDTH / 2, (WINDOW_HEIGHT / 2) + 260))

        self.display_surface.blit(game_over_text, game_over_rect)

        for text, rect in self.ore_values:
            self.display_surface.blit(text, rect.topleft)

        self.display_surface.blit(return_text, return_rect)

    def game_over_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.running = False

            # draw
            self.display_surface.fill((151, 151, 151))

            self.draw()

            pygame.display.update()
