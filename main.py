from pygame import*
from random import*
from instruments import*

joystick.init()
pads = joystick.get_count()
if pads:
    j1 = joystick.Joystick(0)
    j1.init()
    gamepad_connected = True
else:
    gamepad_connected = False

mixer.music.load('sounds/ambient.mp3')
mixer.music.set_volume(0.5)
window = display.set_mode((win_width, win_height), NOFRAME)

run = True
wood = 0
coal = 0
day_len = 300
day = 1
darkness_damage = 0.5
start_time = time.get_ticks()


def place_center_img(img):
    global center_x, center_y
    img_rect = img.get_rect()
    x = center_x - img_rect.width/2
    y = center_y - img_rect.height/2
    window.blit(img, (x, y))

def place_img(img, x, y):
    img_rect = img.get_rect()
    x = x - img_rect.width/2
    y = y - img_rect.height/2
    window.blit(img, (x, y))

def place(s1, x, y):
    x = x - s1.rect.width/2
    y = y - s1.rect.height/2
    s1.rect.x = x
    s1.rect.y = y


class Sprite(sprite.Sprite):
    def __init__(self, img, x, y, size_x = 0, size_y = 0 ):
        super().__init__()
        self.image = image.load(img)
        if size_x != 0:
            self.image = transform.scale(self.image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.visible = True
        all_sprites.append(self)
    def reset(self):
        if self.visible:
            window.blit(self.image, (self.rect.x, self.rect.y))


class UI(Sprite):
    def __init__(self, img, x, y, size_x = 0, size_y = 0):
        super().__init__(img, x, y, size_x, size_y)
        self.text = ''
        self.color = white
        self.text_img = f1.render(self.text, 1, white)
        ui.add(self)

    def set_text(self, text):
        self.text = text
        self.text_img = f2.render(self.text, 1, white)

    def reset(self):
        if self.visible:
            window.blit(self.image, (self.rect.x, self.rect.y))
            x = self.rect.x + self.rect.width/2
            y = self.rect.y + self.rect.height/2
            place_img(self.text_img, x, y)


class Obstacle(Sprite):
    def __init__(self, img_1, img_2, x, y, durability, size_x = 0, size_y = 0):
        super().__init__(img_1, x, y, size_x, size_y)
        obstacles_bot.add(self)
        self.part2 = Sprite(img_2, x, y, size_x, size_y)
        obstacles_top.add(self.part2)
        self.durability = durability
        self.cracks = list()

    def crack(self):
        s_axe2.play()
        c = Sprite(crack_img, self.rect.x, self.rect.y-32, 32, 64)
        self.cracks.append(c)
        obstacles_top.add(c)
        self.durability -= 1
        if self.durability <= 0:
            obstacles_bot.remove(self)
            obstacles_top.remove(self.part2)
            for c in self.cracks:
                obstacles_top.remove(c)
            if distance(self, player) < 50:
                global wood
                wood += 1
                logs_ui_text.set_text(str(wood))

    def reset(self): 
        super().reset()
        self.part2.rect.x = self.rect.x
        self.part2.rect.bottom = self.rect.top


class Obstacle_single(Sprite):
    def __init__(self, img_1, x, y, durability, size_x = 0, size_y = 0):
        super().__init__(img_1, x, y, size_x, size_y)
        obstacles_bot.add(self)
        self.durability = durability
        self.cracks = list()

    def crack(self):
        s_stone.play()
        c = Sprite(crack_img, self.rect.x, self.rect.y, 32, 32)
        self.cracks.append(c)
        obstacles_top.add(c)
        self.durability -= 1
        if self.durability <= 0:
            obstacles_bot.remove(self)
            for c in self.cracks:
                obstacles_top.remove(c)
            if distance(self, player) < 50:
                global coal
                coal += 1
                coal_ui_text.set_text(str(coal))


class Wall(Sprite):
    def __init__(self, img, x, y, durability, size_x = 0, size_y = 0):
        super().__init__(img, x, y, size_x, size_y)
        walls.add(self)
        self.durability = durability
        self.cracks = list()
        s_hammer.play()
    def crack(self):
        self.cracks.append(Sprite(crack_img, self.rect.x, self.rect.y, 48, 48))
        self.durability -= 1
        if self.durability <= 0:
            walls.remove(self)
    def reset(self):
        if self.durability <= 0:
            obstacles_bot.remove(self)
        super().reset()
        for c in self.cracks:
            c.reset()


class Fire(Sprite):
    def __init__(self, img, x, y, durability, size_x = 0, size_y = 0):
        super().__init__(img, x, y, size_x, size_y)
        weapons.add(self)
        self.durability = durability
        self.cracks = list()
        s_hammer.play()
    def crack(self):
        self.cracks.append(Sprite(crack_img, self.rect.x, self.rect.y, 48, 48))
        self.durability -= 1
        if self.durability <= 0:
            weapons.remove(self)
    def reset(self):
        if self.durability <= 0 or is_surrounded(self, darkness):
            obstacles_bot.remove(self)
        super().reset()
        for c in self.cracks:
            c.reset()


class Particle(Sprite):
    def __init__(self, img, x, y, size_x = 0, size_y = 0 ):
        super().__init__(img, x, y, size_x, size_y)
        self.speed = 2
        self.orders = [0,0]
        heroes.add(self)

    def reset(self):
        self.visible = True
        if self.orders[0] > 0:
            self.rect.x += self.speed
            self.orders[0] -= self.speed
        if self.orders[0] < 0:
            self.rect.x -= self.speed
            self.orders[0] += self.speed
        if self.orders[1] > 0:
            self.rect.y += self.speed
            self.orders[1] -= self.speed
        if self.orders[1] < 0:
            self.rect.y -= self.speed
            self.orders[1] += self.speed

        if self.orders[0] == 0 and self.orders[1] == 0:
            self.visible = False
        super().reset()


class Player(Sprite):
    def __init__(self, img, x, y, size_x = 0, size_y = 0, health = 100):
        super().__init__(img, x, y, size_x, size_y)
        self.speed = 3
        self.health = health
        heroes.add(self)
        self.part2 = Sprite('hero\down\hero_down_top_0.png', 100, 100)
        self.direction = 'down'
        self.frame = 0
        self.cooldown = time.get_ticks()

    def change_view(self, n):
        n = str(n)
        s1 = 'hero/'+self.direction+'/hero_'+self.direction+'_bot_'+n+'.png'
        s2 = 'hero/'+self.direction+'/hero_'+self.direction+'_top_'+n+'.png'
        self.image = image.load(s1)
        self.part2.image = image.load(s2)

    def collide(self, group):
        if sprite.spritecollide(self, group):
            return True

    def control(self):
        global gamepad_connected
        if gamepad_connected:
            self.control_gamepad()
        else:
            self.control_keyboard()

    def right(self):
        self.direction = 'right'
        self.rect.x += self.speed
        if sprite.spritecollide(self, obstacles_bot, False) or sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, weapons, False):
            self.rect.x -= self.speed
        self.frame += 0.2
        self.change_view(int(self.frame%3))
    def left(self):
        self.direction = 'left'
        self.rect.x -= self.speed
        if sprite.spritecollide(self, obstacles_bot, False) or sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, weapons, False):
            self.rect.x += self.speed
        self.frame += 0.2
        self.change_view(int(self.frame%3))
    def up(self):
        self.direction = 'up'
        self.rect.y -= self.speed
        if sprite.spritecollide(self, obstacles_bot, False) or sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, weapons, False):
            self.rect.y += self.speed
        self.frame += 0.2
        self.change_view(int(self.frame%3))
    def down(self):
        self.direction = 'down'
        self.rect.y += self.speed
        if sprite.spritecollide(self, obstacles_bot, False) or sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, weapons, False):
            self.rect.y -= self.speed
        self.frame += 0.2
        self.change_view(int(self.frame%3))
            
    def build(self):
        global build_type, wood, typ, coal
        x = scheme.rect.x
        y = scheme.rect.y
        if typ == 'fire':
            wood_price = (build_type+1)*3
            coal_price = (build_type+1)*2
        elif typ == 'walls':
            wood_price = (build_type+1)*5
            coal_price = 0

        if wood < wood_price or sprite.spritecollide(scheme, obstacles_bot, False) or sprite.spritecollide(scheme, darkness, False) or sprite.spritecollide(scheme, walls, False) or coal < coal_price:
            scheme.visible = False
            wood_hint_txt.visible = False
            coal_hint_txt.visible = False
            wood_hint.visible = False
            coal_hint.visible = False
        else:
            if typ == 'walls':
                Wall(walls_img[build_type], x, y, durability = wood_price, size_x = 48, size_y = 48)
                wood -= wood_price
            elif typ == 'fire':
                f = Fire(fire_img[build_type], x, y, durability = wood_price, size_x = 32, size_y = 32)
                cast_light(f, build_type+1)
                wood -= wood_price
                coal -= coal_price
            scheme.visible = False
            wood_hint_txt.visible = False
            coal_hint_txt.visible = False
            wood_hint.visible = False
            coal_hint.visible = False
            logs_ui_text.set_text(str(wood))
            coal_ui_text.set_text(str(coal))
        
    def swing(self):
        if scheme.visible:
            self.build()
        else:
            if axe.orders == [0,0] and not scheme.visible and time.get_ticks()-self.cooldown > 300:
                self.cooldown = time.get_ticks()
                axe.visible = True
                if self.direction == 'right':
                    axe.orders = [30, 0]
                if self.direction == 'left':
                    axe.orders = [-30, 0]
                if self.direction == 'up':
                    axe.orders = [0, -30]
                if self.direction == 'down':
                    axe.orders = [0, 30]
                axe.rect.x = self.rect.x
                axe.rect.y = self.rect.y-16

    def control_keyboard(self):
        keys = key.get_pressed()
        if keys[K_w]:
            self.up()
        elif keys[K_s]:
            self.down()
        elif keys[K_d]:
            self.right()
        elif keys[K_a]:
            self.left()
        if keys[K_f]:
            scheme.visible = True
            select_type('walls')
        if keys[K_e]:
            scheme.visible = False
            wood_hint_txt.visible = False
            coal_hint_txt.visible = False
            wood_hint.visible = False
            coal_hint.visible = False
        if keys[K_ESCAPE]:
            global run
            run = False
        if keys[K_r]:
            scheme.visible = True
            select_type('fire')

    def control_gamepad(self):
        if j1.get_axis(0) > 0.5:
            self.right()
        elif j1.get_axis(0) < -0.5:
            self.left()
        elif j1.get_axis(1) > 0.5:
            self.down()
        elif j1.get_axis(1) < -0.5:
            self.up()
        if j1.get_button(1):
            scheme.visible = False
            wood_hint_txt.visible = False
            coal_hint_txt.visible = False
            wood_hint.visible = False
            coal_hint.visible = False
        if j1.get_button(2):
            scheme.visible = True
            select_type('walls')
        if j1.get_button(7):
            global run
            run = False
        if j1.get_button(3):
            scheme.visible = True
            select_type('fire')

    def reset(self):
        super().reset()
        self.part2.rect.x = self.rect.x
        self.part2.rect.bottom = self.rect.top
        self.part2.reset()
        if scheme.visible:
            if self.direction == 'left':
                scheme.rect.right = self.rect.left
                scheme.rect.y = self.part2.rect.y
            if self.direction == 'right':
                scheme.rect.left = self.rect.right
                scheme.rect.y = self.part2.rect.y
            if self.direction == 'up':
                scheme.rect.x = self.rect.x
                scheme.rect.bottom = self.part2.rect.top
            if self.direction == 'down':
                scheme.rect.x = self.rect.x
                scheme.rect.top = self.rect.bottom


