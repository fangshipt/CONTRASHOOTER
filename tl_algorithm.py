import csv
import heapq
from tl_setting import rows, cols

def read_level_data(filename):
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
      - Nếu ô nằm ở hàng cuối (y == rows-1), thì giá trị không được là -1 (pit)
    """
    val = grid[y][x]
    if val in (9, 10):
        return False
    if y == rows - 1 and val == -1:
        return False
    return True

def a_star(start, goal, grid):
    def get_neighbors(node):
        x, y = node
        neighbors = []
        for dx in range(1, 5):
            candidate_x = x + dx
            if candidate_x >= cols:
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
        for dx in range(1, 5): 
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
        for dy in range(1, 5):  
            candidate_y = y + dy
            if candidate_y >= rows:
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
        for dy in range(1, 5): 
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
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        open_set.remove(current)
        for neighbor in get_neighbors(current):
            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])
            move_cost = dx if dx > dy else dy 
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
    def get_neighbors(node):
        x, y = node
        neighbors = []
        for dx in range(1, 5): 
            candidate_x = x + dx
            if candidate_x >= cols:
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
        for dx in range(1, 5): 
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
        for dy in range(1, 5):  
            candidate_y = y + dy
            if candidate_y >= rows:
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
        for dy in range(1, 5): 
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
            path = [current]
            while current in came_from and came_from[current] is not None:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        for neighbor in get_neighbors(current):
            if neighbor not in came_from:  
                queue.append(neighbor)
                came_from[neighbor] = current
    return None

def beam_search(start, goal, grid, beam_width=5):
    def get_neighbors(node):
        x, y = node
        neighbors = []
        for dx in range(1, 5):  
            candidate_x = x + dx
            if candidate_x >= cols:
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
        for dx in range(1, 5):  
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

        for dy in range(1, 5): 
            candidate_y = y + dy
            if candidate_y >= rows:
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
        for dy in range(1, 5):  
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
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
    queue = [[start]]
    visited = set([start])

    while queue:
        new_queue = []
        for path in queue:
            current = path[-1]
            if current == goal:
                return path  

            neighbors = get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_queue.append(new_path)

        new_queue.sort(key=lambda p: heuristic(p[-1]))
        queue = new_queue[:beam_width]
    return None 

def backtracking_search(start, goal, grid):
    def get_valid_moves_for_backtracking(node, current_path_as_set):
        x, y = node
        potential_moves = []
        for i in range(1, 5):  
            candidate_x_r = x + i
            if candidate_x_r < cols:
                target_r = (candidate_x_r, y)
                if target_r not in current_path_as_set:
                    if i == 1: 
                        if is_safe(candidate_x_r, y, grid):
                            potential_moves.append(target_r)
                    else: 
                        jump_possible = True
                        for step in range(1, i): 
                            if is_safe(x + step, y, grid):
                                jump_possible = False
                                break
                        if jump_possible and is_safe(candidate_x_r, y, grid):
                            potential_moves.append(target_r)
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
        for i in range(1, 5):
            candidate_y_d = y + i
            if candidate_y_d < rows:
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
        potential_moves.sort(key=lambda move: (abs(move[0] - goal[0]) + abs(move[1] - goal[1])))
        return potential_moves
    stack = [(start, [start])]
    MAX_PATH_LENGTH = rows + cols + 20 
    while stack:
        current_node, path = stack.pop()
        if len(path) > MAX_PATH_LENGTH:
            continue
        if current_node == goal:
            return path 
        valid_moves = get_valid_moves_for_backtracking(current_node, set(path))
        for move in reversed(valid_moves):
            new_path = path + [move]
            stack.append((move, new_path))       
    return None 

def ida_star_search(start, goal, grid): 
    def heuristic(node): 
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
    def get_neighbors_with_cost_ida(node):
        x, y = node
        neighbors_data = []
        for dx_direction in [1, -1]: 
            for dist in range(1, 5): 
                candidate_x = x + dx_direction * dist
                if not (0 <= candidate_x < cols): break 
                cost = dist 
                if dist == 1: 
                    if is_safe(candidate_x, y, grid): neighbors_data.append(((candidate_x, y), cost))
                else: 
                    jump_possible = True
                    for step in range(1, dist): 
                        intermediate_x = x + dx_direction * step
                        if is_safe(intermediate_x, y, grid): jump_possible = False; break
                    if jump_possible and is_safe(candidate_x, y, grid): neighbors_data.append(((candidate_x, y), cost))
        for dy_direction in [1, -1]: 
            for dist in range(1, 5):  
                candidate_y = y + dy_direction * dist
                if not (0 <= candidate_y < rows): break
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
        h_val = heuristic(current_node) 
        f_cost = g_cost + h_val
        if f_cost > current_bound_val:
            return f_cost, None 
        if current_node == goal: 
            return "FOUND", path
        min_exceeded_f_cost = float('inf')
        sorted_neighbors_data = sorted(
            get_neighbors_with_cost_ida(current_node),
            key=lambda item: heuristic(item[0]) 
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
    if not is_safe(start[0], start[1], grid) or not is_safe(goal[0], goal[1], grid):
        return None 
    active_bound = heuristic(start)
    while True:
        path_for_this_iteration = [start] 
        status, final_path_nodes = search_recursive_ida(path_for_this_iteration, 0, active_bound)
        if status == "FOUND":
            return final_path_nodes 
        if not isinstance(status, (int, float)) or status == float('inf'):
            return None
        active_bound = status

#### UCS
def is_safe(x, y, grid):
    if not grid: return False
    actual_rows = len(grid)
    if actual_rows == 0: return False
    actual_cols = len(grid[0])
    if not (0 <= y < actual_rows and 0 <= x < actual_cols):
        return False
    val = grid[y][x]
    if val in (9, 10): return False 
    if y == actual_rows - 1 and val == -1: return False 
    return True
def is_safe_for_ucs_intermediate_jump_check(x, y, grid): 
    val = grid[y][x]
    if val in (9, 10, -1): 
        return False 
    return True 
def ucs_search(start, goal, grid):
    def get_neighbors_with_cost_ucs(node):
        x, y = node
        neighbors_data = []
        for dx_direction in [1, -1]: 
            for dist in range(0, 4): 
                candidate_x = x + dx_direction * dist
                if not (0 <= candidate_x <= cols + 1): 
                    break 
                cost = dist 
                if dist <= 1: 
                    if is_safe(candidate_x, y, grid):
                        neighbors_data.append(((candidate_x, y), cost))
                else: 
                    jump_possible = True
                    for step in range(0, dist): 
                        intermediate_x = x + dx_direction * step
                        if is_safe(intermediate_x, y, grid): 
                            jump_possible = False; break
                    if jump_possible: 
                        neighbors_data.append(((candidate_x, y), cost))
        for dy_direction in [1, -1]: 
            for dist in range(1, 5):  
                candidate_y = y + dy_direction * dist
                if not (0 <= candidate_y <= rows + 1): break
                cost = dist
                if dist == 2: 
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
    if not is_safe(start[0], start[1], grid) or not is_safe(goal[0], goal[1], grid):
        return None 
    open_set_pq = [] 
    heapq.heappush(open_set_pq, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while open_set_pq:
        current_cost, current_node = heapq.heappop(open_set_pq)
        if current_node == goal:
            path = [current_node]
            temp_node = current_node
            while came_from[temp_node] is not None:
                temp_node = came_from[temp_node]
                path.append(temp_node)
            path.reverse()
            return path

        for neighbor_node, move_cost in get_neighbors_with_cost_ucs(current_node):
            new_cost = cost_so_far[current_node] + move_cost
            if neighbor_node not in cost_so_far or new_cost < cost_so_far[neighbor_node]:
                cost_so_far[neighbor_node] = new_cost
                heapq.heappush(open_set_pq, (new_cost, neighbor_node))
                came_from[neighbor_node] = current_node
    return None 