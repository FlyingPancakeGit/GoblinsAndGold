import math

from settings import *

from pathfinder import *
from audio import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf, types):
        super().__init__(groups)
        self.types = types
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.hit_box_rect = self.rect

class MineSprite(Sprite):
    def __init__(self, groups, pos, surf, life_time, types):
        super().__init__(groups, pos, surf, types)
        self.age = 0
        self.life_time = life_time
        self.dt = 0

    def update_age(self):
        self.age += 1 * self.dt
        return self.check_age()

    def check_age(self):
        if self.age >= self.life_time:
            return True, self.types[1] if self.types[1] in ('coal', 'iron', 'gold', 'ruby') else None
        else:
            return False, self.types[1] if self.types[1] in ('coal', 'iron', 'gold', 'ruby') else None

    def update(self, dt):
        self.dt = dt

class Entity(Sprite):
    def __init__(self, groups, collision_sprites, gravel_sprites, pos, states, player, audio_channels, mines, types):
        super().__init__(groups, pos, list(states.values())[0], types)
        self.hit_box_rect = self.rect.inflate(-20, -20)
        self.mask = pygame.mask.from_surface(self.image)
        self.states = states

        # groups
        self.all_sprites = groups[0] if isinstance(groups, tuple) else groups

        # audio
        self.player = player
        self.audio_manager = AudioManager(player)
        self.channels = [pygame.mixer.Channel(i) for i in audio_channels]

        # mining
        self.ore_counts = {'coal': 0, 'iron': 0, 'gold': 0}
        self.mine = mines[0]
        self.converted_mine = mines[1]
        self.mine_images = mines[2]

        self.can_mine = True
        self.mine_cooldown = 600
        self.last_mine_time = 0

        # movement
        self.gravel_sprites = gravel_sprites
        self.grid_pos = self.get_grid_pos()

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 500

        # collisions
        self.collision_sprites = collision_sprites

    def check_collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hit_box_rect):
                if sprite != self:
                    if axis == 'horizontal':
                        if self.direction.x > 0: self.hit_box_rect.right = sprite.rect.left
                        elif self.direction.x < 0: self.hit_box_rect.left = sprite.rect.right
                    elif axis == 'vertical':
                        if self.direction.y > 0: self.hit_box_rect.bottom = sprite.rect.top
                        elif self.direction.y < 0: self.hit_box_rect.top = sprite.rect.bottom

    def check_mining(self, rock_pos):
        for sprite in self.collision_sprites:
            if (sprite.rect.collidepoint(rock_pos) and
                    not any(type in sprite.types for type in ('border rock', 'gravel'))):
                kill_sprite, ore = sprite.update_age()

                if not self.channels[0].get_busy():
                    self.audio_manager.mining_sound.play(self.channels[0], self.rect.center)

                if kill_sprite:
                    self.can_mine = False
                    self.last_mine_time = pygame.time.get_ticks()
                    sprite.kill()
                    if ore:
                        if 'ruby' in sprite.types and isinstance(self, Player):
                            self.player.lives += 1
                            print(self.player.lives)
                        elif 'ruby' not in sprite.types:
                            self.ore_counts[sprite.ore_type] += 1
                    self.audio_manager.breaking_sound.play(self.channels[1], self.rect.center)

                    sprite_pos = sprite.rect.topleft
                    image = self.mine_images['gravel.png']
                    Sprite((self.all_sprites, self.gravel_sprites), sprite_pos, image,
                           ('ground', 'gravel'))

    def check_mine_timer(self):
        if pygame.time.get_ticks() - self.last_mine_time >= self.mine_cooldown:
            self.can_mine = True

    def get_grid_pos(self):
        collide_sprites = pygame.sprite.spritecollide(self, self.gravel_sprites, False)
        overlaps = []

        for sprite in collide_sprites:
            overlap_rect = self.hit_box_rect.clip(sprite.hit_box_rect)
            overlap_area = overlap_rect.width * overlap_rect.height

            grid_pos = (sprite.rect.topleft[0] / TILE_SIZE, sprite.rect.topleft[1] / TILE_SIZE)
            overlaps.append((grid_pos, overlap_area))

        if overlaps:
            pos = max(overlaps, key=lambda x: x[1])[0]
            return (int(pos[0]), int(pos[1]))
        else:
            return None

    def move(self, dt):
        self.hit_box_rect.x += dt * self.speed * self.direction.x
        self.check_collision('horizontal')
        self.hit_box_rect.y += dt * self.speed * self.direction.y
        self.check_collision('vertical')

        self.rect.center = self.hit_box_rect.center


