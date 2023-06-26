############## INITIALIZATION ##############

'''
TODO

- saving system
- restarting game
- menus
'''

'''
CONTROLS

space / lmb to jump
jump to start the game
f3 to show debug information
to restart reopen program
'''

import pygame as pg
import easing_functions as easing
import draw
import random

pg.init()

windowx = 400
windowy = 400
cx = 400
cy = 400
clock = pg.time.Clock()
fps = 60
dfps = 0.0

window = pg.display.set_mode((windowx,windowy), pg.RESIZABLE | pg.DOUBLEBUF)
running = True
pg.display.set_caption('Flappy Bird')
screen = pg.Surface((windowx, windowy))
draw.def_surface = screen

halfx = windowx//2
halfy = windowy//2


# app functions


# app classes

class Player:
    def __init__(self):
        self.image = sprites['player']
        self.moving = False
        self.vel = 0
        self.pos = 200
        self.jump_speed = -5
        self.dead = False
        self.effect = False
        self.death_rect_pos = 0
        self.calc_rect()

    def calc_rect(self):
        self.rect = pg.Rect(110,self.pos, 80,30)

    def die(self, pos=200, effect=True):
        if self.dead: return
        self.dead = True
        self.vel = self.jump_speed
        self.effect = effect
        self.death_rect_pos = pos

    def jump(self):
        if self.dead: return
        if not self.moving: self.moving = True

        self.vel = self.jump_speed
        # self.vel -= 0.4

    def update(self, towers):
        if self.moving:
            self.vel += 0.2
            self.pos += self.vel
            if self.pos > 500:
                self.pos = 500

        if jumped:
            self.jump()

        self.calc_rect()
        
        collision = self.rect.collidelistall(towers)
        if collision:
            pos = towers[collision[0]].x+25
            self.die(pos)
        if self.pos < 0 or self.pos > 370:
            self.die(effect=False)

    def draw(self):
        image = self.image.copy()
        image = pg.transform.rotate(image, -self.vel*4)
        rect = image.get_rect()
        rect.center = self.rect.center
        screen.blit(image, rect)


class Towers:
    def __init__(self):
        self.image_top = sprites['tower_top']
        self.image_bottom = sprites['tower_btm']
        self.xpos = 400
        self.ypos = random.randint(100,300)
        self.deletable = False
        self.gave_points = False
        self.calc_rects()

    def calc_rects(self):
        self.top = pg.Rect(self.xpos, self.ypos-370, 50,300)
        self.bottom = pg.Rect(self.xpos, self.ypos+70, 50,300)

    def draw(self):
        screen.blit(self.image_top, (self.top[0], self.top[1]+10))
        screen.blit(self.image_bottom, (self.bottom[0], self.bottom[1]-10))

    def update(self):
        self.xpos -= SPEED
        self.calc_rects()

        if self.xpos < -40:
            self.deletable = True

    def to_rects(self):
        return [self.top, self.bottom]
    

class Particle:
    def __init__(self, image, pos, size, vel=(0,0), gravity=(0,0), lifetime=60, alpha=255, rotation=0, rotation_vel=0):
        self.image = image
        self.pos = list(pos)
        self.vel = list(vel)
        self.size = size
        self.key = 0
        self.lifetime = lifetime
        self.gravity = gravity
        self.alpha = alpha
        self.rotation = rotation
        self.rvel = rotation_vel
        self.deletable = False

    def draw(self):
        size = easing.QuinticEaseOut(0,1,self.lifetime).ease(self.key)
        sizex = size*self.size[0]
        sizey = size*self.size[1]
        alpha = easing.QuinticEaseIn(255,0,self.lifetime).ease(self.key)

        c = self.image.copy()
        c.set_alpha(alpha*self.alpha/255)
        c = pg.transform.scale(pg.transform.rotate(c, self.rotation), (sizex, sizey))

        rect = c.get_rect()
        rect.center = self.pos
        screen.blit(c, rect)

    def update(self):
        self.vel[0] += self.gravity[0]
        self.vel[1] += self.gravity[1]
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.rotation += self.rvel

        self.key += 1
        if self.key > self.lifetime:
            self.deletable = True


class Bg:
    def __init__(self, type):
        self.image = sprites[f'bg{type}']
        self.xpos = 450
        self.deletable = False

    def draw(self):
        screen.blit(self.image, (self.xpos, windowy-75))

    def update(self):
        self.xpos -= SPEED

        if self.xpos < -140:
            self.deletable = True


