import pygame
import os
import math
import heapq
import random

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1260, 840
TILE_SIZE = 128

MINE_SIZE = 64
GOBLIN_COUNT = 8
PLAYER_LIVES = 3

FONT = pygame.font.Font('../graphics/fonts/comic_sans.ttf', 30)
FONT_SCALED = pygame.font.Font('../graphics/fonts/comic_sans.ttf', 36)
FONT_HEADER = pygame.font.Font('../graphics/fonts/comic_sans.ttf', 50)