class Rock(MineSprite):
    def __init__(self, groups, pos, surf, life_time, types):
        super().__init__(groups, pos, surf, life_time, types)

class Ore(MineSprite):
    def __init__(self, groups, pos, surf, life_time, types):
        super().__init__(groups, pos, surf, life_time, types)
        self.ore_type = types[1]

class Goblin(Entity):
    def __init__(self, groups, collision_sprites, gravel_sprites, pos, states, player, audio_channels, mines, types):
        super().__init__(groups, collision_sprites, gravel_sprites, pos, states, player, audio_channels, mines, types)
        self.all_sprites = groups[0] if isinstance(groups, tuple) else groups
        self.speed = 300
        self.player = player

        # pathfinding
        self.pathfinding_cooldown = 1000
        self.last_pathfinding_time = 0
        self.can_pathfind = True

        self.path = []

    def check_pathfinding_cooldown(self):
        if not self.can_pathfind:
            if pygame.time.get_ticks() - self.last_pathfinding_time > self.pathfinding_cooldown:
                self.can_pathfind = True

    def get_path(self):
        next_pos = self.get_pos()
        self.path = Pathfinder(MINE_SIZE, self.converted_mine, self.grid_pos, next_pos).find_path()

        self.last_pathfinding_time = pygame.time.get_ticks()
        self.can_pathfind = False

    def get_direction(self):
        target_pos = ((self.path[0][0] * TILE_SIZE) + (TILE_SIZE / 2), (self.path[0][1] * TILE_SIZE) + (TILE_SIZE / 2)) \
            if self.path else None

        if target_pos:
            current_pos = self.rect.center
            direction = pygame.math.Vector2(target_pos[0] - current_pos[0], target_pos[1] - current_pos[1])
            self.direction = direction.normalize() if direction else direction
        else:
            self.direction = pygame.math.Vector2(0, 0)

    def get_pos(self):
        diff_to_player = (self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.player.rect.centery)
        dist_to_player = math.sqrt(diff_to_player[0] ** 2 + diff_to_player[1] ** 2)

        if dist_to_player < 1600:
            pos_x = int(self.player.rect.topleft[0] / TILE_SIZE)
            pos_y = int(self.player.rect.topleft[1] / TILE_SIZE)
        else:
            pos_x = random.randint(max(1, self.grid_pos[0] - 6), min(MINE_SIZE - 2, self.grid_pos[0] + 6))
            pos_y = random.randint(max(1, self.grid_pos[1] - 6), min(MINE_SIZE - 2, self.grid_pos[1] + 6))

        return pos_x, pos_y

    def check_pos(self):
        target_pos = ((self.path[0][0] * TILE_SIZE) + (TILE_SIZE / 2), (self.path[0][1] * TILE_SIZE) + (TILE_SIZE / 2)) \
            if self.path else None
        current_pos = self.rect.center
        difference = (target_pos[0] - current_pos[0], target_pos[1] - current_pos[1]) if target_pos else None

        if self.path and math.sqrt(difference[0] ** 2 + difference[1] ** 2) < TILE_SIZE / 8:
            self.path.pop(0)
        if self.path and self.can_mine:
            rock_pos = (self.path[0][0] * TILE_SIZE + TILE_SIZE / 2, self.path[0][1] * TILE_SIZE + TILE_SIZE / 2)
            self.check_mining(rock_pos)

    def update(self, dt):
        if self.can_pathfind and not self.path:
            self.get_path()

        self.grid_pos = self.get_grid_pos()
        self.get_direction()
        self.check_pos()
        self.check_pathfinding_cooldown()
        self.check_mine_timer()
        self.move(dt)

