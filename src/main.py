import sys
import pygame
from pygame.locals import *
import random
from pygame.sprite import Group, Sprite
from options import load_pref, save_pref

pygame.init()

game_width = 800
game_height = 600
size = (game_width, game_height)
padding = 15
game_screen = pygame.display.set_mode(size)
pygame.display.set_caption('Space Invaders')

black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)

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
    text = font_large.render(text, True, color)
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
            invader_killed.play()


spaceship_group = Group()
alien_group = Group()
missile_group = Group()
alien_missile_group = Group()
star_group = Group()

invader_killed = pygame.mixer.Sound("../resources/sounds/invader_killed.wav")
invader_killed.set_volume(0.1)
invader_shoot = pygame.mixer.Sound("../resources/sounds/invader_shoot.wav")
invader_shoot.set_volume(0.1)
shoot = pygame.mixer.Sound("../resources/sounds/shoot.wav")
shoot.set_volume(0.1)


# noinspection PyTypeChecker
class Spaceship(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('../resources/images/spaceship.png'), (48, 27))
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

        self.lives = player_lives
        self.lives_left = player_lives

        self.last_missile = pygame.time.get_ticks() - missile_cooldown

    def update(self):

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
                shoot.play()

                self.last_missile = current_time


# noinspection PyTypeChecker
class Alien(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y, image_filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(image_filename), (42, 27))
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
            invader_shoot.play()


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
            invader_killed.play()


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
        '../resources/images/alien_red.png',
        '../resources/images/alien_purple.png',
        '../resources/images/alien_orange.png',
        '../resources/images/alien_green.png'
    ]

    group.empty()

    # number of rows and columns of aliens
    rows_aliens = 4
    cols_aliens = 10

    for row in range(rows_aliens):
        for col in range(cols_aliens // 2 * -1, cols_aliens - cols_aliens // 2):
            group.add(Alien(game_width / 2 - 60 * col - 20, padding + row * 40, image_filenames[row]))


def game():
    global alien_direction_x
    global alien_direction_y
    global count_direction_x_changes
    alien_direction_x = 1
    alien_direction_y = 0
    count_direction_x_changes = 0

    volume = 50

    params = load_pref()
    if params:
        volume = params['volume']

    shoot.set_volume(0.01*volume)
    invader_shoot.set_volume(0.01 * volume)
    invader_killed.set_volume(0.01 * volume)

    create_aliens(alien_group)

    aliens_left_bound = alien_group.sprites()[-1].rect.left
    aliens_right_bound = alien_group.sprites()[0].rect.right

    game_status = 'new game'
    ready_countdown = 0

    running = True
    while running:

        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        game_screen.fill(black)
        star_group.update()

        spaceship_group.draw(game_screen)
        alien_group.draw(game_screen)

        aliens_left_bound += alien_direction_x
        aliens_right_bound += alien_direction_x
        if aliens_left_bound <= padding or aliens_right_bound >= game_width - padding:
            alien_direction_x *= -1
            count_direction_x_changes += 1

        if count_direction_x_changes < 3:
            alien_direction_y = 0
        else:
            alien_direction_y = 50
            count_direction_x_changes = 0

        if len(alien_group.sprites()) > 0:
            aliens_left_bound = alien_group.sprites()[0].rect.left
            aliens_right_bound = alien_group.sprites()[-1].rect.right
        for alien in alien_group.sprites():
            if alien.rect.left < aliens_left_bound:
                aliens_left_bound = alien.rect.left
            if alien.rect.right > aliens_right_bound:
                aliens_right_bound = alien.rect.right

        if game_status == 'new game':
            game_status = 'playing'
            ready_countdown = 3

        elif game_status == 'playing':
            if ready_countdown >= 0:

                write_text(str(ready_countdown), white, game_width / 2, game_height / 2)

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
            key = pygame.key.get_pressed()
            if key[K_ESCAPE]:
                missile_group.empty()
                alien_missile_group.empty()
                main_menu()

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


def quit_game():
    pygame.quit()
    sys.exit()


def options():
    volume = 50

    params = load_pref()
    if params:
        volume = params['volume']

    while True:
        game_screen.fill(black)
        star_group.update()
        text_options = font_large.render("Options", True, (255, 255, 255))
        game_screen.blit(text_options, text_options.get_rect(center=(game_screen.get_width() // 4, 50)))

        button_width = 200
        button_height = 50
        button_left = game_screen.get_width() // 2 - button_width // 2
        button_top = 200
        save_button = pygame.Rect(game_screen.get_width() // 2 - button_width - 25, button_top + 200, button_width,
                                  button_height)
        save_color = (0, 155, 0)
        cancel_button = pygame.Rect(game_screen.get_width() // 2 + 25, button_top + 200, button_width, button_height)
        cancel_color = (155, 0, 0)

        pygame.draw.rect(game_screen, white, (button_left, button_top + 115, button_width, 10))
        volume_rect = pygame.Rect(button_left + volume, 305, 10, 30)
        volume_color = (0, 155, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                    game()
                if event.key == pygame.K_m:
                    main_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if save_button.collidepoint(mx, my):
                    params['volume'] = volume
                    save_pref(params)
                    main_menu()
                elif cancel_button.collidepoint(mx, my):
                    main_menu()
                if pygame.mouse.get_pressed()[0] and button_left <= mx <= button_left+button_width and 280 <= my <= 350:
                    volume = pygame.mouse.get_pos()[0] - button_left
        mx, my = pygame.mouse.get_pos()
        if save_button.collidepoint(mx, my):
            save_color = green
        elif pygame.Rect(button_left, button_top + 110, button_width, 30).collidepoint(mx, my):
            volume_color = green
        elif cancel_button.collidepoint(mx, my):
            cancel_color = red
        volume_text = font_small.render("Volume : ", True, white)
        game_screen.blit(volume_text, volume_text.get_rect(
            center=(button_left + button_width // 2 - 50, 260 + button_height // 2)))
        volume_text2 = font_small.render(str(volume // 2) + " %", True, volume_color)
        game_screen.blit(volume_text2, volume_text2.get_rect(
            center=(button_left + button_width - 30, 260 + button_height // 2)))
        pygame.draw.rect(game_screen, save_color, save_button)
        pygame.draw.rect(game_screen, volume_color, volume_rect)
        save_text = font_small.render("Save", True, white)
        game_screen.blit(save_text, save_text.get_rect(
            center=(game_screen.get_width() // 2 - button_width - 25 + button_width // 2, 400 + button_height // 2)))
        pygame.draw.rect(game_screen, cancel_color, cancel_button)
        cancel_text = font_small.render("Cancel", True, white)
        game_screen.blit(cancel_text,
                         cancel_text.get_rect(
                             center=(game_screen.get_width() // 2 + 25 + button_width // 2, 400 + button_height // 2)))
        pygame.display.update()


def main_menu():
    button_width = 200
    button_height = 50
    button_left = game_screen.get_width() // 2 - button_width // 2
    button_top = 200
    button_play = pygame.Rect(button_left, button_top, button_width, button_height)
    button_options = pygame.Rect(button_left, button_top + 100, button_width, button_height)
    button_exit = pygame.Rect(button_left, button_top + 200, button_width, button_height)

    while True:
        game_screen.fill(black)
        star_group.update()
        text_play = font_small.render("Play", True, white)
        text_options = font_small.render("Options", True, white)
        text_exit = font_small.render("Exit", True, white)
        mx, my = pygame.mouse.get_pos()
        play_color = (0, 0, 155)
        options_color = (0, 155, 0)
        exit_color = (155, 0, 0)
        if button_play.collidepoint(mx, my):
            play_color = blue
        elif button_options.collidepoint(mx, my):
            options_color = green
        elif button_exit.collidepoint(mx, my):
            exit_color = red

        buttons = [(button_play, play_color), (button_options, options_color), (button_exit, exit_color)]

        for button in buttons:
            pygame.draw.rect(game_screen, button[1], button[0])

        game_screen.blit(text_play,
                         text_play.get_rect(center=(button_left + button_width // 2, button_top + button_height // 2)))
        game_screen.blit(text_options,
                         text_options.get_rect(
                             center=(button_left + button_width // 2, button_top + 100 + button_height // 2)))
        game_screen.blit(text_exit,
                         text_exit.get_rect(
                             center=(button_left + button_width // 2, button_top + 200 + button_height // 2)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    game()
                if button_options.collidepoint(mx, my):
                    options()
                if button_exit.collidepoint(mx, my):
                    quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if event.key == pygame.K_g:
                    game()
                if event.key == pygame.K_o:
                    options()
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
