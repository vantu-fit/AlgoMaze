import pygame
import sys
from queue import Queue
import threading
from button import Button

pygame.init()
# Constants
TILE_X,TILE_Y = 32,32
WALL_COLOR = (0, 0, 0)
RED = (0, 0, 0)
game_height,game_width=0,0
# CHARACTER_COLOR = pygame.image.load("./img/walle.png")
PIT_COLOR = (0,0,225)
font=pygame.font.Font('./font/Audiowide-Regular.ttf',15)
# ROCK_COLOR=(0,225,0)

active_maze=None
keys=[]
me=None
dx=[1,-1,0,0]
dy=[0,0,1,-1]
screen=None
# pygame.image.load("./img/walle.png")

def org_draw(s,x,y):
    screen.blit(s,(x, y))

def draw(player_car,x,y,k=1):
    screen.blit(player_car,(TILE_X*x+menu_bar_width, TILE_Y*y))

class Sprite:
    def __init__(self,sprites):
        self.sprites=sprites
        self.speed=0.1
        self.curSprite=0
    def animate(self,x,y):
        self.curSprite+=1
        draw(self.sprites[int(self.curSprite)%len(self.sprites)],x,y,1)

import queue
class Object:
    def __init__(self,name,x,y,sprites):
        self.name=name
        self.x=x
        self.y=y
        self.vx,self.vy=x,y
        # self.idles=idles
        # self.runs=runs
        self.move=0
        self.sprites=sprites
        self.queue=queue.Queue()

    @staticmethod
    def check_move(x,y): #depend on object
        global active_maze
        if (Object.check_boundary(x,y)==0):
            return 0
        if (active_maze[y][x]=='#' or active_maze[y][x]=='$'):
            return 0
        return 1
    
    @staticmethod
    def check_boundary(xx,yy):
        global active_maze
        if (xx>=len(active_maze[0]) or xx<0 or yy>=len(active_maze) or yy<0):
            return 0
        return 1

    def movee(self,changeX,changeY):
        # print(2)
        i=0.1
        while i <=1:
            clock.tick(48)
            self.vx+=changeX*0.1
            self.vy+=changeY*0.1
            i+=0.1
        self.move=0
        
    def upd_pos(self,changeX,changeY):
        # print(self.x,self.y)
        if changeX+changeY!=0 and self.check_move(changeX,changeY) and self.move==0 :
            # self.move=1
            self.queue.put((changeX,changeY))
            self.x+=changeX
            self.y+=changeY
        if not self.queue.empty():
            # self.movee(self.queue.get())
            changeX,changeY=self.queue.get()
            thread=threading.Thread(target=lambda:self.movee(changeX,changeY))
            thread.start()
    
    def draw(self):
        self.sprites.animate(self.vx,self.vy)
    

