import hnq_settings as settings
import csv

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
    if y == settings.ROWS - 1 and val == -1:
        return False
    return True

def a_star(start, goal, grid):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán A*.
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
            if candidate_x >= settings.COLS:
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
            if candidate_y >= settings.ROWS:
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

    open_set = set([start])
    came_from = {}
    g_score = {start: 0}
    # Sử dụng khoảng cách Manhattan làm heuristic
    f_score = {start: abs(goal[0] - start[0]) + abs(goal[1] - start[1])}

    while open_set:
        current = min(open_set, key=lambda node: f_score.get(node, float("inf")))
        if current == goal:
            # Xây dựng lại đường đi từ goal về start
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        open_set.remove(current)
        for neighbor in get_neighbors(current):
            # Tính chi phí di chuyển:
            # Nếu di chuyển liền kề thì chi phí = 1, nếu là nhảy xa thì chi phí = khoảng cách (số ô)
            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])
            move_cost = dx if dx > dy else dy  # vì chỉ di chuyển theo hàng ngang hoặc dọc
            if move_cost == 0:
                move_cost = 1
            tentative_g_score = g_score[current] + move_cost
            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                open_set.add(neighbor)
    return None
