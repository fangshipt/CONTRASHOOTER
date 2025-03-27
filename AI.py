import pygame
from pygame import mixer
import sys
import os
import random
import csv
import button
import math

mixer.init()
pygame.init()

# ------------------------ CẤU HÌNH CHUNG ------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game - AI for Level 1")

clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

# Ở đây chỉ chạy level 1
level = 1

# Biến cuộn màn hình
screen_scroll = 0
bg_scroll = 0

# Các cờ trạng thái
start_game = False
start_intro = False

# Bật chế độ AI (True: AI tự chơi, False: người chơi dùng phím)
ai_mode = True

# Ẩn/hiện các cờ điều khiển bằng tay (nếu ai_mode=False thì dùng)
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# ------------------------ TẢI ÂM THANH ------------------------
pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("audio/shot.wav")
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.7)

# ------------------------ TẢI ẢNH NỀN ------------------------
pine1_img = pygame.image.load("img/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()

# ------------------------ NÚT BẤM (MENU) ------------------------
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()

# ------------------------ TẢI TILE ------------------------
TILE_TYPES = 21
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# ------------------------ TẢI ICON ------------------------
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()

health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}

# ------------------------ CÁC BIẾN MÀU & FONT ------------------------
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

font = pygame.font.SysFont("Futura", 30)

# ------------------------ HÀM VẼ ------------------------
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

# ------------------------ LỚP SOLDIER (PLAYER/ENEMY) ------------------------
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
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
            num_of_frames = len(os.listdir(f"img/{char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
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
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll_local = 0
        dx = 0
        dy = 0

        # Di chuyển theo cờ
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Nhảy
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Trọng lực
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Va chạm tile
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Va chạm nước
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False
        # Va chạm exit
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # Rơi ra ngoài màn hình
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Giới hạn player không vượt biên màn hình
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Cập nhật vị trí
        self.rect.x += dx
        self.rect.y += dy

        # Xử lý cuộn màn hình
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < world.level_length * TILE_SIZE - SCREEN_WIDTH) \
               or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll_local = -dx

        return screen_scroll_local, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Death
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# ------------------------ CÁC LỚP KHÁC ------------------------
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes.get(self.item_type)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
            elif self.item_type == "Grenade":
                player.grenades += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Va chạm tile
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Va chạm player
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        # Va chạm enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.8)
            explosion_group.add(explosion)
            # Gây sát thương
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
               abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class World():
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.level_length = len(data[0])
        player_ = None
        health_bar_ = None
        for y, row in enumerate(data):
            for x, tile_val in enumerate(row):
                if tile_val >= 0:
                    img = img_list[tile_val]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile_val <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile_val <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile_val <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile_val == 15:
                        # Player
                        player_ = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar_ = HealthBar(10, 10, player_.health, player_.health)
                    elif tile_val == 16:
                        # Enemy
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 5)
                        enemy_group.add(enemy)
                    elif tile_val == 17:
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile_val == 18:
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile_val == 19:
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile_val == 20:
                        exit_ = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_)
        return player_, health_bar_

    def draw(self):
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete

# ------------------------ TẠO ĐỐI TƯỢNG FADER, NÚT ------------------------
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 50, restart_img, 1)

