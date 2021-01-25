import pygame
import sys
import time
import random

from pygame.locals import *

snap_time = 0
#rainbow_berry_effects = 0
FPS = 15
pygame.init()
fpsClock=pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((255,255,255))
clock = pygame.time.Clock()

pygame.key.set_repeat(1, 40)

GRIDSIZE=10
GRID_WIDTH = SCREEN_WIDTH / GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT / GRIDSIZE
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)
BERRY_TYPES = 5

screen.blit(surface, (0,0))


def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (GRIDSIZE, GRIDSIZE))
    pygame.draw.rect(surf, color, r)

class Snake(object):
    def __init__(self):
        self.lose()
        self.color = (0,0,0)
        self.snap_time = 0


    def get_head_position(self):
        return self.positions[0]

    def lose(self):
        print('You have lost. The game will restart shortly. Press "q" to quit')
        time.sleep(2.5)
        self.length = 1
        self.positions =  [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def point(self, pt):
        if self.length > 1 and (pt[0] * -1, pt[1] * -1) == self.direction:
            return
        else:
            self.direction = pt

    def move(self):
        cur = self.positions[0]
        x, y = self.direction
        # if timer expires, set in_boost_snap to false
        cur_speed_time = time.time()
        if cur_speed_time - self.snap_time >= 5:
            speed = 1
            # print("timer is off " + str(cur_time) + " " + str(self.snap_time))
            self.snap_time = 0
        else:
            speed = 2
            # print("timer is on " + str(cur_time) + str(self.snap_time))

        new = (((cur[0]+(x*speed*GRIDSIZE)) % SCREEN_WIDTH), (cur[1]+(y*speed*GRIDSIZE)) % SCREEN_HEIGHT)
        if len(self.positions) > 2 and new in self.positions[2:]:
            self.lose()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def draw(self, surf):
        for p in self.positions:
            draw_box(surf, self.color, p)

class Apple(object):
    def __init__(self):
        self.position = (0,0)
        self.color = (255,0,0)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE, random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)

    def draw(self, surf):
        draw_box(surf, self.color, self.position)

def check_eat_apple(snake, apple):
    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.randomize()

class Blueberry(object):
    def __init__(self):
        self.position = (0,0)
        self.color = (0,0,255)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE, random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)

    def draw(self, surf):
        draw_box(surf, self.color, self.position)

def check_eat_blueberry(snake, Blueberry):
    if snake.get_head_position() == blueberry.position:
        #start timer for 5-10 seconds
        snake.snap_time = time.time()
        print("""You have eaten a blueberry.
Your speed will be doubled for the next 5 seconds.
_______________________________________________________""")
        time.sleep(1)
        snake.length += 5
        Blueberry.randomize()




class Rock (object):
    def __init__(self):
        self.position = (0,0)
        self.color = (160,80,30)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE,
        random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)

    def draw(self, surf):
        draw_box(surf, self.color, self.position)

def check_smash_rock(snake, rock):
    if snake.get_head_position() == rock.position:
        snake.lose()


class Thorns (object):
    def __init__(self):
        self.position = (0,0)
        self.color = (50,135,50)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE,
        random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)

    def draw(self, surf):
        draw_box(surf, self.color, self.position)

def check_smash_thorns(snake, thorns):
    if snake.get_head_position() == thorns.position:
        snake.lose()






if __name__ == '__main__':
    #snake
    snake = Snake()

    #fruits
    apple = Apple()
    blueberry = Blueberry()
    #obstacles
    rock = Rock()
    thorns = Thorns()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    snake.point(UP)
                elif event.key == K_DOWN or event.key == K_s:
                    snake.point(DOWN)
                elif event.key == K_LEFT or event.key == K_a:
                    snake.point(LEFT)
                elif event.key == K_RIGHT or event.key == K_d:
                    snake.point(RIGHT)
                elif event.key == K_q:
                    sys.exit()


        surface.fill((255,255,255))
        snake.move()

        #checking for collision
        check_eat_apple(snake, apple)
        check_eat_blueberry(snake, blueberry)
        check_smash_thorns(snake, thorns)
        check_smash_rock(snake, rock)

        #drawing everything
        snake.draw(surface)
        apple.draw(surface)
        blueberry.draw(surface)
        rock.draw(surface)
        thorns.draw(surface)

        #displaying the score
        font = pygame.font.Font(None, 36)
        text = font.render(str(snake.length), 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = 20
        surface.blit(text, textpos)
        screen.blit(surface, (0,0))

        #updating the screen
        pygame.display.flip()
        pygame.display.update()
        fpsClock.tick(FPS + snake.length/3)
