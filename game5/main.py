from configs import *
from pygame.image import load
from pygame.key import get_pressed as keys
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from pygame import mixer
import pygame
import os
import random
import csv
pygame.init()
mixer.init()

# main setting
window = pygame.display.set_mode((W, H))
pygame.display.set_caption('Shooter')
pygame.display.set_icon(load('images/player/Idle/1.png'))
running = True

# main game variables
start_game = False
level = 1
level_complete = False
GRAVITY = 0.5
start_intro = False

# musics and sounds
music = mixer.music.load('audio/music2.mp3')
mixer.music.set_volume(0.4)
mixer.music.play(-1, 0, 5000)

jump_sound = mixer.Sound('audio/jump.wav')
jump_sound.set_volume(0.3)

shoot_sound = mixer.Sound('audio/shot.wav')
shoot_sound.set_volume(0.3)

grenade_sound = mixer.Sound('audio/grenade.wav')
grenade_sound.set_volume(0.3)

# pygame clock
clock = pygame.time.Clock()

# scroll
bg_scroll = 0
screen_scroll = 0

# images
bullet_img = load('images/icons/bullet.png').convert_alpha()
grenade_img = load('images/icons/grenade.png').convert_alpha()
start_img = load('images/start_btn.png').convert_alpha()
exit_img = load('images/exit_btn.png').convert_alpha()
restart_img = load('images/restart_btn.png').convert_alpha()
restart_img = pygame.transform.scale(restart_img, (restart_img.get_width() * 2, restart_img.get_height() * 2))

# Button class
class Button:
    def __init__(self, img, x, y):
        self.image = img
        self.rect = self.image.get_rect(topleft=(x, y))


    def draw(self):
        clicked = False
        if self.rect.x < mouse_pos()[0] < self.rect.x + self.rect.width and \
                self.rect.y < mouse_pos()[1] < self.rect.y + self.rect.height:
            if mouse_buttons()[0] == 1:
                clicked = True

        window.blit(self.image, self.rect)

        return clicked