# ------------------------ TẠO NHÓM SPRITE ------------------------
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# ------------------------ LOAD LEVEL 1 ------------------------
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Đọc file CSV (level1_data.csv)
with open("level1_data.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile_val in enumerate(row):
            world_data[y][x] = int(tile_val)

world = World()
player, health_bar = world.process_data(world_data)

# ------------------------ HÀM AI ĐƠN GIẢN ------------------------
def auto_play_logic(player, enemy_group, world):
    """
    Trả về (moving_left, moving_right, shoot, jump, grenade) cho player.
    Quy tắc đơn giản:
      - Luôn di chuyển sang phải
      - Nếu gặp vật cản quá gần, nhảy
      - Nếu có enemy phía trước trong khoảng 300 px, bắn
      - Nếu enemy trong khoảng 150 px, ném lựu
    """
    moving_left = False
    moving_right = True
    shoot = False
    jump = False
    grenade_ = False

    # Tìm enemy gần nhất ở phía trước
    nearest_enemy_dist = 9999
    nearest_enemy = None
    for e in enemy_group:
        dist = e.rect.x - player.rect.x
        if dist > 0 and dist < nearest_enemy_dist:
            nearest_enemy_dist = dist
            nearest_enemy = e

    # Nếu có enemy ở gần, bắn
    if nearest_enemy and nearest_enemy_dist < 300:
        shoot = True
        # Nếu enemy ở quá gần, ném lựu
        if nearest_enemy_dist < 150 and player.grenades > 0:
            grenade_ = True

        # Kiểm tra chênh lệch độ cao
        if abs(nearest_enemy.rect.y - player.rect.y) > 20 and not player.in_air:
            jump = True

    # Kiểm tra chướng ngại vật (obstacle) phía trước
    # Lấy tile trong world.obstacle_list
    for tile_data in world.obstacle_list:
        tile_rect = tile_data[1]
        # Chỉ xét tile phía trước player, ở khoảng cách nhất định
        if tile_rect.x > player.rect.x and (tile_rect.x - player.rect.x) < 60:
            # Nếu tile cao hơn 1 chút so với chân player -> nhảy
            if tile_rect.bottom > player.rect.bottom - 20 and not player.in_air:
                jump = True
                break

    return moving_left, moving_right, shoot, jump, grenade_

# ------------------------ VÒNG LẶP CHÍNH ------------------------
run = True
while run:
    clock.tick(FPS)

    if not start_game:
        # Trang menu
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False

    else:
        # Vẽ background
        draw_bg()
        # Vẽ world
        world.draw()
        # Vẽ thanh máu
        health_bar.draw(player.health)

        # Vẽ HUD đạn, lựu
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        # Cập nhật + vẽ player
        player.update()
        player.draw()

        # Cập nhật + vẽ enemy
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # Cập nhật + vẽ các sprite
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Hiệu ứng fade đầu game
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Nếu player sống
        if player.alive:
            # ------------------------ AI CHO PLAYER ------------------------
            if ai_mode:
                # Bỏ qua input từ phím, thay bằng auto logic
                auto_left, auto_right, auto_shoot, auto_jump, auto_grenade = auto_play_logic(player, enemy_group, world)
                # Gán các cờ
                moving_left = auto_left
                moving_right = auto_right
                if auto_jump and not player.in_air:
                    player.jump = True
                    jump_fx.play()
                if auto_shoot:
                    player.shoot()
                if auto_grenade and not grenade_thrown and player.grenades > 0:
                    grenade_ = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                       player.rect.top, player.direction)
                    grenade_group.add(grenade_)
                    player.grenades -= 1
                    grenade_thrown = True
            # ------------------------ HOẶC DÙNG BÀN PHÍM (nếu ai_mode=False) ------------------------
            else:
                if shoot:
                    player.shoot()
                if grenade and not grenade_thrown and player.grenades > 0:
                    grenade_ = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                       player.rect.top, player.direction)
                    grenade_group.add(grenade_)
                    player.grenades -= 1
                    grenade_thrown = True

            # Cập nhật animation action
            if player.in_air:
                player.update_action(2)  # Jump
            elif moving_left or moving_right:
                player.update_action(1)  # Run
            else:
                player.update_action(0)  # Idle

            # Di chuyển player
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            # Ở đây, nếu level_complete thì coi như xong level 1, ta không chuyển level 2
            if level_complete:
                # Bạn có thể code gì đó để báo "You Win" rồi reset game, hoặc dừng hẳn
                print("Level 1 Complete!")
                # Dừng game
                run = False

        else:
            # Player chết
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open("level1_data.csv", newline="", encoding="utf-8") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile_val in enumerate(row):
                                world_data[y][x] = int(tile_val)
                    # Tạo lại world, player
                    world = World()
                    player, health_bar = world.process_data(world_data)

    # ------------------------ XỬ LÝ SỰ KIỆN ------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        if not ai_mode:  # Nếu tắt AI, dùng bàn phím
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                    jump_fx.play()
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
        else:
            # Trong chế độ AI, bỏ qua input
            pass

    pygame.display.update()

# Kết thúc game
pygame.quit()
sys.exit()
