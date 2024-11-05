import time
import psutil
import os
from collections import deque
import sys

class SokobanSolver:
    def __init__(self, weights, maze):
        self.weights = weights
        self.maze = maze
        self.walls = set()
        self.switches = set()
        self.stones = {}
        self.ares_pos = None
        self.maze_height = len(maze)
        self.maze_width = max(len(row) for row in maze)
        self.weight_index = 0
        self.initial_state = self.initialize_state()
        
    def initialize_state(self):
        for y, line in enumerate(self.maze):
            for x, ch in enumerate(line):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '@':
                    self.ares_pos = (x, y)
                elif ch == '+':
                    self.ares_pos = (x, y)
                    self.switches.add((x, y))
                elif ch == '$':
                    self.stones[(x, y)] = self.weights[self.weight_index]
                    self.weight_index += 1
                elif ch == '*':
                    self.stones[(x, y)] = self.weights[self.weight_index]
                    self.switches.add((x, y))
                    self.weight_index += 1
                elif ch == '.':
                    self.switches.add((x, y))
                elif ch == ' ':
                    pass

        return {
            'ares_pos': self.ares_pos,
            'stones': self.stones,
            'actions': [],
            'total_weight': 0
        }

    def check_finish(self, state):
        stones = state['stones']
        return all(pos in self.switches for pos in stones.keys())

    def get_memory(self):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
        return mem

    def dfs_with_depth_limit(self, max_depth):
        start_time = time.time()
        nodes_generated = 0

        stack = deque([(self.initial_state, 0)])  # (state, depth)
        visited = set()

        while stack:
            current_state, depth = stack.pop()
            current_state_key = (current_state['ares_pos'], frozenset(current_state['stones'].items()))
            
            if current_state_key in visited:
                continue
                
            visited.add(current_state_key)
            nodes_generated += 1

            if self.check_finish(current_state):
                end_time = time.time()
                time_taken = (end_time - start_time) * 1000  # in ms
                memory_used = self.get_memory()
                steps = len(current_state['actions'])
                total_weight = current_state['total_weight']
                solution = ''.join(current_state['actions'])
                return steps, total_weight, nodes_generated, time_taken, memory_used, solution

            if depth < max_depth:
                for move, action_char in [((0, 1), 'd'), ((0, -1), 'u'), ((1, 0), 'r'), ((-1, 0), 'l')]:
                    new_ares_x = current_state['ares_pos'][0] + move[0]
                    new_ares_y = current_state['ares_pos'][1] + move[1]
                    
                    if 0 <= new_ares_x < self.maze_width and 0 <= new_ares_y < self.maze_height:
                        if (new_ares_x, new_ares_y) not in self.walls:
                            if (new_ares_x, new_ares_y) in current_state['stones']:
                                new_stone_x = new_ares_x + move[0]
                                new_stone_y = new_ares_y + move[1]
                                if 0 <= new_stone_x < self.maze_width and 0 <= new_stone_y < self.maze_height:
                                    if (new_stone_x, new_stone_y) not in self.walls and (new_stone_x, new_stone_y) not in current_state['stones']:
                                        new_stones = current_state['stones'].copy()
                                        weight = new_stones.pop((new_ares_x, new_ares_y))
                                        new_stones[(new_stone_x, new_stone_y)] = weight
                                        action = action_char.upper()
                                        new_total_weight = current_state['total_weight'] + weight
                                        new_actions = current_state['actions'] + [action]
                                        new_state = {
                                            'ares_pos': (new_ares_x, new_ares_y),
                                            'stones': new_stones,
                                            'actions': new_actions,
                                            'total_weight': new_total_weight
                                        }
                                        stack.append((new_state, depth + 1))
                            else:
                                # Move without pushing
                                action = action_char.lower()
                                new_actions = current_state['actions'] + [action]
                                new_state = {
                                    'ares_pos': (new_ares_x, new_ares_y),
                                    'stones': current_state['stones'],
                                    'actions': new_actions,
                                    'total_weight': current_state['total_weight']
                                }
                                stack.append((new_state, depth + 1))

        return None

    def dfs_search(self):
        max_depth = 1
        while True:
            if max_depth > 1000:
                print("Max depth reached.")
                return None
            result = self.dfs_with_depth_limit(max_depth)
            if result:
                return result
            max_depth += 1

    def bfs_search(self):
        start_time = time.time()
        nodes_generated = 0

        queue = deque([self.initial_state]) 
        visited = set()

        while queue:
            current_state = queue.popleft()
            current_state_key = (current_state['ares_pos'], frozenset(current_state['stones'].items()))
            
            if current_state_key in visited:
                continue
                
            visited.add(current_state_key)
            nodes_generated += 1

            if self.check_finish(current_state):
                end_time = time.time()
                time_taken = (end_time - start_time) * 1000  
                memory_used = self.get_memory()
                steps = len(current_state['actions'])
                total_weight = current_state['total_weight']
                solution = ''.join(current_state['actions'])
                return steps, total_weight, nodes_generated, time_taken, memory_used, solution

            for move, action_char in [((0, 1), 'd'), ((0, -1), 'u'), ((1, 0), 'r'), ((-1, 0), 'l')]:
                new_ares_x = current_state['ares_pos'][0] + move[0]
                new_ares_y = current_state['ares_pos'][1] + move[1]
                
                if 0 <= new_ares_x < self.maze_width and 0 <= new_ares_y < self.maze_height:
                    if (new_ares_x, new_ares_y) not in self.walls:
                        # Move with pushing
                        if (new_ares_x, new_ares_y) in current_state['stones']:
                            new_stone_x = new_ares_x + move[0]
                            new_stone_y = new_ares_y + move[1]
                            if 0 <= new_stone_x < self.maze_width and 0 <= new_stone_y < self.maze_height:
                                if (new_stone_x, new_stone_y) not in self.walls and (new_stone_x, new_stone_y) not in current_state['stones']:
                                    new_stones = current_state['stones'].copy()
                                    weight = new_stones.pop((new_ares_x, new_ares_y))
                                    new_stones[(new_stone_x, new_stone_y)] = weight
                                    action = action_char.upper()
                                    new_total_weight = current_state['total_weight'] + weight
                                    new_actions = current_state['actions'] + [action]
                                    new_state = {
                                        'ares_pos': (new_ares_x, new_ares_y),
                                        'stones': new_stones,
                                        'actions': new_actions,
                                        'total_weight': new_total_weight
                                    }
                                    queue.append(new_state)
                        else:
                            # Move without pushing
                            action = action_char.lower()
                            new_actions = current_state['actions'] + [action]
                            new_state = {
                                'ares_pos': (new_ares_x, new_ares_y),
                                'stones': current_state['stones'],
                                'actions': new_actions,
                                'total_weight': current_state['total_weight']
                            }
                            queue.append(new_state)
        return None


    def solve(self, algo_name):
        if algo_name == 'BFS':
            result = self.bfs_search()
        else:
            result = self.dfs_search()
        if result:
            num_steps, total_weight, nodes_generated, time_taken, memory_used, path = result
            return num_steps, total_weight, nodes_generated, time_taken, memory_used, path
        else:
            return None
        
    def write_output(self, filename, algo_name, steps, total_weight, nodes_generated, time_taken, memory_used, path):
        with open(filename, 'w') as f:
            f.write(f"{algo_name}\n")
            f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
            f.write(f"{path}\n")

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    stone_weights = lines[0]
    maze = lines[1:]
    weights = [int(w) for w in stone_weights.strip().split()]
    maze = [line.rstrip('\n') for line in maze]
    return weights, maze


if __name__ == "__main__":
    algo_name = 'DFS'
    input_dir = 'maze'
    output_dir = 'output/' + f'{algo_name.lower()}'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_file in os.listdir(input_dir):
        print(f"Solving {input_file}...")
        input_filename = os.path.join(input_dir, input_file)
        output_filename = os.path.join(output_dir, f'output-{input_file.strip('.txt')[-2:]}.txt')
        stone_weights, maze = read_input(input_filename)
        solver = SokobanSolver(stone_weights, maze)
        result = solver.solve(algo_name=algo_name)
        if result:
            num_steps, total_weight, nodes_generated, time_taken, memory_used, path = result
            solver.write_output(output_filename, algo_name, num_steps, total_weight, nodes_generated, time_taken, memory_used, path)
        else:
            with open(output_filename, 'w') as f:
                f.write("No solution found.\n")