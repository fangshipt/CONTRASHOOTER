import pygame
from pygame import mixer
import sys
import os
import random
import csv
import button
import math
from collections import deque

def read_level_data(filename):
    """
    Đọc dữ liệu level từ file CSV.
    Mỗi hàng trong file được chuyển thành một list số nguyên.
    """
    grid = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            grid.append([int(x) for x in row])
    return grid

def is_safe(x, y, grid):
    """
    Kiểm tra ô (x,y) có an toàn để đi qua hay không.
    An toàn nếu:
      - Giá trị ô không phải là nước (9,10)
      - Nếu ô nằm ở hàng cuối (y == ROWS-1), thì giá trị không được là -1 (pit)
    """
    val = grid[y][x]
    if val in (9, 10):
        return False
    if y == ROWS - 1 and val == -1:
        return False
    return True

def bfs(start, goal, grid):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán BFS.
    Cho phép di chuyển theo cả 2 hướng:
      - Di chuyển “bình thường” theo hàng ngang và dọc với bước = 1 ô.
      - Di chuyển “nhảy” xa: xét các bước nhảy theo hàng ngang và dọc (tối đa 4 ô).
        Trong trường hợp nhảy, các ô trung gian phải là ô nguy hiểm (không an toàn)
        và ô hạ cánh phải an toàn.
    Trả về đường đi (danh sách các ô từ start đến goal) hoặc None nếu không tìm được.
    """
    def get_neighbors(node):
        x, y = node
        neighbors = []

        # Hướng ngang: sang phải và sang trái
        for dx in range(1, 5):  # xét từ 1 đến 4 ô bên phải
            candidate_x = x + dx
            if candidate_x >= COLS:
                break
            if dx == 1:
                # Di chuyển liền kề
                if is_safe(candidate_x, y, grid):
                    neighbors.append((candidate_x, y))
            else:
                # Với bước nhảy xa: các ô trung gian phải không an toàn (nguy hiểm)
                jump_possible = True
                for step in range(1, dx):
                    if is_safe(x + step, y, grid):
                        jump_possible = False
                        break
                if jump_possible and is_safe(candidate_x, y, grid):
                    neighbors.append((candidate_x, y))
        for dx in range(1, 5):  # xét từ 1 đến 4 ô bên trái
            candidate_x = x - dx
            if candidate_x < 0:
                break
            if dx == 1:
                if is_safe(candidate_x, y, grid):
                    neighbors.append((candidate_x, y))
            else:
                jump_possible = True
                for step in range(1, dx):
                    if is_safe(x - step, y, grid):
                        jump_possible = False
                        break
                if jump_possible and is_safe(candidate_x, y, grid):
                    neighbors.append((candidate_x, y))
                    
        # Hướng dọc: xuống và lên
        for dy in range(1, 5):  # xét từ 1 đến 4 ô xuống
            candidate_y = y + dy
            if candidate_y >= ROWS:
                break
            if dy == 1:
                if is_safe(x, candidate_y, grid):
                    neighbors.append((x, candidate_y))
            else:
                jump_possible = True
                for step in range(1, dy):
                    if is_safe(x, y + step, grid):
                        jump_possible = False
                        break
                if jump_possible and is_safe(x, candidate_y, grid):
                    neighbors.append((x, candidate_y))
        for dy in range(1, 5):  # xét từ 1 đến 4 ô lên
            candidate_y = y - dy
            if candidate_y < 0:
                break
            if dy == 1:
                if is_safe(x, candidate_y, grid):
                    neighbors.append((x, candidate_y))
            else:
                jump_possible = True
                for step in range(1, dy):
                    if is_safe(x, y - step, grid):
                        jump_possible = False
                        break
                if jump_possible and is_safe(x, candidate_y, grid):
                    neighbors.append((x, candidate_y))
        return neighbors

    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            # Xây dựng lại đường đi từ goal về start
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current
    return None

# Khởi tạo pygame
mixer.init()
pygame.init()

# Thiết lập màn hình và các hằng số
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")

clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1  # Bắt đầu từ level 1

# Trạng thái trò chơi
start_game = False
start_intro = False
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Tải âm thanh
pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("audio/shot.wav")
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.7)

# Tải hình ảnh nền
# Tải hình ảnh nền cho level 1
pine1_level1_img = pygame.image.load("img/Background/pine1.png").convert_alpha()
pine2_level1_img = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountain_level1_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_level1_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()

# Tải hình ảnh nền cho level 2 trở đi
pine1_level2_img = pygame.image.load("img/Background2/pine1.png").convert_alpha()
pine2_level2_img = pygame.image.load("img/Background2/pine2.png").convert_alpha()
mountain_level2_img = pygame.image.load("img/Background2/mountain.png").convert_alpha()
sky_level2_img = pygame.image.load("img/Background2/sky_cloud.png").convert_alpha()

# Lưu các bộ background vào một dictionary để dễ quản lý
backgrounds = {
    "level1": {
        "sky": sky_level1_img,
        "mountain": mountain_level1_img,
        "pine1": pine1_level1_img,
        "pine2": pine2_level1_img
    },
    "level2_up": {
        "sky": sky_level2_img,
        "mountain": mountain_level2_img,
        "pine1": pine1_level2_img,
        "pine2": pine2_level2_img
    }
}

# Tải hình ảnh nút
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()

# Tải hình ảnh ô (tile)
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Tải hình ảnh vật phẩm
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

# Định nghĩa màu sắc
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Font chữ
font = pygame.font.SysFont("Futura", 30)

# Hàm vẽ văn bản
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Hàm vẽ nền
def draw_bg():
    screen.fill(BG)
    # Chọn bộ background dựa trên level
    bg_set = backgrounds["level2_up"] if level >= 2 else backgrounds["level1"]
    
    width = bg_set["sky"].get_width()
    for x in range(5):
        screen.blit(bg_set["sky"], ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(bg_set["mountain"], ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - bg_set["mountain"].get_height() - 300))
        screen.blit(bg_set["pine1"], ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - bg_set["pine1"].get_height() - 150))
        screen.blit(bg_set["pine2"], ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - bg_set["pine2"].get_height()))

# Hàm reset level
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

# Lớp Soldier (bao gồm cả player và enemy)
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

        # Tải animation
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

        if not self.alive:
            self.kill()
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

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

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

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

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < world.level_length * TILE_SIZE - SCREEN_WIDTH) \
               or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        global level
        if self.shoot_cooldown == 0:
            # Nếu ở level 1: cooldown là 20 (cả player và enemy)
            # Nếu ở level 2: cooldown của enemy là 15, player vẫn là 20
            self.shoot_cooldown = 15 if self.char_type == "enemy" and level >= 2 else 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), 
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            if self.char_type != "enemy":
                self.ammo -= 1
            shot_fx.play()

    def ai(self):
        global level
        if not self.alive or not player.alive:
            return

        distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx,
                                        self.rect.centery - player.rect.centery)
        VISION_RANGE = TILE_SIZE * 6

        if distance_to_player <= VISION_RANGE:
            self.chasing = True

        if self.chasing:
            start = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
            goal = (player.rect.centerx // TILE_SIZE, player.rect.centery // TILE_SIZE)
            path = bfs(start, goal, world_data)

            moving = False
            if path and len(path) > 1:
                next_cell = path[1]
                target_x = next_cell[0] * TILE_SIZE + TILE_SIZE // 2
                target_y = next_cell[1] * TILE_SIZE + TILE_SIZE // 2

                if abs(next_cell[0] - start[0]) > 1 or abs(next_cell[1] - start[1]) > 1:
                    self.jump = True
                elif target_y < self.rect.centery and not self.in_air:
                    self.jump = True

                if self.rect.centerx < target_x:
                    self.move(moving_left=False, moving_right=True)
                    self.direction = 1
                    moving = True
                elif self.rect.centerx > target_x:
                    self.move(moving_left=True, moving_right=False)
                    self.direction = -1
                    moving = True
                else:
                    self.move(moving_left=False, moving_right=False)

                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                if self.vision.colliderect(player.rect):
                    self.shoot()
                    # Chỉ ở level 2 trở lên, enemy mới ném lựu đạn
                    if level >= 2:
                        now_time = pygame.time.get_ticks()
                        if distance_to_player < TILE_SIZE * 5 and self.grenades > 0:
                            if now_time - self.grenade_time > random.randint(1000, 1500):
                                grenade_ = Grenade(self.rect.centerx, self.rect.centery, self.direction)
                                grenade_group.add(grenade_)
                                self.grenade_time = now_time
                                self.grenades -= 1
            else:
                self.move(moving_left=False, moving_right=False)

            if self.in_air:
                self.update_action(2)
            elif moving:
                self.update_action(1)
            else:
                self.update_action(0)
        else:
            self.move(moving_left=False, moving_right=False)

        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
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

# Lớp ItemBox
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

# Lớp HealthBar
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

# Lớp Bullet
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
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

# Lớp Grenade
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
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.8)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
               abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

# Lớp World
class World():
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data, current_level):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if (tile >= 0 and tile <= 8) or tile == 12:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile in [11, 13, 14]:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        # Tốc độ enemy phụ thuộc vào level
                        enemy_speed = 2 if current_level == 1 else 3.5
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, enemy_speed, 20, 5)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit_ = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

# Các lớp hỗ trợ khác
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

# Khởi tạo các đối tượng
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 50, restart_img, 1)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Tải dữ liệu level 1 ban đầu
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f"level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)

world = World()
player, health_bar = world.process_data(world_data, level)

# Vòng lặp chính
run = True
while run:
    clock.tick(FPS)

    if not start_game:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        health_bar.draw(player.health)
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

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

        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade_ = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                   player.rect.top, player.direction)
                grenade_group.add(grenade_)
                player.grenades -= 1
                grenade_thrown = True

            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                start_intro = True
                level += 1  # Tăng level để chuyển sang level tiếp theo
                if level <= MAX_LEVELS:
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f"level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, level)
                else:
                    # Nếu vượt quá số level tối đa, hiển thị màn hình chiến thắng
                    draw_text("YOU WIN!", font, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
                    pygame.display.update()
                    pygame.time.wait(2000)
                    run = False

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f"level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, level)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_space:
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
            if event.key == pygame.K_space:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()