class Map:
    def __init__(self):
        self.towers = []
        self.bgs = []
        self.particles = []
        self.explosion_timer = 0
        self.explosions_left = 5
        self.cur_type = 1
        self.player = Player()
        self.points = 0
        self.spawn_timeout = 0
        self.playing = False
        self.debug = False
        self.smoke_timeout = 0
        self.death_pos = (0,0)

    def new_towers(self):
        self.towers.append(Towers())
        self.bgs.append(Bg(self.cur_type))
        self.spawn_timeout = 90
        self.cur_type += 1
        if self.cur_type > 2:
            self.cur_type = 1

    def draw(self):
        for i in self.bgs:
            i.draw()
        for i in self.towers:
            i.draw()
        self.player.draw()

        for i in self.particles:
            i.draw()

        size = draw.get_text_size(f'{self.points}')
        
        draw.text(f'{self.points}', (halfx-3, 27), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+3, 27), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx-3, 33), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+3, 33), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

        draw.text(f'{self.points}', (halfx+5, 29), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx-1, 35), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+5, 35), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

        draw.text(f'{self.points}', (halfx, 30), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

        if self.debug:
            if not self.player.dead:
                pg.draw.rect(screen, (0,0,255), self.player.rect, 4)
                vel = self.player.vel
                pos = list(self.player.rect.center)
                rpos = list(self.player.rect.topleft)
                death = False

                for i in range(100):
                    rect = pg.Rect(rpos, (80,30))
                    color = (0,255,0)

                    vel += 0.2
                    pos[0] += SPEED
                    pos[1] += vel
                    rpos[0] += SPEED
                    rpos[1] += vel

                    rects = []
                    for j in self.towers:
                        rects.extend(j.to_rects())

                    if rect.collidelistall(rects):
                        color = (255,0,0)
                        if not death:
                            draw.text(f'{i}', (rect.topleft[0]+3, rect.topleft[1]+3), size=8, antialias=False)
                            pg.draw.rect(screen, (255,0,0), rect, 1)
                            death = True
                    elif death:
                        death = False

                    pg.draw.circle(screen, color, pos, 1)

                for i in self.towers:
                    for rect in i.to_rects():
                        pg.draw.rect(screen, (0,255,255), rect, 2)

            draw.text(f'FPS: {dfps}', (2,3), (0,0,0), size=8, antialias=False)
            draw.text(f'FPS: {dfps}', (2,2), size=8, antialias=False)
            

    def update(self):
        for i in self.particles:
            i.update()
            if i.deletable:
                self.particles.remove(i)

        if not self.playing and jumped and not self.player.dead:
            self.player.moving = True
            self.playing = True

        if self.playing:
            self.spawn_timeout -= 1
            if self.spawn_timeout <= 0:
                self.new_towers()

            for i in self.bgs:
                i.update()
                if i.deletable:
                    self.bgs.remove(i)

        towers = []
        for i in self.towers:
            if self.playing:
                i.update()

            if i.xpos < 60 and not i.gave_points:
                self.points += 1
                i.gave_points = True

            if i.deletable:
                self.towers.remove(i)
            towers.extend(i.to_rects())

        self.player.update(towers)

        if self.player.dead:
            if self.playing:
                self.playing = False
                self.death_pos = (self.player.death_rect_pos,self.player.pos+10)
                if self.player.effect:
                    for i in range(3):    
                        size = random.randint(200,300)
                        self.particles.append(Particle(
                            sprites['fire'],
                            self.death_pos,
                            (size,size),
                            vel=(random.random()-0.5,random.random()-0.5),
                            lifetime=random.randint(100,180)
                        ))
    
            if self.player.effect:
                self.smoke_timeout -= 1
                if self.smoke_timeout <= 0:
                    self.smoke_timeout = 15

                    size = random.randint(60,100)
                    self.particles.append(Particle(
                        sprites['fire'],
                        self.death_pos,
                        (size,size),
                        vel=((random.random()-0.5)/2,(random.random()-0.5)/2),
                        lifetime=100
                    ))

                    size = random.randint(130,185)
                    self.particles.append(Particle(
                        sprites['smoke'],
                        self.death_pos,
                        (size,size),
                        vel=(random.random(),random.random()),
                        gravity=(-0.04,-0.03),
                        rotation=random.randint(0,365),
                        rotation_vel=random.random(),
                        lifetime=100
                    ))



# app variables

sprites = {
    'tower_top': pg.transform.scale(pg.image.load('res/sprites/tower_top.png').convert_alpha(), (50,300)),
    'tower_btm': pg.transform.scale(pg.image.load('res/sprites/tower_bottom.png').convert_alpha(), (50,300)),

    'bg1': pg.transform.scale(pg.image.load('res/sprites/bg1.png').convert_alpha(), (140,75)),
    'bg2': pg.transform.scale(pg.image.load('res/sprites/bg2.png').convert_alpha(), (140,75)),

    'player': pg.transform.scale(pg.image.load('res/sprites/player.png').convert_alpha(), (100,35)),

    'smoke': pg.image.load('res/sprites/smoke.png'),
    'fire': pg.image.load('res/sprites/fire.png')
}

SPEED = 2
game = Map()


# preparing


# main loop

while running:

############## INPUT ##############

    events = pg.event.get()
    mouse_pos = pg.mouse.get_pos()
    mouse_press = pg.mouse.get_pressed(5)
    mouse_moved = pg.mouse.get_rel()
    keys = pg.key.get_pressed()
    jumped = False

    screen.fill((70,100,186))

  
############## PROCESSING EVENTS ##############

    for event in events:
        if event.type == pg.QUIT:       
            running = False  

        if (event.type == pg.KEYDOWN and event.key == pg.K_SPACE)\
            or (event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
                jumped = True

        if event.type == pg.KEYDOWN and event.key == pg.K_F3:
            game.debug = not game.debug

        if event.type == pg.VIDEORESIZE:
            cx = event.w
            cy = event.h
            window = pg.display.set_mode((event.w,event.h), pg.RESIZABLE | pg.DOUBLEBUF)



############## UPDATING SCREEN ##############

    game.draw()
    game.update()

    c = screen.copy()
    c = pg.transform.smoothscale(c, (cx, cy))
    window.blit(c, (0,0))
    pg.display.flip()
    clock.tick(fps)
    dfps = round(clock.get_fps(), 1)