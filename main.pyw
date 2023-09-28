############## INITIALIZATION ##############

'''
TODO

- saving system
- restarting game
- menus
'''

import pygame as pg
import easing_functions as easing
import draw
import random

pg.init()

# game size (doesn't change on resize)
windowx = 400
windowy = 400

# window resolution (changes when resizing)
cx = 600
cy = 600

clock = pg.time.Clock()
fps = 60 # target fps (used in clock.tick)
dfps = 0.0 # current fps (clock.get_fps assignes it)

window = pg.display.set_mode((cx,cy), pg.RESIZABLE | pg.DOUBLEBUF)
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
        self.plane_mode = False
        self.vel = 0
        self.smooth_rot = 0
        self.pos = 200
        self.jump_speed = -5
        self.dead = False
        self.effect = False
        self.death_rect_pos = 0
        self.calc_rect()

    # recalcutates rect for the plane
    def calc_rect(self):
        self.rect = pg.Rect(110,self.pos, 80,30)

    # this func gets called when the player collides with a tower
    # or the ceiling/floor, if effect == False then it won't
    # create an explosion effect
    def die(self, pos=200, effect=True):
        if self.dead: return
        self.dead = True
        self.vel = self.jump_speed
        self.effect = effect
        self.death_rect_pos = pos

    # jump/leap, also starts the game
    def jump(self):
        if self.dead: return
        if not self.moving: self.moving = True

        if not self.plane_mode:
            self.vel = self.jump_speed
        else:
            self.vel -= 0.4 # smooth gliding

    # updates the plane
    def update(self, towers):
        # moving the plane
        if self.moving:
            self.vel += 0.22
            self.pos += self.vel
            if self.pos > 500:
                self.pos = 500

        if jumped:
            self.jump()

        # rotating the plane
        self.smooth_rot += (-self.vel*4-self.smooth_rot)/2

        # checking collision
        self.calc_rect()
        
        collision = self.rect.collidelistall(towers)
        if collision:
            pos = towers[collision[0]].x+25
            self.die(pos)
        if self.pos < 0 or self.pos > 370:
            self.die(effect=False)

    # draws the plane
    def draw(self):
        image = self.image.copy()
        image = pg.transform.rotate(image, self.smooth_rot)
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

    # recalculates rects for both of the towers
    def calc_rects(self):
        self.top = pg.Rect(self.xpos, self.ypos-370, 50,300)
        self.bottom = pg.Rect(self.xpos, self.ypos+70, 50,300)

    # draws the towers
    def draw(self):
        screen.blit(self.image_top, (self.top[0], self.top[1]+10))
        screen.blit(self.image_bottom, (self.bottom[0], self.bottom[1]-10))

    # updated the towers
    def update(self):
        self.xpos -= SPEED
        self.calc_rects()

        if self.xpos < -40:
            self.deletable = True

    # returns towers' rects
    def to_rects(self):
        return [self.top, self.bottom]
    

class Particle:
    def __init__(self, image, pos, size, vel=(0,0), gravity=(0,0), lifetime=60, alpha=255, rotation=0, rotation_vel=0):
        self.image = image
        self.pos = list(pos) # starting position of the particle
        self.vel = list(vel) # starting velocity of the particle
        self.size = size
        self.key = 0
        self.lifetime = lifetime
        self.gravity = gravity # how much particle accelerates
                               # eg if pos=(4,0) and gravity=(1,0)
                               # then after updating the pos will be (5,0)
        self.alpha = alpha
        self.rotation = rotation
        self.rvel = rotation_vel
        self.deletable = False

    # draws the particle
    def draw(self):
        # calculating the size and opacity
        size = easing.QuinticEaseOut(0,1,self.lifetime).ease(self.key)
        sizex = size*self.size[0]
        sizey = size*self.size[1]
        alpha = easing.QuinticEaseIn(255,0,self.lifetime).ease(self.key)*self.alpha/255

        # modifying the image
        c = self.image.copy()
        c.set_alpha(alpha)
        c = pg.transform.scale(pg.transform.rotate(c, self.rotation), (sizex, sizey))

        # drawing the image
        rect = c.get_rect()
        rect.center = self.pos
        screen.blit(c, rect)

    # updates the particle
    def update(self):
        # basic physics
        self.vel[0] += self.gravity[0]
        self.vel[1] += self.gravity[1]
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # rotation
        self.rotation += self.rvel

        # updaing
        self.key += 1
        if self.key > self.lifetime:
            self.deletable = True


class Bg:
    def __init__(self, type):
        self.image = sprites[f'bg{type}']
        self.xpos = 450
        self.deletable = False

    # draws the image
    def draw(self):
        screen.blit(self.image, (self.xpos, windowy-75))

    # updates the image
    def update(self):
        self.xpos -= SPEED

        if self.xpos < -140:
            self.deletable = True


