#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import random
import sys
import pygame

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrome Dino Runner")

# Try to load icon, fallback if missing
try:
    Ico = pygame.image.load("assets/DinoWallpaper.png")
    pygame.display.set_icon(Ico)
except:
    pass

# Load Assets safely
def load_img(path, name):
    try:
        return pygame.image.load(os.path.join(path, name))
    except:
        # Fallback surface if assets are missing locally
        surf = pygame.Surface((40, 40))
        surf.fill((128, 128, 128))
        return surf

RUNNING = [load_img("assets/Dino", "DinoRun1.png"), load_img("assets/Dino", "DinoRun2.png")]
JUMPING = load_img("assets/Dino", "DinoJump.png")
DUCKING = [load_img("assets/Dino", "DinoDuck1.png"), load_img("assets/Dino", "DinoDuck2.png")]

SMALL_CACTUS = [load_img("assets/Cactus", "SmallCactus1.png"), load_img("assets/Cactus", "SmallCactus2.png"), load_img("assets/Cactus", "SmallCactus3.png")]
LARGE_CACTUS = [load_img("assets/Cactus", "LargeCactus1.png"), load_img("assets/Cactus", "LargeCactus2.png"), load_img("assets/Cactus", "LargeCactus3.png")]
BIRD = [load_img("assets/Bird", "Bird1.png"), load_img("assets/Bird", "Bird2.png")]

CLOUD = load_img("assets/Other", "Cloud.png")
BG = load_img("assets/Other", "Track.png")

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck: self.duck()
        if self.dino_run: self.run()
        if self.dino_jump: self.jump()

        if self.step_index >= 10: self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.dino_jump:
            self.dino_duck = self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = self.dino_jump = False
            self.dino_run = True

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop(0)

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300

class Bird(Obstacle):
    BIRD_HEIGHTS = [250, 290, 320]
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9: self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1

def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 14
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font(None, 22)
    obstacles = []
    pause = False

    # Initialize highscore file safely
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f: f.write("0")

    def score(current_color):
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        with open("score.txt", "r") as f:
            try: score_ints = [int(x) for x in f.read().split()]
            except: score_ints = [0]
            highscore = max(score_ints) if score_ints else 0
            if points > highscore: highscore = points
        text = font.render(f"High Score: {highscore}  Points: {points}", True, current_color)
        SCREEN.blit(text, (750, 40))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def paused(current_color):
        nonlocal pause, run
        pause = True
        p_font = pygame.font.Font(None, 30)
        text = p_font.render("Game Paused, Press 'u' to Unpause", True, current_color)
        SCREEN.blit(text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3))
        pygame.display.update()
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    pause = False
                    run = True

    while run:
        clock.tick(30)
        current_hour = datetime.datetime.now().hour
        is_day = 7 < current_hour < 19
        bg_color = (255, 255, 255) if is_day else (40, 40, 40)
        font_color = (0, 0, 0) if is_day else (255, 255, 255)
        
        SCREEN.fill(bg_color)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused(font_color)

        userInput = pygame.key.get_pressed()

        background()
        cloud.draw(SCREEN)
        cloud.update()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            rand_choice = random.randint(0, 2)
            if rand_choice == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif rand_choice == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif rand_choice == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                # Save final high score on hit
                with open("score.txt", "r+") as f:
                    try: val = max([int(x) for x in f.read().split()] + [points])
                    except: val = points
                    f.seek(0)
                    f.write(str(val))
                run = False

        score(font_color)
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
