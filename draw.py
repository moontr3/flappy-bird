# LIGRARIES
import glob
import pygame as pg


# INITIALIZING FONTS
pg.font.init()
fonts = {}

for i in glob.glob('res/fonts/*.ttf'):
    i = i.replace('\\','/')
    fonts[i] = []
    for j in range(100):
        try:
            fonts[i].append(pg.font.Font(i, j))
        except:
            fonts[i].append(None)


# DEFAULT SURFACE
def_surface = None


# TEXT DRAWING
def text(
        text='',
        pos=(0,0),
        color=(255,255,255), 
        size=18,
        style='regular', 
        horizontal_margin='l', 
        vertical_margin='t', 
        antialias=True, 
        rotation=0,
        opacity=255,
        rect_size=None,
        surface=None
    ):

    # surface
    if surface == None:
        surface = def_surface

    # getting font
    font = fonts[f'res/fonts/{style}.ttf'][size]
    rtext = font.render(text, antialias, color)

    # rotation
    if rotation != 0:
        rtext = pg.transform.rotate(rtext, rotation)

    # opacity
    if opacity != 255:
        rtext.set_alpha(opacity)

    # resizing
    if rect_size != None:
        rtext = pg.transform.smoothscale(rtext, rect_size)

    # aligning
    btext = rtext.get_rect()

    if vertical_margin == 't':
        if horizontal_margin == 'm':
            btext.midtop = pos[0],pos[1]
        elif horizontal_margin == 'r':
            btext.topright = pos[0],pos[1]
        else:
            btext.topleft = pos[0],pos[1]

    if vertical_margin == 'm':
        if horizontal_margin == 'm':
            btext.center = pos[0],pos[1]
        elif horizontal_margin == 'r':
            btext.midleft = pos[0],pos[1]
        else:
            btext.midright = pos[0],pos[1]

    if vertical_margin == 'b':
        if horizontal_margin == 'm':
            btext.midbottom = pos[0],pos[1]
        elif horizontal_margin == 'r':
            btext.bottomright = pos[0],pos[1]
        else:
            btext.bottomleft = pos[0],pos[1]
    
    # drawing
    surface.blit(rtext, btext)
    return font.size(text)


# TEXT SIZE
def get_text_size(text='', size=18, style='regular'):
    font = fonts[f'res/fonts/{style}.ttf'][size]
    return font.size(text)