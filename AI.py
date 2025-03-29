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
level = 1

# --- AI CODE ---
# Thay vì chờ người chơi, ta để AI điều khiển.
# Vẫn khai báo các biến này, nhưng sẽ được set trong hàm auto_control_player().
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

start_game = False
start_intro = False

pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("audio/shot.wav")
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.7)

pine1_img = pygame.image.load("img/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()

start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

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

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

font = pygame.font.SysFont("Futura", 30)

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
        if self.jump and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Xử lý va chạm tile
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

        # Nước
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Cửa ra
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # Rơi khỏi map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Giữ player trong màn hình (nếu là player)
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        # Cuộn màn hình
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < world.level_length * TILE_SIZE - SCREEN_WIDTH) \
               or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        # AI của địch (đã có sẵn)
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                now_time = pygame.time.get_ticks()
                dist = math.sqrt((abs(self.rect.centerx - player.rect.centerx))**2 + (abs(self.rect.centery - player.rect.centery))**2)
                # Quăng lựu đạn nếu ở gần
                if dist < TILE_SIZE * 5:
                    if self.grenades > 0:
                        if now_time - self.grenade_time > random.randint(2000, 3000):
                            self.update_action(0)
                            self.grenade_time = pygame.time.get_ticks()
                            grenade_ = Grenade(self.rect.centerx, self.rect.centery, self.direction)
                            grenade_group.add(grenade_)
                            self.grenades -= 1

                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                        self.idling_counter = 50
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

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
        self.in_air = True  # Thêm cờ này để tránh spam logic

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

class World():
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 5)
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
player, health_bar = world.process_data(world_data)


# --- AI CODE ---
def auto_control_player(player, enemy_group, world):
    """
    Hàm AI đơn giản:
    1) Luôn di chuyển sang phải
    2) Nếu thấy enemy đủ gần, bắn
    3) Nếu sắp đụng obstacle, nhảy
    4) Ngẫu nhiên ném lựu đạn
    """
    global moving_left, moving_right, shoot, grenade, grenade_thrown

    # Mặc định
    moving_left = False
    moving_right = True
    shoot = False
    grenade = False

    # 1) Kiểm tra khoảng cách enemy
    for enemy in enemy_group:
        dist_x = abs(enemy.rect.centerx - player.rect.centerx)
        # Nếu enemy ở phía trước và đủ gần thì bắn
        if enemy.rect.centerx > player.rect.centerx and dist_x < 300:
            shoot = True
            break  # bắn 1 thằng thôi, tránh bị override

    # 2) Nếu sắp đụng obstacle ngay trước mặt, thì nhảy
    #    Ta quét 1 hình chữ nhật nhỏ phía trước player.
    #    Nếu rect đó va chạm tile -> nhảy
    player_ahead_rect = pygame.Rect(
        player.rect.x + 20 * player.direction,  # một chút phía trước
        player.rect.y,
        player.width,
        player.height
    )
    for tile in world.obstacle_list:
        if tile[1].colliderect(player_ahead_rect):
            if not player.in_air:
                player.jump = True
            break

    # 3) Ngẫu nhiên ném lựu đạn cho vui (tỷ lệ 1/300 mỗi frame)
    if random.randint(1, 300) == 1 and player.grenades > 0:
        grenade = True
        grenade_thrown = False


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

        # Hiệu ứng fade intro
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # --- AI CODE ---
        # Gọi hàm auto_control_player để set moving_left, moving_right, shoot, grenade
        if player.alive:
            auto_control_player(player, enemy_group, world)

            # Xử lý bắn và ném lựu đạn theo cờ AI
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade_ = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                   player.rect.top, player.direction)
                grenade_group.add(grenade_)
                player.grenades -= 1
                grenade_thrown = True

            # Chọn animation
            if player.in_air:
                player.update_action(2)  # Jump
            elif moving_left or moving_right:
                player.update_action(1)  # Run
            else:
                player.update_action(0)  # Idle

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f"level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            # Player chết
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
                    player, health_bar = world.process_data(world_data)

    # ---
    # Đoạn này ta *tắt* bắt phím để game tự chơi.
    # Nếu muốn ESC thoát, bạn có thể giữ lại 1 nút thoát.
    # ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        # Giữ lại ESC để thoát
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()
