screen_width = 800
screen_height = int(screen_width * 0.8)
FPS = 60
gravity = 0.75
scroll_thresh = 200
rows = 16
cols = 150
tile_size = screen_height // rows
tile_types = 21
max_levels = 2
screen_scroll = 0
bg_scroll = 0
level = 1  

# Trạng thái trò chơi
start_game  = False    
start_intro = False   
selection_time = 0
# selected_algorithm = None # This is initialized to None where it's first used or can be here
move_left = False
move_right = False
shoot = False
grenade = False
grenade_thrown = False
# Biến lưu thuật toán được chọn
selected_algorithm = None # Explicitly initialized here

# Định nghĩa màu sắc
bg = (144, 201, 120)
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)
pink = (235, 65, 54) # For death fade

# Khoảng cách giữa các nút 
spacing        = 20 # Vertical spacing between menu buttons
exit_spacing   = 40 # Extra spacing before the exit button in menu