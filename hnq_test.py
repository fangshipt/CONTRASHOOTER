import csv
from setting import ROWS, COLS
import heapq
from collections import defaultdict

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
    if not (0 <= x < COLS and 0 <= y < ROWS):
        return False
    val = grid[y][x]
    if val in (9, 10):
        return False
    if y == ROWS - 1 and val == -1:
        return False
    return True

def can_jump_over(x, y, grid):
    """
    Kiểm tra ô (x,y) có thể nhảy qua được hay không.
    Có thể nhảy qua nếu:
      - Ô là không gian trống (giả sử -2), nước (9, 10), hoặc hố (-1).
    """
    if not (0 <= x < COLS and 0 <= y < ROWS):
        return False
    val = grid[y][x]
    return val in (-2, 9, 10, -1)  # Có thể nhảy qua không gian trống, nước, hố

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

from collections import deque

def bfs(start, goal, grid):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán BFS.
    Cho phép di chuyển theo các hướng "bình thường" và "nhảy xa".
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

    # Khởi tạo hàng đợi BFS
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        # Nếu tìm thấy goal, xây dựng đường đi
        if current == goal:
            path = [current]
            while current in came_from and came_from[current] is not None:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        # Thêm các ô hàng xóm vào hàng đợi
        for neighbor in get_neighbors(current):
            if neighbor not in came_from:  # Đảm bảo không quay lại ô đã duyệt
                queue.append(neighbor)
                came_from[neighbor] = current

    # Nếu không tìm được đường đi
    return None

def heuristic(state, goal, distance):
    """
    Tính heuristic (khoảng cách Manhattan) từ trạng thái hiện tại đến goal.
    Thêm chi phí cho nhảy xa để cân bằng, nhưng không ngăn cản nhảy khi cần.
    """
    manhattan_distance = abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    jump_cost = 3 if distance > 1 else 1  # Chi phí nhảy xa vừa phải
    return manhattan_distance + jump_cost

def and_or_search(start, goal, grid, max_jump=2, max_depth=100):
    """
    AND-OR search trên grid để tìm đường đi từ start đến goal.
    Hỗ trợ di chuyển bình thường (1 ô) và nhảy xa (2–max_jump ô) theo hàng ngang và dọc.
    Cho phép nhảy qua nước, không gian trống, hố khi cần để tiếp cận goal.

    Args:
        start (tuple): Tọa độ bắt đầu (x, y).
        goal (tuple): Tọa độ đích (x, y).
        grid (list): Lưới trò chơi (ma trận 2D).
        max_jump (int): Độ dài tối đa của bước nhảy (mặc định: 2).
        max_depth (int): Độ sâu tối đa để tránh tràn ngăn xếp (mặc định: 100).

    Returns:
        list: Danh sách các ô (tọa độ) từ start đến goal, hoặc None nếu không tìm được.
    """
    def get_neighbors(state):
        x, y = state
        neighbors = []

        # Tất cả các hướng: lên, xuống, trái, phải
        directions = [
            (dx, dy) for dx in range(-max_jump, max_jump + 1) for dy in range(-max_jump, max_jump + 1)
            if (dx != 0 or dy != 0) and abs(dx) <= max_jump and abs(dy) <= max_jump
        ]
        for dx, dy in directions:
            candidate_x, candidate_y = x + dx, y + dy
            if not (0 <= candidate_x < COLS and 0 <= candidate_y < ROWS):
                continue
            distance = abs(dx) if abs(dx) > abs(dy) else abs(dy)
            if distance == 1:
                if is_safe(candidate_x, candidate_y, grid):
                    neighbors.append((candidate_x, candidate_y, distance))
            else:
                jump_possible = True
                for step in range(1, distance):
                    check_x = x + (dx * step // distance)
                    check_y = y + (dy * step // distance)
                    if not can_jump_over(check_x, check_y, grid):
                        jump_possible = False
                        break
                if jump_possible and is_safe(candidate_x, candidate_y, grid):
                    # Ưu tiên nhảy lên (hướng dọc lên) nếu cần
                    if dy < 0 and (dx == 0 or abs(dy) > abs(dx)):
                        neighbors.insert(0, (candidate_x, candidate_y, distance))
                    else:
                        neighbors.append((candidate_x, candidate_y, distance))

        return neighbors

    def and_or_recursive(state, visited, came_from, depth=0):
        """
        Đệ quy AND-OR search:
        - OR node: Chọn neighbor gần goal nhất để tiếp tục.
        - AND node: Đảm bảo điều kiện nhảy được thỏa mãn (xử lý trong get_neighbors).
        """
        if depth > max_depth:
            return None

        if state == goal:
            path = [state]
            current = state
            while current in came_from and came_from[current] is not None:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        if state in visited:
            return None

        visited.add(state)
        neighbors = get_neighbors(state)
        if not neighbors:
            return None

        # Sắp xếp neighbor theo heuristic
        neighbors.sort(key=lambda n: heuristic((n[0], n[1]), goal, n[2]))
        for neighbor in neighbors:
            next_state = (neighbor[0], neighbor[1])
            if next_state not in visited:
                came_from[next_state] = state
                result = and_or_recursive(next_state, visited, came_from, depth + 1)
                if result is not None:
                    return result

        return None

    if not is_safe(start[0], start[1], grid) or not is_safe(goal[0], goal[1], grid):
        return None

    visited = set()
    came_from = {start: None}
    return and_or_recursive(start, visited, came_from)

def beam_search(start, goal, grid, beam_width=5):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán Beam Search.
    Hỗ trợ di chuyển bình thường (bước = 1 ô) và nhảy xa (tối đa 4 ô).
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
                if is_safe(candidate_x, y, grid):
                    neighbors.append((candidate_x, y))
            else:
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

    def heuristic(node):
        # Sử dụng khoảng cách Manhattan làm heuristic
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    # Khởi tạo hàng đợi với đường đi ban đầu chỉ có start
    queue = [[start]]
    visited = set([start])

    while queue:
        new_queue = []
        for path in queue:
            current = path[-1]
            if current == goal:
                return path  # Trả về đường đi nếu đến được goal

            neighbors = get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_queue.append(new_path)

        # Sắp xếp các đường đi mới theo heuristic của nút cuối cùng
        new_queue.sort(key=lambda p: heuristic(p[-1]))
        # Giữ lại chỉ beam_width đường đi tốt nhất
        queue = new_queue[:beam_width]

    return None  # Không tìm được đường đi

