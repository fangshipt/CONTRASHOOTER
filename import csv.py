import csv

def read_level_data(filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            # chuyển các giá trị thành số nguyên
            data.append([int(tile) for tile in row])
    return data

def build_grid(data):
    grid = []
    for row in data:
        grid_row = []
        for tile in row:
            # Giả sử: 0-8 là tile có thể đi, 9 trở lên là chướng ngại vật
            # Ngoài ra, nếu bạn có tile enemy (ví dụ: 16) và exit (ví dụ: 20),
            # bạn có thể quyết định: enemy có thể đi qua (hoặc không) tùy theo logic của game.
            if tile >= 0 and tile <= 8:
                grid_row.append(0)  # ô đi được
            elif tile == 16:
                # Tile enemy: ở đây bạn có thể đặt là 1 để tránh đi qua ô có enemy,
                # hoặc đặt là 0 nếu bạn cho phép đi qua nhưng cần xử lý khác (ví dụ: tránh bị bắn)
                grid_row.append(1)
            else:
                grid_row.append(1)  # coi như chướng ngại vật
        grid.append(grid_row)
    return grid

# Sử dụng:
level_data = read_level_data("level1_data.csv")
grid = build_grid(level_data)
