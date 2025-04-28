# hnq_main.py

import pygame
import os
import csv
import sys
import math

import button
import hnq_settings as settings
from hnq_settings import screen, GRAVITY, SCREEN_WIDTH, SCROLL_THRESH, SCREEN_HEIGHT, TILE_SIZE, ROWS, COLS

from hnq_deco import Explosion, Decoration, Exit, Water, ScreenFade
from hnq_astar import a_star
from hnq_draw import draw_bg, draw_text, reset_level


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.chasing = False
        self.ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = 100
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.vision = pygame.Rect(0, 0, 150, 20)

        # load animations
        for anim in ["Idle","Run","Jump","Death"]:
            frames = []
            path = f"img/{char_type}/{anim}"
            for img_file in sorted(os.listdir(path), key=lambda f: int(f.split(".")[0])):
                img = pygame.image.load(os.path.join(path, img_file)).convert_alpha()
                img = pygame.transform.scale(
                    img,
                    (int(img.get_width()*scale), int(img.get_height()*scale))
                )
                frames.append(img)
            self.animation_list.append(frames)

        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect(topleft=(x,y))
        self.width = self.rect.width
        self.height = self.rect.height

    def update(self):
        self.update_animation()
        self.check_alive()
        if not self.alive:
            self.kill()
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = dy = 0
        scroll = 0
        level_complete = False

        # horizontal
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10: self.vel_y = 10
        dy += self.vel_y

        # tile collisions
        for img, tile_rect in world.obstacle_list:
            # x collision
            if tile_rect.colliderect(self.rect.move(dx,0)):
                dx = 0
                if self.char_type=="enemy":
                    self.direction *= -1
            # y collision
            if tile_rect.colliderect(self.rect.move(0,dy)):
                if self.vel_y < 0:
                    dy = tile_rect.bottom - self.rect.top
                    self.vel_y = 0
                else:
                    dy = tile_rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # water kill
        if pygame.sprite.spritecollide(self, settings.water_group, False, collided=pygame.sprite.collide_rect):
            self.health = 0

        # exit
        if pygame.sprite.spritecollide(self, settings.exit_group, False, collided=pygame.sprite.collide_rect):
            level_complete = True

        # fall off screen
        if self.rect.bottom + dy > SCREEN_HEIGHT:
            self.health = 0

        # screen bounds for player
        if self.char_type=="player":
            if self.rect.left+dx < 0 or self.rect.right+dx>SCREEN_WIDTH:
                dx = 0

        # apply movement
        self.rect.x += dx
        self.rect.y += dy

        # scrolling
        if self.char_type=="player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and settings.bg_scroll < world.level_length*TILE_SIZE - SCREEN_WIDTH) \
            or (self.rect.left < SCROLL_THRESH and settings.bg_scroll > abs(dx)):
                self.rect.x -= dx
                scroll = -dx

        return scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown==0 and self.ammo>0:
            self.shoot_cooldown=20
            bx = self.rect.centerx + 0.75*self.rect.width*self.direction
            by = self.rect.centery
            bullet = Bullet(bx,by,self.direction)
            settings.bullet_group.add(bullet)
            if self.char_type=="player":
                self.ammo-=1
            settings.shot_fx.play()

    def ai(self):
        if not self.alive or not player.alive: return

        dist = math.hypot(self.rect.centerx-player.rect.centerx,
                          self.rect.centery-player.rect.centery)
        if dist <= TILE_SIZE*6:
            self.chasing = True

        moving=False
        if self.chasing:
            start = (self.rect.centerx//TILE_SIZE, self.rect.centery//TILE_SIZE)
            goal  = (player.rect.centerx//TILE_SIZE, player.rect.centery//TILE_SIZE)
            path = a_star(start,goal,world_data)
            if path and len(path)>1:
                nxt = path[1]
                tx = nxt[0]*TILE_SIZE + TILE_SIZE//2
                # decide move
                if self.rect.centerx<tx:
                    _,_ = self.move(False,True); moving=True; self.direction=1
                else:
                    _,_ = self.move(True,False); moving=True; self.direction=-1
                # vision rect
                self.vision.center = (self.rect.centerx+75*self.direction, self.rect.centery)
                if self.vision.colliderect(player.rect):
                    self.shoot()
            else:
                _,_ = self.move(False,False)
        else:
            _,_ = self.move(False,False)

        # animation
        if self.in_air:
            self.update_action(2)
        elif moving:
            self.update_action(1)
        else:
            self.update_action(0)

        # follow scroll
        self.rect.x += settings.bg_scroll

    def update_animation(self):
        cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action==3:  # death
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action!=self.action:
            self.action=new_action
            self.frame_index=0
            self.update_time=pygame.time.get_ticks()

    def check_alive(self):
        if self.health<=0:
            self.health=0
            self.speed=0
            self.alive=False
            self.update_action(3)

    def draw(self):
        screen.blit(
            pygame.transform.flip(self.image,self.flip,False),
            self.rect
        )


class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        super().__init__()
        self.item_type=item_type
        self.image=settings.item_boxes[item_type]
        self.rect=self.image.get_rect(topleft=(x,y))

    def update(self):
        self.rect.x += settings.bg_scroll
        if self.rect.colliderect(player.rect):
            if self.item_type=="Health":
                player.health = min(player.max_health, player.health+25)
            elif self.item_type=="Ammo":
                player.ammo += 15
            else:
                player.grenades += 3
            self.kill()


class HealthBar:
    def __init__(self,x,y,max_health):
        self.x=x; self.y=y; self.max_health=max_health

    def draw(self,current):
        ratio = current/self.max_health
        pygame.draw.rect(screen,settings.BLACK,(self.x-2,self.y-2,154,24))
        pygame.draw.rect(screen,settings.RED,  (self.x,self.y,150,20))
        pygame.draw.rect(screen,settings.GREEN,(self.x,self.y,150*ratio,20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.image=settings.bullet_img
        self.rect=self.image.get_rect(center=(x,y))
        self.direction=direction
        self.speed=10

    def update(self):
        self.rect.x += self.direction*self.speed + settings.bg_scroll

        # tile collision
        for img, tile_rect in world.obstacle_list:
            if tile_rect.colliderect(self.rect):
                self.kill()
                return

        # hit player
        if self.rect.colliderect(player.rect) and player.alive:
            player.health -= 5
            self.kill()
            return

        # hit enemies
        for en in settings.enemy_group:
            if self.rect.colliderect(en.rect) and en.alive:
                en.health -= 25
                self.kill()
                return


class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__()
        self.image=settings.grenade_img
        self.rect=self.image.get_rect(center=(x,y))
        self.direction=direction
        self.vel_y=-11
        self.speed=7
        self.timer=100

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction*self.speed
        dy = self.vel_y

        for img, tile_rect in world.obstacle_list:
            if tile_rect.colliderect(self.rect.move(dx,0)):
                self.direction *= -1; dx = self.direction*self.speed
            if tile_rect.colliderect(self.rect.move(0,dy)):
                dy=0; self.vel_y=0

        self.rect.x += dx + settings.bg_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            settings.screengrenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.8)
            settings.explosion_group.add(explosion)
            # damage area
            for ent in [player]+list(settings.enemy_group):
                if self.rect.colliderect(ent.rect.inflate( TILE_SIZE*2, TILE_SIZE*2 )):
                    ent.health -= 50


class World:
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.obstacle_list.clear()
        self.level_length = len(data[0])
        player_obj = None
        hb = None

        for y, row in enumerate(data):
            for x, val in enumerate(row):
                if val < 0: continue
                img = settings.img_list[val]
                rect = img.get_rect(topleft=(x*TILE_SIZE, y*TILE_SIZE))

                if val <= 8 or val ==12:
                    self.obstacle_list.append((img, rect))
                elif val in (9,10):
                    settings.water_group.add(Water(img,rect.x,rect.y))
                elif val in (11,13,14):
                    settings.decoration_group.add(Decoration(img,rect.x,rect.y))
                elif val==15:
                    player_obj = Soldier("player",rect.x,rect.y,1.65,5,20,5)
                    hb = HealthBar(10,10,player_obj.max_health)
                elif val==16:
                    settings.enemy_group.add(Soldier("enemy",rect.x,rect.y,1.65,2,0,0))
                elif val==17:
                    settings.item_box_group.add(ItemBox("Ammo",rect.x,rect.y))
                elif val==18:
                    settings.item_box_group.add(ItemBox("Grenade",rect.x,rect.y))
                elif val==19:
                    settings.item_box_group.add(ItemBox("Health",rect.x,rect.y))
                elif val==20:
                    settings.exit_group.add(Exit(img,rect.x,rect.y))

        return player_obj, hb

    def draw(self):
        for img, rect in self.obstacle_list:
            rect.x += settings.bg_scroll
            screen.blit(img, rect)


# --- KHỞI TẠO ---
world_data = [[-1]*COLS for _ in range(ROWS)]
world = World()
player, health_bar = world.process_data(world_data)

intro_fade = ScreenFade(1, settings.BLACK, 4)
death_fade = ScreenFade(2, settings.PINK, 4)

start_button   = button.Button(SCREEN_WIDTH//2-130, SCREEN_HEIGHT//2-150, settings.start_img, 1)
exit_button    = button.Button(SCREEN_WIDTH//2-110, SCREEN_HEIGHT//2+50,  settings.exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH//2-90,  SCREEN_HEIGHT//2-50,  settings.restart_img,1)

# load level đầu
with open(f"level{settings.level}_data.csv", newline="") as f:
    reader = csv.reader(f, delimiter=",")
    for y,row in enumerate(reader):
        for x,val in enumerate(row):
            world_data[y][x] = int(val)
world = World()
player, health_bar = world.process_data(world_data)

moving_left = moving_right = shoot = grenade = grenade_thrown = False
run = True

while run:
    settings.clock.tick(settings.FPS)

    if not settings.start_game:
        screen.fill(settings.BG)
        if start_button.draw(screen):
            settings.start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        health_bar.draw(player.health)
        # draw ammo & grenades
        draw_text("AMMO:", settings.font, settings.WHITE, 10, 35)
        for i in range(player.ammo):
            screen.blit(settings.bullet_img,(90+i*10,40))
        draw_text("GRENADES:", settings.font, settings.WHITE, 10, 60)
        for i in range(player.grenades):
            screen.blit(settings.grenade_img,(135+i*15,60))

        player.update(); player.draw()
        for en in settings.enemy_group:
            en.ai(); en.update(); en.draw()

        # update & draw all groups
        settings.bullet_group.update(); settings.bullet_group.draw(screen)
        settings.grenade_group.update(); settings.grenade_group.draw(screen)
        settings.explosion_group.update(); settings.explosion_group.draw(screen)
        settings.item_box_group.update(); settings.item_box_group.draw(screen)
        settings.decoration_group.update(); settings.decoration_group.draw(screen)
        settings.water_group.update(); settings.water_group.draw(screen)
        settings.exit_group.update(); settings.exit_group.draw(screen)

        # fade effect
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades>0:
                g = Grenade(
                    player.rect.centerx+0.5*player.rect.width*player.direction,
                    player.rect.top,
                    player.direction
                )
                settings.grenade_group.add(g)
                player.grenades-=1
                grenade_thrown=True

            # player animation
            if player.in_air:        player.update_action(2)
            elif moving_left or moving_right: player.update_action(1)
            else:                    player.update_action(0)

            scroll, done = player.move(moving_left, moving_right)
            settings.bg_scroll += scroll

            if done:
                settings.level+=1
                settings.bg_scroll=0
                world_data = reset_level()
                with open(f"level{settings.level}_data.csv", newline="") as f:
                    reader = csv.reader(f, delimiter=",")
                    for y,row in enumerate(reader):
                        for x,val in enumerate(row):
                            world_data[y][x]=int(val)
                world = World()
                player, health_bar = world.process_data(world_data)
        else:
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter=0
                    settings.bg_scroll=0
                    world_data=reset_level()
                    with open(f"level{settings.level}_data.csv", newline="") as f:
                        reader=csv.reader(f,delimiter=",")
                        for y,row in enumerate(reader):
                            for x,val in enumerate(row):
                                world_data[y][x]=int(val)
                    world=World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False; pygame.quit(); sys.exit()
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_a: moving_left=True
            if event.key==pygame.K_d: moving_right=True
            if event.key==pygame.K_SPACE: shoot=True
            if event.key==pygame.K_q: grenade=True
            if event.key==pygame.K_w and player.alive:
                player.jump=True; settings.jump_fx.play()
            if event.key==pygame.K_ESCAPE: run=False
        if event.type==pygame.KEYUP:
            if event.key==pygame.K_a: moving_left=False
            if event.key==pygame.K_d: moving_right=False
            if event.key==pygame.K_SPACE: shoot=False
            if event.key==pygame.K_q:
                grenade=False; grenade_thrown=False

    pygame.display.update()