class Map:
    def __init__(self):
        self.towers = []
        self.bgs = []
        self.particles = []
        self.cur_type = 1 # current bg image, cycles through all bg images
        self.player = Player()
        self.points = 0
        self.spawn_timeout = 0 # timer in frames when to spawn newbgs and towers
        self.playing = False
        self.debug = False
        self.smoke_timeout = 0 # timer in frames when to create a smoke particle
        self.death_pos = (0,0)

        self.begin_text_flash = 255
        self.hi_opacity = 255
        self.bottom_text = 'CLICK ANYWHERE TO BEGIN'

        self.load_hi_score()

    def load_hi_score(self):
        try:
            with open('save') as f:
                self.hi_score = int(f.read())
        except:
            with open('save', 'w') as f:
                f.write('0')
            self.hi_score = 0
        self.hi_score_text = f'HI: {self.hi_score}'

    def write_hi_score(self):
        if self.points <= self.hi_score: return
        with open('save', 'w') as f:
            f.write(str(self.points))
        self.hi_score_text = f'NEW BEST'

    def new_towers(self):
        self.towers.append(Towers())
        self.bgs.append(Bg(self.cur_type))
        self.spawn_timeout = 190/SPEED
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

        # hi score
        if self.hi_opacity > 0:
            size = draw.get_text_size(self.hi_score_text, 8)
            ease = easing.SineEaseIn(0,1,1).ease((255-self.hi_opacity)/255)*50
            out_ease = easing.SineEaseInOut(0,1,1).ease(self.hi_opacity/255)*30

            draw.text(self.hi_score_text, (halfx-2, 24-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx+2, 24-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx-2, 28-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx+2, 28-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

            draw.text(self.hi_score_text, (halfx, 26-ease), size=8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        else:
            out_ease = 0

        # score
        size = draw.get_text_size(f'{self.points}')
        
        draw.text(f'{self.points}', (halfx-3, 27+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+3, 27+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx-3, 33+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+3, 33+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+5, 29+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx-1, 35+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        draw.text(f'{self.points}', (halfx+5, 35+out_ease), (0,0,0), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

        draw.text(f'{self.points}', (halfx, 30+out_ease), horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

        # bottom text
        if self.hi_opacity > 0:
            size = draw.get_text_size(self.hi_score_text, 8)
            ease = easing.SineEaseIn(0,1,1).ease((255-self.hi_opacity)/255)*50
            out_ease = easing.SineEaseInOut(0,1,1).ease(self.hi_opacity/255)*30

            draw.text(self.hi_score_text, (halfx-2, 24-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx+2, 24-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx-2, 28-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
            draw.text(self.hi_score_text, (halfx+2, 28-ease), (0,0,0), 8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))

            draw.text(self.hi_score_text, (halfx, 26-ease), size=8, horizontal_margin='m', rect_size=(size[0]*2, size[1]*2))
        else:
            out_ease = 0

        # debug menu
        if self.debug:
            if not self.player.dead:
                # player
                pg.draw.rect(screen, (0,0,255), self.player.rect, 4)

                # where the player gonna be
                vel = self.player.vel
                pos = list(self.player.rect.center)
                rpos = list(self.player.rect.topleft)
                death = False

                for i in range(100):
                    rect = pg.Rect(rpos, (80,30))
                    color = (128,128,128)

                    vel += 0.22
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
                            pg.draw.rect(screen, (192,128,128), rect, 1)
                            death = True
                    elif death:
                        death = False

                    pg.draw.circle(screen, color, pos, 1)

                # where the player gonna be if he jumped
                vel = self.player.jump_speed
                pos = list(self.player.rect.center)
                rpos = list(self.player.rect.topleft)
                death = False

                for i in range(100):
                    rect = pg.Rect(rpos, (80,30))
                    color = (0,255,0)

                    vel += 0.22
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
                            pg.draw.rect(screen, (255,0,0), rect, 1)
                            death = True

                    pg.draw.circle(screen, color, pos, 1)

                for i in self.towers:
                    for rect in i.to_rects():
                        pg.draw.rect(screen, (0,255,255), rect, 2)

            # fps
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

        # basically the main loop
        if self.playing:
            if self.hi_opacity > 0:
                self.hi_opacity -= 10

            self.spawn_timeout -= 1
            if self.spawn_timeout <= 0:
                self.new_towers()

            for i in self.bgs:
                i.update()
                if i.deletable:
                    self.bgs.remove(i)

        elif self.hi_opacity < 255:
            self.hi_opacity += 10

        # towers and points
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

        # player
        self.player.update(towers)

        if self.player.dead:
            if self.playing:
                # on player death
                self.bottom_text = 'CLICK ANYWHERE TO RESTART'
                self.write_hi_score()

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
                # that smoke effect
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

    # scaling the surface to match the window resolution (cx, cy)
    c = screen.copy()
    c = pg.transform.smoothscale(c, (cx, cy))
    window.blit(c, (0,0))

    # updating
    pg.display.flip()
    clock.tick(fps)
    dfps = round(clock.get_fps(), 1)