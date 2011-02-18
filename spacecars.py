#! /usr/bin/env python
#  dependencies: pygame 1.9.1 
# SPACECARS v1.1 Written by Robby Cerantola 
# License is GPL 

# INIT
import pygame, math, sys,os, random
from pygame.locals import *


def play_music(music_file):
    """
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
    """
    clock = pygame.time.Clock()
    try:
        pygame.mixer.music.load(music_file)
        print "Music file %s loaded!" % music_file
    except pygame.error:
        print "File %s not found! (%s)" % (music_file, pygame.get_error())
        return
    pygame.mixer.music.play()
    #while pygame.mixer.music.get_busy():
        # check if playback has finished
     #   clock.tick(30)

music_file = "music.mid"

freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 1024    # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)

# optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.8)




RESOLUTION=(1024,768)
pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()

#Add joysticks for cars
try:
    joy=pygame.joystick.Joystick(0)
    joy.init()
    print "Using Joystick 0" 
except:
    print "Joystick 0 not found!!"
    
try:
    joy2=pygame.joystick.Joystick(1)
    joy2.init()
    print "Using Joystick 1"
except:
    print "Joystick 1 not found!!"
    
    
# show introduction image
background=pygame.image.load("presentation.png")
background=pygame.transform.scale(background,RESOLUTION)
screen.blit(background,(0,0))
pygame.display.flip()

#wait untill spacebar key is pressed

done = False
while not done:
   for event in pygame.event.get():
      if (event.type == KEYUP) or (event.type == KEYDOWN):
         #print event
         if (event.key == K_SPACE):
            done = True


#load resources
background=pygame.image.load("background.png")
background=background.convert()
screen.blit(background,(0,0))

victory_sound=pygame.mixer.Sound("victory.wav")
explosion_sound=pygame.mixer.Sound("bum.wav")
bell_sound=pygame.mixer.Sound("AGOGO.wav")
sputnik=pygame.mixer.Sound("morse.wav")
sputnik.play()

font=pygame.font.Font(None,17)

play_music(music_file)


def winner(txt):
	text = font.render(txt,True,(255,255,255),(159,182,205))
        textRect=text.get_rect()
        textRect.x=(RESOLUTION[0]/2)
        textRect.y=(RESOLUTION[1]/2)
        screen.blit(text,textRect)
        pygame.mixer.music.stop()
        victory_sound.play()
	pygame.display.flip()
	done = False
	while not done:
	    for event in pygame.event.get():
    		if (event.type == KEYUP) or (event.type == KEYDOWN):
         	    if (event.key == K_SPACE):
        		done = True
			sys.exit()



def load_sliced_sprites(w, h, filename):
    '''
    Specs :
    	Master can be any height.
    	Sprites frames width must be the same width
    	Master width must be len(frames)*frame.width
    Assuming you ressources directory is current directory
    '''
    images = []
    master_image = pygame.image.load(filename).convert_alpha()

    master_width, master_height = master_image.get_size()
    for i in xrange(int(master_width/w)):
    	images.append(master_image.subsurface((i*w,0,w,h)))
    return images


class AnimatedSprite(pygame.sprite.Sprite):
    """Permette l'implementazione di Sprite animate con pygame
    Si possono usare i metodi della classe pygame.sprite.RenderPlain"""
    def __init__(self, images,position, fps=10, ):
        pygame.sprite.Sprite.__init__(self)
        self._images = images
        
        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0
        self.position=position
        self.rect = self._images[0].get_rect()
        # Call update to set our first image.
        self.update(pygame.time.get_ticks())

    def update(self, t):
        # Note that this doesn't work if it's been more that self._delay
        # time between calls to update(); we only update the image once
        # then, but it really should be updated twice.
        self.rect.center = self.position
        if t - self._last_update > self._delay:
            self._frame += 1
            if self._frame >= len(self._images): self._frame = 0
            self.image = self._images[self._frame]
            self._last_update = t
        
    
    def draw(self,screen):
        """Si usa per il refresh manuale"""
        self.update(pygame.time.get_ticks())      
        screen.blit(self.image,self.position)
     
