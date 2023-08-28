import pygame
import csv
import os
from configs import *
from pygame.image import load
from pygame.key import get_pressed as keys

class Background:
    def __init__(self):
        self.images = self.get_images()
        self.scroll = 0
        self.scroll_right = False
        self.scroll_left = False


    def get_images(self):
        images = []
        for key, value in BG_IMG.items():
            img = load(value[0])
            img = pygame.transform.scale(img, (1200, value[1]))
            images.append(img)
        return images

    def draw(self, window, scroll):
        width = self.images[0].get_width()
        for x in range(4):
            window.blit(self.images[0], ((x * width) - scroll * 0.5, 0))
            window.blit(self.images[1], ((x * width) - scroll * 0.6, 100))
            window.blit(self.images[2], ((x * width) - scroll * 0.7, 230))
            window.blit(self.images[3], ((x * width) - scroll * 0.8, 280))

class TileImages:

    def __init__(self):
        self.images = self.get_images()

    def get_images(self):
        images = []
        for index, path in TILE_DATA.items():
            img = load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            images.append(img)
        return images

class Tile(pygame.sprite.Sprite):
    def __init__(self, img, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = rect
        self.scroll = 0

    def draw(self, window):
        window.blit(self.image, (self.rect.x - self.scroll, self.rect.y))

    def update(self, screen_scroll):
        self.scroll += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = rect
        self.scroll = 0

    def draw(self, window):
        window.blit(self.image, (self.rect.x - self.scroll, self.rect.y))

    def update(self, screen_scroll):
        self.scroll += screen_scroll

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = rect
        self.scroll = 0

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def update(self, screen_scroll):
        self.scroll += screen_scroll

class Solider(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, speed, scale=(40, 60)):
        pygame.sprite.Sprite.__init__(self)
        self.obstacle_list = []
        self.char_type = char_type
        self.images = self.get_anim_images(scale)

        self.health = 100
        self.max_health = self.health
        self.alive = True

        self.ammo = 20
        self.grenade = 5

        self.speed = speed
        self.move_right = False
        self.move_left = False
        self.jumping = False
        self.jump_button = False
        self.jump_force = 10
        self.vel_y = -10

        self.action = 0
        self.frame_index = 0
        self.direction = 1

        self.shooting = False
        self.tick = pygame.time.get_ticks()

        self.image = self.images[self.action][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_anim_images(self, scale: tuple):
        data = []
        dir_names = ['Idle', 'Run', 'Jump', 'Death']
        for i in range(4):
            length = len(os.listdir(f'images/player/{dir_names[i]}'))
            images = []
            for j in range(length):
                image = load(f'images/{self.char_type}/{dir_names[i]}/{j}.png')
                image = pygame.transform.scale(image, scale)
                images.append(image)
            data.append(images)
        return data

    def draw(self, window):
        window.blit(self.image, self.rect)
        pygame.draw.rect(window, 'red', self.rect, 1)

    def update(self):
        self.get_action()
        self.animate()
        screen_scroll = self.move()
        self.jump()
        return screen_scroll

    def animate(self):
        if self.frame_index // 7 > len(self.images[self.action]) - 1:
            self.frame_index = 0

        image = self.images[self.action][self.frame_index // 7]
        self.image = pygame.transform.flip(image, self.direction - 1, 0)

        self.frame_index += 1

    def move(self):
        self.event_key()
        dx = 0
        screen_scroll = 0

        if self.move_right:
            dx = self.speed

        if self.move_left:
            dx = -self.speed

        for tile in self.obstacle_list:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0


        self.rect.x += dx
        screen_scroll += dx
        return screen_scroll

    def event_key(self):
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

    def get_action(self):
        if self.jump_button:
            self.action = 2
        else:
            if self.move_right or self.move_left:
                self.action = 1

            else:
                self.action = 0

    def jump(self):
        dy = 0

        if self.jumping:
            self.vel_y = -15
            self.jumping = False

        self.vel_y += 1
        dy += self.vel_y

        for tile in self.obstacle_list:
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                dy = -self.rect.bottom + tile.rect.top
                self.vel_y = 0
                self.jump_button = False

        self.rect.y += dy

class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, obstacles):
        pygame.sprite.Sprite.__init__(self)
        self.obstacle_list = obstacles
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction
        self.speed = 2

    def get_image(self):
        image = load('images/icons/blt.png').convert_alpha()
        image = pygame.transform.scale(image, (32, 32))
        return image

    def draw(self, window):
        window.blit(self.image, self.rect)

    def update(self):
        self.rect.x += self.direction * self.speed

        for tile in self.obstacle_list:
            if tile.rect.colliderect(self.rect.x - (self.direction * self.rect.size[0] // 2), self.rect.y, self.rect.width, self.rect.height):
                self.kill()









