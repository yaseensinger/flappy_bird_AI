import pygame
import neat
import os
import random 
pygame.font.init()

win_width = 500
win_heingt = 800

bird_img = [pygame.image.load(os.path.join("imgs", "flat.png")), pygame.image.load(os.path.join("imgs", "up.png")), pygame.image.load(os.path.join("imgs", "down.png"))]
lamp_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "lamp.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.jpg")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

stat_font = pygame.font.SysFont("comicsans",40)

class Bird:
    imgs =bird_img
    max_rotation=25
    rot_vel = 20
    animation_time = 5


    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y 
        self.img_count = 0
        self.img = self.imgs[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d>= 16:
            d = 16

        if d < 0:
            d-= 2

        self.y = self.y +d

        if d< 0 or self.y< self.height + 50:
            if self.tilt<self.max_rotation:
                self.tilt = self.max_rotation 
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.animation_time*2:
            self.img = self.imgs[0]
        elif self.img_count < self.animation_time*2:
            self.img = self.imgs[1]
        elif self.img_count < self.animation_time*3:
                self.img = self.imgs[2]
        elif self.img_count < self.animation_time*4:
                self.img = self.imgs[1]
        elif self.img_count == self.animation_time*4 + 1:  
             self.img = self.imgs[0]
             self.img_count = 0
        if self.tilt <= -80:
             self.img = self.imgs[1]
             self.img_count = self.animation_time*2
        
        rotate_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotate_image.get_rect(center =self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotate_image, new_rect.topleft)

    def get_mask(self) :
        return pygame.mask.from_surface(self.img)

class Lamp:
    gap = 200
    vel = 5
    

    def __init__(self,x):
        self.x = x
        self.height =0
        self.gap = 200

        self.top = 0
        self.bottom = 0
        self.lamp_top =  pygame.transform.flip(lamp_img, False, True)
        self.lamp_bottom = lamp_img

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height =random.randrange(50,450)
        self.top = self.height - self.lamp_top.get_height()
        self.bottom = self.height + self.gap

    def draw(self,win):
        win.blit(self.lamp_top,(self.x, self.top))
        win.blit(self.lamp_bottom,(self.x, self.bottom))

    def move(self):
        self.x -= self.vel
    
    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.lamp_top)
        bottom_mask = pygame.mask.from_surface(self.lamp_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset =(self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False

class Base:
    vel = 5
    width = base_img.get_width()
    img = base_img

    def __init__(self,y):
        self.y = y 
        self.x1 = 0
        self.x2= self.width

    def move (self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self,win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def draw_window(win, birds, base, lamps, score) :
    win.blit(bg_img, (0,0))

    for lamp in lamps:
         lamp.draw(win)

    text =stat_font.render("Score: "+ str(score),1,(255,255,255))
    win.blit(text, (win_width - 10 - text.get_width(),10))
    for bird in birds:
          bird.draw(win)
    base.draw(win)
    pygame.display.update()

def main(genoms, config):
    birds = []
    nets =[]
    ge=[]
    for _,g in genoms:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
    base = Base(730)
    lamps = [Lamp(700)]
    win = pygame.display.set_mode((win_width, win_heingt))
    clock = pygame.time.Clock()
    score = 0
    run =True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        lamp_ind= 0
        if len(birds)> 0:
            if len(lamps) > 1 and birds[0].x >lamps[0].x + lamps [0].lamp_top.get_width():
                lamp_ind =1
        else:
            run=False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird.y,abs(bird.y - lamps[lamp_ind].height), abs(bird.y - lamps[lamp_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump()
        rem=[]
        add_lamp = False
        for lamp in lamps:
            for x, bird in enumerate(birds):
                if lamp.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    ge.pop(x)
                    nets.pop(x)
                if not lamp.passed and lamp.x < bird.x:
                        lamp.passed = True
                        add_lamp = True

            if lamp.x + lamp.lamp_top.get_width() < 0:
                rem.append(lamp)
            lamp.move()

        if add_lamp:
            score += 1
            for g in ge:
                g.fitness += 5 
            lamps.append(Lamp(600))
            lamp.move()

        for r in rem:

            lamps.remove(r)
            
        for x, bird in enumerate(birds):
                
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                
                birds.pop(x)
                ge.pop(x)
                nets.pop(x)  

        base.move()
        draw_window(win, birds, base, lamps,score)
          



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet , neat.DefaultStagnation,config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)