class Darkness(Sprite):
    def __init__(self, img, x, y, size_x = 0, size_y = 0 ):
        super().__init__(img, x, y, size_x, size_y)
        darkness.add(self)
        self.active = True


def cast_shadow(s):
    for x in range(-1, 1):
        for y in range(-1, 1):
            shadows.add(Sprite(shadow_img, s.rect.x + 32*x, s.rect.y + 32*y, 32, 32))

def cast_light(s, n):
    for x in range(-n, n+1):
        for y in range(-n, n+1):
            light.add(Sprite(light_img, s.rect.x + 32*x, s.rect.y + 32*y, 32, 32)) 

def corrupt():
    d2 = darkness
    for i in d2:
        if i.active:
            x = i.rect.x + 32*randint(-1, 1)
            y = i.rect.y + 32*randint(-1, 1)
            if not is_occupied(x, y, darkness) and x in range(0, win_width) and y in range(0, win_height):
                img = choice(darkness_img)
                cast_shadow(Darkness(img, x, y, 32, 32))
            if is_surrounded(i, darkness):
                i.active = False
        else:
            i.image = transform.scale(image.load(choice(darkness_img)), (32, 32))
    for s1 in sprite.groupcollide(obstacles_bot, darkness, False, False):
        s1.crack()
    for s1 in sprite.groupcollide(walls, darkness, False, False):
        s1.crack()
    for s1 in sprite.groupcollide(weapons, darkness, False, False):
        s1.crack()
    sprite.groupcollide(tiles, darkness, True, False)
    sprite.groupcollide(shadows, darkness, True, False)
    sprite.groupcollide(darkness, walls, True, False)
    sprite.groupcollide(darkness, weapons, True, False)
    sprite.groupcollide(darkness, light, True, True)