class Merchant(Entity):
    def __init__(self, groups, collision_sprites, gravel_sprites, pos, states, player, audio_channels, mines, types):
        super().__init__(groups, collision_sprites, gravel_sprites, pos, states, player, audio_channels, mines, types)
        self.original_image = list(states.values())[0]

        # rotation
        self.player = player
        self.rotation = 0

    def get_direction(self):
        self.direction.x = self.player.rect.centerx - self.rect.centerx
        self.direction.y = self.player.rect.centery - self.rect.centery
        self.direction = self.direction.normalize() if self.direction else self.direction

    def check_trade(self):
        offset_x = self.player.rect.x - self.rect.x
        offset_y = self.player.rect.y - self.rect.y

        if self.mask.overlap(self.player.mask, (offset_x, offset_y)):
           self.trade()

    def rotate(self):
        self.rotation = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 270
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def trade(self):
        play_selling_sound = False

        for key, value in self.player.ore_counts.items():
            if value:
                play_selling_sound = True
            if key == 'coal':
                self.player.coin_count += value * 1
            elif key == 'iron':
                self.player.coin_count += value * 3
            elif key == 'gold':
                self.player.coin_count += value * 9
            self.player.ore_counts[key] = 0

        if play_selling_sound:
            self.audio_manager.selling_sound.play(self.channels[1], self.rect.center)

    def update(self, dt):
        self.get_direction()
        self.check_trade()
        self.rotate()

class Player(Entity):
    def __init__(self, groups, collision_sprites, gravel_sprites, pos, states, mines, audio_channels, types):
        super().__init__(groups, collision_sprites, gravel_sprites, pos, states, self, audio_channels, mines, types)
        self.state = 'up'

        # items
        self.coin_count = 0

        # lives
        self.lives = PLAYER_LIVES
        self.can_lose_lives = True
        self.lose_lives_cooldown = 1000
        self.last_lose_life_time = 0

    def get_input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        self.direction = self.direction.normalize() if self.direction else self.direction

        if pygame.mouse.get_pressed()[0] and self.can_mine and self.validate_mouse_pos(self.get_mouse_pos()):
            rock_pos = self.get_rock_pos(self.get_mouse_pos())
            self.check_mining(rock_pos) if rock_pos else None

    def get_mouse_pos(self):
        mouse_pos_screen = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos_screen[0] - ((self.rect.centerx - WINDOW_WIDTH / 2) * -1),
                     mouse_pos_screen[1] - ((self.rect.centery - WINDOW_HEIGHT / 2) * -1))
        return mouse_pos

    def get_rock_pos(self, overlap_pos):
        for sprite in self.collision_sprites:
            if sprite.rect.collidepoint(overlap_pos):
                return sprite.rect.center
        return False

    def check_lose_life_timer(self):
        if pygame.time.get_ticks() - self.last_lose_life_time >= self.lose_lives_cooldown:
            self.can_lose_lives = True

    def validate_mouse_pos(self, mouse_pos):
        player_pos = (int(self.rect.centerx), int(self.rect.centery))
        pos = (int(mouse_pos[0]), int(mouse_pos[1]))
        if (pos[0] in range(player_pos[0] - 192, player_pos[0] + 192)
                and pos[1] in range(player_pos[1] - 192, player_pos[1] + 192)):
            return True
        else:
            return False

    def animate(self):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        self.image = self.states[f'player_{self.state}.png']

    def update(self, dt):
        self.grid_pos = self.get_grid_pos()

        self.check_lose_life_timer()
        self.check_mine_timer()
        self.get_input()
        self.animate()
        self.move(dt)
