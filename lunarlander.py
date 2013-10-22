#!/usr/bin/env python

import pygame
import sys
import time
import os
import random
import math

from pygame.locals import RLEACCEL, QUIT, K_r, K_SPACE, K_UP, K_LEFT, K_RIGHT
#from pygame.locals import *

FPS = 80

pygame.init()

fpsClock=pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ARENA_WIDTH, ARENA_HEIGHT = 10 * SCREEN_WIDTH, 10 * SCREEN_HEIGHT 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((255,255,255))
clock = pygame.time.Clock()

pygame.key.set_repeat(1, 1)

def load_image(name, colorkey=None):
    fullname = os.path.join('lunarlander', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class V(object):
    """
    A simple class to keep track of vectors, including initializing
    from Cartesian and polar forms.
    """
    def __init__(self, x=0, y=0, angle=None, magnitude=None):
        self.x = x
        self.y = y

        if (angle is not None and magnitude is not None):
            self.x = magnitude * math.sin(math.radians(angle))
            self.y = magnitude * math.cos(math.radians(angle))

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    @property
    def angle(self):
        if self.y == 0:
            if self.x > 0:
                return 90.0
            else:
                return 270.0
        if math.floor(self.x) == 0:
            if self.y < 0:
                return 180.0
        return math.degrees(math.atan(self.x / float(self.y)))

    def __add__(self, other):
        return V(x=(self.x + other.x), y=(self.y + other.y))

    def rotate(self, angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        self.x = self.x * c - self.y * s
        self.y = self.x * s + self.y * c

    def __str__(self):
        return "X: %.3d Y: %.3d Angle: %.3d degrees Magnitude: %.3d" % (self.x, self.y, self.angle, self.magnitude)

class Lander(pygame.sprite.DirtySprite):
    """
    Our intrepid lunar lander!
    """
    def __init__(self):
        self.image, self.rect = load_image('lander.jpg', -1)
        
        self.original = self.image
        self.original_flame, self.flame_rect = load_image('lander_flame.jpg', -1)
        
        self.mass = 10
        self.orientation = 0.0                       # 
        self.rect.topleft = ((SCREEN_WIDTH / 2), 20) # The starting point.
        self.engine_power = 2   # The power of the engine.
        self.velocity = V(0.0,0.0) # Starting velocity. 
        self.landed = False        # Have we landed yet?
        self.intact = True         # Is the ship still shipshape?
        self.fuel = 100            # Units of fuel
        self.boosting = 0          # Are we in "boost" mode? (show the flame graphic)
        return super(pygame.sprite.DirtySprite, self).__init__()

    def update_image(self):
        """
        Update our image based on orientation and engine state of the craft.
        """
        img = self.original_flame if self.boosting else self.original
        center = self.rect.center
        self.image = pygame.transform.rotate(img, -1 * self.orientation)
        self.rect = self.image.get_rect(center=center)

    def rotate(self, angle):
        """
        Rotate the craft.
        """
        self.orientation += angle

    def boost(self):
        """
        Provide a boost to our craft's velocity in whatever orientation we're currently facing. 
        """
        if not self.fuel: return
        self.velocity += V(magnitude=self.engine_power, angle=self.orientation)
        self.fuel -= 1
        if self.landed:
            self.landed = False
            np = self.rect.move(0, -5)
            self.rect = np
        self.boosting = 3
    
    def physics_update(self):
        if not self.landed:
            self.velocity += V(magnitude=.5, angle=180)

    def ok_to_land(self):
        return (self.orientation < 10 or self.orientation > 350) and self.velocity.magnitude < 5

    def check_landed(self, surface):
        if self.landed: return
        if hasattr(surface, "radius"):
            collision = pygame.sprite.collide_circle(self, surface)
        else:
            collision = pygame.sprite.collide_rect(self, surface)
        if collision:
            self.landed = True
            if self.ok_to_land() and surface.landing_ok:
                self.intact = True
            else:
                # Hard landing, kaboom!
                self.intact = False
            self.velocity = V(0.0,0.0)                       # In any case, we stop moving.

    def update(self):
        self.physics_update()   # Iterate physics
        if self.boosting:
            self.boosting -= 1  # Tick over engine time
        self.update_image()
        np = self.rect.move(self.velocity.x, -1 * self.velocity.y)
        self.rect = np
        self.dirty = True
            
    def explode(self, screen):
        for i in range(random.randint(20,40)):
            pygame.draw.line(screen, 
                             (random.randint(190, 255), 
                              random.randint(0,100), 
                              random.randint(0,100)), 
                             self.rect.center, 
                             (random.randint(0, SCREEN_WIDTH), 
                              random.randint(0, SCREEN_HEIGHT)), 
                             random.randint(1,3))

    def stats(self):
        return "Position: [%.2d,%.2d] Velocity: %.2f m/s at %.3d degrees Orientation: %.3d degrees  Fuel: %d Status: [%s]" % (self.rect.top, self.rect.left, self.velocity.magnitude, self.velocity.angle, self.orientation, self.fuel, ("Crashed" if not self.intact else ("Landed" if self.landed else ("OK to Land" if self.ok_to_land() else "Not OK"))))


class Moon(pygame.sprite.DirtySprite):
    def __init__(self):
        self.width = SCREEN_WIDTH+20
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(-10, SCREEN_HEIGHT - 20, SCREEN_WIDTH + 20, 20)
        self.landing_ok = True
        return super(pygame.sprite.DirtySprite, self).__init__()


class Boulder(pygame.sprite.DirtySprite):
    def __init__(self):
        self.diameter = random.randint(2, 300)
        self.radius = self.diameter / 2
        self.x_pos = random.randint(0, SCREEN_WIDTH)
        self.image = pygame.Surface((self.diameter, self.diameter))
        #self.image.fill((255,255,255,128))
        pygame.draw.circle(self.image, (128,128,128), (self.radius, self.radius), self.radius)
        self.rect = pygame.Rect(self.x_pos, SCREEN_HEIGHT - (20 + self.radius), 
                                self.diameter, self.diameter)
        self.image = self.image.convert()
        self.landing_ok = False
        self.dirty = False
        return super(pygame.sprite.DirtySprite, self).__init__()

        
def initialize():        
    lander = Lander()
    moon = Moon()
    sprites = [lander]
    boulders = [Boulder() for i in range(random.randint(2,5))]
    sprites.extend(boulders)
    sprites.append(moon)
    return lander, moon, boulders, pygame.sprite.RenderPlain(sprites)


if __name__ == '__main__':

    lander, moon, boulders, allsprites = initialize()

    while True:
        
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        if keys[K_r]:
            lander, moon, boulders, allsprites = initialize()
        elif keys[K_SPACE] or keys[K_UP]:
            lander.boost()
        elif keys[K_LEFT]:
            lander.rotate(-5)
        elif keys[K_RIGHT]:
            lander.rotate(5)

        lander.check_landed(moon)
        for boulder in boulders:
            lander.check_landed(boulder)

        surface.fill((255,255,255))

        font = pygame.font.Font(None, 14)

        text = font.render(lander.stats(), 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = SCREEN_WIDTH / 2
        surface.blit(text, textpos)
        screen.blit(surface, (0,0))
        allsprites.update()
        allsprites.draw(screen)

        def render_center_text(surface, screen, txt, color):
            font2 = pygame.font.Font(None, 36)
            text = font2.render(txt, 1, color)
            textpos = text.get_rect()
            textpos.centerx = SCREEN_WIDTH / 2
            textpos.centery = SCREEN_HEIGHT / 2
            surface.blit(text, textpos)
            screen.blit(surface, (0,0))

        if lander.landed:
            if not lander.intact:
                lander.explode(screen)
                #render_center_text(surface, screen, "Kaboom! Your craft is destroyed.", (255,0,0))
            else:
                render_center_text(surface, screen, "You landed successfully!", (0,255,0))

            pygame.display.flip()
            pygame.display.update()
            time.sleep(1)
            lander, moon, boulders, allsprites = initialize()
        else:
            pygame.display.flip()
            pygame.display.update()

        fpsClock.tick(FPS) # and tick the clock.
