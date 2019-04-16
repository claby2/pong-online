import sys
import pygame
import random
import socket
from ast import literal_eval as le
import time

version = "v2.2"
compatibility = ["v2.1.1","v2.2"] #This only includes the current versions and for below. Newer versions have their own list, and when connecting with multiplayer, it checks for their compatibility with each other and the higher player version takes priority. If the lower version str was in the higher version's list, it will work.
fps_limit = 60 #This cannot be above the device's monitor refresh rate. Macbook Air's monitor refresh rate is 60 per second.

#################
#Settings Values:
#################

showfps = True
fpsval = 1000000000
fpsval = 10**0
#print(10**9)
#print(1000000000)
fpsrefresh = 50

showping = True #Show ping
pingval = 1000000000 #Ping decimal place
pingval = 10**0
pingrefresh = 50 #Ping display refresh rate | refresh every x frames

#####################
# Part A: GAME SETUP:
#####################
# define classes, constants, initialize & import game assets below

# Color lists. Check out http://www.colorpicker.com/

BLOCK = 16
SPEED = 5

# Start pygame
pygame.init()
pygame.font.init()

# create the screen
SIZE = [700,500]
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Pong " + version)

#Fonts
font = pygame.font.Font("./Fonts/bit5x3.ttf", 50)
font_selected = pygame.font.Font("./Fonts/bit5x3.ttf", 55)
title_font = pygame.font.Font("./Fonts/bit5x3.ttf", 130)
large_font = pygame.font.Font("./Fonts/bit5x3.ttf", 65)
medium_font = pygame.font.Font("./Fonts/bit5x3.ttf", 30)
small_font = pygame.font.Font("./Fonts/bit5x3.ttf", 25)

pygame.mouse.set_visible(False)
past_mouse = False

# create game objects

class Color:

    def __init__(self, rgb, lightened=100, darkened=100):
        self.normal = rgb

        lightenedlist = []
        for value in rgb:
            if value > 255 - lightened:
                lightenedlist.append(255)
            else:
                lightenedlist.append(value + lightened)
        self.lightened = lightenedlist

        darkenedlist = []
        for value in rgb:
            if value < darkened:
                darkenedlist.append(0)
            else:
                darkenedlist.append(value - darkened)
        self.darkened = darkenedlist

class Paddle(pygame.sprite.Sprite):

    def __init__(self, color, x):
        self.height = BLOCK*5
        self.width = BLOCK
        self.img = pygame.Surface([self.width, self.height])
        self.img.fill(color)
        self.rect = self.img.get_rect()
        self.rect.centerx = x
        self.rect.centery = SIZE[1] // 2
        self.score = 0

    def move(self, dir):
        self.rect.top = self.rect.top + (dir*BLOCK)

    def draw(self):
        screen.blit(self.img, self.rect)

    def reset(self):
        self.rect.centery = SIZE[1]//2
        self.score = 0

class Net(pygame.sprite.Sprite):

    def __init__(self, y):
        self.img = pygame.Surface([BLOCK, BLOCK])
        self.img.fill(WHITE.normal)
        self.rect = self.img.get_rect()
        self.rect.centerx = SIZE[0]//2
        self.rect.centery = y

    def draw(self):
        screen.blit(self.img, self.rect)
    