class CarSprite(pygame.sprite.Sprite):
    MAX_FORWARD_SPEED = 10
    MAX_REVERSE_SPEED = 10
    ACCELERATION = 2
    TURN_SPEED = 5
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image)
        self.position = position
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        self.hiper=0
        self.score=0
        self.damage=0
    def update(self, deltat):
        # SIMULATION
        self.speed += (self.k_up + self.k_down)
        if self.speed > self.MAX_FORWARD_SPEED:
            self.speed = self.MAX_FORWARD_SPEED       
        if self.speed < -self.MAX_REVERSE_SPEED:
            self.speed = -self.MAX_REVERSE_SPEED        
        self.direction += (self.k_right + self.k_left)
        x, y = self.position
        rad = self.direction * math.pi / 180
        y += self.speed*math.sin(rad)
        x += self.speed*math.cos(rad)
        
        if self.hiper==0:
            if x <1 : x=1
            if x >RESOLUTION[0] : x=RESOLUTION[0]
            if y <1 : y =1
            if y > RESOLUTION[1] : y=RESOLUTION[1]
        if self.hiper==1:
            if x <1 : x=RESOLUTION[0]
            if x >RESOLUTION[0] : x=1
            if y <1 : y =RESOLUTION[1]
            if y > RESOLUTION[1] : y=1
            self.hiper=0
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
    
    def accident(self,value):
        if self in value:
        
            self.score +=1
            print "Score:",self.score
            self.speed=0
    
    def caraccident(self):
        self.direction = self.direction * -1 

class PadSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('bomb.png')
    hit = pygame.image.load('explosion.png')
    t=0
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image=self.normal
        self.dirx=random.randrange(-1,1,1)
        self.diry=random.randrange(-1,1,1)
    
    def update(self, hit_list):
        
        if self in hit_list:
            if self.image==self.normal:
        	explosion_sound.play()
            self.image = self.hit
            
            self.t += 1
        else: self.image = self.normal
        if self.t>15:
            self.kill()
            self.image=self.normal
            self.t=0
        
            
    def move(self):   
        x,y=self.rect.center
        if x<0 : 
            x=0
            self.dirx=1
        if y<0:
            y=0
            self.diry=1
        if x > RESOLUTION[0]:
            x=RESOLUTION[0]
            self.dirx=-1
        if y > RESOLUTION[1]:
            y=RESOLUTION[1]
            self.diry=-1
        self.rect.center=(x+self.dirx,y+self.diry)
        


class AlienSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('alien.png')
    hit = pygame.image.load('pizza.png')
    t=0
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image=self.normal
        self.dirx=random.randrange(-1,1,1)
        self.diry=random.randrange(-1,1,1)
        
    def update(self, hit_list,subject):
        
        if self in hit_list:
            if self.image==self.normal:
        	bell_sound.play()
            self.image = self.hit
            
            self.t += 1
        else: self.image = self.normal
        if self.t>8:
            self.kill()
            subject.score +=1
            self.t=0
        
            
    def move(self):   
        x,y=self.rect.center
        if x<0 : 
            x=0
            self.dirx=1
        if y<0:
            y=0
            self.diry=1
        if x > RESOLUTION[0]:
            x=RESOLUTION[0]
            self.dirx=-1
        if y > RESOLUTION[1]:
            y=RESOLUTION[1]
            self.diry=-1
        self.rect.center=(x+self.dirx,y+self.diry)
        

