import csv
import heapq
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
def ida_star_search(start, goal, grid): # 'goal' ở đây sẽ được hàm heuristic lồng sử dụng
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán IDA*.
    Sử dụng logic get_neighbors tương tự A*, BFS, Beam Search.
    Chi phí di chuyển: liền kề = 1, nhảy = khoảng cách.
    Heuristic: Manhattan distance (sử dụng hàm heuristic lồng bên trong).
    """
    def heuristic(node): 
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
    def get_neighbors_with_cost_ida(node):
        # ... (Nội dung hàm này giữ nguyên như phiên bản đúng trước đó)
        x, y = node
        neighbors_data = []
        # Hướng ngang
        for dx_direction in [1, -1]: 
            for dist in range(1, 5): 
                candidate_x = x + dx_direction * dist
                if not (0 <= candidate_x < COLS): break 
                cost = dist 
                if dist == 1: 
                    if is_safe(candidate_x, y, grid): neighbors_data.append(((candidate_x, y), cost))
                else: 
                    jump_possible = True
                    for step in range(1, dist): 
                        intermediate_x = x + dx_direction * step
                        if is_safe(intermediate_x, y, grid): jump_possible = False; break
                    if jump_possible and is_safe(candidate_x, y, grid): neighbors_data.append(((candidate_x, y), cost))
        # Hướng dọc
        for dy_direction in [1, -1]: 
            for dist in range(1, 5):  
                candidate_y = y + dy_direction * dist
                if not (0 <= candidate_y < ROWS): break
                cost = dist
                if dist == 1: 
                    if is_safe(x, candidate_y, grid): neighbors_data.append(((x, candidate_y), cost))
                else: 
                    jump_possible = True
                    for step in range(1, dist):
                        intermediate_y = y + dy_direction * step
                        if is_safe(x, intermediate_y, grid): jump_possible = False; break
                    if jump_possible and is_safe(x, candidate_y, grid): neighbors_data.append(((x, candidate_y), cost))
        return neighbors_data


    # Hàm đệ quy cho IDA*
    def search_recursive_ida(path, g_cost, current_bound_val):
        current_node = path[-1]
        
        # SỬA Ở ĐÂY: Gọi heuristic(node)
        h_val = heuristic(current_node) 
        f_cost = g_cost + h_val

        if f_cost > current_bound_val:
            return f_cost, None 

        if current_node == goal: # 'goal' ở đây là tham số của ida_star_search
            return "FOUND", path

        min_exceeded_f_cost = float('inf')

        # Sắp xếp neighbors theo heuristic
        # SỬA Ở ĐÂY: Gọi heuristic(node) cho key của sorted
        sorted_neighbors_data = sorted(
            get_neighbors_with_cost_ida(current_node),
            key=lambda item: heuristic(item[0]) # item[0] là neighbor_node
        )

        for neighbor_node, move_cost in sorted_neighbors_data:
            if neighbor_node not in path: 
                path.append(neighbor_node)
                
                result_status, result_path = search_recursive_ida(path, g_cost + move_cost, current_bound_val)
                
                if result_status == "FOUND":
                    return "FOUND", result_path
                
                if isinstance(result_status, (int, float)) and result_status < min_exceeded_f_cost:
                     min_exceeded_f_cost = result_status
                
                path.pop() 

        return min_exceeded_f_cost, None

    # --- Phần chính của IDA* ---
    if not is_safe(start[0], start[1], grid) or not is_safe(goal[0], goal[1], grid):
        return None 

    # SỬA Ở ĐÂY: Gọi heuristic(node)
    active_bound = heuristic(start)
    
    while True:
        # print(f"IDA* trying bound: {active_bound}") # Debugging
        
        path_for_this_iteration = [start] 
        status, final_path_nodes = search_recursive_ida(path_for_this_iteration, 0, active_bound)

        if status == "FOUND":
            return final_path_nodes 
        
        if not isinstance(status, (int, float)) or status == float('inf'):
            return None
        
        active_bound = status
def ucs_search(start, goal, grid):
    """
    Tìm đường đi từ start đến goal trong grid bằng thuật toán Uniform Cost Search (UCS).
    Ưu tiên mở rộng nút có chi phí g(n) (tổng chi phí từ start đến n) thấp nhất.
    Chi phí di chuyển: liền kề = 1, nhảy = khoảng cách.
    """

    def get_neighbors_with_cost_ucs(node):
        """
        Lấy các hàng xóm hợp lệ và chi phí di chuyển đến chúng.
        Tương tự như get_neighbors_with_cost_ida nhưng dành cho UCS.
        Trả về list các tuple: ((neighbor_x, neighbor_y), cost)
        """
        x, y = node
        neighbors_data = []

        # Hướng ngang: sang phải và sang trái
        for dx_direction in [1, -1]: 
            for dist in range(1, 5): 
                candidate_x = x + dx_direction * dist
                
                if not (0 <= candidate_x < COLS): 
                    break 
                cost = dist 
                if dist == 1: 
                    if is_safe(candidate_x, y, grid):
                        neighbors_data.append(((candidate_x, y), cost))
                else: 
                    jump_possible = True
                    for step in range(1, dist): 
                        intermediate_x = x + dx_direction * step
                        if is_safe(intermediate_x, y, grid): 
                            jump_possible = False; break
                    if jump_possible and is_safe(candidate_x, y, grid): 
                        neighbors_data.append(((candidate_x, y), cost))
                        
        # Hướng dọc: xuống và lên
        for dy_direction in [1, -1]: 
            for dist in range(1, 5):  
                candidate_y = y + dy_direction * dist
                if not (0 <= candidate_y < ROWS): break
                cost = dist
                if dist == 1: 
                    if is_safe(x, candidate_y, grid):
                        neighbors_data.append(((x, candidate_y), cost))
                else: 
                    jump_possible = True
                    for step in range(1, dist):
                        intermediate_y = y + dy_direction * step
                        if is_safe(x, intermediate_y, grid): 
                            jump_possible = False; break
                    if jump_possible and is_safe(x, candidate_y, grid): 
                        neighbors_data.append(((x, candidate_y), cost))
        return neighbors_data

    # --- Phần chính của UCS ---
    if not is_safe(start[0], start[1], grid) or not is_safe(goal[0], goal[1], grid):
        return None 

    # Hàng đợi ưu tiên (min-heap) lưu trữ (tổng_chi_phí, nút)
    # Tổng chi phí được dùng để ưu tiên, nên nó đứng đầu tuple.
    open_set_pq = [] # Priority Queue
    heapq.heappush(open_set_pq, (0, start)) # (cost_from_start, node)

    # Dictionary để lưu đường đi ngược từ nút về start
    came_from = {start: None}
    
    # Dictionary để lưu chi phí thấp nhất đã biết từ start đến một nút
    cost_so_far = {start: 0}

    while open_set_pq:
        current_cost, current_node = heapq.heappop(open_set_pq)

        # Nếu đã tìm thấy đường đi đến goal, và đường đi này có chi phí cao hơn
        # một đường đi khác đã được xử lý và cập nhật trong cost_so_far,
        # thì bỏ qua (tuy nhiên, với UCS chuẩn, lần đầu tiên pop goal ra khỏi PQ là tối ưu)
        # Dòng này thường không cần thiết nếu không có heuristic và lần đầu pop goal là tối ưu.
        # if current_cost > cost_so_far.get(current_node, float('inf')):
        #    continue

        if current_node == goal:
            # Xây dựng lại đường đi từ goal về start
            path = [current_node]
            temp_node = current_node
            while came_from[temp_node] is not None:
                temp_node = came_from[temp_node]
                path.append(temp_node)
            path.reverse()
            return path

        for neighbor_node, move_cost in get_neighbors_with_cost_ucs(current_node):
            new_cost = cost_so_far[current_node] + move_cost
            
            # Nếu chưa từng đến neighbor này, hoặc tìm thấy đường đi tốt hơn đến nó
            if neighbor_node not in cost_so_far or new_cost < cost_so_far[neighbor_node]:
                cost_so_far[neighbor_node] = new_cost
                # Ưu tiên trong hàng đợi là new_cost (tổng chi phí từ start)
                heapq.heappush(open_set_pq, (new_cost, neighbor_node))
                came_from[neighbor_node] = current_node
                
    return None # Không tìm thấy đường đi