class Ball(pygame.sprite.Sprite):
     
    def __init__(self, speed=0):
        self.size = BLOCK
        self.img = pygame.Surface([self.size, self.size])
        self.img.fill(WHITE.normal)
        self.rect = self.img.get_rect()
        self.rect.centerx = SIZE[0]//2
        self.rect.centery = SIZE[1]//2
        if speed == 0:
            self.speedx = (-1 + random.randint(0,1)*2) * SPEED
        else:
            self.speedx = speed
        self.speedy = 0

        self.sfx_wall = pygame.mixer.Sound("./Sounds/sfx_wall.wav")
        self.sfx_score = pygame.mixer.Sound("./Sounds/sfx_score.wav")
        self.sfx_racket = pygame.mixer.Sound("./Sounds/sfx_racket.wav")

    def update(self):
        self.rect.centerx = self.rect.centerx + self.speedx
        self.rect.centery = self.rect.centery + self.speedy
        if self.rect.centerx  > SIZE[0]:
            self.rect.centerx = SIZE[0]//2
            player1.score = player1.score + 1

            if mode == 1 or mode == 2:
                self.sfx_score.play()

            if mode == 2:
                senddict["score"] = None

        if self.rect.centerx < 0:
            self.rect.centerx = SIZE[0]//2
            player2.score = player2.score + 1

            if mode == 1 or mode == 2:
                self.sfx_score.play()

            if mode == 2:
                senddict["score"] = None
        
        if self.rect.centery > SIZE[1]-BLOCK:
            self.speedy = self.speedy - SPEED
            self.sfx_wall.play()
            try:
                if mode == 2:
                    senddict["wall"] = None
            except:
                pass
        if self.rect.centery < BLOCK:
            self.speedy = self.speedy + SPEED
            self.sfx_wall.play()
            try:
                if mode == 2:
                    senddict["wall"] = None
            except:
                pass


    def did_collide(self, paddle, is_up, is_down):
        if pygame.sprite.collide_rect(self, paddle):

            if mode == 1 or mode == 2:
                self.sfx_racket.play()

            if mode == 2:
                senddict["racket"] = None

            if paddle.rect.centerx < SIZE[0]//2:
                self.rect.left = self.rect.right
            else:
                self.rect.right = self.rect.left
            self.speedx = self.speedx * -1
            if is_up:
                self.speedy = self.speedy - SPEED
            if is_down:
                self.speedy = self.speedy + SPEED


    def draw(self):
        screen.blit(self.img, self.rect)
        
    def reset(self, speed):
        self.rect.centerx = SIZE[0]//2
        self.rect.centery = SIZE[1]//2
        self.speedx = speed
        self.speedy = 0

class Cursor(pygame.sprite.Sprite):

    def __init__(self):
        mouse_positions = pygame.mouse.get_pos()
        self.mouseposx = mouse_positions[0]
        self.mouseposy = mouse_positions[1]
        self.img = pygame.Surface([BLOCK, BLOCK])
        self.img.fill(WHITE.normal)
        self.rect = self.img.get_rect()
        self.rect.centerx = self.mouseposx
        self.rect.centery = self.mouseposy

    def update(self):
        mouse_positions = pygame.mouse.get_pos()
        self.mouseposx = mouse_positions[0]
        self.mouseposy = mouse_positions[1]
        self.rect.centerx = self.mouseposx
        self.rect.centery = self.mouseposy

    def did_click(self, button):
        if pygame.sprite.collide_rect(self, button):
            return True
        else: 
            return False

    def draw(self):
        screen.blit(self.img, self.rect)

    def get_pos(self):
        mouse_positions = pygame.mouse.get_pos()
        return mouse_positions

class Render(pygame.sprite.Sprite):

    def __init__(self, sizex, sizey, posx, posy, horizontal="centerx", vertical="centery"):
        self.pos = (posx, posy)
        self.size = (sizex, sizey)
        self.has_rect = False
        self.has_text = False
        self.horizontal = horizontal
        self.vertical = vertical

    def rectangle(self, color):
        self.rect_surface = pygame.Surface(self.size)
        self.rect_surface.fill(color)
        self.rect = self.rect_surface.get_rect()

        exec("self.rect." + self.horizontal + " = self.pos[0]\nself.rect." + self.vertical + " = self.pos[1]")

        self.has_rect = True

    def text(self, color, text, textfont):
        self.text_surface = textfont.render(text, True, color, self.size)
        self.text = self.text_surface.get_rect()

        exec("self.text." + self.horizontal + " = self.pos[0]\nself.text." + self.vertical + " = self.pos[1] + 4")
        
        self.has_text = True

    def draw(self):
        if self.has_rect:
            screen.blit(self.rect_surface, self.rect)
        if self.has_text:
            screen.blit(self.text_surface, self.text)