class TextProgress:
    def __init__(self, font, message, color, bgcolor):
        self.font = font
        self.message = message
        self.color = color
        self.bgcolor = bgcolor
        self.offcolor = [c^40 for c in color]
        self.notcolor = [c^0xFF for c in color]
        self.text = font.render(message, 0, (255,0,0), self.notcolor)
        self.text.set_colorkey(1)
        self.outline = self.textHollow(font, message, color)
        self.bar = pygame.Surface(self.text.get_size())
        self.bar.fill(self.offcolor)
        width, height = self.text.get_size()
        stripe = Rect(0, height/2, width, height/4)
        self.bar.fill(color, stripe)
        self.ratio = width / 100.0

    def textHollow(self, font, message, fontcolor):
        base = font.render(message, 0, fontcolor, self.notcolor)
        size = base.get_width() + 2, base.get_height() + 2
        img = pygame.Surface(size, 16)
        img.fill(self.notcolor)
        base.set_colorkey(0)
        img.blit(base, (0, 0))
        img.blit(base, (2, 0))
        img.blit(base, (0, 2))
        img.blit(base, (2, 2))
        base.set_colorkey(0)
        base.set_palette_at(1, self.notcolor)
        img.blit(base, (1, 1))
        img.set_colorkey(self.notcolor)
        return img

    def render(self, percent=50):
        surf = pygame.Surface(self.text.get_size())
        if percent < 100:
            surf.fill(self.bgcolor)
            surf.blit(self.bar, (0,0), (0, 0, percent*self.ratio, 100))
        else:
            surf.fill(self.color)
        surf.blit(self.text, (0,0))
        surf.blit(self.outline, (-1,-1))
        surf.set_colorkey(self.notcolor)
        return surf


class StatusBar:
    def __init__(self, text="StatusBar",colour=(255,255,255),initialvalue=0, position=(0,0)):
        self.position=position
        self.text=text
        bigfont = pygame.font.Font(None, 30)
        self.colour = colour
        self.renderer = TextProgress(bigfont, self.text, self.colour, (40, 40, 40))
        self.update(initialvalue)
    
    def update(self,value):
        self.textprogress = self.renderer.render(value)
        screen.blit(self.textprogress,self.position)        
    



# CREATE CARs Bombs and satelite AND RUN

rect = screen.get_rect()
car = CarSprite('car.png', rect.center)
car2 = CarSprite('car2.png',(100,100))

alien=AlienSprite((500,500))

explosion=AnimatedSprite(load_sliced_sprites(20,20,'explosed-sprite.png'),(180,400))

satellite=AnimatedSprite(load_sliced_sprites(180,256,'satellite.png'),(200,300))

pads = [
    PadSprite((200, 200)),
    PadSprite((800, 200)),
    PadSprite((200, 600)),
    PadSprite((800, 600)),
]


pad_group = pygame.sprite.RenderPlain(*pads)

car_group = pygame.sprite.RenderPlain(car,car2)

alien_group=pygame.sprite.RenderPlain(alien)

animated_group = pygame.sprite.RenderPlain(satellite,explosion)
period=0


bigfont = pygame.font.Font(None, 100)
white = 255, 0, 0

#init status and score bars
status1=StatusBar("Shields",(0,255,0),100,(0,0))
status2=StatusBar("Shields",(255,0,0),100,(RESOLUTION[0]-100,0))

score1=StatusBar("Score",(0,255,0),0,(0,20))
score2=StatusBar("Score",(255,0,0),0,(RESOLUTION[0]-100,20))

