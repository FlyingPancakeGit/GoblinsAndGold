import pygame.mixer

from settings import *

from groups import *
from sprites import *
from ui import *
from mine import *
from game_over import *

class Game:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.running = True
        self.clock = pygame.time.Clock()

        # groups
        self.all_sprites = AllSpritesGroup()

        self.collision_sprites = pygame.sprite.Group()
        self.gravel_sprites = pygame.sprite.Group()
        self.rock_sprites = pygame.sprite.Group()
        self.goblin_sprites = pygame.sprite.Group()

        # ui
        self.ui = UI()

        # audio
        self.channels = pygame.mixer.get_num_channels()
        self.channel_index = 0

        # player
        self.player_pos = None
        self.player_clearing_pos_list = []
        self.player_states = {}
        self.player = None

        # merchant
        self.merchant_pos = None
        self.merchant_states = {}

        # goblins
        self.goblin_pos_list = []
        self.goblin_clearing_pos_list = []
        self.goblin_states = {}

        # imports
        self.mine_images = {}
        self.import_images()

        # mine
        self.mine = Mine().mine_loop()
        self.converted_mine = [[0] * MINE_SIZE for _ in range(MINE_SIZE)]

        # spawning
        self.vein_count = 0
        self.ruby_count = 10

        self.coal_ore_pos_list = []
        self.iron_ore_pos_list = []
        self.gold_ore_pos_list = []
        self.ruby_pos_list = []

        self.get_ore_pos()
        self.get_entities_pos()

        self.place_mine()
        self.spawn_entities()

        # mining timer
        self.can_mine = True
        self.mine_cooldown = 600
        self.last_mine_time = 0

    def import_images(self):
        root_path = '../graphics/ground'
        for dir in os.listdir(root_path):
            for sub_dir in os.listdir(os.path.join(root_path, dir)):
                if os.path.isfile(os.path.join(root_path, dir, sub_dir)):
                    image = pygame.image.load(os.path.join(root_path, dir, sub_dir)).convert_alpha()
                    self.mine_images[sub_dir] = image
                else:
                    for file in os.listdir(os.path.join(root_path, dir, sub_dir)):
                        image = pygame.image.load(os.path.join(root_path, dir, sub_dir, file)).convert_alpha()
                        self.mine_images[file] = image

        root_path = '../graphics/entities'
        for path in ['player', 'merchant', 'goblin']:
            for dir in os.listdir(os.path.join(root_path, path)):
                if os.path.isfile(os.path.join(root_path, path, dir)):
                    image = pygame.image.load(os.path.join(root_path, path, dir)).convert_alpha()
                    if path == 'player':
                        self.player_states[dir] = image
                    elif path == 'merchant':
                        self.merchant_states[dir] = image
                    elif path == 'goblin':
                        self.goblin_states[dir] = image

    def get_ore_pos(self):
        for vein in range(self.vein_count):
            type = random.choice(['gold'] + ['iron'] * 3 + ['coal'] * 9)
            pos = (random.randint(1, MINE_SIZE - 1), random.randint(1, MINE_SIZE - 1))
            offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

            vein_size = random.randint(3, 10)

            for ore in range(vein_size):
                offset = random.choice(offsets)
                pos = (pos[0] + offset[0], pos[1] + offset[1])
                if type == 'coal':
                    self.coal_ore_pos_list.append(pos)
                elif type == 'iron':
                    self.iron_ore_pos_list.append(pos)
                elif type == 'gold':
                    self.gold_ore_pos_list.append(pos)

        for ruby in range(self.ruby_count):
            pos = (random.randint(1, MINE_SIZE - 1), random.randint(1, MINE_SIZE - 1))
            self.ruby_pos_list.append(pos)

    def place_mine(self):
        for x in range(MINE_SIZE):
            for y in range(MINE_SIZE):
                groups = [self.all_sprites, self.collision_sprites, self.rock_sprites]
                types = ['ground']
                image = None
                life_time = 0

                if x == 0 or x == MINE_SIZE - 1 or y == 0 or y == MINE_SIZE - 1:
                    self.converted_mine[x][y] = 100
                    image = self.mine_images['border-rock.png']
                    types.append('border rock')
                elif (x, y) in self.player_clearing_pos_list or (x, y) in self.goblin_clearing_pos_list:
                    self.converted_mine[x][y] = 1
                    image = self.mine_images['gravel.png']
                    types.append('gravel')
                    groups.remove(self.collision_sprites)
                    groups.remove(self.rock_sprites)
                    groups.append(self.gravel_sprites)
                elif (x, y) in self.ruby_pos_list:
                    self.converted_mine[x][y] = 2
                    image = self.place_ore((x, y), 'ruby')
                    types.append('ruby')
                    life_time = 1.2
                elif (x, y) in self.coal_ore_pos_list:
                    self.converted_mine[x][y] = 2
                    image = self.place_ore((x, y), 'coal')
                    types.append('coal')
                    life_time = 1.2
                elif (x, y) in self.iron_ore_pos_list:
                    self.converted_mine[x][y] = 2
                    image = self.place_ore((x, y), 'iron')
                    types.append('iron')
                    life_time = 1.2
                elif (x, y) in self.gold_ore_pos_list:
                    self.converted_mine[x][y] = 2
                    image = self.place_ore((x, y), 'gold')
                    types.append('gold')
                    life_time = 1.2
                elif self.mine[x][y] < -0.05:
                    self.converted_mine[x][y] = 5
                    image = self.mine_images['hard-rock.png']
                    types.append('hard rock')
                    life_time = 1
                elif self.mine[x][y] < 0:
                    self.converted_mine[x][y] = 4
                    image = self.mine_images['medium-rock.png']
                    types.append('medium rock')
                    life_time = 0.75
                else:
                    self.converted_mine[x][y] = 30
                    image = self.mine_images['rock.png']
                    types.append('rock')
                    life_time = 0.5

                x_pos = x * TILE_SIZE
                y_pos = y * TILE_SIZE

                if {'coal', 'iron', 'gold'}.intersection(set(types)):
                    Ore(tuple(groups), (x_pos, y_pos), image, life_time, types)
                else:
                    Rock(tuple(groups), (x_pos, y_pos), image, life_time, types)

    def place_ore(self, pos, ore_type):
        if self.mine[pos[0]][pos[1]] < -0.05:
            return self.mine_images[f'hard-{ore_type}.png']
        elif self.mine[pos[0]][pos[1]] < 0:
            return self.mine_images[f'medium-{ore_type}.png']
        else:
            return self.mine_images[f'{ore_type}.png']

    def get_entities_pos(self):
        offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for goblin in range(GOBLIN_COUNT):
            pos = (random.randint(1, MINE_SIZE - 2), random.randint(1, MINE_SIZE - 2))

            self.goblin_pos_list.append((pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
            self.goblin_clearing_pos_list.append(pos)

            for offset in offsets:
                new_pos = (pos[0] + offset[0], pos[1] + offset[1])
                self.goblin_clearing_pos_list.append(new_pos)

        pos = (random.randint(1, MINE_SIZE - 2), random.randint(1, MINE_SIZE - 2))
        self.player_pos = (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
        self.player_clearing_pos_list.append(pos)

        for offset in offsets:
            new_pos = (pos[0] + offset[0], pos[1] + offset[1])
            self.player_clearing_pos_list.append(new_pos)

        options = [pos for pos in self.player_clearing_pos_list[1:] if pos[0] != 0 and pos[1] != 0
                   and pos[0] != MINE_SIZE - 1 and pos[1] != MINE_SIZE - 1]

        grid_merchant_pos = random.choice(options)
        abs_merchant_pos = (grid_merchant_pos[0] * TILE_SIZE, grid_merchant_pos[1] * TILE_SIZE)
        self.merchant_pos = abs_merchant_pos

    def spawn_entities(self):
        self.player = Player((self.all_sprites), self.collision_sprites,
                             self.gravel_sprites, self.player_pos, self.player_states,
                             (self.mine, self.converted_mine, self.mine_images),
                             (self.channel_index, self.channel_index + 1), 'entity')
        self.channel_index += 2

        self.merchant = Merchant((self.all_sprites), self.collision_sprites, self.gravel_sprites,
                                 self.merchant_pos, self.merchant_states, self.player,
                                 (self.channel_index, self.channel_index + 1),
                                 (self.mine, self.converted_mine, self.mine_images), 'entity')
        self.channel_index += 2

        for pos in self.goblin_pos_list:
            Goblin((self.all_sprites, self.goblin_sprites), self.collision_sprites, self.gravel_sprites, pos, self.goblin_states,
                   self.player, (self.channel_index, self.channel_index + 1),
                   (self.mine, self.converted_mine, self.mine_images),'entity')
            self.channel_index += 2

    def check_goblin_collision(self):
        for goblin in self.goblin_sprites:
            offset_x  = goblin.hit_box_rect.x - self.player.hit_box_rect.x
            offset_y = goblin.hit_box_rect.y - self.player.hit_box_rect.y

            if self.player.mask.overlap(goblin.mask, (offset_x, offset_y)) and self.player.can_lose_lives:
                self.player.lives -= 1

                self.player.can_lose_lives = False
                self.player.last_lose_life_time = pygame.time.get_ticks()

    def check_game_over(self):
        if self.player.lives <= 0:
            return False
        else:
            return True

    def game_loop(self):
        while self.running:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.running = False

            # update
            self.all_sprites.update(dt)

            self.check_goblin_collision()

            self.running = self.ui.ui_loop(dt) and self.running
            self.running = self.check_game_over() and self.running

            # draw
            if self.running:
                self.display_surface.fill((0, 0, 0))
                self.all_sprites.draw(self.player.rect.center)
                self.ui.draw(self.player.lives, list(self.player.ore_counts.values()), self.player.coin_count)
            elif self.player.lives <= 0:
                GameOver(list(self.player.ore_counts.values()), self.player.coin_count).game_over_loop()

            pygame.display.update()