# TileMap class
class TileMap:
    def __init__(self):
        self.obstacle_list = []
        self.tile_data = self.get_tile_data()
        self.images = self.get_image_data()

    def get_image_data(self):
        images = []
        for i in range(21):
            image = load(f'images/tile/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            images.append(image)
        return images

    def get_tile_data(self):
        data = []
        for i in range(20):
            r = [-1] * 150
            data.append(r)
        with open(f'levels/level_{level}.csv', mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    data[y][x] = int(tile)

        return data

    def process_data(self):
        player = None
        self.level_lenth = len(self.tile_data[0])
        for y, row in enumerate(self.tile_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    image = self.images[tile]
                    if 0 <= tile <= 8:
                        tile_obj = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                        self.obstacle_list.append(tile_obj)

                    elif 8 < tile < 11:
                        water = Water(image, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)

                    elif 10 < tile < 15:
                        decor = Decoration(image, x * TILE_SIZE, y * TILE_SIZE)
                        if tile == 12:
                            decor.tile_name = 'box'
                            self.obstacle_list.append(decor)
                        decoration_group.add(decor)



                    elif tile == 15:
                        player = Solider('player', x * TILE_SIZE, y * TILE_SIZE)

                    elif tile == 16:
                        enemy = Solider('enemy', x * TILE_SIZE - 20, y * TILE_SIZE)
                        enemy_group.add(enemy)

                    elif tile == 17:
                        ammo = AmmoBox(x * TILE_SIZE, y * TILE_SIZE)
                        ammo_box_group.add(ammo)

                    elif tile == 18:
                        grenade_box = GrenadeBox(x * TILE_SIZE, y * TILE_SIZE)
                        grenade_box_group.add(grenade_box)

                    elif tile == 19:
                        health = HealthBox(x * TILE_SIZE, y * TILE_SIZE)
                        health_box_group.add(health)

                    elif tile == 20:
                        exit_box = Exit(image, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_box)
        return player
    def draw(self):
        for tile in self.obstacle_list:
            tile.draw()
            tile.update()

# Background class
class Background:
    def __init__(self):
        self.images = self.get_image_data()

    def get_image_data(self):
        images = []
        names = ['sky.png', 'cloud.png', 'mountain.png', 'pine1.png', 'pine2.png']
        for name in names:
            image = load(f'images/background/{name}').convert_alpha()
            image = pygame.transform.scale(image, (W, image.get_height() * 1.5))
            images.append(image)
        return images

    def draw_bg(self, bg_scroll=0):

        width = self.images[0].get_width()
        for x in range((tile_map.level_lenth * TILE_SIZE) // W):
            window.blit(self.images[0], ((x * width) - bg_scroll * 0.1, 0))
            window.blit(self.images[1], ((x * width) - bg_scroll * 0.3, 50))
            window.blit(self.images[2], ((x * width) - bg_scroll * 0.5, 100))
            window.blit(self.images[3], ((x * width) - bg_scroll * 0.7, 200))
            window.blit(self.images[4], ((x * width) - bg_scroll * 0.9, 250))

# Solider
class Solider(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, speed=5, scale=(50, 60), color='red'):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.way = 0

        self.char_type = char_type
        self.x = x
        self.y = y
        self.scale = scale

        self.is_live = True
        self.health = 100
        # if char_type == 'player':
        #     self.health = 100
        self.max_health = self.health
        self.killen_enemies = 0

        self.image_data = self.get_image_data()
        self.action = 0
        self.frame_index = 0
        self.image = self.image_data[self.action][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = speed
        self.moving = False
        self.move_right = False
        self.move_left = False
        self.direction = 1

        self.is_jumping = False
        self.on_air = False
        self.velocity = 0

        self.ammo = 30
        self.grenades = 5
        self.is_shooting = False
        self.is_grenade_throw = False

        self.no_run = True
        self.no_run_dx = 0

        # for enemy objects
        self.ai_action_changer_timer = 50
        self.ai_action_changer_counter = 0
        self.ai_last_move = 'right'
        self.change_ai_ac = 'run'
        self.jump_timer = 30
        self.jump_counter = 30

        self.ai_shoot_timer = 30
        self.ai_shoot_counter = self.ai_shoot_timer

        self.ai_vision = pygame.Rect(0, 0, 400, 20)
        self.ai_shooting = False
        self.ai_killen = False
        self.kill_timer = 50
        self.kill_counter = 0

    def get_image_data(self):
        actions = ['Idle', 'Run', 'Jump', 'Death']
        image_data = []
        for i in range(4):
            length = len(os.listdir(f'images/player/{actions[i]}'))
            images = []
            for j in range(length):
                image = load(f'images/{self.char_type}/{actions[i]}/{j}.png').convert_alpha()
                image = pygame.transform.scale(image, self.scale)
                images.append(image)
            image_data.append(images)
        return image_data

    def draw(self):
        window.blit(self.image, self.rect)
        # pygame.draw.rect(window, self.color, self.rect, 2)

    def update(self):
        self.change_action()
        self.animation()
        self.draw_health_indicator()
        self.check_alive()

        if self.is_live:
            self.event_loop()
            if self.char_type == 'player':
                if self.is_shooting:
                    self.shoot()

                self.throw_grenade()
        if self.char_type == 'enemy':
            self.enemy_ai()

    def animation(self, anim_speed=6):

        if self.frame_index // anim_speed > len(self.image_data[self.action]) - 1:
            self.frame_index = 0

        self.image = self.image_data[self.action][self.frame_index // anim_speed]
        self.image = pygame.transform.flip(self.image, self.direction - 1, 0)

        if self.is_live:
            self.frame_index += 1
        else:
            if self.frame_index <= len(self.image_data[self.action]) * anim_speed - 2:
                self.frame_index += 1
            else:
                self.frame_index = len(self.image_data[self.action]) * anim_speed - 2

    def change_action(self):
        if self.is_live:
            if not self.is_jumping and self.on_air == False:
                if self.move_left or self.move_right:
                    self.action = 1
                else:
                    self.action = 0
            else:
                self.action = 2
        else:
            self.action = 3

    def move(self):
        dx = 0
        dy = 0
        screen_scroll = 0

        if self.is_live:
            if self.move_right:
                dx = self.speed

            elif self.move_left:
                dx = -self.speed


            if self.is_jumping:
                if self.char_type == 'enemy':
                    jump_sound.set_volume(0.1)
                jump_sound.play(1)
                self.velocity = -11
                self.is_jumping = False
                self.on_air = True


        self.velocity += GRAVITY
        dy += self.velocity


        for tile in tile_map.obstacle_list:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
                if self.char_type == 'enemy':
                    if self.change_ai_ac == 'run':
                        self.change_ai_ac = 'jump'
                        if self.ai_last_move == 'right':
                            self.move_right = False
                            self.move_left = True
                            self.direction = -1
                            self.ai_last_move = 'left'
                        elif self.ai_last_move == 'left':
                            self.move_left = False
                            self.move_right = True
                            self.direction = 1
                            self.ai_last_move = 'right'
                    elif self.change_ai_ac == 'jump':
                        self.change_ai_ac = 'run'
                        if self.jump_counter == self.jump_timer:
                            self.is_jumping = True
                            self.jump_counter = 0



            if tile.rect.colliderect(self.rect.x, self.rect.y + dy + 1, self.rect.width, self.rect.height):

                if self.rect.top - dy >= tile.rect.bottom:
                    self.velocity = 0
                    dy = tile.rect.bottom - self.rect.top


                elif self.on_air:
                    self.on_air = False
                    dy = tile.rect.top - self.rect.bottom


                elif self.velocity > 0:
                    self.velocity = 0
                    dy = 0


        self.rect.x += dx
        self.rect.y += dy

        self.way += dx

        level_complete = False
        if self.char_type == 'player':

            if (self.rect.right > W / 3) or (self.way - self.rect.x > -TILE_SIZE and self.direction == -1):
                self.rect.x -= dx
                screen_scroll = -dx

            if abs(self.way - tile_map.level_lenth * TILE_SIZE) < W - 200:
                screen_scroll = 0
                self.rect.x += dx

            if self.rect.x + dx <= 0:
                self.rect.x -= dx

            if pygame.sprite.spritecollide(self, water_group, False):
                self.health = 0

            if self.rect.y + dy >= H - TILE_SIZE:
                self.health = 0

            if pygame.sprite.spritecollide(self, exit_group, False):
                level_complete = True

        else:

            if pygame.sprite.spritecollide(self, water_group, False):
                self.is_jumping = True
                self.move_right = True
                self.direction = 1

        return screen_scroll, level_complete

    def shoot(self):

        if self.ammo > 0:
            bullet = Bullet(self.rect.x + (self.direction * self.rect.size[0]),
                            self.rect.y + (self.rect.size[0] // 4),
                            self.direction, **{'owner': self.char_type})
            bullet_group.add(bullet)
            self.ammo -= 1
            shoot_sound.play()
        self.is_shooting = False

    def throw_grenade(self):
        if self.is_grenade_throw and self.grenades > 0:
            grenade = Grenade(self.rect.centerx + (self.direction * self.rect.size[0] // 2),
                              self.rect.y, self.direction)
            grenade_group.add(grenade)
            self.is_grenade_throw = False
            self.grenades -= 1

    def enemy_ai(self):

        if self.is_live:
            if self.jump_counter < self.jump_timer:
                self.jump_counter += 1
            self.ai_vision.center = (self.rect.centerx + self.direction * 200, self.rect.centery)

            if player.rect.colliderect(self.ai_vision) and player.is_live:
                self.action = 0
                self.move_right = self.move_left = False
                if self.ai_shoot_counter == self.ai_shoot_timer:
                    self.ai_shoot_counter = 0
                    self.shoot()
                self.ai_shoot_counter += 1

            else:
                self.ai_action_changer_counter += 1
                if self.ai_action_changer_counter == self.ai_action_changer_timer:
                    self.ai_action_changer_counter = 0
                    self.ai_action_changer_timer = random.randint(50, 90)

                    if self.action == 0:
                        self.action = 1

                        if self.ai_last_move == 'right':
                            self.move_right = False
                            self.move_left = True
                            self.direction = -1
                            self.ai_last_move = 'left'
                        elif self.ai_last_move == 'left':
                            self.move_left = False
                            self.move_right = True
                            self.direction = 1
                            self.ai_last_move = 'right'

                    else:
                        self.action = 0
                        self.move_left = self.move_right = False

        self.move()
        self.rect.x += screen_scroll

    def check_alive(self):

        if self.health <= 0:
            self.is_live = False

    def draw_health_indicator(self):
        # pygame.draw.rect(window, 'red', (self.rect.topleft, self.rect.topleft, 10, 50))
        health = self.health / self.max_health

        if self.char_type == 'enemy':
            pygame.draw.rect(window, 'red', (self.rect.x, self.rect.y - 20, 50, 10))
            pygame.draw.rect(window, 'green', (self.rect.x, self.rect.y - 20, 50 * health, 10))
            pygame.draw.rect(window, 'black', (self.rect.x, self.rect.y - 20, 51, 11), 3)

        else:
            pygame.draw.rect(window, 'red', (10, 10, 200, 30))
            pygame.draw.rect(window, 'green', (10, 10, 200 * health, 30))
            pygame.draw.rect(window, 'black', (10, 10, 200, 30), 3)

    def event_loop(self):
        if self.char_type == 'player':
            if keys()[pygame.K_d]:
                self.move_right = True
                self.direction = 1
            else:
                self.move_right = False

            if keys()[pygame.K_a]:
                self.move_left = True
                self.direction = -1
            else:
                self.move_left = False

# Bullet class
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.kwargs = kwargs
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 12
        self.direction = direction


    def get_image(self):
        image = load('images/icons/blt.png').convert_alpha()
        image = pygame.transform.scale(image, (image.get_width() // 16, image.get_height() // 16))
        return image

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        self.rect.x += self.speed * self.direction + screen_scroll

        if self.rect.x > W or self.rect.x < 0:
            self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.is_live:
                self.kill()
                player.health -= 3
                if player.health <= 0:
                    player.is_live = False

        for tile in tile_map.obstacle_list:
            if tile.rect.colliderect(self.rect.x, self.rect.y, self.rect.width, self.rect.height):
                self.kill()

        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect) and self.kwargs['owner'] != 'enemy':
                if enemy.is_live:
                    self.kill()
                    enemy.health -= 25
                    if enemy.health <= 0:
                        enemy.is_live = False

# Tile class
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        self.rect.x += screen_scroll

# Grenade class
class Grenade(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = load('images/icons/grenade.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction
        self.speed = 10
        self.velocity = -5
        self.explosing = False
        self.timer = 50
        self.counter = 0


    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        # pygame.draw.rect(window, 'blue', self.rect)
        dy = 0
        dx = 0

        dx += self.speed * self.direction
        self.velocity += GRAVITY
        dy += self.velocity


        for tile in tile_map.obstacle_list:

            if tile.rect.colliderect(self.rect.x + dx, self.rect.y + dy, self.rect.width, self.rect.height):
                self.direction *= -1

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy - self.rect.size[1] // 1.6, self.rect.width, self.rect.height):
                if self.velocity > 5 and tile.rect.top <= self.rect.bottom:
                    dy = 0
                    dx = 0
                    self.explosing = True

        if self.rect.y >= H - TILE_SIZE:
            self.kill()

        if pygame.sprite.spritecollide(self, water_group, False):
            self.kill()

        if self.explosing:
            self.counter += 1
            if self.counter == self.timer:
                self.kill()
                exp = Explosion(self.rect.x - TILE_SIZE, self.rect.y - TILE_SIZE)
                explosion_group.add(exp)
                grenade_sound.play()





        self.rect.y += dy
        self.rect.x += dx + screen_scroll

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = self.get_animation_list()
        self.frame_index = 0
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_not_kill = True


    def get_animation_list(self):
        images = []
        for index in range(1, 6):
            image = load(f'images/explosion/exp{index}.png').convert_alpha()
            images.append(image)
        return images

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        self.animation()
        # pygame.draw.rect(window, 'blue', self.rect, 4)
        self.kill_characters()
        self.rect.x += screen_scroll

    def animation(self, anim_speed=6):
        if self.frame_index == len(self.animation_list) * anim_speed - 1:
            self.kill()
            self.frame_index = 0

        self.image = self.animation_list[self.frame_index // anim_speed]
        self.frame_index += 1

    def kill_characters(self):

        if pygame.sprite.spritecollide(player, explosion_group, False) and self.is_not_kill:
            if player.is_live:
                player.health -= 50
                if player.health <= 0:
                    player.is_live = False
                self.is_not_kill = False


        for enemy in enemy_group:
            if enemy.rect.colliderect(self.rect) and self.is_not_kill:
                if enemy.is_live:
                    enemy.health -= 50
                    if enemy.health <= 0:
                        enemy.is_live = False
                self.is_not_kill = False

# HealthBox class
class HealthBox(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))


    def get_image(self):
        image = load('images/icons/health_box.png').convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):

        if pygame.sprite.spritecollide(player, health_box_group, False):
            player.health += 40
            if player.health >= 100:
                player.health = player.max_health
            self.kill()

        self.rect.x += screen_scroll

# AmmoBox class
class AmmoBox(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))


    def get_image(self):
        image = load('images/icons/ammo_box.png').convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        if pygame.sprite.spritecollide(player, ammo_box_group, False):
            player.ammo += 10
            if player.ammo >= 20:
                player.ammo = 20
            self.kill()
        self.rect.x += screen_scroll

# GrenadeBox class
class GrenadeBox(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_image(self):
        image = load('images/icons/grenade_box.png').convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        if pygame.sprite.spritecollide(player, grenade_box_group, False):
            player.grenades += 3
            if player.grenades >= 5:
                player.grenades = 5
            self.kill()
        self.rect.x += screen_scroll

# Water class
class Water(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.x += screen_scroll

# Decoration class
class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, x, y, tile_name=''):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.tile_name = tile_name

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        self.rect.x += screen_scroll

# Exit group
class Exit(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        window.blit(self.image, self.rect)

    def update(self):
        self.rect.x += screen_scroll

# writer class
class Writer:
    def __init__(self):
        self.font = pygame.font.SysFont('Futura', 30)

    def write_image(self, text, x, y, margin_x, margin_y, img, count):

        f_text = self.font.render(f"{text}: ", 1, 'black')
        window.blit(f_text, (x, y))
        for i in range(count):
            window.blit(img, (x + margin_x + img.get_rect().width * i, y + margin_y))

    def write_text(self, text, value, x, y):
        f_text = self.font.render(f'{text}: {value}', 1, 'black')
        window.blit(f_text, (x, y))

class FadeScreen:

    def __init__(self, direction, color):
        self.direction = direction
        self.color = color
        self.speed = 5
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(window, self.color, (0, 0, W, 0 + self.fade_counter))
        elif self.direction == 2:
            pygame.draw.rect(window, self.color, (0 - self.fade_counter, 0, W // 2, H))
            pygame.draw.rect(window, self.color, (W // 2 + self.fade_counter, 0, W // 2, H))
            pygame.draw.rect(window, self.color, (0, 0 - self.fade_counter, W, H // 2))
            pygame.draw.rect(window, self.color, (0, H // 2 + self.fade_counter, W, H // 2))

        if self.fade_counter == H:
            self.speed = 0
            fade_complete = True


        return fade_complete

def restart_game():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    health_box_group.empty()
    ammo_box_group.empty()
    grenade_box_group.empty()
    water_group.empty()
    decoration_group.empty()
    exit_group.empty()

    tile_map = TileMap()

    return tile_map


enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
health_box_group = pygame.sprite.Group()
ammo_box_group = pygame.sprite.Group()
grenade_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# ...
bg = Background()

# ...
tile_map = TileMap()
player = tile_map.process_data()
writer = Writer()

start_btn = Button(start_img, W // 2 - start_img.get_width() // 2, H // 2 - 2 *start_img.get_height())
exit_btn = Button(exit_img, W // 2 - exit_img.get_width() // 2, H // 2 + exit_img.get_height() // 1 - start_img.get_height())
restart_btn = Button(restart_img, (W - restart_img.get_width()) // 2, (H - restart_img.get_height()) // 2)

# fade
restart_fade = FadeScreen(1, RED)
start_fade = FadeScreen(2, 'black')

while running:

    clock.tick(FPS)
    pygame.display.update()


    # background
    if not start_game:
        window.fill(GREEN)
        if start_btn.draw():
            start_game = True
            start_intro = True

        if exit_btn.draw():
            running = False
    else:
        bg.draw_bg(bg_scroll)
        # player
        player.draw()
        player.update()

        # enemies
        for enemy in enemy_group:
            enemy.draw()
            enemy.update()
            if not enemy.is_live:
                if not enemy.ai_killen:
                    enemy.ai_killen = True
                    player.killen_enemies += 1
                enemy.kill_counter += 1
                if enemy.kill_counter == enemy.kill_timer:
                    enemy.kill()


        # Tile Map
        tile_map.draw()

        # bullets
        for bullet in bullet_group:
            bullet.draw()
            bullet.update()

        # grenades
        for grenade in grenade_group:
            grenade.draw()
            grenade.update()

        # explosion
        for exp in explosion_group:
            exp.draw()
            exp.update()

        # health box
        for health in health_box_group:
            health.draw()
            health.update()

        # ammo box
        for ammo in ammo_box_group:
            ammo.draw()
            ammo.update()

        # grenade box
        for grenade_box in grenade_box_group:
            grenade_box.draw()
            grenade_box.update()

        # water
        for water in water_group:
            water.draw()
            water.update()

        # decoration
        for decor in decoration_group:
            if decor.tile_name != 'box':
                decor.draw()
                decor.update()

        # exit
        for exit_box in exit_group:
            exit_box.draw()
            exit_box.update()

        if start_intro:
            if start_fade.fade():
                start_intro = False
                start_fade.fade_counter = 0
                start_fade.speed = 5

        screen_scroll, level_complete = player.move()
        if player.is_live:

            writer.write_image('Ammo', 10, 50, 80, 5, bullet_img, player.ammo)
            writer.write_image('Grenades', 10, 80, 110, 3, grenade_img, player.grenades)
            writer.write_text('Killen enemies', player.killen_enemies,10, 110)

            if level_complete:
                start_intro = True
                screen_scroll = 0
                bg_scroll = 0
                level += 1
                if level > len(os.listdir('levels')):
                    level = 1
                    start_game = False
                tile_map = restart_game()
                player = tile_map.process_data()

        else:
            screen_scroll = 0
            if restart_fade.fade():
                if restart_btn.draw():
                    restart_fade.fade_counter = 0
                    restart_fade.speed = 5
                    start_intro = True
                    tile_map = restart_game()
                    bg_scroll = 0
                    player = tile_map.process_data()


        bg_scroll -= screen_scroll


    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and not player.on_air:
                player.is_jumping = True

            if event.key == pygame.K_SPACE:
                player.is_shooting = True

            if event.key == pygame.K_q:
                player.is_grenade_throw = True


pygame.quit()