while 1:
    # USER INPUT
    deltat = clock.tick(20)
    
    for event in pygame.event.get():
        
        if (hasattr(event, 'key') ):
            
           
            down = event.type == KEYDOWN
            
            if event.key == K_RIGHT: car.k_right=down* -2
            elif event.key == K_LEFT: car.k_left = down * 2
            elif event.key == K_UP: car.k_up = down * -2
            elif event.key == K_DOWN: car.k_down = down * 2
            elif event.key == K_MINUS: car.hiper=1
            elif event.key == K_s: car2.k_right=down* -2
            elif event.key == K_a: car2.k_left = down * 2
            elif event.key == K_w: car2.k_up = down * -2
            elif event.key == K_z: car2.k_down = down * 2
            elif event.key == K_x: car2.hiper=1
            elif event.key == K_ESCAPE: sys.exit(0)
            
        if hasattr(event,'joy'):
            #intercept joystick ID = 0
            
            if event.joy==0:
           
        
                if (hasattr(event,'axis')):
                    
                    if int(event.value)==1 and event.axis==0 :car.k_right=-2
                    elif int(event.value)==-1 and event.axis==0 :car.k_left=2
                    elif int(event.value)==-1 and event.axis==1 :car.k_up=-2
                    elif int(event.value)==1 and event.axis==1 :car.k_down=2
                    elif int(event.value)==0 :car.k_right=car.k_left=car.k_up=car.k_down=0
                    
                    
                                
                if hasattr(event,'button'):
                    if event.button==0 : car.hiper=1

            #intercept joystick ID = 1
            if event.joy==1:
           
        
                if (hasattr(event,'axis')):
                    if int(event.value)==1 and event.axis==0 :car2.k_right=-2
                    elif int(event.value)==-1 and event.axis==0 :car2.k_left=2
                    elif int(event.value)==-1 and event.axis==1 :car2.k_up=-2
                    elif int(event.value)==1 and event.axis==1 :car2.k_down=2
                    elif int(event.value)==0 :car2.k_right=car2.k_left=car2.k_up=car2.k_down=0
            
                    #print event.axis
                                
                if hasattr(event,'button'):
                    if event.button==0 : car2.hiper=1
    
    
    # RENDERING
    
    
    #every n secs ad a bomb and an allien!
    period +=1
    if period >100:
        
        pad_group.add(PadSprite((300,300)))
        alien_group.add(AlienSprite((random.randrange(1,RESOLUTION[0],1),random.randrange(1,RESOLUTION[1],1))))
        
        period=0       
       
    animated_group.clear(screen,background)
    
    animated_group.update(pygame.time.get_ticks()) #<-attenzione che qui l'unita di misura e diversa da deltat
    
    car_group.clear(screen, background)
    
    car_group.update(deltat)
    
    
    pad_group.clear(screen,background)
    
    alien_group.clear(screen,background)
    
    for pad in pad_group.sprites():            #muoviamo le bombe perche non usare update?
        pad.move()
    
    for ali in alien_group.sprites():
        ali.move()
    
    collisions = pygame.sprite.groupcollide(car_group, pad_group,0,0,collided=pygame.sprite.collide_mask)
    
    
    for j in collisions.keys():
        
        j.damage +=1
        
        pad_group.update(collisions[j])
    
    aliencides = pygame.sprite.groupcollide(alien_group,pad_group,1,1,collided=pygame.sprite.collide_mask) #if an allien meet a bomb both desappear
    
    alienabord = pygame.sprite.groupcollide(car_group,alien_group,0,0) #if an allien meet a car get in
    
    
    for t in alienabord.keys():
       
        alien_group.update(alienabord[t],t)
    
    
    carcollision = pygame.sprite.spritecollide(car,car_group,0)
    for g in carcollision:
        if g == car2:
            car.caraccident()
            car2.caraccident()
                        
    
    animated_group.draw(screen)
    
    pad_group.draw(screen)
    
    alien_group.draw(screen)
    car_group.draw(screen)
    
    # update scores
    
    status1.update(100-car.damage)
    status2.update(100-car2.damage)
    
    
    score1.update(car.score*3)
    score2.update(car2.score*3)
    
    if car.damage > 100 :
        pygame.sprite.Group.remove(car_group,car)
        
    if car2.damage > 100 :
        car_group.remove(car2)
    
    if car.damage > 100 and car2.damage > 100:
        text = font.render('GAME OVER',True,(255,255,255),(159,182,205))
        textRect=text.get_rect()
        textRect.x=(RESOLUTION[0]/2)
        textRect.y=(RESOLUTION[1]/2)
        screen.blit(text,textRect)       
    
    if car.score >=100:
	winner('GREEN CAR WINS !!')
    if car2.score >=100:
	winner('RED CAR WINS!!')
    	
	    
    pygame.display.flip()
    
    if not(pygame.mixer.music.get_busy()):
        #print "Music loop start again...."
        play_music(music_file)

