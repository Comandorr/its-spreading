from pygame import*
from random import*

clock = time.Clock()
font.init()
mixer.init()
f1 = font.Font(None, 48)
f2 = font.Font(None, 24)
s_stone = mixer.Sound('sounds/камень.ogg')
s_axe1 = mixer.Sound('sounds/топор1.ogg')
s_axe2 = mixer.Sound('sounds/топор2.ogg')
s_hammer = mixer.Sound('sounds/молоток.ogg')
s_newday = mixer.Sound('sounds/new_day.ogg')

win_width = 1920
win_height = 1080
center = (win_width/2, win_height/2)
center_x = win_width/2
center_y = win_height/2
typ = 'walls'
build_type = 0

black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
gray = (150, 150, 150)

ground_tiles = ['tiles/dirt_tile.png', 'tiles/grass_tile.png', 'tiles/grass_tile.png']
#ground_tiles = ['tiles/grass.png', 'tiles/grass.png', 'tiles/sand.png']
tree_img_top = ['obstacles/tree_1top.png', 'obstacles/tree_2top.png', 'obstacles/tree_3top.png']
tree_img_bot = ['obstacles/tree_1bot.png', 'obstacles/tree_2bot.png', 'obstacles/tree_3bot.png']
darkness_img = ['darkness/dark_1.png', 'darkness/dark_2.png', 'darkness/dark_3.png', 'darkness/dark_4.png', 'darkness/dark_5.png', 'darkness/dark_6.png']
walls_img = ['obstacles/wall1.png', 'obstacles/wall2.png', 'obstacles/wall3.png']
fire_img = ['obstacles/torch.png', 'obstacles/fire.png']
ui_rect = 'ui/rect.png'
hp_bar = 'ui/hp_bar.png'
hp_rect = 'ui/hp_rect.png'
dark_img = 'darkness/dark_main.png'
shadow_img = 'tiles/shadow.png'
light_img = 'tiles/light.png'
axe_img = 'axe.png'
logs_img = 'ui/logs.png'
logs_rect = 'ui/rect_logs.png'
crack_img = 'obstacles/cracked.png'
coal_ui_img = 'ui/coal_ui.png'
coal_img = 'obstacles/stone4.png'


def chance(c):
    ch = randint(0, 99)
    if ch < c:
        return True
    else:
        return False

def distance(s1, s2):
    x1 = s1.rect.x + s1.rect.width/2
    y1 = s1.rect.y + s1.rect.height/2
    x2 = s2.rect.x + s2.rect.width/2
    y2 = s2.rect.y + s2.rect.height/2
    d = float(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
    d = abs(round(d, 3))
    return d

def distance_to_point(s1, x2, y2):
    x1 = s1.rect.x + s1.rect.width/2
    y1 = s1.rect.y + s1.rect.height/2
    d = float(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
    d = round(d, 3)
    return d

def distance_p_to_p(x1, y1, x2, y2):
    d = float(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
    d = round(d, 3)
    return d
    
def is_occupied(x, y, group):
    result = False
    for i in group:
        if i.rect.x == x and i.rect.y == y:
            result = True
    return result

def is_surrounded(s1, group):
    x = s1.rect.x
    y = s1.rect.y
    left = s1.rect.x - s1.rect.width
    right = s1.rect.x + s1.rect.width
    up = s1.rect.y - s1.rect.height
    down = s1.rect.y + s1.rect.height
    oc_left = is_occupied(left, y, group) 
    oc_right = is_occupied(right, y, group) 
    oc_up = is_occupied(x, up, group) 
    oc_down = is_occupied(x, down, group) 
    result = oc_up and oc_right and oc_left and oc_down
    return result

class Group(sprite.Group):
    def reset(self):
        for i in self.sprites():
            if i.visible:
                i.reset()


all_sprites = list()                
tiles = Group()
obstacles_bot = Group()
obstacles_top = Group()
heroes = Group()
ui = Group()
darkness = Group()
walls = Group()
shadows = Group()
weapons = Group()
light = Group()