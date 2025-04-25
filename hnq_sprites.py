import pygame
import os
import button
import csv
import hnq_settings as settings
from hnq_settings import screen, GRAVITY, SCREEN_WIDTH, SCROLL_THRESH, SCREEN_HEIGHT, TILE_SIZE, ROWS, COLS
from hnq_deco import Explosion, Decoration, Exit, Water, ScreenFade
from hnq_astar import a_star
from hnq_draw import draw_bg, draw_text, reset_level
import math
import sys

# Khởi tạo các biến trạng thái
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Đảm bảo biến scroll trong module settings
settings.screen_scroll = 0
settings.bg_scroll = 0

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.chasing = False
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.grenade_time = pygame.time.get_ticks()

        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            temp_list = []
            num_frames = len(os.listdir(f"img/{char_type}/{animation}"))
            for i in range(num_frames):
                img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if not self.alive:
            self.kill()
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx, dy = 0, 0
        scroll = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Va chạm với obstacle
        for tile in world.obstacle_list:
            # ngang
            if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # đứng
            if tile[1].colliderect(self.rect.x, self.rect.y+dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                else:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Nước
        if pygame.sprite.spritecollide(self, settings.water_group, False):
            self.health = 0
        # Exit
        level_complete = False
        if pygame.sprite.spritecollide(self, settings.exit_group, False):
            level_complete = True
        # Rơi khỏi map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Giới hạn trong player
        if self.char_type == 'player':
            if self.rect.left+dx < 0 or self.rect.right+dx > SCREEN_WIDTH:
                dx = 0

        # Cập nhật vị trí
        self.rect.x += dx
        self.rect.y += dy

        # Scroll màn hình
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and settings.bg_scroll < world.level_length*TILE_SIZE) or \
               (self.rect.left < SCROLL_THRESH and settings.bg_scroll > 0):
                self.rect.x -= dx
                scroll = -dx

        return scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown==0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75*self.rect.size[0]*self.direction),
                            self.rect.centery, self.direction)
            settings.bullet_group.add(bullet)
            if self.char_type != 'enemy':
                self.ammo -= 1
            settings.shot_fx.play()

    def ai(self):
        if not self.alive or not player.alive:
            return
        # Khoảng cách
        dist = math.hypot(self.rect.centerx-player.rect.centerx,
                          self.rect.centery-player.rect.centery)
        if dist <= TILE_SIZE*6:
            self.chasing = True
        moving = False
        if self.chasing:
            start = (self.rect.centerx//TILE_SIZE, self.rect.centery//TILE_SIZE)
            goal  = (player.rect.centerx//TILE_SIZE, player.rect.centery//TILE_SIZE)
            path = a_star(start, goal, world_data)
            if path and len(path)>1:
                next_cell = path[1]
                tx = next_cell[0]*TILE_SIZE + TILE_SIZE//2
                ty = next_cell[1]*TILE_SIZE + TILE_SIZE//2
                # Nhảy
                if abs(next_cell[0]-start[0])>1 or abs(next_cell[1]-start[1])>1:
                    self.jump = True
                elif ty < self.rect.centery and not self.in_air:
                    self.jump = True
                # Di chuyển
                if self.rect.centerx < tx:
                    dx, _ = self.move(False, True)
                    self.direction = 1
                    moving=True
                elif self.rect.centerx > tx:
                    dx, _ = self.move(True, False)
                    self.direction=-1
                    moving=True
                else:
                    dx, _ = self.move(False, False)
                self.vision.center = (self.rect.centerx+75*self.direction,
                                      self.rect.centery)
                if self.vision.colliderect(player.rect):
                    self.shoot()
            else:
                dx, _ = self.move(False, False)
        else:
            dx, _ = self.move(False, False)
        # Animation
        if self.in_air:
            self.update_action(2)
        elif moving:
            self.update_action(1)
        else:
            self.update_action(0)
        # Ứng dụng scroll
        self.rect.x += settings.screen_scroll

    def update_animation(self):
        ANIM_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIM_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index+=1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action==3:
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action!=self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <=0:
            self.health=0
            self.speed=0
            self.alive=False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = settings.item_boxes.get(item_type)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE//2, y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x += settings.screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type=='Health':
                player.health = min(player.max_health, player.health+25)
            elif self.item_type=='Ammo':
                player.ammo +=15
            elif self.item_type=='Grenade':
                player.grenades +=3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x, self.y = x, y
        self.max_health = max_health
    def draw(self, health):
        ratio = health/self.max_health
        pygame.draw.rect(screen, settings.BLACK, (self.x-2,self.y-2,154,24))
        pygame.draw.rect(screen, settings.RED,   (self.x,self.y,150,20))
        pygame.draw.rect(screen, settings.GREEN, (self.x,self.y,150*ratio,20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = settings.bullet_img
        self.rect  = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    def update(self):
        self.rect.x += self.direction*self.speed + settings.screen_scroll
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, settings.bullet_group, False):
            if player.alive:
                player.health -=5
                self.kill()
        for enemy in settings.enemy_group:
            if pygame.sprite.spritecollide(enemy, settings.bullet_group, False):
                if enemy.alive:
                    enemy.health -=25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = settings.grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
        self.width, self.height = self.image.get_width(), self.image.get_height()
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction*self.speed
        dy = self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction*self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y+dy, self.width, self.height):
                self.speed = 0
                if self.vel_y <0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                else:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
        self.rect.x += dx + settings.screen_scroll
        self.rect.y += dy
        self.timer -=1
        if self.timer<=0:
            self.kill()
            settings.screengrenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y,0.8)
            settings.explosion_group.add(explosion)
            # sát thương
            if abs(self.rect.centerx-player.rect.centerx)<TILE_SIZE*2 and abs(self.rect.centery-player.rect.centery)<TILE_SIZE*2:
                player.health -=50
            for enemy in settings.enemy_group:
                if abs(self.rect.centerx-enemy.rect.centerx)<TILE_SIZE*2 and abs(self.rect.centery-enemy.rect.centery)<TILE_SIZE*2:
                    enemy.health -=50

class World():
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0
    def process_data(self, data):
        self.level_length = len(data[0])
        player_obj = None
        health_bar = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = settings.img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    if (tile >=0 and tile <=8) or tile==12:
                        self.obstacle_list.append((img, img_rect))
                    elif tile in [9,10]:
                        water = Water(img, img_rect.x, img_rect.y)
                        settings.water_group.add(water)
                    elif tile in [11,13,14]:
                        deco = Decoration(img, img_rect.x, img_rect.y)
                        settings.decoration_group.add(deco)
                    elif tile==15:
                        player_obj = Soldier('player', img_rect.x, img_rect.y, 1.65,5,20,5)
                        health_bar = HealthBar(10,10, player_obj.health, player_obj.health)
                    elif tile==16:
                        enemy = Soldier('enemy', img_rect.x, img_rect.y,1.65,2,20,5)
                        settings.enemy_group.add(enemy)
                    elif tile==17:
                        box = ItemBox('Ammo', img_rect.x, img_rect.y)
                        settings.item_box_group.add(box)
                    elif tile==18:
                        box = ItemBox('Grenade', img_rect.x, img_rect.y)
                        settings.item_box_group.add(box)
                    elif tile==19:
                        box = ItemBox('Health', img_rect.x, img_rect.y)
                        settings.item_box_group.add(box)
                    elif tile==20:
                        ex = Exit(img, img_rect.x, img_rect.y)
                        settings.exit_group.add(ex)
        return player_obj, health_bar
    def draw(self):
        for img, rect in self.obstacle_list:
            # dịch chuyển theo camera
            screen.blit(img, (rect.x + settings.screen_scroll, rect.y))

# Đọc dữ liệu level ban đầu
world_data = [[-1]*COLS for _ in range(ROWS)]
world = World()
player, health_bar = world.process_data(world_data)

# Fade hiệu ứng
intro_fade = ScreenFade(1, settings.BLACK, 4)
death_fade = ScreenFade(2, settings.PINK, 4)

# Nút nhấn
start_button   = button.Button(SCREEN_WIDTH//2-130, SCREEN_HEIGHT//2-150, settings.start_img, 1)
exit_button    = button.Button(SCREEN_WIDTH//2-110, SCREEN_HEIGHT//2+50,  settings.exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH//2-90,  SCREEN_HEIGHT//2-50,  settings.restart_img,1)

# Đọc dữ liệu level hiện tại từ CSV
with open(f"level{settings.level}_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    world_data = []
    for _ in range(ROWS): world_data.append([-1]*COLS)
    csvfile.seek(0)
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

# Vòng lặp chính
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
        # Cập nhật và tính scroll
        scroll_val, level_complete = player.move(moving_left, moving_right)
        settings.screen_scroll = scroll_val
        settings.bg_scroll     -= scroll_val

        # Vẽ nền và world
        draw_bg()
        world.draw()

        # HUD
        health_bar.draw(player.health)
        draw_text("AMMO:", settings.font, settings.WHITE, 10, 35)
        for i in range(player.ammo):
            screen.blit(settings.bullet_img, (90 + i*10, 40))
        draw_text("GRENADES:", settings.font, settings.WHITE, 10, 60)
        for i in range(player.grenades):
            screen.blit(settings.grenade_img, (135 + i*15, 60))

        # Cập nhật nhân vật và enemy
        player.update()
        player.draw()
        for enemy in settings.enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # Nhóm sprite khác
        settings.bullet_group.update()
        settings.grenade_group.update()
        settings.explosion_group.update()
        settings.item_box_group.update()
        settings.decoration_group.update()
        settings.water_group.update()
        settings.exit_group.update()

        settings.bullet_group.draw(screen)
        settings.grenade_group.draw(screen)
        settings.explosion_group.draw(screen)
        settings.item_box_group.draw(screen)
        settings.decoration_group.draw(screen)
        settings.water_group.draw(screen)
        settings.exit_group.draw(screen)

        # Intro fade
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Xử lý bắn/ném
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades>0:
                g = Grenade(player.rect.centerx + 0.5*player.rect.size[0]*player.direction,
                            player.rect.top, player.direction)
                settings.grenade_group.add(g)
                player.grenades -= 1
                grenade_thrown = True

            # Chọn animation player
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)

            # Nếu lên level mới
            if level_complete:
                start_intro = True
                settings.bg_scroll = 0
                settings.level += 1
                if settings.level <= settings.MAX_LEVELS:
                    world_data = reset_level()
                    with open(f"level{settings.level}_data.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            # Player chết
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    settings.bg_scroll = 0
                    settings.screen_scroll = 0
                    world_data = reset_level()
                    with open(f"level{settings.level}_data.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    # Sự kiện người dùng
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a: moving_left = True
            if event.key == pygame.K_d: moving_right = True
            if event.key == pygame.K_SPACE: shoot = True
            if event.key == pygame.K_q: grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                settings.jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()