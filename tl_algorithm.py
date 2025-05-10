import csv
from setting import ROWS, COLS
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
def backtracking_search(start, goal, grid):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán Backtracking.
    Hỗ trợ di chuyển bình thường và nhảy xa.
    Trả về đường đi (danh sách các ô từ start đến goal) hoặc None nếu không tìm được.
    """

    def get_valid_moves_for_backtracking(node, current_path_as_set):
        # Hàm này gần giống get_neighbors của A* và BFS,
        # nhưng nó cần kiểm tra xem nước đi tiếp theo có nằm trong current_path_as_set không
        # để tránh tạo chu trình trong đường đi hiện tại.
        x, y = node
        potential_moves = []

        # Hướng ngang: sang phải và sang trái
        for i in range(1, 5):  # i là khoảng cách di chuyển/nhảy (1 đến 4)
            # Sang phải
            candidate_x_r = x + i
            if candidate_x_r < COLS:
                target_r = (candidate_x_r, y)
                if target_r not in current_path_as_set:
                    if i == 1: # Di chuyển liền kề
                        if is_safe(candidate_x_r, y, grid):
                            potential_moves.append(target_r)
                    else: # Nhảy xa
                        jump_possible = True
                        for step in range(1, i): # Kiểm tra các ô trung gian
                            if is_safe(x + step, y, grid):
                                jump_possible = False
                                break
                        if jump_possible and is_safe(candidate_x_r, y, grid):
                            potential_moves.append(target_r)
            # Sang trái
            candidate_x_l = x - i
            if candidate_x_l >= 0:
                target_l = (candidate_x_l, y)
                if target_l not in current_path_as_set:
                    if i == 1:
                        if is_safe(candidate_x_l, y, grid):
                            potential_moves.append(target_l)
                    else:
                        jump_possible = True
                        for step in range(1, i):
                            if is_safe(x - step, y, grid):
                                jump_possible = False
                                break
                        if jump_possible and is_safe(candidate_x_l, y, grid):
                            potential_moves.append(target_l)
        
        # Hướng dọc: xuống và lên
        for i in range(1, 5):
            # Xuống
            candidate_y_d = y + i
            if candidate_y_d < ROWS:
                target_d = (x, candidate_y_d)
                if target_d not in current_path_as_set:
                    if i == 1:
                        if is_safe(x, candidate_y_d, grid):
                            potential_moves.append(target_d)
                    else:
                        jump_possible = True
                        for step in range(1, i):
                            if is_safe(x, y + step, grid):
                                jump_possible = False
                                break
                        if jump_possible and is_safe(x, candidate_y_d, grid):
                            potential_moves.append(target_d)
            # Lên
            candidate_y_u = y - i
            if candidate_y_u >= 0:
                target_u = (x, candidate_y_u)
                if target_u not in current_path_as_set:
                    if i == 1:
                        if is_safe(x, candidate_y_u, grid):
                            potential_moves.append(target_u)
                    else:
                        jump_possible = True
                        for step in range(1, i):
                            if is_safe(x, y - step, grid):
                                jump_possible = False
                                break
                        if jump_possible and is_safe(x, candidate_y_u, grid):
                            potential_moves.append(target_u)
        
        # Heuristic: Sắp xếp các nước đi để ưu tiên những nước gần goal hơn.
        # Điều này giúp Backtracking tìm ra giải pháp nhanh hơn (nếu có) bằng cách
        # thử các nhánh có vẻ hứa hẹn trước. Nó không làm thay đổi tính đúng đắn
        # của Backtracking nhưng cải thiện hiệu suất trung bình.
        potential_moves.sort(key=lambda move: (abs(move[0] - goal[0]) + abs(move[1] - goal[1])))
        return potential_moves

    # Stack cho Backtracking (DFS): mỗi phần tử là (node, current_path_list)
    stack = [(start, [start])]  # (nút hiện tại, danh sách đường đi đến nút đó)
    
    # Giới hạn độ sâu để ngăn tìm kiếm vô hạn hoặc quá lâu trên bản đồ lớn/phức tạp
    # Bạn có thể điều chỉnh giá trị này
    MAX_PATH_LENGTH = ROWS + COLS + 20 # Một ước lượng, ví dụ: đường đi không quá dài
    # Hoặc một giá trị cố định như 50 hoặc 75
    # MAX_PATH_LENGTH = 75


    while stack:
        current_node, path = stack.pop()

        # Kiểm tra giới hạn độ sâu
        if len(path) > MAX_PATH_LENGTH:
            continue

        if current_node == goal:
            return path # Tìm thấy đường đi

        # Lấy các nước đi hợp lệ từ current_node
        # Chuyển path sang set để kiểm tra 'in' nhanh hơn O(1)
        valid_moves = get_valid_moves_for_backtracking(current_node, set(path))
        
        # Thêm các nước đi mới vào stack.
        # Vì `valid_moves` đã được sắp xếp từ "tốt nhất" đến "tệ nhất" (theo heuristic),
        # và stack là LIFO, chúng ta thêm vào theo thứ tự đảo ngược để
        # nước đi "tốt nhất" được pop ra và thử trước.
        for move in reversed(valid_moves):
            new_path = path + [move]
            stack.append((move, new_path))
            
    return None # Không tìm thấy đường đi