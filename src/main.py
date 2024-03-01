import pygame
from pygame.locals import *
import random
from pygame.sprite import Group, Sprite

pygame.init()

game_width = 800
game_height = 600
size = (game_width, game_height)
padding = 15
game_screen = pygame.display.set_mode(size)
pygame.display.set_caption('Space Invaders')

black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

alien_direction_x = 1
alien_direction_y = 0
count_direction_x_changes = 0

player_speed = 8
player_lives = 5
missile_cooldown = 500

# frames per second
fps = 30
clock = pygame.time.Clock()


def write_text(text, color, pos_x, pos_y):
    text = font.render(text, True, color)
    text_rect = text.get_rect()
    text_rect.center = (pos_x, pos_y)
    game_screen.blit(text, text_rect)


class Missile(Sprite):

    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.rect = Rect(pos_x - 2, pos_y, 4, 8)

    def update(self):
        self.rect.y -= 5

        if self.rect.bottom > 0:
            for w in range(self.rect.width):
                for h in range(self.rect.height):
                    game_screen.set_at((self.rect.x + w, self.rect.y - h), yellow)
        else:
            self.kill()

        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()


spaceship_group = Group()
alien_group = Group()
missile_group = Group()
alien_missile_group = Group()
star_group = Group()


# noinspection PyTypeChecker
class Spaceship(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('../resources/spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

        self.lives = player_lives
        self.lives_left = player_lives

        self.last_missile = pygame.time.get_ticks() - missile_cooldown

    def update(self):

        # draw health bar
        for life in range(self.lives):

            health_x = int(game_width / self.lives * life)
            health_y = game_height - padding

            if life < self.lives_left:
                pygame.draw.rect(game_screen, green, (health_x, health_y, int(game_width / self.lives), padding))
            else:
                pygame.draw.rect(game_screen, red, (health_x, health_y, int(game_width / self.lives), padding))

        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and self.rect.left > padding / 2:
            self.rect.x -= player_speed
        elif keys[K_RIGHT] and self.rect.right < game_width - padding / 2:
            self.rect.x += player_speed

        if keys[K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_missile > missile_cooldown:
                missile = Missile(self.rect.centerx, self.rect.y)
                missile_group.add(missile)

                self.last_missile = current_time


# noinspection PyTypeChecker
class Alien(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y, image_filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

    def update(self):
        self.rect.x += alien_direction_x
        self.rect.y += alien_direction_y

        alien_fire_probability = 1

        max_alien_missiles = 3

        fire_chance = random.randint(0, 100)
        if fire_chance < alien_fire_probability and len(alien_missile_group.sprites()) < max_alien_missiles:
            alien_missile = AlienMissile(self.rect.centerx, self.rect.y)
            alien_missile_group.add(alien_missile)


class AlienMissile(Missile):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)

    def update(self):

        self.rect.y += 5

        if self.rect.top <= game_height:
            for w in range(self.rect.width):
                for h in range(self.rect.height):
                    game_screen.set_at((self.rect.x + w, self.rect.y - h), red)
        else:
            self.kill()

        if pygame.sprite.spritecollide(self, spaceship_group, False):
            self.kill()
            spaceship.lives_left -= 1


class Star(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(pos_x, pos_y, 2, 2)

    def update(self):
        game_screen.set_at((self.rect.x, self.rect.y), white)


for i in range(500):
    star = Star(random.randint(0, game_width - 1), random.randint(0, game_height - 1))
    # noinspection PyTypeChecker
    star_group.add(star)

spaceship = Spaceship(int(game_width / 2), int(game_height - 2 * padding))
# noinspection PyTypeChecker
spaceship_group.add(spaceship)


def create_aliens(group):
    # alien images
    image_filenames = [
        '../resources/alien_red.png',
        '../resources/alien_purple.png',
        '../resources/alien_orange.png',
        '../resources/alien_green.png'
    ]

    group.empty()

    # number of rows and columns of aliens
    rows_aliens = 4
    cols_aliens = 12

    for row in range(rows_aliens):
        for col in range(cols_aliens // 2 * -1, cols_aliens - cols_aliens // 2):
            group.add(Alien(game_width / 2 - 50 * col, padding + row * 40, image_filenames[row]))


create_aliens(alien_group)

# define the boundaries of the leftmost and rightmost aliens
aliens_left_bound = alien_group.sprites()[-1].rect.left
aliens_right_bound = alien_group.sprites()[0].rect.right

# game variables
game_status = 'new game'
ready_countdown = 0

font = pygame.font.Font(pygame.font.get_default_font(), 16)

# game loop
running = True
while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # draw the background
    game_screen.fill(black)
    star_group.update()

    # draw the spaceship
    spaceship_group.draw(game_screen)

    # draw the aliens
    alien_group.draw(game_screen)

    # check if aliens need to change direction
    aliens_left_bound += alien_direction_x
    aliens_right_bound += alien_direction_x
    if aliens_left_bound <= padding or aliens_right_bound >= game_width - padding:
        alien_direction_x *= -1
        count_direction_x_changes += 1

    # after three x direction changes, move the aliens down
    if count_direction_x_changes < 3:
        alien_direction_y = 0
    else:
        alien_direction_y = 50
        count_direction_x_changes = 0

    # check if the left/right bounds need to be updated
    if len(alien_group.sprites()) > 0:
        aliens_left_bound = alien_group.sprites()[0].rect.left
        aliens_right_bound = alien_group.sprites()[-1].rect.right
    for alien in alien_group.sprites():
        if alien.rect.left < aliens_left_bound:
            aliens_left_bound = alien.rect.left
        if alien.rect.right > aliens_right_bound:
            aliens_right_bound = alien.rect.right

    if game_status == 'new game':
        # display start screen
        write_text('Space Invaders', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to Start', white, game_width / 2, game_height / 2 + 50)
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'playing'
            ready_countdown = 3

    elif game_status == 'playing':
        if ready_countdown >= 0:

            write_text(str(ready_countdown), white, game_width / 2, game_height / 2)

            countdown_timer = pygame.time.get_ticks()
            pygame.time.delay(1000)
            ready_countdown -= 1
            pygame.display.update()

        else:
            spaceship_group.update()
            alien_group.update()
            missile_group.update()
            alien_missile_group.update()

        if len(alien_group.sprites()) == 0:
            game_status = 'cleared'
        elif spaceship.lives_left == 0:
            game_status = 'game over'
        for alien in alien_group.sprites():
            if alien.rect.bottom > spaceship.rect.top:
                game_status = 'game over'

    elif game_status == 'cleared':
        write_text('Game Cleared', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to play again', white, game_width / 2, game_height / 2 + 50)

        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'restart'

    elif game_status == 'game over':
        write_text('Game Over', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to play again', white, game_width / 2, game_height / 2 + 50)

        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'restart'

    elif game_status == 'restart':
        create_aliens(alien_group)
        alien_direction_x = 1
        alien_direction_y = 0
        count_direction_x_changes = 0
        aliens_left_bound = alien_group.sprites()[0].rect.left
        aliens_right_bound = alien_group.sprites()[-1].rect.right

        spaceship.rect.centerx = int(game_width / 2)
        spaceship.lives_left = spaceship.lives

        missile_group.empty()
        alien_missile_group.empty()

        ready_countdown = 3

        game_status = 'playing'

    pygame.display.update()

pygame.quit()
