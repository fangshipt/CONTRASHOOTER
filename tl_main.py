import pygame
from pygame import mixer
import sys
import os
import random
import csv
import button
import math
from tl_setting import *
from tl_algorithm import *

mixer.init()
pygame.init()

game_window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("CONTRA SHOOTER")
game_clock = pygame.time.Clock()

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
pine1_level1_img = pygame.image.load("img/Background1/pine1.png").convert_alpha()
pine2_level1_img = pygame.image.load("img/Background1/pine2.png").convert_alpha()
mountain_level1_img = pygame.image.load("img/Background1/mountain.png").convert_alpha()
sky_level1_img = pygame.image.load("img/Background1/sky_cloud.png").convert_alpha()

pine1_level2_img = pygame.image.load("img/Background2/pine1.png").convert_alpha()
pine2_level2_img = pygame.image.load("img/Background2/pine2.png").convert_alpha()
mountain_level2_img = pygame.image.load("img/Background2/mountain.png").convert_alpha()
sky_level2_img = pygame.image.load("img/Background2/sky_cloud.png").convert_alpha()

stage_sceneries = {
    "level1": {
        "sky": sky_level1_img,
        "mountain": mountain_level1_img,
        "pine1": pine1_level1_img,
        "pine2": pine2_level1_img
    },
    "level2": {
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
beamsearch_img = pygame.image.load("img/start_BeamSearch_btn.png").convert_alpha()
bfs_img = pygame.image.load("img/start_BFS_btn.png").convert_alpha()
astar_img = pygame.image.load("img/start_AStar_btn.png").convert_alpha()
backtracking_img = pygame.image.load("img/start_Backtracking_btn.png").convert_alpha()
ucssearch_img = pygame.image.load("img/start_UCSSearch_btn.png").convert_alpha()
idastar_img = pygame.image.load("img/start_IDAStar_btn.png").convert_alpha()

# Tải hình ảnh ô (tile)
tile_graphics_list = []
for x in range(tile_types):
    tile_graphic = pygame.image.load(f"img/tile/{x}.png")
    tile_graphic = pygame.transform.scale(tile_graphic, (tile_size, tile_size))
    tile_graphics_list.append(tile_graphic)

# Tải hình ảnh vật phẩm
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenade_img_icon = pygame.image.load("img/icons/grenade.png").convert_alpha()
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
pickup_graphics = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}

# Font chữ
font = pygame.font.SysFont("Courier New", 25)
small_font = pygame.font.SysFont('Courier New', 20)  

# Vẽ văn bản
def draw_text(text_content, font, text_color, x, y):
    img = font.render(text_content, True, text_color)
    game_window.blit(img, (x, y))
# Vẽ nền
def render_stage_scenery():
    game_window.fill(bg)
    bg_set = stage_sceneries["level2"] if level >= 2 else stage_sceneries["level1"]
    width = bg_set["sky"].get_width()
    for x in range(5):
        game_window.blit(bg_set["sky"], ((x * width) - bg_scroll * 0.5, 0))
        game_window.blit(bg_set["mountain"], ((x * width) - bg_scroll * 0.6, screen_height - bg_set["mountain"].get_height() - 300))
        game_window.blit(bg_set["pine1"], ((x * width) - bg_scroll * 0.7, screen_height - bg_set["pine1"].get_height() - 150))
        game_window.blit(bg_set["pine2"], ((x * width) - bg_scroll * 0.8, screen_height - bg_set["pine2"].get_height()))

# Hàm reset level
def reset_level():
    foe_squad.empty()
    projectile_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    supply_crate_group.empty()
    decoration_group.empty()
    water_group.empty()
    stage_portal_group.empty()
    data = []
    for row in range(rows):
        r = [-1] * cols
        data.append(r)
    return data

class GameCharacter(pygame.sprite.Sprite):
    def __init__(self, character_role, x, y, visual_scale, move_speed, ammo_count, explosive_count):
        super().__init__()
        self.is_operational = True
        self.role = character_role
        self.movement_velocity = move_speed
        self.chasing = False
        self.ammunition = ammo_count
        self.initial_ammunition = ammo_count
        self.shoot_cooldown = 0
        self.grenades = explosive_count
        self.health = 100
        self.max_health = self.health
        self.facing = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_frames_collection = []
        self.current_animation_frame = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.perception_zone = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.grenade_time = pygame.time.get_ticks()

        # Tải animation
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for anim_type in animation_types:
            frame_list = []
            num_of_frames = len(os.listdir(f"img/{character_role}/{anim_type}"))
            for i in range(num_of_frames):
                char_img = pygame.image.load(f"img/{character_role}/{anim_type}/{i}.png").convert_alpha()
                char_img = pygame.transform.scale(char_img, (int(char_img.get_width() * visual_scale), int(char_img.get_height() * visual_scale)))
                frame_list.append(char_img)
            self.animation_frames_collection.append(frame_list)
        self.image = self.animation_frames_collection[self.action][self.current_animation_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.process_animation()
        self.check_alive()
        if not self.is_operational:
            self.kill()
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def relocate(self, move_left, move_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        if move_left:
            dx = -self.movement_velocity
            self.flip = True
            self.facing = -1
        if move_right:
            dx = self.movement_velocity
            self.flip = False
            self.facing = 1
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        for tile in world.solid_barriers:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.role == "enemy":
                    self.facing *= -1
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
        if pygame.sprite.spritecollide(self, stage_portal_group, False):
            level_complete = True
        if self.rect.bottom > screen_height:
            self.health = 0
        if self.role == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
                dx = 0
        self.rect.x += dx
        self.rect.y += dy
        if self.role == "player":
            if (self.rect.right > screen_width - scroll_thresh and bg_scroll < world.level_length * tile_size - screen_width) \
               or (self.rect.left < scroll_thresh and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def shoot(self):
        global level
        if self.shoot_cooldown == 0:
            if self.role != "enemy" and self.ammunition <= 0:
                return
            self.shoot_cooldown = 15 if self.role == "enemy" and level >= 2 else 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.facing), 
                            self.rect.centery, self.facing)
            projectile_group.add(bullet)
            if self.role != "enemy":
                self.ammunition -= 1
            shot_fx.play()

    def ai(self):
        global level
        if not self.is_operational or not player.is_operational:
            return
        distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx,
                                        self.rect.centery - player.rect.centery)
        detection_radius = tile_size * 6
        if distance_to_player <= detection_radius:
            self.chasing = True
        if self.chasing:
            start = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
            goal = (player.rect.centerx // tile_size, player.rect.centery // tile_size)

            if selected_algorithm == "Beam Search":
                path = beam_search(start, goal, world_data)
            elif selected_algorithm == "BFS":
                path = bfs(start, goal, world_data)
            elif selected_algorithm == "A*":
                path = a_star(start, goal, world_data)
            elif selected_algorithm == "Backtracking":
                path = backtracking_search(start, goal, world_data)
            elif selected_algorithm == "UCS Search":
                path = ucs_search(start, goal, world_data)
            elif selected_algorithm == "IDA*":
                path = ida_star_search(start, goal, world_data)
            else:
                path = None 

            moving = False
            if path and len(path) > 1:
                next_cell = path[1]
                destination_x = next_cell[0] * tile_size + tile_size // 2
                destination_y = next_cell[1] * tile_size + tile_size // 2

                if abs(next_cell[0] - start[0]) > 1 or abs(next_cell[1] - start[1]) > 1:
                    self.jump = True
                elif destination_y < self.rect.centery and not self.in_air:
                    self.jump = True

                if self.rect.centerx < destination_x:
                    self.relocate(move_left=False, move_right=True)
                    self.facing = 1
                    moving = True
                elif self.rect.centerx > destination_x:
                    self.relocate(move_left=True, move_right=False)
                    self.facing = -1
                    moving = True
                else:
                    self.relocate(move_left=False, move_right=False)
                self.perception_zone.center = (self.rect.centerx + 75 * self.facing, self.rect.centery)

                if self.perception_zone.colliderect(player.rect):
                    self.shoot()
                    if level >= 2:
                        current_time = pygame.time.get_ticks()
                        if distance_to_player < tile_size * 5 and self.grenades > 0:
                            if current_time - self.grenade_time > random.randint(1000, 1500):
                                thrown_bomb = Grenade(self.rect.centerx, self.rect.centery, self.facing)
                                grenade_group.add(thrown_bomb)
                                self.grenade_time = current_time
                                self.grenades -= 1
            else:
                self.relocate(move_left=False, move_right=False)

            if self.in_air:
                self.update_action(2)
            elif moving:
                self.update_action(1)
            else:
                self.update_action(0)
        else:
            self.relocate(move_left=False, move_right=False)

        self.rect.x += screen_scroll

    def process_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_frames_collection[self.action][self.current_animation_frame]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.current_animation_frame += 1
        if self.current_animation_frame >= len(self.animation_frames_collection[self.action]):
            if self.action == 3:
                self.current_animation_frame = len(self.animation_frames_collection[self.action]) - 1
            else:
                self.current_animation_frame = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.current_animation_frame = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.movement_velocity = 0
            self.is_operational = False
            self.update_action(3)

    def draw(self):
        game_window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class SupplyCrateObject(pygame.sprite.Sprite):
    def __init__(self, crate_content_type, x, y):
        super().__init__()
        self.content_type = crate_content_type
        self.image = pickup_graphics.get(self.content_type)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.content_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.content_type == "Ammo":
                player.ammunition += 15
            elif self.content_type == "Grenade":
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
        pygame.draw.rect(game_window, black, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(game_window, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(game_window, green, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, flight_direction_val):
        super().__init__()
        self.movement_velocity = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.facing = flight_direction_val

    def update(self):
        self.rect.x += (self.facing * self.movement_velocity) + screen_scroll
        for tile in world.solid_barriers:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, projectile_group, False):
            if player.is_operational:
                player.health -= 5
                self.kill()
        for enemy in foe_squad:
            if pygame.sprite.spritecollide(enemy, projectile_group, False):
                if enemy.is_operational:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.movement_velocity = 7
        self.image = grenade_img_icon
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.facing = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += gravity
        dx = self.facing * self.movement_velocity
        dy = self.vel_y
        for tile in world.solid_barriers:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.facing *= -1
                dx = self.facing * self.movement_velocity
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.movement_velocity = 0
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
            if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and \
               abs(self.rect.centery - player.rect.centery) < tile_size * 2:
                player.health -= 50
            for enemy in foe_squad:
                if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < tile_size * 2:
                    enemy.health -= 50

class LevelStageManager():
    def __init__(self):
        self.solid_barriers = []
        self.level_length = 0

    def process_data(self, data, current_level):
        self.level_length = len(data[0])
        for y, map_row in enumerate(data):
            for x, tile_code in enumerate(map_row):
                if tile_code >= 0:
                    img = tile_graphics_list[tile_code]
                    tile_rect = img.get_rect()
                    tile_rect.x = x * tile_size
                    tile_rect.y = y * tile_size
                    tile_data = (img, tile_rect)
                    if (tile_code >= 0 and tile_code <= 8) or tile_code == 12:
                        self.solid_barriers.append(tile_data)
                    elif tile_code >= 9 and tile_code <= 10:
                        water = Water(img, x * tile_size, y * tile_size)
                        water_group.add(water)
                    elif tile_code in [11, 13, 14]:
                        scenery_item = Decoration(img, x * tile_size, y * tile_size)
                        decoration_group.add(scenery_item)
                    elif tile_code == 15:
                        player = GameCharacter("player", x * tile_size, y * tile_size, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile_code == 16:
                        foe_move_speed = 2 if current_level == 1 else 3.5
                        enemy = GameCharacter("enemy", x * tile_size, y * tile_size, 1.65, foe_move_speed, 20, 5)
                        foe_squad.add(enemy)
                    elif tile_code == 17:
                        supply_crate = SupplyCrateObject("Ammo", x * tile_size, y * tile_size)
                        supply_crate_group.add(supply_crate)
                    elif tile_code == 18:
                        supply_crate = SupplyCrateObject("Grenade", x * tile_size, y * tile_size)
                        supply_crate_group.add(supply_crate)
                    elif tile_code == 19:
                        supply_crate = SupplyCrateObject("Health", x * tile_size, y * tile_size)
                        supply_crate_group.add(supply_crate)
                    elif tile_code == 20:
                        exit_ = Exit(img, x * tile_size, y * tile_size)
                        stage_portal_group.add(exit_)
        return player, health_bar

    def draw(self):
        for barrier_tile in self.solid_barriers:
            barrier_tile[1][0] += screen_scroll
            game_window.blit(barrier_tile[0], barrier_tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, prop_image, x, y):
        super().__init__()
        self.image = prop_image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, water_image, x, y):
        super().__init__()
        self.image = water_image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, portal_image, x, y):
        super().__init__()
        self.image = portal_image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for frame_num in range(1, 6):
            blast_img = pygame.image.load(f"img/explosion/exp{frame_num}.png").convert_alpha()
            blast_img = pygame.transform.scale(blast_img, (int(blast_img.get_width() * scale), int(blast_img.get_height() * scale)))
            self.images.append(blast_img)
        self.current_animation_frame = 0
        self.image = self.images[self.current_animation_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    def update(self):
        self.rect.x += screen_scroll
        explosion_speed = 4
        self.counter += 1
        if self.counter >= explosion_speed:
            self.counter = 0
            self.current_animation_frame += 1
            if self.current_animation_frame >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.current_animation_frame]

class ScreenTransitionEffect():
    def __init__(self, direction, color, speed):
        self.facing = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0
    def fade(self):
        is_transition_complete = False
        self.fade_counter += self.speed
        if self.facing == 1:
            pygame.draw.rect(game_window, self.color, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
            pygame.draw.rect(game_window, self.color, (screen_width // 2 + self.fade_counter, 0, screen_width, screen_height))
            pygame.draw.rect(game_window, self.color, (0, 0 - self.fade_counter, screen_width, screen_height // 2))
            pygame.draw.rect(game_window, self.color, (0, screen_height // 2 + self.fade_counter, screen_width, screen_height))
        if self.facing == 2:
            pygame.draw.rect(game_window, self.color, (0, 0, screen_width, 0 + self.fade_counter))
        if self.fade_counter >= screen_width:
            is_transition_complete = True
        return is_transition_complete

# Khởi tạo các đối tượng
intro_fade = ScreenTransitionEffect(1, black, 4)
death_fade = ScreenTransitionEffect(2, pink, 4)
restart_button = button.Button(screen_width // 2 - 90, screen_height // 2 - 50, restart_img, 1)
################
'''button_width      = beamsearch_img.get_width()
button_height      = beamsearch_img.get_height()
exit_button_width     = exit_img.get_width()
exit_button_height     = exit_img.get_height()'''
column_spacing = 50  
row_spacing = 20     
exit_spacing = 40    

# Lấy kích thước của các nút
beam_w = beamsearch_img.get_width()
beam_h = beamsearch_img.get_height()
bfs_w = bfs_img.get_width()
bfs_h = bfs_img.get_height()
astar_w = astar_img.get_width()
astar_h = astar_img.get_height()
backtracking_w = backtracking_img.get_width()
backtracking_h = backtracking_img.get_height()
ucssearch_w = ucssearch_img.get_width()
ucssearch_h = ucssearch_img.get_height()
idastar_w = idastar_img.get_width()
idastar_h = idastar_img.get_height()
exit_w = exit_img.get_width()
exit_h = exit_img.get_height()


column1_width = max(beam_w, bfs_w)
column2_width = max(astar_w, backtracking_w)
column3_width = max(ucssearch_w, idastar_w)


total_width = column1_width + column2_width + column3_width + 2 * column_spacing


start_x = (screen_width - total_width) // 2

# Tính chiều cao của hàng (dựa trên nút cao nhất trong mỗi hàng)
row1_height = max(beam_h, astar_h, ucssearch_h)
row2_height = max(bfs_h, backtracking_h, idastar_h)
#####
group_height = (
   row1_height + row2_height +  
    row_spacing +             
    exit_spacing +              
    exit_h              
)
start_y = (screen_height - group_height) // 2

column1_x = start_x
column2_x = column1_x + column1_width + column_spacing
column3_x = column2_x + column2_width + column_spacing

# Tọa độ x cho từng nút (căn giữa trong cột của nó)
beam_x = column1_x + (column1_width - beam_w) // 2
bfs_x = column1_x + (column1_width - bfs_w) // 2
astar_x = column2_x + (column2_width - astar_w) // 2
backtracking_x = column2_x + (column2_width - backtracking_w) // 2
ucssearch_x = column3_x + (column3_width - ucssearch_w) // 2
idastar_x = column3_x + (column3_width - idastar_w) // 2
exit_x = (screen_width - exit_w) // 2

# Tọa độ y cho các hàng
row1_y = start_y
row2_y = row1_y + row1_height + row_spacing
exit_y = row2_y + row2_height + exit_spacing

# Khởi tạo các nút
start_beamsearch_button = button.Button(beam_x, row1_y, beamsearch_img, 1)
start_bfs_button = button.Button(bfs_x, row2_y, bfs_img, 1)
start_astar_button = button.Button(astar_x, row1_y, astar_img, 1)
start_backtracking_button = button.Button(backtracking_x, row2_y, backtracking_img, 1)
start_ucssearch_button = button.Button(ucssearch_x, row1_y, ucssearch_img, 1)
start_idastar_button = button.Button(idastar_x, row2_y, idastar_img, 1)
exit_button = button.Button(exit_x, exit_y, exit_img, 1)


menu_exit_button_graphic = exit_img
in_game_exit_scale = 0.5
ingame_exit_button_graphic = pygame.transform.rotozoom(menu_exit_button_graphic, 0, in_game_exit_scale)
# Khởi tạo 
in_game_exit_btn = button.Button(
    screen_width - ingame_exit_button_graphic.get_width() - 10,  
    60,                                            
    ingame_exit_button_graphic,
    1
)
foe_squad = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
supply_crate_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
stage_portal_group = pygame.sprite.Group()

# Tải dữ liệu level 1 ban đầu
world_data = []
for row in range(rows):
    r = [-1] * cols
    world_data.append(r)

with open(f"level{level}.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)

world = LevelStageManager()
player, health_bar = world.process_data(world_data, level)

# Vòng lặp chính
run = True
while run:
    game_clock.tick(FPS)
    if start_intro:
        game_window.fill(bg)
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        game_window.blit(overlay, (0,0))
        algorithm_info_message = f"Selected: {selected_algorithm}"
        msg_width, msg_height = font.size(algorithm_info_message)
        msg_x = screen_width  // 2 - msg_width // 2
        msg_y = screen_height // 2 - msg_height // 2
        draw_text(algorithm_info_message, font, (255,255,0), msg_x, msg_y)
        if pygame.time.get_ticks() - selection_time > 1000:
            start_intro = False
            start_game  = True
    elif not start_game:
        game_window.fill(bg)
        menu_title_content = "CHOOSE ALGORITHM:"
        title_w, title_h = font.size(menu_title_content)
        title_x = (screen_width - title_w) // 2
        title_y = start_y - title_h - 20
        draw_text(menu_title_content, font, white, title_x, title_y)

        # Vẽ các nút
        if start_beamsearch_button.draw(game_window):
            selected_algorithm = "Beam Search"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if start_bfs_button.draw(game_window):
            selected_algorithm = "BFS"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if start_astar_button.draw(game_window):
            selected_algorithm = "A*"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if start_backtracking_button.draw(game_window):
            selected_algorithm = "Backtracking"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if start_ucssearch_button.draw(game_window):
            selected_algorithm = "UCS Search"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if start_idastar_button.draw(game_window):
            selected_algorithm = "IDA*"
            start_intro = True
            selection_time = pygame.time.get_ticks()
        if exit_button.draw(game_window):
            run = False

    else:
        render_stage_scenery()
        world.draw()
        health_bar.draw(player.health)
        draw_text("AMMO: ", font, white, 10, 35)
        for x in range(player.ammunition):
            game_window.blit(bullet_img, (90 + (x * 10), 40))
        draw_text("GRENADES: ", font, white, 10, 60)
        for x in range(player.grenades):
            game_window.blit(grenade_img_icon, (135 + (x * 15), 60))
        foes_on_stage_count = len(foe_squad)
        draw_text(f"ENEMIES: {foes_on_stage_count}", font, white, 10, 85)
        exit_rect = in_game_exit_btn.rect
        margin    = 0   
        line_spc   = 2 
        label_text = " Algorithm:"
        label_width, label_height     = font.size(label_text)
        selected_algo_name_content = selected_algorithm
        name_width, name_height    = font.size(selected_algo_name_content)
        total_h = label_height + line_spc + name_height 
        start_y = exit_rect.y - margin - total_h
        label_x = exit_rect.x + (exit_rect.width  - label_width) // 2
        label_y = start_y
        draw_text(label_text, small_font, white, label_x, label_y)
        name_x = exit_rect.x + (exit_rect.width  - name_width) // 2
        name_y = label_y + label_height + line_spc
        draw_text(selected_algo_name_content, small_font, white, name_x, name_y)
        if in_game_exit_btn.draw(game_window):
            start_game = False
            start_intro = False
            selected_algorithm = None
            level = 1  
            bg_scroll = 0

            # Đặt lại level
            world_data = reset_level()
            with open(f"level{level}.csv", newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for y, row in enumerate(reader):
                    for x, tile in enumerate(row):
                        world_data[y][x] = int(tile)

            world = LevelStageManager()
            player, health_bar = world.process_data(world_data, level)
        player.update()
        player.draw()
        for foe_unit in foe_squad:
            foe_unit.ai()
            foe_unit.update()
            foe_unit.draw()

        projectile_group.update()
        grenade_group.update()
        explosion_group.update()
        supply_crate_group.update()
        decoration_group.update()
        water_group.update()
        stage_portal_group.update()

        projectile_group.draw(game_window)
        grenade_group.draw(game_window)
        explosion_group.draw(game_window)
        supply_crate_group.draw(game_window)
        decoration_group.draw(game_window)
        water_group.draw(game_window)
        stage_portal_group.draw(game_window)
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        if player.is_operational:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade_ = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.facing),
                                   player.rect.top, player.facing)
                grenade_group.add(grenade_)
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)
            elif move_left or move_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.relocate(move_left, move_right)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1  
                if level <= max_levels:
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f"level{level}.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = LevelStageManager()
                    player, health_bar = world.process_data(world_data, level)
                else:
                    draw_text("YOU WIN!", font, white, screen_width // 2 - 100, screen_height // 2)
                    pygame.display.update()
                    pygame.time.wait(2000)
                    run = False

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(game_window):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f"level{level}.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for y, row in enumerate(reader):
                            for x, tile in enumerate(row):
                                world_data[y][x] = int(tile)
                    world = LevelStageManager()
                    player, health_bar = world.process_data(world_data, level)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.is_operational:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()