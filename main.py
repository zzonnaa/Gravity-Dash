from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint
import pygame
from os.path import join
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Gravity Dash')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets()
        self.setup()

        # score
        self.score = 0
        self.high_score = self.load_high_score()

        # font
        self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
        self.text_color = (255, 255, 255)

        # timers 
        self.bee_timer = Timer(600, func=self.create_bee, autostart=True, repeat=True)

    def create_bee(self):
        Bee(frames=self.bee_frames, 
            pos=((self.level_width + WINDOW_WIDTH), (randint(0, self.level_height))), 
            groups=(self.all_sprites, self.enemy_sprites),
            speed=randint(300, 500))

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')

        # sounds 
        self.audio = audio_importer('audio')


    def game_over(self):
        self.audio['music'].stop()
        self.save_high_score()

        game_over_screen = True
        while game_over_screen:
            self.display_surface.fill((0, 0, 0))
            game_over_text = self.font.render("Game Over", True, (255, 0, 0))
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
            restart_text = self.font.render("Press R to Restart", True, (200, 200, 200))

            self.display_surface.blit(game_over_text, (WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 - 80))
            self.display_surface.blit(score_text, (WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 - 40))
            self.display_surface.blit(high_score_text, (WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2))
            self.display_surface.blit(restart_text, (WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 40))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        self.run()
                        return

    def check_player_fall(self):
        if self.player.rect.top > WINDOW_HEIGHT + 1000:
            self.game_over()

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet)
            if obj.name == 'Worm':
                Worm(self.worm_frames, pygame.FRect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        self.audio['music'].play(loops=-1)

    def collision(self):
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    if isinstance(sprite, Bee):
                        self.score += 10
                    elif isinstance(sprite, Worm):
                        self.score += 5
                    sprite.destroy()

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, self.text_color)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, self.text_color)

        score_width = score_text.get_width()
        high_score_width = high_score_text.get_width()

        x_position = WINDOW_WIDTH - max(score_width, high_score_width) - 20

        self.display_surface.blit(score_text, (x_position, 10))
        self.display_surface.blit(high_score_text, (x_position, 40))

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # if event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_p:
                #         self.pause_game()

            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()
            self.check_player_fall()

            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(self.player.rect.center)
            self.draw_score()
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()