keys=[]
class Key(Object):
    def __init__(self,name,x,y,sprites,weight):
        super().__init__(name,x,y,sprites)
        # self.open=0
        self.weight=weight
        self.number=font.render(str(weight), True, RED)
    def check_move(self,changeX,changeY): #depend on object
        # if (self.move):return 0
        xx,yy=self.x+changeX,self.y+changeY
        if (Object.check_boundary(xx,yy)==0):
            return 0
        if (active_maze[yy][xx]=='#' or active_maze[yy][xx]=='$'):
            return 0
        return 1
    def draw(self):
        super().draw()
        text_rect = self.number.get_rect()
        width=self.vx*TILE_X
        height=self.vy*TILE_Y
        # Calculate the position to place the text at the center of the screen
        text_x = ((TILE_X - text_rect.width) // 2 + width + menu_bar_width)*1.01
        text_y = (TILE_Y - text_rect.height) // 2 +height-8*TILE_Y/32
        org_draw(self.number,text_x,text_y)
        # draw(self.number,self.vx,self.vy,1)

    @staticmethod
    def findd(xx,yy):
        for i,key in enumerate(keys):
            if (key.x==xx and key.y==yy):
                return i
        return -1
    
    @staticmethod
    def trace_route(sx,sy):
        global active_maze,me
        queue=Queue()
        dp=[]
        for y, row in enumerate(active_maze):
            dp.append([])
            for x, tile in enumerate(row):
                dp[y].append(None)

        dp[sy][sx]=0
        fy,fx=None,None
        for i in range(4):
            if Object.check_move(sx+dx[i],sy+dy[i]):
                dp[sy+dy[i]][sx+dx[i]]=0
                
                queue.put((sx+dx[i],sy+dy[i]))

        while (not queue.empty()):
            x,y=queue.get()
            for i in range(4):
                xx,yy=x+dx[i],y+dy[i]
                if Object.check_move(xx,yy):
                    if dp[yy][xx]==None:
                        
                        dp[yy][xx]=dp[y][x]+1
                        
                        queue.put((xx,yy))
                    if (active_maze[yy][xx]=='@'):
                        fy,fx=yy,xx
                        break
            if fy!=None: break              
        # return
        while (True):
            clock.tick(2)
            for i in range(4):
                ty=fy+dy[i]
                tx=fx+dx[i]
                if (dp[ty][tx]==dp[fy][fx]-1):
                    fy,fx=ty,tx
                    # print(ty,tx)
                    me.upd_pos(dx[i],dy[i])
                    break
                if (dp[fy][fx]==0):
                    break
            if (dp[fy][fx]==0):
                    break
        # print("#####")

    @staticmethod
    def get_trace(i):
        if (i>=len(keys)):
            return
        Key.trace_route(keys[i].x,keys[i].y)

    
class Me(Object):
    def __init__(self,name,x,y,leftS):
        super().__init__(name,x,y,leftS)
        self.left=1
    def check_move(self, changeX, changeY):
        global stat_weight
        xx,yy=int(self.x+changeX),int(self.y+changeY)
        if not Object.check_boundary(xx,yy):
            return 0
        # print(xx,yy)
        if (active_maze[yy][xx]=='#'):
            return 0
        
        if (active_maze[yy][xx]=='$'):
            j=Key.findd(xx,yy)
            # print(j)   
            if keys[j].check_move(changeX,changeY):
                stat_weight+=keys[j].weight
                keys[j].upd_pos(changeX,changeY)
            else:
                return 0
        if (changeX==1):
            self.sprites=RobotSpriteR
        else:
            self.sprites=RobotSpriteL
        return 1

def resize(img,x,y):
        return pygame.transform.scale(img,(x,y))

WaterSprite,RobotSpriteL,RobotSpriteR,GrassSprite,RobotSpriteL,RockSprite,Closed_TreasureSprite,KeySprite,Opened_TreasureSprite,SoilSprite,PauseImage,PauseImageH,RockSprite1,RockSprite2=None,None,None,None,None,None,None,None,None,None,None,None,None,None

def resetSprite():
    global RobotSpriteL,RobotSpriteR,GrassSprite,RobotSpriteL,RockSprite,Closed_TreasureSprite,KeySprite,Opened_TreasureSprite,SoilSprite,PauseImage,PauseImageH,WaterSprite,RockSprite1,RockSprite2
    RobotSpriteL=Sprite([resize(pygame.image.load(f'./img/robotball/skeleton-animation_{str(i).zfill(2)}.png'),TILE_X,TILE_Y) for i in range(0,16)])
    RobotSpriteR=Sprite([pygame.transform.flip(resize(pygame.image.load(f'./img/robotball/skeleton-animation_{str(i).zfill(2)}.png'),TILE_X,TILE_Y),True,False) for i in range(0,16)])
    GrassSprite= Sprite([resize(pygame.image.load('./img/soil1.png'),TILE_X,TILE_Y)])
    RockSprite= Sprite([resize(pygame.image.load('./img/coal.png'),TILE_X,TILE_Y)])
    RockSprite1= Sprite([resize(pygame.image.load('./img/rocks.png'),TILE_X,TILE_Y)])
    RockSprite2= Sprite([resize(pygame.image.load('./img/granite.png'),TILE_X,TILE_Y)])
    Closed_TreasureSprite=Sprite([resize(pygame.image.load('./img/treasure.png'),TILE_X,TILE_Y)])
    KeySprite=Sprite([resize(pygame.image.load('./img/key.png'),TILE_X*1.15,TILE_Y*1.15)])
    SoilSprite=Sprite([resize(pygame.image.load('./img/grass2.png'),TILE_X,TILE_Y)])
    Opened_TreasureSprite=Sprite([resize(pygame.image.load('./img/treasure1.png'),TILE_X,TILE_Y)])
    WaterSprite=Sprite([resize(pygame.image.load('./img/water.png'),TILE_X,TILE_Y)])

weightss=[]

def load_maze(filename):
    global weights,TILE_X,TILE_Y,maze_height,maze_width
    with open(filename, 'r') as file:
        numbers_line = file.readline().strip()
        weightss.append(list(map(int, numbers_line.split())))
        maze = [list(line.strip('\n')) for line in file.readlines()]

    w=getMax([len(a) for a in maze])
    for i in range(len(maze)):
        while len(maze[i])<w:
            maze[i].append(')')
        
    return maze


def update_stats(): #update steps and weight
    global steps,stat_weight
    statfont=pygame.font.Font('./font/Audiowide-Regular.ttf',20)
    text_steps=statfont.render(f"Steps: {steps}",True,'Orange')
    text_weight=statfont.render(f"Total weight: {stat_weight}",True,'Orange')
    org_draw(text_steps,50,500)
    org_draw(text_weight,50,530)

def update_size():
    global TILE_X,TILE_Y,screen_height,screen_width,screen_height,menu_bar_height,menu_bar_width,screen
    TILE_X= int(400/maze_width)
    TILE_Y= int(400/maze_height)
    game_width=TILE_X*maze_width
    game_height=TILE_Y*maze_height
    menu_bar_height=600
    menu_bar_width=200
    screen_width=game_width+menu_bar_width
    screen_height=menu_bar_height
    resetSprite()
    screen = pygame.display.set_mode((screen_width, screen_height))
    # print(TILE_SIZE,screen_width,game_width)

render_maze=[]
def draw_update_maze(screen,maze):
    global me,keys,render_maze
    new_maze=[]
    for y, row in enumerate(maze):
        new_maze.append([])
        for x, tile in enumerate(row):
            SoilSprite.animate(x,y)
            if tile=="#":
                GrassSprite.animate(x,y)
                a=random.randint(0,30)%3
                if (render_maze[y][x] is None):
                    # print(123)
                    if (a==0):
                        render_maze[y][x]=RockSprite2
                    elif (a==1):
                        render_maze[y][x]=RockSprite2
                    else:
                        render_maze[y][x]=RockSprite
   
                render_maze[y][x].animate(x,y)
            elif tile==".":
                if Key.findd(x,y)==-1:
                    Closed_TreasureSprite.animate(x,y)
                else:
                    Opened_TreasureSprite.animate(x,y)
            elif tile==")":
                GrassSprite.animate(x,y)
            new_maze[y].append(tile)

    for key in keys:
        # print(key.x,key.y)
        key.draw()
        new_maze[int(key.y)][int(key.x)]='$'

    me.draw()
    new_maze[int(me.y)][int(me.x)]='@'
    return new_maze

fontLevel= pygame.font.Font('./font/Audiowide-Regular.ttf',25)

def calPosLevel(x):
    sz=60
    if (x<6):
        return (sz,sz*x+30)
    else:
        return (sz*2+20,30+sz*(x-5)+30)

textLevel= fontLevel.render("Levels:", True, 'Red')
textMode=fontLevel.render("Modes:", True, 'Red')
StartButton= Button(image=resize(pygame.image.load('./img/pause-button.png'),40,40),
                        Himage=resize(pygame.image.load('./img/play-button.png'),40,40),
                        pos=(50,20),font=font,
                        text_input="",base_color='White', hovering_color='Green',cSelected='Orange')
LevelButtons= [Button(image=None,Himage=None,pos=calPosLevel(i),font=fontLevel,selected=(i==1),
                      text_input=str(i).zfill(2),base_color="White", hovering_color="Green",cSelected='Orange') for i in range(1,11,1)]

def calPosMode(x):
    k=150+x*100
    return (k,450)

# algos=['DFS','BFS','UCS',"A*"]
algos = ['A*','BFS','DFS','UCS']
ModeButtons=[Button(image=None,Himage=None,pos=calPosMode(i),font=fontLevel,selected=(i==0),
                      text_input=algos[i],base_color="White", hovering_color="Green",cSelected='Orange') for i in range(4) ]

def draw_update_UI(MOUSE_POS):
    global LevelButtons
    org_draw(textLevel,10,40)
    org_draw(textMode,10,430)
    StartButton.update(screen)
    for LevelButton in LevelButtons:
        LevelButton.changeColor(MOUSE_POS)
        LevelButton.update(screen)
    for button in ModeButtons:
        button.changeColor(MOUSE_POS)
        button.update(screen)

import random

def clear_maze(maze):
    n_maze=[]
    for y, row in enumerate(maze):
        n_maze.append([])
        for x, tile in enumerate(row):
            if tile=="@" or tile=='$':
                tile=" "
            if tile=='+' or tile=='*':
                tile='.'
            n_maze[y].append(tile)
    return n_maze

def get_object(maze):
    global me,keys
    i=0
    me,keys=None,[]
    weights=weightss[level]
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            if (tile=='$' or tile =='*'):
                key=Key(tile,x,y,KeySprite,weights[i])
                i+=1
                keys.append(key)
            if (tile=='@' or tile=='+'):
                me=Me(tile,x,y,RobotSpriteL)


def print_maze(maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            print(tile,end='')
        print("")

def update_object(changeX,changeY):
    me.upd_pos(changeX,changeY)


start,level,mode=0,0,0
start_time = 0
elapsed_time = 0

output=dict()
def readOutput():
    global output
    files=os.listdir('./output/all')
    for i in algos:
        output[i]=[[] for _ in range(10)]
    for j,file in enumerate(files):
        lines=None
        with open("./output/all/"+file,'r') as f:
            lines=f.readlines()
        lines= [a.strip("\n") for a in lines]
        for i in range(0,len(lines),3):
            if (lines[i]=='No solution found.'):
                continue
            output[lines[i]][j]=lines[i+2].lower()

def reset_stopwatch():
    global start_time, elapsed_time
    # print(123)
    start_time = pygame.time.get_ticks()
    # elapsed_time = 0

def startTimer():
    # if start==0: return
    global elapsed_time
    statfont=pygame.font.Font('./font/Audiowide-Regular.ttf',20)
    if start:
        elapsed_time = pygame.time.get_ticks() - start_time
    # Convert milliseconds to minutes, seconds, and milliseconds
    minutes = int(elapsed_time / 60000)
    seconds = int((elapsed_time % 60000) / 1000)
    milliseconds = int((elapsed_time % 1000)/10)

    # Render text
    time_str = f"Time: {minutes:02}:{seconds:02}:{milliseconds:02}"
    # text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    text=statfont.render(time_str,True,'Orange')
    # screen.blit(text, text_rect)
    org_draw(text,50,560)
    
stat_weight,steps=0,0
def runMaze():
    global output,me,steps,stat_weight
    res=output[algos[mode]][level]
    steps=0
    stat_weight=0
    # print(res)
    for i,c in enumerate(res):
        if (start==0):
            return
        d=None
        # print(c)
        steps=i
        stat_weight+=1
        if c=='u': d=3
        if c=='r': d=0
        if c=='l': d=1
        if c=='d': d=2
        update_object(dx[d],dy[d])
        # update_stats(i,stat_weight)
        clock.tick(3)
        
    checkStart((StartButton.x_pos,StartButton.y_pos))

def checkStart(pos):
    global start
    # print(output)
    if not StartButton.checkForInput(pos): return
    start=1-start
    if (start==1):
        # print(start)
        reset_stopwatch()
        resetMaze()
        thread= threading.Thread(target=runMaze)
        thread.start()
 
def getMax(a):
    res=0
    for b in a:
        res=max(b,res)
    return res

def resetMaze():
    global level,org_mazes,static_maze,active_maze,render_maze,maze_height,maze_width
    active_maze= org_mazes[level]
    static_maze = clear_maze(active_maze) 
    maze_width=getMax([len(a) for a in active_maze])
    maze_height=len(active_maze)
    render_maze = [[None for _ in range(20)] for _ in range(20)]
    update_size()
    get_object(active_maze)

def check_buttons(buttons,pos):
    # global start
    k=None
    global level,mode,org_mazes,active_maze,static_maze
    for i in range(len(buttons)):

        if buttons[i].checkForInput(pos):
            k=i
            break
    if k!= None:
        # start=0
        # checkStart((StartButton.x_pos,StartButton.y_pos))
        for i in range(len(buttons)):
            if i!=k:
                buttons[i].resetSelection()
        if len(buttons)==10: #levels:
            level=k
            resetMaze()
        else:
            mode=k

# Set up the screen dimensions
screen_width = 800
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Blind search")


# Create the menu bar surface
menu_bar_width = 200
menu_bar_height = 0
menu_bar_surface = pygame.Surface((menu_bar_width, menu_bar_height))
menu_bar_surface.fill((100, 100, 100))  # Fill the menu bar surface with a color

clock = pygame.time.Clock()
FPS = 32
static_maze,org_mazes=None,None

import os 

def main(filename):
    global screen,static_maze,A_screen,maze_width,maze_height,game_height,game_width,render_maze,start,org_mazes
    global start,start_time,elapsed_time
    # Initialize pygame
    global active_maze
    # pygame.init()
    
    # Load maze
    org_mazes=[load_maze('./maze/'+filename) for filename in os.listdir('./maze')]
    resetMaze()
    # Set up display
    readOutput()

    clock = pygame.time.Clock()

    

    # Main loop
    running = True
    while running:
        MOUSE_POS = pygame.mouse.get_pos()
        changeX,changeY=0,0          
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                check_buttons(LevelButtons,MOUSE_POS)
                check_buttons(ModeButtons,MOUSE_POS) 
                checkStart(MOUSE_POS) 
            if event.type == pygame.QUIT:
                running = False
            if event.type== pygame.KEYUP and start==0:
                if event.key== pygame.K_LEFT:
                    changeX-=1
                if event.key== pygame.K_RIGHT:
                    changeX+=1
                if event.key== pygame.K_DOWN:
                    changeY+=1
                if event.key== pygame.K_UP:
                    changeY-=1
                    # startTimer()
                    # update_stats()
        # update_size()
        screen.fill((25, 25, 25))
        update_object(changeX,changeY)
        # Draw the maze
        active_maze=draw_update_maze(screen, static_maze)

        #Update stats
        update_stats()
        startTimer()

        # Update the display UI
        draw_update_UI(MOUSE_POS)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":

    main("")