for x in range(win_width):
    for y in range(win_height):
        if x%32==0 and y%32==0:
            tiles.add(Sprite(choice(ground_tiles), x, y, 32, 32))
            if chance(25):
                if distance_p_to_p(center_x, center_y, x+16, y+32) > 150:
                    n = randint(0, len(tree_img_top)-1)
                    Obstacle(tree_img_bot[n], tree_img_top[n], x, y, 5, 32, 32)
            elif chance(5):
                if distance_p_to_p(center_x, center_y, x+16, y+16) > 150:
                    Obstacle_single(coal_img, x, y, 5, 32, 32)

scheme = Sprite('obstacles/wall1.png', 0, 0, 48, 48)
scheme.visible = False

player = Player('hero/down/hero_down_bot_0.png', 100, 100)
axe = Particle(axe_img, 0, 0, 32, 32)
place(player, center_x, center_y)
dark_main = Darkness(dark_img, center_x, center_y, 32, 32)
while distance(player, dark_main) < 100:
    place(dark_main, randint(200, win_width-200)//32*32+16, randint(100, win_height-100)//32*32+16)

day_ui = UI(ui_rect, win_width-120-5, 5, 120, 30)
day_ui.set_text(' ДЕНЬ 1 ')
hp_rect_ui = UI(hp_rect, 5, 5, 200, 30)
hp_bar_ui = UI(hp_bar, 15, 12, 181, 16) #+10x +7y

logs_rect_ui = UI(logs_rect, 5, 40, 64, 64)
logs_ui = UI(logs_img, 16, 50, 44, 44)
logs_ui_text = UI(logs_rect, 5, 107, 64, 32)
logs_ui_text.set_text(str(wood))

coal_rect_ui = UI(logs_rect, 79, 40, 64, 64)
coal_ui = UI(coal_ui_img, 90, 50, 44, 44)
coal_ui_text = UI(logs_rect, 79, 107, 64, 32)
coal_ui_text.set_text(str(coal))

wood_hint_txt = UI(logs_rect, 150, 40, 133, 48)
coal_hint_txt = UI(logs_rect, 150, 93, 133, 48)
wood_hint = UI(logs_img, 170, 47, 33, 33)
coal_hint = UI(coal_ui_img, 170, 100, 33, 33)
wood_hint_txt.visible = False
coal_hint_txt.visible = False
wood_hint.visible = False
coal_hint.visible = False

def update_healthbar():
    lenght = int(181*player.health/100)
    hp_bar_ui.image = transform.scale(hp_bar_ui.image, (lenght, 16))

def death():
    global run
    run = False
    window.fill(black)
    text = f1.render('ВЫ ПОГИБЛИ', 1, white, gray)
    place_center_img(text)
    display.update()
    time.wait(3000)

def new_day():
    global day, day_len
    if day_len > 3:
        day_len -= 0.5
    mixer.music.set_volume(mixer.music.get_volume()+0.05)
    day += 1
    text = ' ДЕНЬ ' + str(day) + ' '
    nd_text = f1.render(text, 1, white, gray)
    #window.blit(transform.scale(image.load(shadow_img), (win_width, win_height)), (0,0))
    #window.blit(transform.scale(image.load(shadow_img), (win_width, win_height)), (0,0))
    place_center_img(nd_text)
    display.update()
    #corrupt()
    corrupt()
    #time.wait(500)
    s_newday.play()
    day_ui.set_text(' ДЕНЬ ' + str(day) + ' ')
    player.health += 10
    if player.health > 100:
        player.health = 100
    update_healthbar()
    for i in range(30):
        if len(tiles.sprites()) == 0:
            global run
            run = False
            window.fill(black)
            text = f1.render('МИР ПОГЛОТИЛА ТЬМА', 1, white, gray)
            place_center_img(text)
            display.update()
            time.wait(3000)
            break
        t = choice(tiles.sprites())
        if not is_occupied(t.rect.x, t.rect.y, obstacles_bot) and distance_to_point(player, t.rect.x, t.rect.y) > 50 and not is_occupied(t.rect.x, t.rect.y, walls) and not is_occupied(t.rect.x, t.rect.y, weapons):
            n = randint(0, len(tree_img_top)-1)
            Obstacle(tree_img_bot[n], tree_img_top[n], t.rect.x, t.rect.y, 5, 32, 32)
    for i in range(20):
        t = choice(tiles.sprites())
        if not is_occupied(t.rect.x, t.rect.y, obstacles_bot) and distance_to_point(player, t.rect.x, t.rect.y) > 50 and not is_occupied(t.rect.x, t.rect.y, walls) and not is_occupied(t.rect.x, t.rect.y, weapons):
            Obstacle_single(coal_img, x, y, 5, 32, 32)
    
def select_type(t):
    global typ, build_type
    typ = t
    build_type = 0
    if t == 'walls':
        scheme.image = transform.scale(image.load(walls_img[build_type]), (48, 48))
        wood_hint_txt.set_text(' '*10+str((build_type+1)*5))
        coal_hint_txt.set_text(' '*10+'0')
    if t == 'fire':
        scheme.image = transform.scale(image.load(fire_img[build_type]), (32, 32))
        wood_hint_txt.set_text(' '*10+str((build_type+1)*3))
        coal_hint_txt.set_text(' '*10+str((build_type+1)*2))
    wood_hint_txt.visible = True
    coal_hint_txt.visible = True
    wood_hint.visible = True
    coal_hint.visible = True

def next_type():
        global build_type, typ
        if typ == 'walls':
            build_type = (build_type + 1) % len(walls_img)
            scheme.image = transform.scale(image.load(walls_img[build_type]), (48, 48))
            wood_hint_txt.set_text(' '*10+str((build_type+1)*5))
            coal_hint_txt.set_text(' '*10+'0')
        elif typ == 'fire':
            build_type = (build_type + 1) % len(fire_img)
            scheme.image = transform.scale(image.load(fire_img[build_type]), (32, 32))
            wood_hint_txt.set_text(' '*10+str((build_type+1)*3))
            coal_hint_txt.set_text(' '*10+str((build_type+1)*2))

def joy_click(n):
    if pads:
        return j1.get_button(n)
    else:
        return False

mixer.music.play(100)
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if (e.type == KEYDOWN and e.key == K_q) or joy_click(5):
            next_type()
        if (e.type == KEYDOWN and e.key == K_SPACE) or joy_click(0):
            player.swing()
    player.control()

    if sprite.spritecollide(player, darkness, False):
        player.health -= darkness_damage
        update_healthbar()
        if player.health <= 0:
            death()

    for s1 in sprite.spritecollide(axe, obstacles_bot, False):
        if axe.visible:
            s1.crack()
            axe.orders = [0,0]
    
    window.fill(black)
    tiles.reset()
    darkness.reset()
    obstacles_bot.reset()
    walls.reset()
    weapons.reset()
    heroes.reset()
    obstacles_top.reset()
    shadows.reset()
    light.reset()
    scheme.reset()
    ui.reset()

    if time.get_ticks() - start_time > int(day_len):
        new_day()
        start_time = time.get_ticks()
    clock.tick_busy_loop(60)
    display.update()
