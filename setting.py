import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
FPS = 60
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 2
screen_scroll = 0
bg_scroll = 0
level = 1  # Bắt đầu từ level 1

# Trạng thái trò chơi
start_game  = False    # đã vào play chưa?
start_intro = False    # đang show intro chưa?
selection_time = 0
selected_algorithm = None
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
# Biến lưu thuật toán được chọn
selected_algorithm = None

# Định nghĩa màu sắc
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)


# Khoảng cách giữa 3 nút thuật toán
spacing        = 20
# Khoảng cách từ nút A* đến Exit
exit_spacing   = 40