BLACK = Color([0,0,0])

WHITE = Color([255,255,255])

RED = Color([255,0,0])

GREEN = Color([0,255,0])

BLUE = Color([0,0,255])

mode = 0

cursor = Cursor()

ball = Ball()

player1 = Paddle(RED.normal, BLOCK*2)
player2 = Paddle(BLUE.normal, SIZE[0]-BLOCK*2)

number_of_net = SIZE[1]//BLOCK

nets = []
netx = 0
for i in range((number_of_net//2) + 1):
    net = Net(netx)
    nets.append(net)
    netx = netx + (BLOCK*2)

# clock for setting FPS
clock = pygame.time.Clock()

###################
# Part B: GAME LOOP
###################

def menu():
    global cursor,screen,mode,version,past_mouse
    
    selection = None
    past_mouse = False
    enter_pressed = False

    start_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*3.4)
    start_button.rectangle(GREEN.normal)
    start_button.text(BLACK.normal, "START LOCAL", font)
    start_button.draw()

    host_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*4.7)
    host_button.rectangle(BLUE.normal)
    host_button.text(BLACK.normal, "HOST LAN", font)
    host_button.draw()

    join_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*6)
    join_button.rectangle(RED.normal)
    join_button.text(BLACK.normal, "JOIN LAN", font)
    join_button.draw()

    set_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*7.3)
    set_button.rectangle(WHITE.normal)
    set_button.text(BLACK.normal, "SETTINGS", font)
    set_button.draw()
    
    while mode == 0:
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                mode = 4
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mode = 4
                    
                if event.key == pygame.K_UP:
                    if selection is None:
                        selection = 0
                    elif selection == 0:
                        selection = 3
                    else:
                        selection = selection - 1

                if event.key == pygame.K_DOWN:
                    if selection is None:
                        selection = 3
                    elif selection == 3:
                        selection = 0
                    else:
                        selection = selection + 1
                if event.key == pygame.K_RETURN:
                    enter_pressed = True

        screen.fill(BLACK.normal)

        cursor.update()
        
        mouse_press = pygame.mouse.get_pressed()
        now_mouse = mouse_press[0]

        if cursor.did_click(start_button):
            selection = 0
            if not now_mouse and past_mouse:
                mode = 1
        elif cursor.did_click(host_button):
            selection = 1
            if not now_mouse and past_mouse:
                mode = 2
        elif cursor.did_click(join_button):
            selection = 2
            if not now_mouse and past_mouse:
                mode = 3
        elif cursor.did_click(set_button):
            selection = 3
            if not now_mouse and past_mouse:
                mode = 5

        past_mouse = now_mouse

        if selection == 0:
            start_button = Render(SIZE[0]//2*1.1, SIZE[1]//7*1.1, SIZE[0]//2, SIZE[1]//8*3.4)
            start_button.text(BLACK.normal, "START LOCAL", font_selected)
            if enter_pressed:
                mode = 1
        else:
            start_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*3.4)
            start_button.text(BLACK.normal, "START LOCAL", font)
        start_button.rectangle(GREEN.normal)
        start_button.draw()

        if selection == 1:
            host_button = Render(SIZE[0]//2*1.1, SIZE[1]//7*1.1, SIZE[0]//2, SIZE[1]//8*4.7)
            host_button.text(BLACK.normal, "HOST LAN", font_selected)
            if enter_pressed:
                mode = 2
        else:
            host_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*4.7)
            host_button.text(BLACK.normal, "HOST LAN", font)
        host_button.rectangle(BLUE.normal)
        host_button.draw()

        if selection == 2:
            join_button = Render(SIZE[0]//2*1.1, SIZE[1]//7*1.1, SIZE[0]//2, SIZE[1]//8*6)
            join_button.text(BLACK.normal, "JOIN LAN", font_selected)
            if enter_pressed:
                mode = 3
        else:
            join_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*6)
            join_button.text(BLACK.normal, "JOIN LAN", font)
        join_button.rectangle(RED.normal)
        join_button.draw()

        if selection == 3:
            set_button = Render(SIZE[0]//2*1.1, SIZE[1]//7*1.1, SIZE[0]//2, SIZE[1]//8*7.3)
            set_button.text(BLACK.normal, "SETTINGS", font_selected)
            if enter_pressed:
                mode = 5
        else:
            set_button = Render(SIZE[0]//2, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*7.3)
            set_button.text(BLACK.normal, "SETTINGS", font)
        set_button.rectangle(WHITE.normal)
        set_button.draw()

        enter_pressed = False

        title = Render(SIZE[0]//4,SIZE[1]//2, SIZE[0]//4, SIZE[1]//8*1.5, horizontal="left")
        title.text(WHITE.normal, "PONG", title_font)
        title.draw()

        vershow = Render(SIZE[0]//5*1.2, SIZE[1]//15, SIZE[0] - 4, SIZE[1] - 4, horizontal="right", vertical="bottom")
        vershow.text(WHITE.normal, "VERSION: " + version.upper(), small_font)
        vershow.draw()

        cursor.draw()

        pygame.display.update()
        clock.tick(fps_limit)

#Mode | 0 = Menu | 1 = Local | 2 = LAN Host | 3 = LAN Join | 4 = Quit | 5 = Settings |

while mode != 4:
    menu()
    
    if mode == 2:
        ip = socket.gethostbyname(socket.gethostname())
        port = 0

        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind((ip,port))
        sock.settimeout(0.01)
        wait2 = 0
        data = ""

        while wait2 == 0:
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    wait2 = 3

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        wait2 = 1
            
            try:
                data,playeraddr = sock.recvfrom(1024)
                data = le(data.decode())
                if data[0] == "join":
                    if version in data[1]:
                        sock.sendto("compatible".encode(),playeraddr)
                        #print("Compatible, host version (host compatible to client): " + version + " host compatibility: " + " ".join([v for v in compatibility]) + " client version: " + data[2] + " client compatibility: " + " ".join([v for v in data[1]]))
                        wait2 = 2
                    else:
                        try:
                            if data[2] in compatibility:
                                sock.sendto("compatible".encode(),playeraddr)
                                #print("Compatible, host version (client compatible to host): " + version + " host compatibility: " + " ".join([v for v in compatibility]) + " client version: " + data[2] + " client compatibility: " + " ".join([v for v in data[1]]))
                                wait2 = 2
                            else:
                                sock.sendto("incompatible".encode(),playeraddr)
                        except IndexError:
                            sock.sendto("incompatible".encode(),playeraddr)
            except (socket.timeout, OSError, ValueError):
                pass
            
            screen.fill(BLACK.normal)
            cursor.update()

            join = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8)
            join.text(GREEN.normal, "GAME HOSTED ON IP:", large_font)
            join.draw()

            joinip = Render(SIZE[0]//2*1.4, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*2 + 10)
            joinip.text(WHITE.normal, ip, font)
            joinip.draw()

            join = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*3.5)
            join.text(GREEN.normal, "GAME HOSTED ON PORT:", large_font)
            join.draw()

            joinport = Render(SIZE[0]//4, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*4.5 + 10)
            joinport.text(WHITE.normal, str(sock.getsockname()[1]), font)
            joinport.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*6)
            comp.text(BLUE.normal, "COMPATIBLE IF EITHER PLAYER'S COMPATIBILITY", medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*6.5)
            comp.text(BLUE.normal, "LIST HAS THE OTHER PLAYER'S VERSION.", medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*7)
            comp.text(WHITE.normal, "COMPATIBILITY LIST: " + " ".join([v.upper() for v in compatibility]), medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*7.5)
            comp.text(WHITE.normal, "THIS VERSION: " + version, medium_font)
            comp.draw()

            cursor.draw()
            pygame.display.update()
            clock.tick(fps_limit)


        if wait2 == 1:
            sock.close()
            mode = 0
        elif wait2 == 3:
            sock.close()
            mode = 4

    elif mode == 3:
        ip = ""
        port = ""

        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.settimeout(0.01)

        textbox = 0
        wait3 = 0
        while wait3 == 0:

            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    wait3 = 1
                    mode = 4
                
                if event.type == pygame.KEYDOWN:

                    if chr(event.key) in ("0","1","2","3","4","5","6","7","8","9","."):
                        if textbox == 0 and len(ip) < 17:
                            ip = "{}{}".format(ip,chr(event.key))
                        elif textbox == 1 and chr(event.key) != "." and len(port) < 5:
                            port = "{}{}".format(port,chr(event.key))
                    if event.key == pygame.K_BACKSPACE:
                        if textbox == 0:
                            ip = ip[:len(ip) - 1]
                        else:
                            port = port[:len(port) - 1]
                    if event.key == pygame.K_UP:
                        textbox = 0
                    if event.key == pygame.K_DOWN:
                        textbox = 1
                    if event.key == pygame.K_ESCAPE:
                        wait3 = 1
                        mode = 0
                    if event.key == pygame.K_RETURN:
                        try:
                            playeraddr = (ip, int(port))
                            sock.sendto(str(["join", compatibility, version]).encode(),playeraddr)
                            data,addr = sock.recvfrom(1024)
                            if data == "compatible".encode():
                                wait3 = 2
                            else:
                                ip = ""
                                port = ""
                                textbox = 0
                                
                        except (socket.timeout, OSError, ValueError):
                            ip = ""
                            port = ""
                            textbox = 0

            screen.fill(BLACK.normal)
            
            #=======================
            #Rect draw without Class
            #=======================

            #select_surface = pygame.Surface([SIZE[0]//1.5,SIZE[1]//7])
            #select_surface.fill(WHITE.normal)
            #screen.blit(select_surface, (SIZE[0]//2 - select_surface.get_rect().width//2, SIZE[1]//8*(textbox*3 + 2) - select_surface.get_rect().height//2 + 15))

            cursor.update()

            join = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8)
            join.text(GREEN.normal, "JOIN GAME ON IP:", large_font)
            join.draw()

            joinip = Render(SIZE[0]//2*1.4, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*2 + 10)
            if textbox == 0:
                joinip.rectangle(WHITE.normal)
                joinip.text(BLACK.normal, ip, font)
            else:
                joinip.text(WHITE.normal, ip, font)
            joinip.draw()

            join = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*3.5)
            join.text(GREEN.normal, "JOIN GAME ON PORT:", large_font)
            join.draw()

            joinport = Render(SIZE[0]//4, SIZE[1]//7, SIZE[0]//2, SIZE[1]//8*4.5 + 10)
            if textbox == 1:
                joinport.rectangle(WHITE.normal)
                joinport.text(BLACK.normal, port, font)
            else:
                joinport.text(WHITE.normal, port, font)
            joinport.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*6)
            comp.text(BLUE.normal, "COMPATIBLE IF EITHER PLAYER'S COMPATIBILITY", medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*6.5)
            comp.text(BLUE.normal, "LIST HAS THE OTHER PLAYER'S VERSION.", medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*7)
            comp.text(WHITE.normal, "COMPATIBILITY LIST: " + " ".join([v.upper() for v in compatibility]), medium_font)
            comp.draw()

            comp = Render(SIZE[0]//4, SIZE[1]//10, SIZE[0]//2, SIZE[1]//8*7.5)
            comp.text(WHITE.normal, "THIS VERSION: " + version, medium_font)
            comp.draw()

            cursor.draw()
            pygame.display.update()
            clock.tick(fps_limit)

        if wait3 == 1:
            sock.close()

    elif mode == 5:
        wait5 = 0
        while wait5 == 0:
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    wait5 = 1
                    mode = 4

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        wait5 = 1
                        mode = 0

            screen.fill(BLACK.normal)
            cursor.update()

            showping_set = Render(SIZE[0]//8*5, SIZE[1]//8, SIZE[0]//8, SIZE[1]//8*4, horizontal="left")
            showping_set.text(WHITE.normal, "SHOW PING", font)
            showping_set.draw()

            showping_set = Render(SIZE[0]//8, SIZE[1]//8, SIZE[0]//8*7, SIZE[1]//8*4)
            if showping:
                showping_set.rectangle(GREEN.normal)
                showping_set.text(BLACK.normal, "ON", font)
            else:
                showping_set.rectangle(RED.normal)
                showping_set.text(BLACK.normal, "OFF", font)
            showping_set.draw()

            showfps_set = Render(SIZE[0]//8*5, SIZE[1]//8, SIZE[0]//8, SIZE[1]//8, horizontal="left")
            showfps_set.text(WHITE.normal, "SHOW FPS", font)
            showfps_set.draw()

            showfps_set = Render(SIZE[0]//8, SIZE[1]//8, SIZE[0]//8*7, SIZE[1]//8)
            if showfps:
                showfps_set.rectangle(GREEN.normal)
                showfps_set.text(BLACK.normal, "ON", font)
            else:
                showfps_set.rectangle(RED.normal)
                showfps_set.text(BLACK.normal, "OFF", font)
            showfps_set.draw()

            mouse_press = pygame.mouse.get_pressed()

            if not mouse_press[0]:
                if not past_mouse:
                    if cursor.did_click(showping_set):
                        if showping:
                            showping = False
                        else:
                            showping = True
                    if cursor.did_click(showfps_set):
                        if showfps:
                            showfps = False
                        else:
                            showfps = True
                    past_mouse = True
            else:
                past_mouse = False

            cursor.draw()
            pygame.display.update()
            clock.tick(fps_limit)

    if mode == 1 or (mode == 2 and wait2 == 2) or (mode == 3 and wait3 == 2):
        wait1 = 0
        data = ""
        if mode == 1 or mode == 2:
            ball.reset((-1 + random.randint(0,1)*2) * SPEED)
        else:
            ball.reset(0)
        K_UP = False
        K_DOWN = False
        K_w = False
        K_s = False
        player1.reset()
        player2.reset()
        fps_past = 0.0
        fps = 0.0
        fps_cycle_count = 0
        fps_last_update = 0.0
        ping_past = time.time()
        ping = 0.0
        ping_cycle_count = 0
        ping_last_update = 0.0
        while wait1 == 0:
            #----------------------#
            # STEP 1: GET USER INPUT
            #----------------------#
            event_list = pygame.event.get()
            
            for event in event_list:
                if event.type == pygame.QUIT:
                    wait1 = 1

                if event.type == pygame.KEYDOWN:

                    if mode == 1:
                        if event.key == pygame.K_UP:
                            K_UP = True
                        if event.key == pygame.K_DOWN:
                            K_DOWN = True
                        if event.key == pygame.K_w:
                            K_w = True
                        if event.key == pygame.K_s:
                            K_s = True

                    elif mode == 2:
                        if event.key == pygame.K_UP:
                            K_w = True
                        if event.key == pygame.K_DOWN:
                            K_s = True
                        if event.key == pygame.K_w:
                            K_w = True
                        if event.key == pygame.K_s:
                            K_s = True

                    elif mode == 3:
                        if event.key == pygame.K_UP:
                            K_UP = True
                        if event.key == pygame.K_DOWN:
                            K_DOWN = True
                        if event.key == pygame.K_w:
                            K_UP = True
                        if event.key == pygame.K_s:
                            K_DOWN = True
                    
                    if event.key == pygame.K_ESCAPE:
                        wait1 = 1

                if event.type == pygame.KEYUP:
                    
                    if mode == 1:
                        if event.key == pygame.K_UP:
                            K_UP = False
                        if event.key == pygame.K_DOWN:
                            K_DOWN = False
                        if event.key == pygame.K_w:
                            K_w = False
                        if event.key == pygame.K_s:
                            K_s = False
                    
                    elif mode == 2:
                        if event.key == pygame.K_UP:
                            K_w = False
                        if event.key == pygame.K_DOWN:
                            K_s = False
                        if event.key == pygame.K_w:
                            K_w = False
                        if event.key == pygame.K_s:
                            K_s = False
                    
                    elif mode == 3:
                        if event.key == pygame.K_UP:
                            K_UP = False
                        if event.key == pygame.K_DOWN:
                            K_DOWN = False
                        if event.key == pygame.K_w:
                            K_UP = False
                        if event.key == pygame.K_s:
                            K_DOWN = False
            
            if K_w and player1.rect.top > BLOCK:
                player1.move(-1)

            if K_s and player1.rect.bottom < SIZE[1]-BLOCK:
                player1.move(1)

            if K_UP and player2.rect.top > BLOCK:
                player2.move(-1)

            if K_DOWN and player2.rect.bottom < SIZE[1]-BLOCK:
                player2.move(1)

            senddict = {}

            if mode == 2:
                if K_w:
                    senddict["up"] = True
                else:
                    senddict["up"] = False
                if K_s:
                    senddict["down"] = True
                else:
                    senddict["down"] = True

                senddict["paddlepos"] = player1.rect.top
                senddict["paddlescore"] = player1.score

                senddict["ballx"] = ball.rect.centerx
                senddict["bally"] = ball.rect.centery
                senddict["ballspeedx"] = ball.speedx
                senddict["ballspeedy"] = ball.speedy

                ping = time.time() - ping_past

                try:
                    sock.sendto(str(senddict).encode(), playeraddr)
                    data,addr = sock.recvfrom(1024)
                    data = le(data.decode())
                except (socket.timeout, OSError):
                    pass
                else:
                    ping_past = time.time()
                    for key in data:
                        if key == "up":
                            if data[key]:
                                K_UP = True
                            else:
                                K_UP = False
                        elif key == "down":
                            if data[key]:
                                K_DOWN = True
                            else:
                                K_DOWN = False
                        elif key == "paddlepos":
                            player2.rect.top = data[key]
                        elif key == "paddlescore":
                            player2.score = data[key]
                    data = ""

                if ping > 0.5:
                    wait1 = 2

            elif mode == 3:
                if K_UP:
                    senddict["up"] = True
                else:
                    senddict["up"] = False
                if K_DOWN:
                    senddict["down"] = True
                else:
                    senddict["down"] = False
                
                senddict["paddlepos"] = player2.rect.top
                senddict ["paddlescore"] = player2.score
                
                ping = time.time() - ping_past

                try:
                    sock.sendto(str(senddict).encode(), playeraddr)
                    data,addr = sock.recvfrom(1024)
                    data = le(data.decode())
                except (socket.timeout, OSError, ValueError):
                    pass
                else:
                    ping_past = time.time()
                    for key in data:
                        if key == "up":
                            if data[key]:
                                K_w = True
                            else:
                                K_w = False
                        elif key == "down":
                            if data[key]:
                                K_s = True
                            else:
                                K_s = False
                        elif key == "paddlepos":
                            player1.rect.top = data[key]
                        elif key == "paddlescore":
                            player1.score = data[key]
                        elif key == "ballx":
                            ball.rect.centerx = data[key]
                        elif key == "bally":
                            ball.rect.centery = data[key]
                        elif key == "ballspeedx":
                            ball.speedx = data[key]
                        elif key == "ballspeedy":
                            ball.speedy = data[key]
                        elif key == "score":
                            ball.sfx_score.play()
                        elif key == "wall":
                            ball.sfx_wall.play()
                        elif key == "racket":
                            ball.sfx_racket.play()
                    data = ""

                if ping > 0.5:
                    wait1 = 2
            
            fps = 1/(time.time() - fps_past)
            fps_past = time.time()

            #------------------------#
            # STEP 2: UPDATE GAME DATA
            #------------------------#

            ball.update()

            ball.did_collide(player1, K_w, K_s)
            ball.did_collide(player2, K_UP, K_DOWN)

            #-----------#
            #STEP 3: DRAW
            #-----------#

            
            # First draw the background
            screen.fill(BLACK.normal)
            
            # Next draw all game objects

            player1.draw()
            player2.draw()

            score1 = Render(100, 100, 10, BLOCK + 4, horizontal="left", vertical="top")
            score1.text(WHITE.normal, str(player1.score), font)
            score1.draw()

            score2 = Render(100, 100, SIZE[0] - 4, BLOCK + 4, horizontal="right", vertical="top")
            score2.text(WHITE.normal, str(player2.score), font)
            score2.draw()

            for net in nets:
                net.draw()

            if showping:
                if mode == 2 or mode == 3:

                    ping_surface = Render(SIZE[0]//8*2.8, SIZE[1]//16, SIZE[0]//8*0.8, BLOCK + 4, horizontal="left", vertical="top")
                    ping_surface.rectangle(BLACK.normal)
                    if pingval == 1:
                        ping_surface.text(WHITE.normal, "PING: " + str(int(ping_last_update*1000)) + "MS", small_font)
                    else:
                        ping_surface.text(WHITE.normal, "PING: " + str(int(ping_last_update*1000*pingval)/pingval) + "MS", small_font)
                        print("else")
                    ping_surface.draw()
                    
            if showfps:
                if (mode == 2 or mode == 3) and showping:
                    fps_surface = Render(SIZE[0]//8*2.8, SIZE[1]//16, SIZE[0]//8*4.2, BLOCK + 4, horizontal="left", vertical="top")
                else:
                    fps_surface = Render(SIZE[0]//8*2.8, SIZE[1]//16, SIZE[0]//8*0.8, BLOCK + 4, horizontal="left", vertical="top")
                fps_surface.rectangle(BLACK.normal)
                if fpsval == 1:
                    fps_surface.text(WHITE.normal, "FPS: " + str(int(fps_last_update)), small_font)
                else:
                    fps_surface.text(WHITE.normal, "FPS: " + str(int(fps_last_update*fpsval)/fpsval), small_font)
                fps_surface.draw()

            ball.draw()

            pygame.draw.rect(screen, WHITE.normal, [0,0,SIZE[0],BLOCK])
            pygame.draw.rect(screen, WHITE.normal, [0,SIZE[1]-BLOCK, SIZE[0], BLOCK])

            if ping_cycle_count < pingrefresh:
                ping_cycle_count = ping_cycle_count + 1
            else:
                ping_cycle_count = 0
                ping_last_update = ping

            if fps_cycle_count < fpsrefresh:
                fps_cycle_count = fps_cycle_count + 1
            else:
                fps_cycle_count = 0
                fps_last_update = fps
            pygame.display.update()
            clock.tick(fps_limit)

        if wait1 == 1:
            if mode == 2 or mode == 3:
                sock.close()
            player1.reset()
            player2.reset()
            mode = 0
        elif wait1 == 2:
            sock.close()
            player1.reset()
            player2.reset()

            while wait1 == 2:
                event_list = pygame.event.get()

                for event in event_list:
                    if event.type == pygame.QUIT:
                        wait1 = 3
                        mode = 4
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            wait1 = 3
                        elif event.key == pygame.K_RETURN:
                            wait1 = 3

                screen.fill(BLACK.normal)
                cursor.update()

                info_surface = font.render("PLAYER DISCONNECTED", True, WHITE.normal, [100,100])
                screen.blit(info_surface, (SIZE[0]//2 - info_surface.get_rect().width//2,SIZE[1]//2 - info_surface.get_rect().height//2))

                cursor.draw()
                pygame.display.update()
                clock.tick(fps_limit)
            mode = 0
pygame.quit()
sys.exit()